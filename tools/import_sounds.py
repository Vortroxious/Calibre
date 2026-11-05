#!/usr/bin/env python3
"""
Builds Calibre's real-recording sounds from CC0 source packs (see CREDITS.md) according to tools/sound_map.json.

  python3 tools/gen_sounds.py                      # synthesized fallbacks for everything
  python3 -I tools/import_sounds.py <src_dir>      # replace mapped events with cuts of the real recordings

<src_dir> holds one folder per pack (<pack>/x/... extracted files), as listed in tools/sound_sources.tsv.
Output: assets/calibre/sounds/real/<event>_<n>.ogg + updated assets/calibre/sounds.json (same event names).
Unreferenced .ogg files are removed afterwards so the jar only ships what is used.
"""
import json
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "common", "src", "main", "resources")  # shared by the neoforge and fabric builds
SND = os.path.join(RES, "assets", "calibre", "sounds")
CACHE = {}


def load(path):
    if path not in CACHE:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        CACHE[path] = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    return CACHE[path]


def pitch(x, semis):
    if not semis:
        return x
    f = 2 ** (semis / 12.0)
    n = int(len(x) / f)
    return np.interp(np.arange(n) * f, np.arange(len(x)), x)


def expand(x, ratio=2.0):
    """Downward expander: pushes the recording's hiss floor down without touching the transients."""
    hop = 256
    n = len(x) // hop
    if n < 8:
        return x
    rms = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1)) + 1e-9
    floor = np.percentile(rms, 15)
    g = np.clip((rms / (floor * 4)) ** ratio, 0.03, 1.0)
    # fast attack, slow release
    sm = np.empty_like(g)
    acc = g[0]
    for i, v in enumerate(g):
        acc = v if v > acc else acc * 0.85 + v * 0.15
        sm[i] = acc
    gain = np.interp(np.arange(len(x)), np.arange(n) * hop + hop / 2, sm)
    return x * gain


def finish(x, kind, gain_db):
    if kind != "shot":
        x = expand(x)
    # trim leading silence (keep 3 ms), trailing below -52 dB (foley) / -64 dB (shots, keep the room tail)
    peak = np.max(np.abs(x)) + 1e-9
    thr = peak * 10 ** ((-64 if kind == "shot" else -52) / 20)
    idx = np.nonzero(np.abs(x) > thr)[0]
    if len(idx):
        x = x[max(0, idx[0] - int(0.003 * SR)): idx[-1] + int(0.01 * SR)]
    # remove DC, fades
    x = x - np.mean(x[: min(len(x), 256)]) * 0
    fi = min(len(x), int(0.002 * SR))
    x[:fi] *= np.linspace(0, 1, fi)
    if kind == "shot":
        n = len(x)
        tail = int(n * 0.45)
        x[n - tail:] *= np.linspace(1, 0, tail) ** 2
        target = 10 ** (-1.0 / 20)
    else:
        fo = min(len(x), int(0.025 * SR))
        x[len(x) - fo:] *= np.linspace(1, 0, fo)
        target = 10 ** (-3.0 / 20)
    x = x / (np.max(np.abs(x)) + 1e-9) * target * 10 ** (min(0, gain_db) / 20)
    if gain_db > 0:  # positive gain = saturate a little (bigger, not just louder)
        g = 10 ** (gain_db / 20)
        x = np.tanh(x * g) / np.tanh(g) * target
    return np.clip(x, -1, 1)


# ------------------------------------------------------------------------------------------------ FPS shot mastering
def _fft_gain(x, gain_fn):
    n = len(x)
    N = 1 << (n - 1).bit_length()
    X = np.fft.rfft(x, N)
    f = np.fft.rfftfreq(N, 1 / SR)
    return np.fft.irfft(X * gain_fn(f), N)[:n]


def _db(v):
    return 10 ** (v / 20)


def master_shot(x, st, mech=None, seed=0):
    """
    Turns a raw field recording into a game-style gunshot:
    EQ (low shelf body + presence bite) -> transient boost -> sub thump layer -> optional action clack ->
    outdoor reverb/echo tail -> saturation driven to a target crest factor -> ceiling -> exponential tail fade.
    """
    rng = np.random.default_rng(seed)
    x = x.astype(float)
    # trim leading silence
    pk = np.max(np.abs(x)) + 1e-9
    idx = np.nonzero(np.abs(x) > pk * _db(-40))[0]
    if len(idx):
        x = x[max(0, idx[0] - int(0.002 * SR)):]
    x = x / (np.max(np.abs(x)) + 1e-9)
    # EQ
    ls, pr = _db(st["low_shelf_db"]), _db(st["presence_db"])
    x = _fft_gain(x, lambda f: (1 + (ls - 1) / (1 + (f / 150.0) ** 4))
                  * (1 + (pr - 1) * np.exp(-(np.log2(np.maximum(f, 1) / 3000.0) ** 2) / (2 * 0.6 ** 2))))
    # transient boost around the main peak
    p = int(np.argmax(np.abs(x)))
    t = (np.arange(len(x)) - p) / SR
    tg = np.where(t < 0, 1.0, 1.0 + (_db(st["transient_db"]) - 1) * np.exp(-np.maximum(t, 0) / 0.012))
    x = x * tg
    # sub thump (sine sweep), aligned to the crack
    n_sub = int(st["sub_decay"] * 6 * SR)
    ts = np.arange(n_sub) / SR
    freq = st["sub_end"] + (st["sub_f0"] - st["sub_end"]) * np.exp(-ts / 0.025)
    sub = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-ts / st["sub_decay"]) * (1 - np.exp(-ts / 0.0015))
    out = np.zeros(max(len(x), p + n_sub) + int(st["verb_len"] * SR))
    out[:len(x)] += x
    out[p:p + n_sub] += sub * np.max(np.abs(x)) * _db(st["sub_db"])
    # mechanical action clack
    if mech is not None and st.get("mech_db") is not None:
        d = p + int(st.get("mech_delay", 0.03) * SR)
        m = mech / (np.max(np.abs(mech)) + 1e-9) * np.max(np.abs(x)) * _db(st["mech_db"])
        out[d:d + len(m)] += m[:len(out) - d]
    # outdoor reverb: band-limited noise IR + a couple of discrete slap echoes
    L = int(st["verb_len"] * SR)
    tl = np.arange(L) / SR
    ir = rng.standard_normal(L) * np.exp(-tl * 6.9 / st["verb_len"])
    ir[: int(0.02 * SR)] = 0
    ir = _fft_gain(ir, lambda f: 1 / (1 + (220 / np.maximum(f, 1)) ** 2) / (1 + (f / 4500.0) ** 2))
    for delay, g in ((0.13, 0.5), (0.29, 0.3)):
        k = int(delay * st["verb_len"] / 1.5 * SR)
        if k < L:
            ir[k] += g * np.max(np.abs(ir)) * 3
    dry = out.copy()
    nconv = len(dry) + L - 1
    N = 1 << (nconv - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(dry, N) * np.fft.rfft(ir, N), N)[: len(out)]
    wet = wet / (np.max(np.abs(wet)) + 1e-9) * np.max(np.abs(dry)) * _db(st["verb_db"])
    out = dry + wet
    # saturation: raise drive until the crest factor of the first 150 ms reaches the target
    out = out / (np.max(np.abs(out)) + 1e-9)
    win = slice(max(0, p - int(0.005 * SR)), p + int(0.15 * SR))
    drive = 1.0
    for _ in range(40):
        y = np.tanh(out * drive) / np.tanh(drive)
        seg = y[win]
        crest = 20 * np.log10(np.max(np.abs(seg)) / (np.sqrt(np.mean(seg ** 2)) + 1e-9))
        if crest <= st["crest_db"] or drive > 12:
            break
        drive *= 1.25
    out = y / (np.max(np.abs(y)) + 1e-9) * _db(-0.8 + min(0.0, st.get("out_db", 0.0)))
    # trim the silent end, exponential fade over the final 30%
    idx = np.nonzero(np.abs(out) > _db(-62))[0]
    out = out[: (idx[-1] + int(0.02 * SR)) if len(idx) else len(out)]
    n = len(out)
    fo = int(n * 0.3)
    out[n - fo:] *= np.exp(np.linspace(0, -6.9, fo))
    out[: int(0.0015 * SR)] *= np.linspace(0, 1, int(0.0015 * SR))
    return np.clip(out, -1, 1)


def write_ogg(path, x):
    pcm = (x * 32767).astype(np.int16)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        tmp = tf.name
    with wave.open(tmp, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    os.makedirs(os.path.dirname(path), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-c:a", "libvorbis", "-q:a", "5", path], check=True)
    os.remove(tmp)


def click_pool(src, files):
    """Split the click recordings into individual clicks."""
    pool = []
    for f in files:
        x = load(os.path.join(src, f))
        hop = 128
        e = np.array([np.abs(x[i:i + hop]).max() for i in range(0, len(x) - hop, hop)])
        peak = e.max()
        last = -1
        onsets = []
        for i in range(1, len(e)):
            t = i * hop / SR
            if e[i] > 0.12 * peak and e[i] > 5 * e[max(0, i - 6):i].mean() + 1e-5 and t - last > 0.09:
                onsets.append(t)
                last = t
        for k, t in enumerate(onsets):
            end = min(t + 0.22, onsets[k + 1] - 0.004 if k + 1 < len(onsets) else len(x) / SR)
            seg = x[int((t - 0.004) * SR): int(end * SR)]
            if len(seg) > 0.02 * SR:
                pool.append(seg)
    return pool


def main(src):
    with open(os.path.join(HERE, "sound_map.json")) as fh:
        smap = json.load(fh)
    lens = smap["_shot_len"]
    with open(os.path.join(RES, "assets", "calibre", "sounds.json")) as fh:
        events = json.load(fh)
    styles = smap.get("_shot_style", {})
    classes = smap.get("_gun_class", {})
    mech = None
    if "_mech" in smap:
        mc = smap["_mech"]
        mx = load(os.path.join(src, mc["src"]))
        mech = expand(mx[int(mc["start"] * SR): int(mc["end"] * SR)].copy())
    made = {}
    for ev, clips in smap.items():
        if ev.startswith("_"):
            continue
        kind = "shot" if ev.startswith(("fire_", "suppressed", "rocket_launch", "explosion")) else "foley"
        style = styles.get(classes.get(ev, ""), None)
        out = []
        for c in clips:
            if "layers" in c:
                # several real cuts mixed at offsets into one clip (cloth + click for a draw, ...)
                parts = []
                for l in c["layers"]:
                    lx = load(os.path.join(src, l["src"]))
                    end = l.get("end")
                    seg = lx[int(l.get("start", 0.0) * SR): (int(end * SR) if end is not None else len(lx))]
                    seg = expand(pitch(seg.copy(), l.get("pitch", 0)))
                    seg = seg / (np.max(np.abs(seg)) + 1e-9) * 10 ** (l.get("gain", 0) / 20)
                    parts.append((int(l.get("at", 0.0) * SR), seg))
                mix = np.zeros(max(o + len(g) for o, g in parts))
                for o, g in parts:
                    mix[o:o + len(g)] += g
                out.append(finish(mix, "foley", c.get("gain", 0)))
                continue
            x = load(os.path.join(src, c["src"]))
            pitches = c.get("pitch", 0)
            pitches = pitches if isinstance(pitches, list) else [pitches]
            cuts = []
            if "at" in c:
                ln = c["len"]
                ln = lens[ln] if isinstance(ln, str) else ln
                ats = sorted(c["at"])
                every = sorted(c.get("all_at", ats))
                for t in ats:
                    # never run into the next shot of the same take
                    nxt = [u for u in every if u > t + 0.05]
                    end = min(t + ln, nxt[0] - 0.08) if nxt else t + ln
                    cuts.append(x[max(0, int((t - 0.006) * SR)): int(end * SR)])
            else:
                end = c.get("end")
                cuts.append(x[int(c.get("start", 0.0) * SR): (int(end * SR) if end is not None else len(x))])
            for seg in cuts:
                for p in pitches:
                    if style is not None:
                        m = pitch(mech.copy(), style.get("mech_pitch", 0)) if mech is not None else None
                        out.append(master_shot(pitch(seg.copy(), p), style, m, seed=len(out) + hash(ev) % 1000))
                    else:
                        out.append(finish(pitch(seg.copy(), p), kind, c.get("gain", 0)))
        made[ev] = out
    clicks = smap["_clicks"]
    pool = click_pool(src, clicks["src"])
    print(f"click pool: {len(pool)} clicks")
    cursor = 0
    for ev, (count, semis) in clicks["events"].items():
        if count <= 0:
            continue
        out = []
        for i in range(count):
            seg = pool[(cursor + i * 7) % len(pool)]
            out.append(finish(pitch(seg.copy(), semis), "foley", 0))
        cursor += count * 3 + 5
        made[ev] = out
    # click trains (a revolver cylinder freewheeling on its ratchet: real clicks, spacing growing, dying away)
    for ev, tr in smap.get("_trains", {}).items():
        out = []
        for v in range(tr.get("variants", 3)):
            t, dt, clips_ = 0.0, tr["dt0"], []
            for i in range(tr["n"]):
                seg = pitch(pool[(cursor + v * 11 + i * 5) % len(pool)].copy(), tr.get("semis", 0) + 0.3 * ((i * 7 + v) % 3))
                seg = seg[: int(0.05 * SR)] * (10 ** (-tr["decay_db"] * i / 20))
                clips_.append((int(t * SR), seg))
                t += dt
                dt *= 1 + tr["grow"]
            mix = np.zeros(max(o + len(g) for o, g in clips_))
            for o, g in clips_:
                mix[o:o + len(g)] += g
            out.append(finish(mix, "foley", tr.get("gain", 0)))
        made[ev] = out
    # write files + sounds.json
    for ev, variants in made.items():
        if ev not in events:
            print(f"WARNING: {ev} is not a known sound event, skipped")
            continue
        old = events[ev]["sounds"][0] if events[ev]["sounds"] else {}
        extra = {k: v for k, v in old.items() if k != "name"}
        entries = []
        for i, v in enumerate(variants):
            write_ogg(os.path.join(SND, "real", f"{ev}_{i}.ogg"), v)
            entries.append({"name": f"calibre:real/{ev}_{i}", **extra})
        events[ev]["sounds"] = entries
    with open(os.path.join(RES, "assets", "calibre", "sounds.json"), "w") as fh:
        json.dump(events, fh, indent=1)
    # drop .ogg files nothing references any more
    used = {s["name"].split(":", 1)[1] for e in events.values() for s in e["sounds"]}
    removed = 0
    for dp, _, fs in os.walk(SND):
        for f in fs:
            rel = os.path.relpath(os.path.join(dp, f), SND)[:-4].replace(os.sep, "/")
            if f.endswith(".ogg") and rel not in used:
                os.remove(os.path.join(dp, f))
                removed += 1
    real = sum(1 for e in events.values() if any(s["name"].startswith("calibre:real/") for s in e["sounds"]))
    print(f"{real}/{len(events)} events now use real recordings ({sum(len(v) for v in made.values())} clips); "
          f"removed {removed} unused files")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])

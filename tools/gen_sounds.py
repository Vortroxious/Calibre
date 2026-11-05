#!/usr/bin/env python3
"""
Synthesizes every Calibre sound (gunshots per gun, mechanical foley, impacts) into mono .ogg files and writes
assets/calibre/sounds.json plus calibre_gen/sounds.json (the list Java registers).

Requires numpy and ffmpeg. Everything is procedural: replace any .ogg with a recording and keep the name.
"""
import json
import os
import subprocess
import sys
import tempfile
import wave
import glob
import zlib

import numpy as np

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "common", "src", "main", "resources")  # shared by the neoforge and fabric builds
SND = os.path.join(RES, "assets", "calibre", "sounds")


# ------------------------------------------------------------------------------------------------ dsp
def t_axis(dur):
    return np.arange(int(SR * dur)) / SR


def noise(dur, rng):
    return rng.standard_normal(int(SR * dur))


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def lp(x, fc, order=2):
    # cheap FFT brickwall-ish lowpass with soft knee
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / fc) ** (2 * order))
    return np.fft.irfft(X, len(x))


def hp(x, fc, order=2):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (fc / np.maximum(f, 1)) ** (2 * order))
    return np.fft.irfft(X, len(x))


def bp(x, lo, hi):
    return hp(lp(x, hi), lo)


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (SR * tau))


def place(out, sig, t):
    i = int(t * SR)
    j = min(len(out), i + len(sig))
    if i < len(out):
        out[i:j] += sig[:j - i]


def ring(freqs, dur, decay, rng, amp=1.0):
    t = t_axis(dur)
    y = np.zeros_like(t)
    for f in freqs:
        f2 = f * rng.uniform(0.97, 1.03)
        y += np.sin(2 * np.pi * f2 * t + rng.uniform(0, 6)) * np.exp(-t / (decay * rng.uniform(0.7, 1.3)))
    return y * amp / max(1, len(freqs))


def click(rng, bright=4000, body=1800, dur=0.06, amp=1.0, metal=True):
    n = noise(dur, rng) * env_exp(int(SR * dur), 0.004)
    y = bp(n, body * 0.5, bright * 1.5)
    if metal:
        y += ring([body, body * 2.7, bright], dur, 0.012, rng, 0.6)
    return y * amp


def scrape(rng, dur=0.12, lo=1500, hi=7000, amp=0.4):
    n = noise(dur, rng)
    t = t_axis(dur)
    e = np.sin(np.pi * t / dur) ** 0.6
    grit = 1 + 0.6 * np.sign(np.sin(2 * np.pi * rng.uniform(60, 140) * t))
    return bp(n, lo, hi) * e * grit * amp


def thud(rng, f=110, dur=0.12, amp=0.8):
    t = t_axis(dur)
    sweep = f * (1 + 0.8 * np.exp(-t / 0.01))
    ph = 2 * np.pi * np.cumsum(sweep) / SR
    return np.sin(ph) * np.exp(-t / 0.03) * amp + lp(noise(dur, rng), 600) * np.exp(-t / 0.01) * amp * 0.5


def cloth(rng, dur=0.35, amp=0.25):
    n = noise(dur, rng)
    t = t_axis(dur)
    e = np.sin(np.pi * t / dur) ** 1.5 * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t) ** 2)
    return bp(n, 300, 3000) * e * amp


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak


def reverb(x, tail=0.8, mix=0.35, rng=None, lo=200, hi=5000):
    rng = rng or np.random.default_rng(1)
    n = int(SR * tail)
    ir = bp(rng.standard_normal(n), lo, hi) * env_exp(n, tail / 5)
    ir[:int(SR * 0.012)] = 0
    wet = np.convolve(x, ir)[:len(x) + n] if len(x) < 30000 else fft_conv(x, ir)
    out = np.zeros(len(x) + n)
    out[:len(x)] += x
    wet = norm(wet, np.max(np.abs(x)))[:len(out)]
    out[:len(wet)] += wet * mix
    return out


def fft_conv(a, b):
    n = len(a) + len(b) - 1
    N = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(a, N) * np.fft.rfft(b, N), N)[:n]


# ------------------------------------------------------------------------------------------------ gunshots
def gunshot(rng, size=1.0, crack=0.5, bass=90, tail=1.0, suppressed=False, mech=None):
    """size ~ energy (pistol 0.6 .. .50 BMG 2.0); crack = supersonic snap amount."""
    dur = 0.35 + tail
    out = np.zeros(int(SR * dur))
    if suppressed:
        n = noise(0.09, rng) * env_exp(int(SR * 0.09), 0.012)
        out[:len(n)] += lp(n, 1800) * 0.9
        out[:len(n)] += thud(rng, bass * 1.2, 0.09, 0.4)[:len(n)]
        if crack > 0.4:  # supersonic ammo still cracks through a can
            c = hp(noise(0.012, rng), 3000) * env_exp(int(SR * 0.012), 0.002)
            place(out, c * 0.5 * crack, 0.002)
        if mech is not None:
            place(out, click(rng, 5000, 2200, 0.05, 0.5), 0.03)
        out = reverb(out[:int(SR * 0.5)], tail=0.4 * size, mix=0.2, rng=rng)
        return norm(out, 0.7)
    # muzzle blast
    n = noise(0.25, rng)
    blast = lp(n, 2500 + 1500 / size) * env_exp(len(n), 0.018 * size)
    blast += hp(n, 1500) * env_exp(len(n), 0.006) * 0.6
    out[:len(blast)] += blast
    out[:int(SR * 0.25)] += thud(rng, bass, 0.25, 1.4 * size)[:int(SR * 0.25)]
    if crack > 0:
        c = hp(noise(0.01, rng), 4000) * env_exp(int(SR * 0.01), 0.0015)
        place(out, c * crack * 1.5, 0.0)
    # distant echo/tail
    tl = bp(noise(tail, rng), 150, 2500) * env_exp(int(SR * tail), tail / 4.5)
    place(out, tl * 0.35 * size, 0.05)
    # soft clip for the "punch"
    out = np.tanh(out * 1.6) / np.tanh(1.6)
    if mech is not None:
        place(out, click(rng, 4500, 2000, 0.05, 0.15), 0.035)
    return norm(out, 0.95)


GUN_SHOTS = {
    # gun: (size, crack, bass, tail)
    "glock17": (0.6, 0.1, 120, 0.7), "m1911": (0.7, 0.0, 100, 0.8), "m9": (0.62, 0.1, 118, 0.7),
    "deagle": (1.15, 0.3, 80, 1.1), "model29": (1.1, 0.25, 78, 1.1),
    "mp5": (0.58, 0.1, 125, 0.6), "ump45": (0.66, 0.0, 105, 0.6), "uzi": (0.6, 0.1, 120, 0.6),
    "p90": (0.55, 0.6, 140, 0.6),
    "m4a1": (0.95, 0.9, 95, 1.0), "hk416": (0.97, 0.9, 92, 1.0), "akm": (1.05, 0.7, 85, 1.1),
    "aug": (0.95, 0.9, 95, 1.0),
    "fal": (1.25, 1.0, 75, 1.3), "scar_h": (1.25, 1.0, 76, 1.3), "svd": (1.3, 1.0, 72, 1.4),
    "m14ebr": (1.25, 1.0, 75, 1.3),
    "m24": (1.35, 1.0, 70, 1.6), "awm": (1.55, 1.0, 64, 1.8), "m82a1": (2.0, 1.0, 50, 2.2),
    "rem870": (1.3, 0.0, 70, 1.2), "benelli_m4": (1.28, 0.0, 72, 1.2),
    "m249": (0.95, 0.9, 92, 0.9), "pkm": (1.2, 1.0, 76, 1.1),
    # expansion (real recordings replace these via import_sounds.py)
    "mosin": (1.35, 1.0, 70, 1.5), "m1917": (1.4, 1.0, 68, 1.5), "arisaka": (1.3, 1.0, 72, 1.5),
    "sks": (1.05, 0.7, 85, 1.1), "ppsh41": (0.7, 0.5, 110, 0.6), "m45": (0.58, 0.1, 125, 0.6),
    "ak47": (1.05, 0.7, 85, 1.1), "win1894": (1.1, 0.6, 84, 1.2), "marlin336": (1.1, 0.6, 84, 1.2),
    "tikka_t3": (1.35, 1.0, 70, 1.6), "savage10": (1.0, 0.3, 88, 1.0), "model12": (1.3, 0.0, 70, 1.2),
    "nova": (1.3, 0.0, 70, 1.2), "cdaly": (1.28, 0.0, 72, 1.2), "mossberg190": (1.2, 0.0, 76, 1.1),
    "ppq": (0.6, 0.1, 120, 0.7), "bersa": (0.5, 0.0, 130, 0.6), "rugermk3": (0.35, 0.2, 160, 0.4),
    "sw642": (0.8, 0.1, 100, 0.8), "singlesix": (0.38, 0.2, 155, 0.45),
}

# mechanical recipes: list of (time, generator)
def R(*parts):
    return parts


def mech_recipes():
    return {
        "mag_out_pistol": R((0.0, lambda r: click(r, 4500, 2100, 0.05, 0.8)), (0.02, lambda r: scrape(r, 0.08, 2000, 6000, 0.3))),
        "mag_in_pistol": R((0.0, lambda r: scrape(r, 0.06, 1500, 5000, 0.3)), (0.06, lambda r: click(r, 4200, 1600, 0.07, 1.0))),
        "mag_out_rifle": R((0.0, lambda r: click(r, 3800, 1500, 0.06, 0.9)), (0.03, lambda r: scrape(r, 0.12, 1200, 5000, 0.35))),
        "mag_in_rifle": R((0.0, lambda r: scrape(r, 0.08, 1200, 4500, 0.35)), (0.08, lambda r: click(r, 3600, 1300, 0.09, 1.0)),
                          (0.085, lambda r: thud(r, 160, 0.06, 0.5))),
        "mag_out_smg": R((0.0, lambda r: click(r, 4200, 1800, 0.05, 0.8)), (0.02, lambda r: scrape(r, 0.1, 1500, 5500, 0.3))),
        "mag_in_smg": R((0.0, lambda r: scrape(r, 0.07, 1500, 5000, 0.3)), (0.07, lambda r: click(r, 4000, 1500, 0.08, 1.0))),
        "mag_out_p90": R((0.0, lambda r: click(r, 3000, 1100, 0.05, 0.7, metal=False)), (0.03, lambda r: scrape(r, 0.14, 800, 3500, 0.35))),
        "mag_in_p90": R((0.0, lambda r: scrape(r, 0.1, 800, 3500, 0.3)), (0.1, lambda r: click(r, 3200, 1000, 0.08, 1.0, metal=False))),
        "mag_release": R((0.0, lambda r: click(r, 5000, 2400, 0.04, 0.7)),),
        "slide_release": R((0.0, lambda r: click(r, 5200, 2300, 0.08, 1.0)), (0.01, lambda r: ring([2600, 5400, 7800], 0.2, 0.04, r, 0.4))),
        "slide_forward_light": R((0.0, lambda r: click(r, 4800, 2100, 0.06, 0.6)),),
        "press_check": R((0.0, lambda r: scrape(r, 0.12, 2000, 7000, 0.35)),),
        "bolt_release": R((0.0, lambda r: click(r, 4500, 1700, 0.06, 0.5)), (0.03, lambda r: click(r, 3600, 1400, 0.1, 1.0)),
                          (0.03, lambda r: ring([1800, 4100, 6500], 0.25, 0.05, r, 0.4))),
        "charging_handle_back": R((0.0, lambda r: click(r, 4000, 1800, 0.04, 0.5)), (0.02, lambda r: scrape(r, 0.12, 1500, 6000, 0.5)),
                                  (0.13, lambda r: click(r, 3500, 1400, 0.05, 0.6))),
        "charging_handle_forward": R((0.0, lambda r: scrape(r, 0.05, 1500, 6000, 0.3)), (0.05, lambda r: click(r, 3600, 1300, 0.1, 1.0)),
                                     (0.05, lambda r: ring([1700, 3900, 6100], 0.25, 0.05, r, 0.45))),
        "charging_handle_lock": R((0.0, lambda r: scrape(r, 0.1, 1500, 6000, 0.4)), (0.1, lambda r: click(r, 4200, 1900, 0.06, 0.8))),
        "hk_slap": R((0.0, lambda r: thud(r, 220, 0.06, 0.5)), (0.0, lambda r: click(r, 3600, 1300, 0.1, 1.0)),
                     (0.01, lambda r: ring([1500, 3700, 5900], 0.3, 0.06, r, 0.5))),
        "forward_assist": R((0.0, lambda r: click(r, 3000, 1200, 0.05, 0.8)),),
        "dust_cover": R((0.0, lambda r: click(r, 5000, 2600, 0.04, 0.6)),),
        "bolt_open": R((0.0, lambda r: click(r, 3800, 1600, 0.05, 0.8)),),
        "bolt_back": R((0.0, lambda r: scrape(r, 0.14, 1200, 5500, 0.5)), (0.13, lambda r: click(r, 3400, 1300, 0.05, 0.6))),
        "bolt_forward": R((0.0, lambda r: scrape(r, 0.1, 1200, 5500, 0.45)), (0.1, lambda r: click(r, 3600, 1400, 0.06, 0.7))),
        "bolt_close": R((0.0, lambda r: click(r, 3800, 1500, 0.07, 1.0)),),
        "round_insert": R((0.0, lambda r: scrape(r, 0.05, 2000, 6000, 0.25)), (0.05, lambda r: click(r, 4400, 2000, 0.05, 0.7))),
        "shell_insert": R((0.0, lambda r: scrape(r, 0.06, 800, 4000, 0.35)), (0.06, lambda r: click(r, 2600, 900, 0.07, 0.9, metal=False)),
                          (0.065, lambda r: click(r, 4200, 2000, 0.04, 0.4))),
        "pump_back": R((0.0, lambda r: click(r, 3000, 1100, 0.05, 0.6)), (0.02, lambda r: scrape(r, 0.1, 800, 4500, 0.6)),
                       (0.11, lambda r: click(r, 2800, 1000, 0.07, 1.0))),
        "pump_back_light": R((0.0, lambda r: scrape(r, 0.12, 800, 4500, 0.35)),),
        "pump_forward": R((0.0, lambda r: scrape(r, 0.08, 800, 4500, 0.5)), (0.08, lambda r: click(r, 3000, 1100, 0.09, 1.0)),
                          (0.08, lambda r: thud(r, 170, 0.06, 0.4))),
        "pump_rattle": R(*[(i * 0.05, (lambda k: (lambda r: click(r, 3200, 1200, 0.03, 0.3 + 0.1 * (k % 2), metal=True)))(i)) for i in range(4)]),
        "selector": R((0.0, lambda r: click(r, 5200, 2600, 0.04, 0.7)),),
        "selector_ak": R((0.0, lambda r: click(r, 3800, 1500, 0.08, 1.0)), (0.0, lambda r: ring([1300, 3100, 5200], 0.2, 0.05, r, 0.5))),
        "safety": R((0.0, lambda r: click(r, 5200, 2600, 0.04, 0.6)),),
        "decocker": R((0.0, lambda r: click(r, 4200, 1800, 0.05, 0.6)), (0.03, lambda r: click(r, 3500, 1300, 0.06, 0.9))),
        "hammer_cock": R((0.0, lambda r: click(r, 4600, 2100, 0.04, 0.5)), (0.04, lambda r: click(r, 4300, 1900, 0.05, 0.8))),
        "dry_fire": R((0.0, lambda r: click(r, 4800, 2400, 0.05, 0.8)),),
        "click_small": R((0.0, lambda r: click(r, 5600, 3000, 0.03, 0.5)),),
        "tap": R((0.0, lambda r: thud(r, 260, 0.05, 0.4)), (0.0, lambda r: click(r, 3000, 1200, 0.03, 0.3))),
        "cylinder_latch": R((0.0, lambda r: click(r, 5000, 2400, 0.04, 0.6)),),
        "cylinder_open": R((0.0, lambda r: scrape(r, 0.06, 2000, 6000, 0.3)), (0.05, lambda r: click(r, 4400, 2000, 0.05, 0.7))),
        "cylinder_close": R((0.0, lambda r: click(r, 4000, 1700, 0.08, 1.0)), (0.0, lambda r: ring([2100, 4600, 7000], 0.22, 0.04, r, 0.4))),
        "cylinder_spin": R(*[(i * 0.03 * (1 + i * 0.12), (lambda k: (lambda r: click(r, 6000, 3000, 0.02, 0.35 * (1 - k / 22))))(i)) for i in range(20)]),
        "ejector_rod": R((0.0, lambda r: click(r, 4200, 1800, 0.05, 0.7)),
                         *[(0.08 + i * 0.03, (lambda k: (lambda r: ring([3000 + 300 * k, 6800], 0.25, 0.05, r, 0.5)))(i)) for i in range(6)]),
        "speedloader_insert": R((0.0, lambda r: scrape(r, 0.06, 1500, 5000, 0.3)), (0.06, lambda r: click(r, 3800, 1500, 0.06, 0.8))),
        "speedloader_release": R((0.0, lambda r: click(r, 4600, 2100, 0.05, 0.6)), (0.04, lambda r: scrape(r, 0.08, 1500, 5000, 0.2))),
        "cover_open": R((0.0, lambda r: click(r, 3600, 1300, 0.06, 0.7)), (0.02, lambda r: ring([900, 2300, 4300], 0.25, 0.05, r, 0.3))),
        "cover_close": R((0.0, lambda r: thud(r, 140, 0.08, 0.7)), (0.0, lambda r: click(r, 3200, 1100, 0.1, 1.0)),
                         (0.01, lambda r: ring([800, 2100, 3900], 0.35, 0.07, r, 0.45))),
        "belt_rattle": R(*[(i * 0.04 + 0.01 * (i % 3), (lambda k: (lambda r: click(r, 5200, 2600, 0.03, 0.25 + 0.15 * ((k * 7) % 3))))(i)) for i in range(9)]),
        "belt_seat": R((0.0, lambda r: scrape(r, 0.1, 1500, 6000, 0.3)), (0.1, lambda r: click(r, 4000, 1700, 0.05, 0.6))),
        "box_out": R((0.0, lambda r: click(r, 2600, 900, 0.06, 0.7, metal=False)), (0.02, lambda r: scrape(r, 0.12, 400, 2500, 0.3))),
        "box_in": R((0.0, lambda r: scrape(r, 0.08, 400, 2500, 0.3)), (0.08, lambda r: thud(r, 150, 0.08, 0.6)),
                    (0.08, lambda r: click(r, 3000, 1000, 0.07, 0.8))),
        "stock_unlock": R((0.0, lambda r: click(r, 3200, 1100, 0.04, 0.6, metal=False)),),
        "stock_lock": R((0.0, lambda r: click(r, 3600, 1300, 0.06, 0.9)),),
        "stock_adjust": R((0.0, lambda r: scrape(r, 0.06, 1000, 4000, 0.3)), (0.06, lambda r: click(r, 3800, 1500, 0.05, 0.7))),
        "rocket_slide": R((0.0, lambda r: scrape(r, 0.4, 300, 2500, 0.35)),),
        "rocket_seat": R((0.0, lambda r: thud(r, 120, 0.1, 0.7)), (0.0, lambda r: click(r, 2800, 1000, 0.1, 0.9))),
        "cloth": R((0.0, lambda r: cloth(r, 0.3, 0.3)),),
        # inspect handling foley (real cuts from tools/sound_map.json replace these)
        "grip": R((0.0, lambda r: cloth(r, 0.08, 0.25)), (0.03, lambda r: click(r, 2400, 900, 0.04, 0.35, metal=False))),
        "handle_rifle": R((0.0, lambda r: cloth(r, 0.18, 0.2)), (0.04, lambda r: click(r, 3000, 1100, 0.04, 0.3, metal=True)),
                          (0.11, lambda r: click(r, 3400, 1300, 0.03, 0.2, metal=True))),
        "handle_pistol": R((0.0, lambda r: cloth(r, 0.12, 0.15)), (0.03, lambda r: click(r, 4200, 1800, 0.03, 0.25, metal=True))),
        "handle_heavy": R((0.0, lambda r: cloth(r, 0.25, 0.25)), (0.05, lambda r: click(r, 2200, 800, 0.06, 0.4, metal=True)),
                          (0.14, lambda r: click(r, 2600, 900, 0.05, 0.3, metal=True))),
        "mag_check": R(*[(i * 0.07, (lambda k: (lambda r: click(r, 3600, 1400, 0.03, 0.3 - 0.05 * k, metal=True)))(i)) for i in range(3)]),
        "spin_whoosh": R((0.0, lambda r: cloth(r, 0.16, 0.2)),),
        # expansion foley (real cuts replace most of these via import_sounds.py)
        "clip_insert": R((0.0, lambda r: scrape(r, 0.04, 1500, 5000, 0.3)), (0.04, lambda r: click(r, 3600, 1400, 0.06, 0.9))),
        "clip_strip": R((0.0, lambda r: scrape(r, 0.22, 900, 4500, 0.5)), (0.2, lambda r: click(r, 3000, 1200, 0.07, 0.8))),
        "clip_eject": R((0.0, lambda r: click(r, 5200, 2600, 0.04, 0.6)), (0.03, lambda r: scrape(r, 0.06, 3000, 8000, 0.2))),
        "drum_out": R((0.0, lambda r: click(r, 3200, 1200, 0.07, 0.9)), (0.04, lambda r: scrape(r, 0.18, 700, 3500, 0.4))),
        "drum_in": R((0.0, lambda r: scrape(r, 0.1, 700, 3500, 0.35)), (0.1, lambda r: click(r, 2600, 900, 0.1, 1.0)),
                     (0.105, lambda r: thud(r, 120, 0.08, 0.7))),
        "lever_open": R((0.0, lambda r: click(r, 3400, 1300, 0.06, 0.8)), (0.03, lambda r: scrape(r, 0.1, 1000, 5000, 0.35))),
        "lever_close": R((0.0, lambda r: scrape(r, 0.06, 1000, 5000, 0.3)), (0.06, lambda r: click(r, 3000, 1100, 0.08, 1.0))),
        "loading_gate": R((0.0, lambda r: click(r, 4800, 2200, 0.04, 0.6)), (0.03, lambda r: scrape(r, 0.06, 2000, 7000, 0.25))),
        "hammer_thumb": R((0.0, lambda r: click(r, 4200, 1800, 0.04, 0.5)), (0.06, lambda r: click(r, 3600, 1400, 0.05, 0.9))),
        "pouch": R((0.0, lambda r: cloth(r, 0.25, 0.35)), (0.12, lambda r: scrape(r, 0.12, 300, 2000, 0.2))),
        "draw_pistol": R((0.0, lambda r: cloth(r, 0.25, 0.35)), (0.2, lambda r: click(r, 4000, 1800, 0.05, 0.4))),
        "draw_rifle": R((0.0, lambda r: cloth(r, 0.45, 0.4)), (0.3, lambda r: click(r, 3200, 1200, 0.06, 0.5)),
                        (0.32, lambda r: ring([600, 1500], 0.2, 0.05, r, 0.3))),
        # world sounds
        "impact_hard": R((0.0, lambda r: click(r, 6000, 2500, 0.06, 1.0)), (0.0, lambda r: lp(noise(0.12, r), 3000) * env_exp(int(SR * 0.12), 0.02))),
        "impact_soft": R((0.0, lambda r: lp(noise(0.12, r), 900) * env_exp(int(SR * 0.12), 0.025)),),
        "impact_wood": R((0.0, lambda r: thud(r, 300, 0.1, 0.8)), (0.0, lambda r: bp(noise(0.08, r), 600, 3000) * env_exp(int(SR * 0.08), 0.012))),
        "impact_metal": R((0.0, lambda r: click(r, 6000, 2800, 0.05, 0.8)), (0.0, lambda r: ring([2200, 5300, 8400], 0.4, 0.09, r, 0.7))),
        "impact_glass": R(*[(i * 0.018, (lambda k: (lambda r: ring([5000 + 700 * k, 9000 - 300 * k], 0.15, 0.03, r, 0.6)))(i)) for i in range(8)]),
        "impact_flesh": R((0.0, lambda r: thud(r, 90, 0.12, 0.9)), (0.0, lambda r: lp(noise(0.06, r), 1400) * env_exp(int(SR * 0.06), 0.01))),
        "hitmarker": R((0.0, lambda r: ring([2400, 4800], 0.08, 0.015, r, 0.9)),),
        "headshot": R((0.0, lambda r: ring([3200, 6400], 0.1, 0.02, r, 0.9)), (0.0, lambda r: thud(r, 140, 0.08, 0.5))),
        "rocket_launch": R((0.0, lambda r: gunshot(r, 1.6, 0.0, 60, 1.6)), (0.05, lambda r: lp(noise(1.2, r), 2500) * env_exp(int(SR * 1.2), 0.4) * 0.5)),
        "rocket_flight": R((0.0, lambda r: bp(noise(1.5, r), 200, 3000) * 0.5),),
        "explosion": R((0.0, lambda r: gunshot(r, 2.6, 0.0, 40, 3.0)),),
        "suppressed_pistol": R((0.0, lambda r: gunshot(r, 0.6, 0.0, 120, 0.3, suppressed=True, mech=1)),),
        "suppressed_rifle": R((0.0, lambda r: gunshot(r, 1.0, 0.6, 90, 0.4, suppressed=True, mech=1)),),
    }


SUPERSONIC_WHIZ = "bullet_whiz"


def whiz(rng):
    dur = 0.35
    t = t_axis(dur)
    n = bp(noise(dur, rng), 1500, 9000)
    e = np.exp(-((t - 0.12) / 0.05) ** 2)
    return hp(np.sin(2 * np.pi * (3000 - 4000 * t) * t) * 0.3 + n, 1000) * e


# ------------------------------------------------------------------------------------------------ io
def write_ogg(path, sig):
    sig = np.clip(sig, -1, 1)
    pcm = (sig * 32767).astype(np.int16)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        tmp = tf.name
    with wave.open(tmp, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    os.makedirs(os.path.dirname(path), exist_ok=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp, "-c:a", "libvorbis", "-q:a", "4", path], check=True)
    os.remove(tmp)


def render_recipe(parts, rng):
    sigs = [(t, np.asarray(fn(rng), dtype=float)) for t, fn in parts]
    dur = max(t + len(s) / SR for t, s in sigs) + 0.02
    out = np.zeros(int(SR * dur))
    for t, s in sigs:
        place(out, s, t)
    fade = min(len(out), int(SR * 0.01))
    out[-fade:] *= np.linspace(1, 0, fade)
    return norm(out, 0.85)


def main():
    events = {}
    variants = 3
    for gun, (size, crack, bass, tail) in GUN_SHOTS.items():
        files = []
        for v in range(variants):
            rng = np.random.default_rng(zlib.crc32(f'{gun}:{v}'.encode()))
            write_ogg(os.path.join(SND, "fire", f"{gun}_{v}.ogg"), gunshot(rng, size, crack, bass, tail, mech=1))
            files.append(f"calibre:fire/{gun}_{v}")
        events[f"fire_{gun}"] = {"sounds": [{"name": f, "attenuation_distance": int(48 + 64 * size)} for f in files],
                                 "subtitle": "subtitles.calibre.fire"}
    for name, parts in mech_recipes().items():
        files = []
        n = 3 if name.startswith(("impact", "suppressed")) else 1
        for v in range(n):
            rng = np.random.default_rng(zlib.crc32(f'{name}:{v}'.encode()))
            write_ogg(os.path.join(SND, "foley", f"{name}_{v}.ogg"), render_recipe(parts, rng))
            files.append(f"calibre:foley/{name}_{v}")
        ev = {"sounds": [{"name": f} for f in files]}
        if name.startswith(("explosion", "rocket", "suppressed")):
            ev["sounds"] = [{"name": f, "attenuation_distance": 96} for f in files]
        events[name] = ev
    write_ogg(os.path.join(SND, "foley", "bullet_whiz_0.ogg"), norm(whiz(np.random.default_rng(9)), 0.7))
    events["bullet_whiz"] = {"sounds": [{"name": "calibre:foley/bullet_whiz_0"}]}
    with open(os.path.join(RES, "assets", "calibre", "sounds.json"), "w") as fh:
        json.dump(events, fh, indent=1)
    os.makedirs(os.path.join(RES, "calibre_gen"), exist_ok=True)
    with open(os.path.join(RES, "calibre_gen", "sounds.json"), "w") as fh:
        json.dump(sorted(events), fh, indent=1)
    # sanity: every animation sound exists
    missing = set()
    for f in glob.glob(os.path.join(RES, "calibre_gen", "guns", "*.json")):
        for a in json.load(open(f))["actions"].values():
            for _, s in a["sounds"]:
                if s not in events:
                    missing.add(s)
    print(f"{len(events)} sound events written; missing: {sorted(missing) or 'none'}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Publish Calibre to Modrinth (stdlib only).

  export MODRINTH_TOKEN=...        # Personal Access Token: Create projects, Create versions, Write projects, Read user
                                   # (or a network secret: the proxy adds "Authorization: <token>" for api.modrinth.com)
  python3 tools/modrinth_publish.py whoami            # who the token belongs to
  python3 tools/modrinth_publish.py publish --dry-run # check everything without uploading (no token needed)
  python3 tools/modrinth_publish.py publish           # first run: creates the project as a DRAFT, then uploads
                                                      # icon, both loader versions and the gallery; later runs only
                                                      # update the page and upload versions that are not there yet

Never put the token in a file or on the command line; it is read from the environment only.
The project stays a draft: review it on modrinth.com and press "Submit for review" yourself.
"""
import argparse
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MR = os.path.join(HERE, "modrinth")
API = "https://api.modrinth.com/v2"
UA = "calibre-mod-publisher/1.0 (Calibre Minecraft mod release script)"


def gradle_prop(name):
    with open(os.path.join(ROOT, "gradle.properties")) as fh:
        for line in fh:
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip()
    raise KeyError(name)


def get_token():
    """The token from MODRINTH_TOKEN, or None when an environment network secret adds the header for us."""
    return os.environ.get("MODRINTH_TOKEN") or None


def request(method, path, token=None, body=None, headers=None, ok404=False):
    h = {"User-Agent": UA}
    if token:
        h["Authorization"] = token
    h.update(headers or {})
    req = urllib.request.Request(API + path, data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = r.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        if ok404 and e.code == 404:
            return None
        detail = e.read().decode("utf-8", "replace")
        raise SystemExit(f"Modrinth {method} {path} -> HTTP {e.code}: {detail}")


def multipart(fields, files):
    """fields: {name: json-able}, files: [(name, filename, bytes)] -> (body, content_type)"""
    boundary = "----calibre" + uuid.uuid4().hex
    out = []
    for k, v in fields.items():
        out += [f"--{boundary}\r\n".encode(), f'Content-Disposition: form-data; name="{k}"\r\n'.encode(),
                b"Content-Type: application/json\r\n\r\n", json.dumps(v).encode(), b"\r\n"]
    for name, fn, data in files:
        ctype = mimetypes.guess_type(fn)[0] or "application/octet-stream"
        if fn.endswith(".jar"):
            ctype = "application/java-archive"
        out += [f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{name}"; filename="{fn}"\r\n'.encode(),
                f"Content-Type: {ctype}\r\n\r\n".encode(), data, b"\r\n"]
    out.append(f"--{boundary}--\r\n".encode())
    return b"".join(out), f"multipart/form-data; boundary={boundary}"


def load_project(version):
    with open(os.path.join(MR, "project.json")) as fh:
        p = json.load(fh)
    with open(os.path.join(MR, "description.md")) as fh:
        p["body"] = fh.read()
    for v in p["versions"]:
        for k in ("jar", "name", "version_number"):
            v[k] = v[k].replace("{version}", version)
    return p


def check(p, version):
    problems = []
    cats = {c["name"] for c in request("GET", "/tag/category") if c["project_type"] == "mod"}
    for c in p["categories"] + p.get("additional_categories", []):
        if c not in cats:
            problems.append(f"unknown category {c}")
    gv = {g["version"] for g in request("GET", "/tag/game_version")}
    for g in p["game_versions"]:
        if g not in gv:
            problems.append(f"unknown game version {g}")
    if len(p["description"]) > 256:
        problems.append("summary longer than 256 characters")
    for f in ["icon.png"] + [g["file"] for g in p["gallery"]]:
        if not os.path.isfile(os.path.join(MR, f)):
            problems.append(f"missing {f}")
    if os.path.getsize(os.path.join(MR, "icon.png")) > 256 * 1024:
        problems.append("icon.png is over 256 KiB")
    for v in p["versions"]:
        if not os.path.isfile(os.path.join(ROOT, v["jar"])):
            problems.append(f"missing {v['jar']} (run ./gradlew buildAll)")
        for d in v["dependencies"]:
            info = request("GET", f"/project/{d['slug']}", ok404=True)
            if info is None:
                problems.append(f"dependency {d['slug']} not found")
            else:
                d["project_id"] = info["id"]
    return problems


def whoami(token):
    h = {"User-Agent": UA}
    if token:
        h["Authorization"] = token
    try:
        with urllib.request.urlopen(urllib.request.Request(API + "/user", headers=h), timeout=60) as r:
            u = json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise SystemExit("Modrinth says 401: no token reached it. Set MODRINTH_TOKEN, or add a network secret for "
                             "api.modrinth.com (header Authorization, value = the raw token).")
        raise SystemExit(f"Modrinth GET /user -> HTTP {e.code}: {e.read().decode('utf-8', 'replace')}")
    print(f"token belongs to {u['username']} (id {u['id']})")
    return u


def publish(args):
    version = args.version or gradle_prop("mod_version")
    p = load_project(version)
    problems = check(p, version)
    for v in p["versions"]:
        print(f"version {v['version_number']}: {v['jar']} deps "
              + ", ".join(f"{d['slug']}={d['dependency_type']}" for d in v["dependencies"]))
    print(f"gallery: {len(p['gallery'])} images; categories {p['categories']} + {p.get('additional_categories')}")
    if problems:
        raise SystemExit("problems:\n  " + "\n  ".join(problems))
    if args.dry_run:
        print("dry run OK: nothing uploaded")
        return
    token = get_token()
    me = whoami(token)
    proj = request("GET", f"/project/{p['slug']}", token, ok404=True)
    if proj is None:   # drafts are not found by slug; look in the owner's own projects
        mine = request("GET", f"/user/{me['id']}/projects", token, ok404=True) or []
        proj = next((x for x in mine if x.get("slug") == p["slug"]), None)
    pid_file = os.path.join(MR, "project_id.txt")
    if proj is None and os.path.isfile(pid_file):   # token without the "Read projects" scope cannot see its draft
        proj = {"id": open(pid_file).read().strip(), "slug": p["slug"]}
    if proj is None:
        data = {k: p[k] for k in ("slug", "title", "description", "categories", "additional_categories",
                                  "client_side", "server_side", "body", "license_id", "project_type")}
        data.update({k: p[k] for k in ("source_url", "issues_url") if p.get(k)})
        data.update(initial_versions=[], is_draft=True, license_url=p.get("license_url"))
        with open(os.path.join(MR, "icon.png"), "rb") as fh:
            body, ct = multipart({"data": data}, [("icon", "icon.png", fh.read())])
        proj = request("POST", "/project", token, body, {"Content-Type": ct})
        with open(pid_file, "w") as fh:
            fh.write(proj["id"] + "\n")
        print(f"created draft project {proj['slug']} ({proj['id']})")
    else:
        request("PATCH", f"/project/{proj['id']}", token, json.dumps(
            {k: p[k] for k in ("title", "description", "categories", "additional_categories", "client_side",
                               "server_side", "body", "license_id")} | {k: p[k] for k in ("source_url", "issues_url")
                                                                         if p.get(k)}).encode(), {"Content-Type": "application/json"})
        with open(os.path.join(MR, "icon.png"), "rb") as fh:
            request("PATCH", f"/project/{proj['id']}/icon?ext=png", token, fh.read(), {"Content-Type": "image/png"})
        print(f"updated project page {proj['slug']} ({proj['id']})")
    pid = proj["id"]
    have = {v["version_number"] for v in request("GET", f"/project/{pid}/version", token, ok404=True) or []}
    for v in p["versions"]:
        if v["version_number"] in have:
            print(f"version {v['version_number']} already uploaded, skipped")
            continue
        data = {"project_id": pid, "name": v["name"], "version_number": v["version_number"],
                "changelog": args.changelog, "game_versions": p["game_versions"], "loaders": [v["loader"]],
                "version_type": "release", "featured": True, "status": "listed",
                "dependencies": [{"project_id": d["project_id"], "dependency_type": d["dependency_type"]}
                                 for d in v["dependencies"]],
                "file_parts": ["file0"], "primary_file": "file0"}
        with open(os.path.join(ROOT, v["jar"]), "rb") as fh:
            body, ct = multipart({"data": data}, [("file0", os.path.basename(v["jar"]), fh.read())])
        made = request("POST", "/version", token, body, {"Content-Type": ct})
        print(f"uploaded {v['version_number']} ({made['id']})")
    if args.skip_gallery:
        return
    existing = {g.get("title") for g in (request("GET", f"/project/{pid}", token, ok404=True) or {}).get("gallery", [])}
    for i, g in enumerate(p["gallery"]):
        if g["title"] in existing:
            continue
        q = urllib.parse.urlencode({"ext": "png", "featured": str(bool(g.get("featured"))).lower(),
                                    "title": g["title"], "description": g.get("description", ""), "ordering": i})
        with open(os.path.join(MR, g["file"]), "rb") as fh:
            request("POST", f"/project/{pid}/gallery?{q}", token, fh.read(), {"Content-Type": "image/png"})
        print(f"gallery: added {g['title']}")
    print(f"done: https://modrinth.com/mod/{p['slug']} (draft until you submit it for review)")


def set_author(args):
    """Put the token owner's Modrinth username into gradle.properties and LICENSE (rebuild the jars afterwards)."""
    name = whoami(get_token())["username"]
    gp = os.path.join(ROOT, "gradle.properties")
    s = open(gp).read()
    s = re.sub(r"^mod_authors=.*$", f"mod_authors={name}", s, flags=re.M)
    open(gp, "w").write(s)
    lic = os.path.join(ROOT, "LICENSE")
    s = open(lic).read().replace("the Calibre author", name)
    open(lic, "w").write(s)
    print(f"author set to {name}; now run ./gradlew buildAll")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("whoami")
    sub.add_parser("set-author")
    pp = sub.add_parser("publish")
    pp.add_argument("--dry-run", action="store_true")
    pp.add_argument("--version", help="mod version (default: mod_version from gradle.properties)")
    pp.add_argument("--changelog", default="First release.")
    pp.add_argument("--skip-gallery", action="store_true")
    args = ap.parse_args()
    if args.cmd == "whoami":
        whoami(get_token())
    elif args.cmd == "set-author":
        set_author(args)
    else:
        publish(args)


if __name__ == "__main__":
    sys.exit(main())

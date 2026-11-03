#!/usr/bin/env python3
"""Find npm package versions known to be compromised, in lockfiles and installed node_modules.

Standard library only. Read-only. Works on its own or as a module for audit.py.

    npm_ioc_scan.py [ROOT ...] [--offline] [--iocs-url URL] [--iocs-file FILE] [--quick] [--json]

ROOT defaults to the home directory plus the npx cache and the global node_modules trees.
Exit code 0 = nothing found, 2 = something found, 1 = could not run.

The version list is the public one maintained at
https://github.com/Drasrax/npm-shai-hulud-scanner (shai-hulud-iocs.json, ~8,400 versions
as of 2026-11), merged with the small built-in list below so the scan still means
something offline. Downloaded data is parsed as JSON and never executed.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.request

IOC_URL = "https://raw.githubusercontent.com/Drasrax/npm-shai-hulud-scanner/main/shai-hulud-iocs.json"

# name -> versions. Sources and dates: ../references/known-campaigns.md
BUILTIN = {
    # 2025-09-08, maintainer phishing: chalk / debug wave (crypto-clipper in the browser)
    "chalk": {"5.6.1"}, "debug": {"4.4.2"}, "ansi-styles": {"6.2.2"}, "strip-ansi": {"7.1.1"},
    "supports-color": {"10.2.1"}, "color-convert": {"3.1.1"}, "color-name": {"2.0.1"},
    "ansi-regex": {"6.2.1"}, "wrap-ansi": {"9.0.1"}, "slice-ansi": {"7.1.1"}, "color-string": {"2.1.1"},
    "simple-swizzle": {"0.2.3"}, "is-arrayish": {"0.3.3"}, "error-ex": {"1.3.3"}, "has-ansi": {"6.0.1"},
    "backslash": {"0.2.1"}, "chalk-template": {"1.1.1"}, "supports-hyperlinks": {"4.1.1"},
    "proto-tinker-wc": {"1.8.7"},
    # 2025-09-15, Shai-Hulud 1: first package hit
    "@ctrl/tinycolor": {"4.1.1", "4.1.2"},
    # 2025-08-26, Nx "s1ngularity"
    "nx": {"20.9.0", "20.10.0", "20.11.0", "20.12.0", "21.5.0", "21.6.0", "21.7.0", "21.8.0"},
    # 2025-07-18, eslint-config-prettier (Windows DLL payload, listed for completeness)
    "eslint-config-prettier": {"8.10.1", "9.1.1", "10.1.6", "10.1.7"},
    "eslint-plugin-prettier": {"4.2.2", "4.2.3"},
    # 2026-03-31, axios published by a compromised maintainer account (postinstall payload)
    "axios": {"1.14.1", "0.30.4"},
}

# File names dropped inside packages or repositories by known worms.
IOC_FILENAMES = {
    "setup_bun.js": "Shai-Hulud 2.0 (2025-11) loader",
    "bun_environment.js": "Shai-Hulud 2.0 (2025-11) payload",
    "shai-hulud-workflow.yml": "Shai-Hulud 1 (2025-09) exfil workflow",
    "shai-hulud.yml": "Shai-Hulud 1 (2025-09) exfil workflow",
}
# Paths relative to a repository root that the ChainDrop worm (2026-08) injects.
INJECTED_PATHS = {".claude/setup.mjs", ".vscode/setup.mjs"}
INJECTED_REFERENCE = {".claude/settings.json", ".claude/settings.local.json", ".vscode/tasks.json"}
# ChainDrop bundle, sha256 (Microsoft, 2026-08-04). Any Math_*.js over this size gets hashed.
CHAINDROP_BUNDLE_SHA256 = "9fc2570b7cef51c1b8df116d144d11ff4096357be7d2c4c6367cfc2509cf1bcc"
CHAINDROP_SETUP_SHA256 = {
    "54dc7ea54a1317cca0e890a2770630cf7fa6c97813e0cb9d2caa93012b350668",
    "fd3ca4007b225fdf8de7af4345a19179d5efa8c4bb9205f88cda806e5684b1eb",
}
MATH_BUNDLE_MIN_BYTES = 50_000

SUSPICIOUS_SCRIPT = re.compile(
    r"setup\.mjs|setup_bun\.js|bun_environment\.js|\bcurl\b|\bwget\b|base64|child_process|"
    r"\beval\(|Buffer\.from\(|\.\/\.[a-z]|/tmp/|\$TMPDIR|powershell|certutil",
    re.I,
)

PRUNE = {
    "Library", ".Trash", ".cache", ".git", ".npm", ".docker", ".gradle", ".m2", ".cargo", ".rustup",
    ".pyenv", ".nvm", ".ollama", ".local", ".cursor", ".vscode", ".vscode-insiders", ".antigravity",
    ".codex", ".codeium", "Applications", "Movies", "Music", "Pictures", "__pycache__", ".venv", "venv",
}


def default_roots():
    home = os.path.expanduser("~")
    roots = [home]
    for extra in (
        os.path.join(home, ".npm", "_npx"),
        "/opt/homebrew/lib/node_modules",
        "/usr/local/lib/node_modules",
    ):
        if os.path.isdir(extra):
            roots.append(extra)
    nvm = os.path.join(home, ".nvm", "versions", "node")
    if os.path.isdir(nvm):
        for v in sorted(os.listdir(nvm)):
            p = os.path.join(nvm, v, "lib", "node_modules")
            if os.path.isdir(p):
                roots.append(p)
    return roots


def _add(bad, name, ver):
    name = (name or "").strip()
    ver = (ver or "").strip().lstrip("v")
    if name and ver:
        bad.setdefault(name, set()).add(ver)


def _absorb_json(bad, data):
    """Pull name/version pairs out of whatever shape the IOC file has."""
    def walk(x):
        if isinstance(x, dict):
            if "name" in x and isinstance(x.get("version"), str):
                _add(bad, x["name"], x["version"])
                return
            if "name" in x and isinstance(x.get("versions"), list):
                for v in x["versions"]:
                    if isinstance(v, str):
                        _add(bad, x["name"], v)
                return
            for k, v in x.items():
                if isinstance(v, list) and v and all(isinstance(i, str) for i in v) and re.match(r"^(@[\w.-]+/)?[\w.-]+$", k):
                    for i in v:
                        _add(bad, k, i)
                else:
                    walk(v)
        elif isinstance(x, list):
            for i in x:
                if isinstance(i, str) and "@" in i[1:]:
                    n, _, v = i.rpartition("@")
                    _add(bad, n, v)
                else:
                    walk(i)
    walk(data)


def load_iocs(offline=False, url=IOC_URL, path=None, timeout=30):
    """Return (name -> set(versions), description of what was loaded)."""
    bad = {n: set(v) for n, v in BUILTIN.items()}
    parts = ["built-in %d packages / %d versions" % (len(BUILTIN), sum(len(v) for v in BUILTIN.values()))]
    raw = None
    if path:
        try:
            raw = open(path, "rb").read()
            parts.append("file %s" % path)
        except OSError as e:
            parts.append("file %s unreadable (%s)" % (path, e))
    elif not offline:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mac-supply-chain-audit"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read(50_000_000)
            parts.append("downloaded %s" % url)
        except Exception as e:  # network is optional
            parts.append("download failed (%s), built-in list only" % e.__class__.__name__)
    if raw:
        before = sum(len(v) for v in bad.values())
        try:
            _absorb_json(bad, json.loads(raw))
        except ValueError:
            for line in raw.decode("utf-8", "ignore").splitlines():
                m = re.match(r"^\s*(@?[\w.-]+(?:/[\w.-]+)?)[@\s:,|]+v?(\d+\.\d+\.\d+\S*)\s*$", line.strip("| "))
                if m:
                    _add(bad, m.group(1), m.group(2))
        parts.append("+%d versions" % (sum(len(v) for v in bad.values()) - before))
    return bad, "; ".join(parts)


def _sha256(path, cap=20_000_000):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        n = 0
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
            n += len(chunk)
            if n > cap:
                return None
    return h.hexdigest()


def _lockfile_versions(path):
    """Yield (name, version) from package-lock.json, yarn.lock or pnpm-lock.yaml."""
    base = os.path.basename(path)
    try:
        text = open(path, "rb").read().decode("utf-8", "ignore")
    except OSError:
        return
    if base == "package-lock.json":
        try:
            d = json.loads(text)
        except ValueError:
            return
        for k, v in (d.get("packages") or {}).items():
            if isinstance(v, dict) and v.get("version"):
                yield k.split("node_modules/")[-1], v["version"]
        for k, v in (d.get("dependencies") or {}).items():
            if isinstance(v, dict) and v.get("version"):
                yield k, v["version"]
    elif base == "yarn.lock":
        for block in re.split(r"\n\s*\n", text):
            lines = block.strip().splitlines()
            if not lines or lines[0].startswith("#"):
                continue
            head = lines[0].rstrip(":").split(",")[0].strip().strip('"')
            name = head.rpartition("@")[0] if head.count("@") > (1 if head.startswith("@") else 0) else head
            m = re.search(r'^\s+version:?\s+"?([^"\s]+)"?', block, re.M)
            if name and m:
                yield name, m.group(1)
    elif base == "pnpm-lock.yaml":
        for m in re.finditer(r"^\s*/?'?(@?[\w.-]+(?:/[\w.-]+)?)@(\d[^\s:'()]*)", text, re.M):
            yield m.group(1), m.group(2)


def scan(roots=None, bad=None, quick=False, max_depth=14, time_budget=600, progress=None):
    """Walk roots. Returns a dict with hits, suspicious install scripts, IOC files, counts."""
    roots = roots or default_roots()
    if bad is None:
        bad, _ = load_iocs(offline=True)
    res = {
        "hits": [], "suspicious_scripts": [], "ioc_files": [], "injected": [], "hash_matches": [],
        "big_math_bundles": [], "npmrc": [], "lockfiles": 0, "packages": 0, "incomplete": False,
        "roots": roots,
    }
    t0 = time.time()
    seen_pkg = set()
    for root0 in roots:
        if not os.path.isdir(root0):
            continue
        base_depth = root0.rstrip(os.sep).count(os.sep)
        for root, dirs, files in os.walk(root0):
            if time.time() - t0 > time_budget:
                res["incomplete"] = True
                dirs[:] = []
                break
            depth = root.count(os.sep) - base_depth
            parts = root.split(os.sep)
            in_nm = "node_modules" in parts
            dirs[:] = [d for d in dirs if d not in PRUNE and not (quick and d == "node_modules")]
            if depth >= max_depth:
                dirs[:] = []
            fset = set(files)
            # Lockfiles (anywhere outside node_modules)
            if not in_nm:
                for lf in ("package-lock.json", "yarn.lock", "pnpm-lock.yaml"):
                    if lf in fset:
                        res["lockfiles"] += 1
                        p = os.path.join(root, lf)
                        for name, ver in _lockfile_versions(p):
                            if name in bad and ver in bad[name]:
                                res["hits"].append({"where": p, "name": name, "version": ver, "kind": "lockfile"})
                if ".npmrc" in fset:
                    res["npmrc"].append(os.path.join(root, ".npmrc"))
                for rel in INJECTED_PATHS:
                    d, f = rel.split("/")
                    if parts[-1] == d and f in fset:
                        res["injected"].append(os.path.join(root, f))
                for rel in INJECTED_REFERENCE:
                    d, f = rel.split("/")
                    if parts[-1] == d and f in fset:
                        p = os.path.join(root, f)
                        try:
                            if "setup.mjs" in open(p, "rb").read(200_000).decode("utf-8", "ignore"):
                                res["injected"].append(p + " (references setup.mjs)")
                        except OSError:
                            pass
            # Known dropped file names
            for f in fset & IOC_FILENAMES.keys():
                res["ioc_files"].append({"path": os.path.join(root, f), "campaign": IOC_FILENAMES[f]})
            # Installed packages
            if in_nm and "package.json" in fset:
                p = os.path.join(root, "package.json")
                try:
                    d = json.loads(open(p, "rb").read(2_000_000))
                except (OSError, ValueError):
                    continue
                if not isinstance(d, dict):
                    continue
                name, ver = d.get("name"), d.get("version")
                if not isinstance(name, str) or not isinstance(ver, str):
                    continue
                key = (name, ver, os.path.realpath(root))
                if key in seen_pkg:
                    continue
                seen_pkg.add(key)
                res["packages"] += 1
                if name in bad and ver in bad[name]:
                    res["hits"].append({"where": root, "name": name, "version": ver, "kind": "installed"})
                scripts = d.get("scripts") if isinstance(d.get("scripts"), dict) else {}
                for hook in ("preinstall", "install", "postinstall"):
                    s = scripts.get(hook)
                    if isinstance(s, str) and SUSPICIOUS_SCRIPT.search(s):
                        res["suspicious_scripts"].append({"package": "%s@%s" % (name, ver), "hook": hook, "script": s[:200], "where": root})
                if "setup.mjs" in fset:
                    p2 = os.path.join(root, "setup.mjs")
                    h = _sha256(p2)
                    if h in CHAINDROP_SETUP_SHA256:
                        res["hash_matches"].append({"path": p2, "campaign": "ChainDrop setup.mjs loader"})
                    elif any(isinstance(scripts.get(k), str) and "setup.mjs" in scripts[k] for k in ("preinstall", "install", "postinstall")):
                        res["suspicious_scripts"].append({"package": "%s@%s" % (name, ver), "hook": "preinstall", "script": "runs setup.mjs (ChainDrop pattern)", "where": root})
            if in_nm:
                for f in fset:
                    if f.lower().startswith("math_") and f.endswith(".js"):
                        p = os.path.join(root, f)
                        try:
                            size = os.path.getsize(p)
                        except OSError:
                            continue
                        if size >= MATH_BUNDLE_MIN_BYTES:
                            h = _sha256(p)
                            if h == CHAINDROP_BUNDLE_SHA256:
                                res["hash_matches"].append({"path": p, "campaign": "ChainDrop Math_*.js bundle"})
                            else:
                                res["big_math_bundles"].append({"path": p, "bytes": size})
            if progress and res["packages"] % 5000 == 0 and res["packages"]:
                progress(res["packages"])
    res["elapsed"] = round(time.time() - t0, 1)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("roots", nargs="*", help="directories to scan (default: home, npx cache, global node_modules)")
    ap.add_argument("--offline", action="store_true", help="do not download the public IOC list")
    ap.add_argument("--iocs-url", default=IOC_URL)
    ap.add_argument("--iocs-file", help="use this IOC list instead of downloading")
    ap.add_argument("--quick", action="store_true", help="lockfiles only, do not walk node_modules")
    ap.add_argument("--max-depth", type=int, default=14)
    ap.add_argument("--time-budget", type=int, default=600, help="seconds before the walk stops")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args(argv)

    bad, src = load_iocs(a.offline, a.iocs_url, a.iocs_file)
    res = scan(a.roots or None, bad, a.quick, a.max_depth, a.time_budget)
    res["ioc_source"] = src
    res["ioc_packages"] = len(bad)
    res["ioc_versions"] = sum(len(v) for v in bad.values())
    found = bool(res["hits"] or res["ioc_files"] or res["injected"] or res["hash_matches"])
    if a.json:
        print(json.dumps(res, indent=1))
    else:
        print("IOC list: %s" % src)
        print("scanned %d lockfiles and %d installed packages in %ss%s" % (
            res["lockfiles"], res["packages"], res["elapsed"], " (INCOMPLETE: time budget hit)" if res["incomplete"] else ""))
        for h in res["hits"]:
            print("COMPROMISED %s@%s  %s (%s)" % (h["name"], h["version"], h["where"], h["kind"]))
        for f in res["ioc_files"]:
            print("IOC FILE    %s  <- %s" % (f["path"], f["campaign"]))
        for p in res["injected"]:
            print("INJECTED    %s" % p)
        for m in res["hash_matches"]:
            print("HASH MATCH  %s  <- %s" % (m["path"], m["campaign"]))
        for s in res["suspicious_scripts"]:
            print("install hook to review: %s %s: %s" % (s["package"], s["hook"], s["script"]))
        for b in res["big_math_bundles"]:
            print("large Math_*.js (hash did not match, review): %s (%d bytes)" % (b["path"], b["bytes"]))
        print("RESULT: %s" % ("SOMETHING FOUND" if found else "nothing known-bad found"))
    return 2 if found else 0


if __name__ == "__main__":
    sys.exit(main())

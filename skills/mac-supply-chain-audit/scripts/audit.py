#!/usr/bin/env python3
"""Read-only audit of a Mac for supply-chain compromise and unexpected outbound traffic.

Prints a Markdown report. Standard library only, macOS only, no sudo. Nothing is changed.

    audit.py [--out FILE] [--project DIR] [--offline] [--no-lookup] [--quick] [--btm] [--skip SECTION ...]

Sections: posture, network, persistence, shell, packages, ide, browser, agents, campaigns.
Network use: reverse-DNS (dig) and AS lookups (whois.cymru.com) of the machine's current
peers, and one download of the public npm IOC list. --no-lookup and --offline turn those off.
--btm runs `sfltool dumpbtm` (login items), which makes macOS ask for an admin password.
"""
import argparse
import concurrent.futures
import datetime
import glob
import json
import os
import plistlib
import re
import socket
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import npm_ioc_scan  # noqa: E402

HOME = os.path.expanduser("~")
FLAGS = []          # (level, section, text)
SECTION_TIMES = {}


# ---------------------------------------------------------------- helpers
def flag(level, section, text):
    FLAGS.append((level, section, text))


def sh(args, timeout=25, stderr=False):
    """Run a command (no shell). Returns stdout (or stdout+stderr), '' on any failure."""
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, errors="replace")
        return (p.stdout + p.stderr) if stderr else p.stdout
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return ""


TOKEN_RE = re.compile(
    r"(sk-[A-Za-z0-9_-]{10,}|AIza[0-9A-Za-z_-]{30,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"xox[baprs]-[A-Za-z0-9-]{10,}|npm_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|"
    r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+|[A-Fa-f0-9]{40,}|[A-Za-z0-9+=_-]{40,})"
)
KV_RE = re.compile(r"(?i)\b([\w-]*(key|token|secret|password|passwd|credential|auth)[\w-]*)(\s*[=:]\s*)(\S+)")


def redact(s):
    if not isinstance(s, str):
        s = str(s)
    s = KV_RE.sub(lambda m: m.group(1) + m.group(3) + "<redacted>", s)
    return TOKEN_RE.sub("<redacted>", s)


def cell(x):
    return str(x).replace("|", "\\|").replace("\n", " ")


def table(headers, rows, empty="(none)"):
    if not rows:
        return [empty, ""]
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for r in rows:
        out.append("| " + " | ".join(cell(c) for c in r) + " |")
    out.append("")
    return out


def short_home(p):
    return p.replace(HOME, "~") if isinstance(p, str) else p


def short_exe(p):
    """/Applications/X.app/Contents/.../Helper -> /Applications/X.app/…/Helper"""
    p = short_home(p)
    m = re.match(r"^(.*?\.app)/(.*/)?([^/]+)$", p)
    return "%s/…/%s" % (m.group(1), m.group(3)) if m and m.group(2) else p


def age_days(path):
    try:
        return (time.time() - os.path.getmtime(path)) / 86400
    except OSError:
        return None


def mtime(path):
    try:
        return datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d")
    except OSError:
        return "?"


TMP_LIKE = re.compile(r"^(/tmp/|/private/tmp/|/private/var/folders/|/var/folders/|" + re.escape(HOME) + r"/Library/Caches/)")


def codesign_team(path):
    """'Apple', 'TEAMID (Authority)', 'unsigned', 'script', 'missing'."""
    if not path or not os.path.exists(path):
        return "missing"
    out = sh(["codesign", "-dv", "--verbose=2", path], timeout=10, stderr=True)
    if "not signed at all" in out:
        return "unsigned"
    if "not a Mach-O" in out or "unrecognized" in out or "bundle format" in out:
        return "script/not Mach-O"
    team = re.search(r"TeamIdentifier=(\S+)", out)
    auth = re.search(r"Authority=([^\n]+)", out)
    if team and team.group(1) != "not set":
        return "%s (%s)" % (team.group(1), auth.group(1)[:60] if auth else "?")
    if auth and "Software Signing" in auth.group(1):
        return "Apple"
    if auth:
        return "adhoc/%s" % auth.group(1)[:50]
    return "unsigned"


# ---------------------------------------------------------------- 1. posture
def sec_posture(a):
    L = ["## 1. Security posture", ""]
    L.append("- host: `%s`, macOS %s (%s), user `%s`" % (
        socket.gethostname(), sh(["sw_vers", "-productVersion"]).strip(), sh(["uname", "-m"]).strip(), os.environ.get("USER", "?")))
    sip = sh(["csrutil", "status"], stderr=True).strip().splitlines()
    L.append("- SIP: %s" % (sip[0] if sip else "?"))
    gk = sh(["spctl", "--status"], stderr=True).strip()
    L.append("- Gatekeeper: %s" % gk)
    if "disabled" in gk:
        flag("red", "posture", "Gatekeeper assessments are disabled")
    try:
        xp = plistlib.load(open("/Library/Apple/System/Library/CoreServices/XProtect.bundle/Contents/Info.plist", "rb"))
        L.append("- XProtect version: %s" % xp.get("CFBundleShortVersionString"))
    except Exception:
        L.append("- XProtect version: ?")
    sshd = sh(["lsof", "-nP", "-iTCP:22", "-sTCP:LISTEN"])
    L.append("- Remote Login (sshd listening on 22): %s" % ("YES" if sshd.strip() else "no"))
    if sshd.strip():
        flag("yellow", "posture", "Remote Login is on (sshd listening); make sure that is deliberate")
    users = []
    for line in sh(["dscl", ".", "-list", "/Users", "UniqueID"]).splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].isdigit() and int(parts[1]) >= 500:
            users.append(parts[0])
    admins = sh(["dscl", ".", "-read", "/Groups/admin", "GroupMembership"]).replace("GroupMembership:", "").split()
    L.append("- user accounts (uid>=500): %s" % ", ".join("%s%s" % (u, " (admin)" if u in admins else "") for u in users))
    px = [l.strip() for l in sh(["scutil", "--proxy"]).splitlines() if re.search(r"Enable\s*:\s*1", l)]
    L.append("- proxies enabled: %s" % (", ".join(px) if px else "none"))
    if px:
        flag("yellow", "posture", "a system proxy is enabled (%s); all traffic may route through it" % ", ".join(px))
    ns = sorted(set(re.findall(r"nameserver\[\d+\]\s*:\s*(\S+)", sh(["scutil", "--dns"]))))
    L.append("- DNS servers: %s" % ", ".join(ns))
    try:
        hosts = [l.strip() for l in open("/etc/hosts") if l.strip() and not l.startswith("#")
                 and "localhost" not in l and "broadcasthost" not in l]
    except OSError:
        hosts = []
    L.append("- /etc/hosts non-default entries: %s" % (", ".join(hosts) if hosts else "none"))
    if hosts:
        flag("yellow", "posture", "/etc/hosts has custom entries: %s" % "; ".join(hosts[:5]))
    sud = [f for f in (os.listdir("/etc/sudoers.d") if os.path.isdir("/etc/sudoers.d") else []) if not f.startswith(".")]
    L.append("- /etc/sudoers.d: %s" % (", ".join(sud) if sud else "empty"))
    L.append("")
    return L


# ---------------------------------------------------------------- 2. network
TUNNEL_RE = re.compile(r"\bssh\b.*\s-[NfqTt]*[RD]\b|\bautossh\b|\bngrok\b|\bcloudflared\b|\bfrpc?\b|\bchisel\b|\bsocat\b|\bbore\b|\brathole\b|\bzrok\b")
LOCAL_RE = re.compile(r"^(127\.|\[::1\]|\[fe80:|\[fd|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|169\.254\.)")


def _lookup(ip):
    bare = ip.strip("[]")
    r = sh(["dig", "+short", "+time=2", "+tries=1", "-x", bare], timeout=6).strip().splitlines()
    if r:
        return r[0].rstrip(".")
    w = sh(["whois", "-h", "whois.cymru.com", " -v " + bare], timeout=8).strip().splitlines()
    if len(w) >= 2 and "|" in w[-1]:
        return "AS: " + w[-1].split("|")[-1].strip()
    return "?"


def sec_network(a):
    L = ["## 2. Who is talking out right now", ""]
    comm = {}
    args = {}
    for line in sh(["ps", "-axo", "pid=,comm="]).splitlines():
        p = line.strip().split(None, 1)
        if len(p) == 2:
            comm[p[0]] = p[1]
    for line in sh(["ps", "-axo", "pid=,args="]).splitlines():
        p = line.strip().split(None, 1)
        if len(p) == 2:
            args[p[0]] = p[1]
    for pid, cmd in args.items():
        if TUNNEL_RE.search(cmd):
            flag("red", "network", "tunnel-like process %s: %s" % (pid, redact(cmd[:160])))

    # established connections
    conns = {}
    pid = name = None
    for line in sh(["lsof", "-nP", "+c", "0", "-iTCP", "-sTCP:ESTABLISHED", "-F", "pcn"]).splitlines():
        if line.startswith("p"):
            pid = line[1:]
        elif line.startswith("c"):
            name = line[1:]
        elif line.startswith("n") and "->" in line:
            remote = line[1:].split("->", 1)[1]
            conns.setdefault(pid, {"name": name, "remote": set(), "local": set()})
            (conns[pid]["local"] if LOCAL_RE.match(remote) else conns[pid]["remote"]).add(remote)
    ips = sorted({r.rsplit(":", 1)[0] for c in conns.values() for r in c["remote"]})
    names = {}
    if not a.no_lookup and ips:
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
            for ip, nm in zip(ips[:80], ex.map(_lookup, ips[:80])):
                names[ip] = nm
    rows = []
    for pid, c in sorted(conns.items(), key=lambda kv: (-len(kv[1]["remote"]), kv[1]["name"])):
        if not c["remote"]:
            continue
        path = comm.get(pid, "?")
        if TMP_LIKE.match(path):
            flag("red", "network", "process %s (%s) talking out runs from a temp/cache path: %s" % (pid, c["name"], path))
        peers = {}
        for r in c["remote"]:
            ip, port = r.rsplit(":", 1)
            peers.setdefault((names.get(ip, ""), ip), set()).add(port)
        peer_txt = "; ".join("%s%s:%s" % (ip, (" (%s)" % nm) if nm else "", ",".join(sorted(ps))) for (nm, ip), ps in sorted(peers.items()))
        rows.append((c["name"], pid, short_exe(path), len(c["remote"]), peer_txt[:400]))
    L += ["Established TCP connections to non-local addresses, by process (snapshot):", ""]
    L += table(["process", "pid", "executable", "conns", "peers (host, org, ports)"], rows)
    loc = [(c["name"], pid, ", ".join(sorted(c["local"]))[:120]) for pid, c in conns.items() if c["local"] and not c["remote"]]
    if loc:
        L += ["Local-only connections (loopback / LAN):", ""] + table(["process", "pid", "peers"], loc)

    # listeners
    rows = []
    pid = name = None
    for line in sh(["lsof", "-nP", "+c", "0", "-iTCP", "-sTCP:LISTEN", "-F", "pcn"]).splitlines():
        if line.startswith("p"):
            pid = line[1:]
        elif line.startswith("c"):
            name = line[1:]
        elif line.startswith("n"):
            addr = line[1:]
            rows.append((name, pid, short_exe(comm.get(pid, "?")), addr, "all interfaces" if addr.startswith("*:") or addr.startswith("[::]:") else "local"))
    rows = sorted(set(rows))
    L += ["Listening TCP ports:", ""] + table(["process", "pid", "executable", "address", "reach"], rows)

    # bytes per process on open sockets
    out = sh(["nettop", "-P", "-x", "-L", "1", "-J", "bytes_in,bytes_out", "-t", "external"], timeout=20)
    rows = []
    for line in out.splitlines()[1:]:
        p = line.split(",")
        if len(p) >= 3 and p[1].isdigit() and p[2].isdigit():
            rows.append((int(p[2]), int(p[1]), p[0]))
    rows.sort(reverse=True)

    def hb(n):
        for u in ("B", "KB", "MB", "GB"):
            if n < 1024:
                return "%.0f %s" % (n, u)
            n /= 1024.0
        return "%.1f TB" % n
    L += ["Bytes on currently open external sockets, per process (nettop; not lifetime totals):", ""]
    L += table(["sent", "received", "process.pid"], [(hb(o), hb(i), p) for o, i, p in rows[:20]])
    return L


# ---------------------------------------------------------------- 3. persistence
def _program(d):
    if d.get("Program"):
        return d["Program"]
    pa = d.get("ProgramArguments")
    if isinstance(pa, list) and pa:
        return pa[0]
    return ""


def sec_persistence(a):
    L = ["## 3. Persistence", ""]
    rows = []
    for d in (os.path.join(HOME, "Library/LaunchAgents"), "/Library/LaunchAgents", "/Library/LaunchDaemons"):
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".plist"):
                continue
            p = os.path.join(d, f)
            try:
                pl = plistlib.load(open(p, "rb"))
            except PermissionError:
                rows.append((short_home(d), f, "(root-only, unreadable)", "", "", mtime(p)))
                continue
            except Exception as e:
                rows.append((short_home(d), f, "(unparseable: %s)" % e.__class__.__name__, "", "", mtime(p)))
                continue
            label = pl.get("Label") or f
            prog = _program(pl)
            sig = codesign_team(prog) if prog else ("empty plist (inert)" if not pl else "no program; keys: %s" % ",".join(sorted(pl.keys()))[:60])
            runs = ",".join(k for k in ("RunAtLoad", "KeepAlive") if pl.get(k))
            rows.append((short_home(d), label, short_home(prog), sig, runs, mtime(p)))
            if label.startswith("com.apple.") and not d.startswith("/System"):
                flag("red", "persistence", "'%s' in %s uses an Apple-looking label (Apple's own live in /System)" % (label, short_home(d)))
            if prog and (TMP_LIKE.match(prog) or re.match(re.escape(HOME) + r"/\.[^/]+/", prog) and "/.local/" not in prog):
                flag("red", "persistence", "'%s' runs %s (temp, cache or hidden directory)" % (label, short_home(prog)))
            elif sig in ("unsigned", "missing") or sig.startswith("adhoc"):
                flag("yellow", "persistence", "'%s' program is %s: %s" % (label, sig, short_home(prog)))
            ad = age_days(p)
            if ad is not None and ad < 14 and not (sig == "Apple" or "Developer ID" in sig):
                flag("yellow", "persistence", "'%s' plist modified %d day(s) ago and its program is %s" % (label, ad, sig))
    L += ["Launch agents and daemons (program signature via codesign):", ""]
    L += table(["dir", "label", "program", "signed by", "runs", "modified"], rows)

    lc = []
    for line in sh(["launchctl", "list"]).splitlines()[1:]:
        p = line.split("\t")
        if len(p) == 3 and "com.apple." not in p[2]:
            lc.append("%s%s" % (p[2], (" (pid %s)" % p[0]) if p[0] != "-" else ""))
    L += ["Non-Apple jobs loaded in this user's launchd (includes app-bundled login items): " + (", ".join(lc) if lc else "none"), ""]

    cron = sh(["crontab", "-l"], stderr=True).strip()
    L.append("- user crontab: %s" % ("none" if "no crontab" in cron or not cron else "PRESENT, see below"))
    if cron and "no crontab" not in cron:
        L += ["", "```", cron[:2000], "```"]
        flag("yellow", "persistence", "user crontab has entries")
    for p in ("/etc/crontab", "/etc/cron.d"):
        if os.path.exists(p):
            L.append("- %s exists" % p)
            flag("yellow", "persistence", "%s exists (not standard on macOS)" % p)
    for d in ("/Library/StartupItems", "/etc/emond.d/rules"):
        try:
            items = [f for f in os.listdir(d) if not f.startswith(".")]
        except OSError:
            items = []
        if items:
            L.append("- %s: %s" % (d, ", ".join(items)))
            flag("yellow", "persistence", "%s is not empty: %s" % (d, ", ".join(items)))
    if a.btm:
        out = sh(["sfltool", "dumpbtm"], timeout=120)
        items = re.findall(r"Name:\s*(.+?)\n.*?Team Identifier:\s*(\S+).*?Type:\s*([^\n]+).*?URL:\s*([^\n]+)", out, re.S)
        L += ["", "Login items / background tasks (sfltool dumpbtm):", ""]
        L += table(["name", "team", "type", "url"], [(n.strip(), t, ty.strip(), u.strip()) for n, t, ty, u in items])
    else:
        L.append("- login items (sfltool dumpbtm): skipped; pass `--btm` (prompts for an admin password)")
    L.append("")
    return L


# ---------------------------------------------------------------- 4. shell
SHELL_PATTERNS = [
    (re.compile(r"(curl|wget)[^|\n]*\|\s*(sudo\s+)?(ba|z|da)?sh\b"), "red", "pipe-to-shell"),
    (re.compile(r"eval\s+[\"']?\$\((curl|wget)"), "red", "eval of a download"),
    (re.compile(r"\bshutdown\b"), "red", "shutdown (nx s1ngularity signature)"),
    (re.compile(r"/dev/tcp/|\bnc\b[^\n]*\s-e\b|\bncat\b|\bsocat\b|\bmkfifo\b"), "red", "reverse-shell primitive"),
    (re.compile(r"DYLD_INSERT_LIBRARIES|LD_PRELOAD"), "red", "library injection variable"),
    (re.compile(r"base64\s+(-d|-D|--decode)"), "red", "base64 decode"),
    (re.compile(r"^\s*alias\s+(sudo|ssh|git|npm|npx|brew|curl|wget|ls|cd)="), "yellow", "alias over a core command"),
    (re.compile(r"\bosascript\b"), "yellow", "AppleScript call"),
    (re.compile(r"\bpython[23]?\s+-c\b|\bnode\s+-e\b|\bperl\s+-e\b"), "yellow", "inline interpreter code"),
]
SECRET_RE = re.compile(r"(?i)^\s*(export\s+)?([A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL)[A-Z0-9_]*)\s*=\s*\S")
RC_FILES = [".zshenv", ".zprofile", ".zshrc", ".zlogin", ".zlogout", ".bash_profile", ".bashrc", ".bash_login",
            ".profile", ".bash_logout", ".config/fish/config.fish"]
SYS_RC = ["/etc/zshenv", "/etc/zprofile", "/etc/zshrc", "/etc/zlogin", "/etc/profile", "/etc/bashrc"]


def sec_shell(a):
    L = ["## 4. Shell start-up files", ""]
    rows = []
    for f in [os.path.join(HOME, r) for r in RC_FILES] + SYS_RC:
        if not os.path.isfile(f):
            continue
        try:
            lines = open(f, errors="replace").read().splitlines()
        except OSError:
            continue
        notes = []
        for i, line in enumerate(lines, 1):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            for rx, lvl, what in SHELL_PATTERNS:
                if rx.search(s):
                    notes.append("L%d %s" % (i, what))
                    flag(lvl, "shell", "%s line %d: %s: %s" % (short_home(f), i, what, redact(s[:120])))
            m = SECRET_RE.match(s)
            if m:
                notes.append("L%d plaintext %s" % (i, m.group(2)))
                flag("yellow", "shell", "%s line %d sets %s in plaintext (readable by every process you run)" % (short_home(f), i, m.group(2)))
            m = re.match(r"^(source|\.)\s+([\"']?)(\S+)", s)
            if m:
                notes.append("sources %s" % m.group(3).strip("\"'"))
        rows.append((short_home(f), mtime(f), len(lines), "; ".join(notes)[:300] if notes else ""))
    L += table(["file", "modified", "lines", "notes (flags, secrets by name, sourced files)"], rows)
    L.append("Secrets are reported by variable name only; values never appear in this report.")
    L.append("")
    return L


# ---------------------------------------------------------------- 5. packages
PLACEHOLDER_RE = re.compile(r"reserved|to be continued|placeholder|coming soon|stay tuned", re.I)


def _global_npm_dirs():
    dirs = []
    root = sh(["npm", "root", "-g"]).strip()
    if root:
        dirs.append(root)
    for d in ("/opt/homebrew/lib/node_modules", "/usr/local/lib/node_modules") + tuple(glob.glob(os.path.join(HOME, ".nvm/versions/node/*/lib/node_modules"))):
        if os.path.isdir(d) and d not in dirs:
            dirs.append(d)
    return dirs


def sec_packages(a):
    L = ["## 5. Packages", ""]
    # --- npm global
    L += ["### npm", ""]
    L.append("- npm %s, registry `%s`, ignore-scripts `%s`" % (
        sh(["npm", "-v"]).strip(), sh(["npm", "config", "get", "registry"]).strip(), sh(["npm", "config", "get", "ignore-scripts"]).strip()))
    reg = sh(["npm", "config", "get", "registry"]).strip()
    if reg and "registry.npmjs.org" not in reg:
        flag("yellow", "packages", "npm registry is %s (not registry.npmjs.org)" % reg)
    npmrc = os.path.join(HOME, ".npmrc")
    if os.path.isfile(npmrc):
        keys = [redact(l.strip()) for l in open(npmrc, errors="replace") if l.strip() and not l.startswith("#")]
        L.append("- ~/.npmrc: %s" % ("; ".join(keys)[:300] if keys else "empty"))
    rows = []
    for d in _global_npm_dirs():
        for pj in sorted(glob.glob(os.path.join(d, "*", "package.json")) + glob.glob(os.path.join(d, "@*", "*", "package.json"))):
            try:
                m = json.load(open(pj))
            except Exception:
                continue
            pdir = os.path.dirname(pj)
            name, ver = m.get("name", "?"), m.get("version", "?")
            hooks = [h for h in ("preinstall", "install", "postinstall") if isinstance(m.get("scripts"), dict) and m["scripts"].get(h)]
            notes = []
            readme = ""
            for rn in ("README.md", "readme.md", "README"):
                if os.path.isfile(os.path.join(pdir, rn)):
                    try:
                        readme = open(os.path.join(pdir, rn), errors="replace").read(2000)
                    except OSError:
                        pass
                    break
            if PLACEHOLDER_RE.search((m.get("description") or "") + " " + readme):
                notes.append("placeholder README")
                flag("yellow", "packages", "global npm package %s@%s is a placeholder/name-squat ('%s'); uninstall it" % (name, ver, (m.get("description") or readme[:60]).strip()[:80]))
            if not m.get("repository") and not m.get("bin") and not m.get("dependencies") and str(ver).startswith("0.0."):
                notes.append("bare 0.0.x, no repo/bin/deps")
            if hooks:
                notes.append("install hooks: " + ",".join(hooks))
            rows.append((short_home(d), "%s@%s" % (name, ver), (m.get("description") or "")[:70], mtime(pdir), "; ".join(notes)))
    L += ["", "Globally installed packages:", ""] + table(["root", "package", "description", "installed", "notes"], rows)

    # --- IOC scan
    L += ["### Known-compromised versions (lockfiles + every installed node_modules under ~)", ""]
    bad, src = npm_ioc_scan.load_iocs(offline=a.offline)
    res = npm_ioc_scan.scan(None, bad, quick=a.quick, time_budget=a.time_budget)
    a._npm_scan = res
    L.append("- IOC list: %s (%d packages, %d versions)" % (src, len(bad), sum(len(v) for v in bad.values())))
    L.append("- scanned %d lockfiles and %d installed packages in %ss%s" % (
        res["lockfiles"], res["packages"], res["elapsed"], " **INCOMPLETE: time budget hit, rerun with --time-budget**" if res["incomplete"] else ""))
    for h in res["hits"]:
        flag("red", "packages", "COMPROMISED %s@%s at %s" % (h["name"], h["version"], short_home(h["where"])))
    for f in res["ioc_files"]:
        flag("red", "packages", "worm file %s (%s)" % (short_home(f["path"]), f["campaign"]))
    for p in res["injected"]:
        flag("red", "packages", "ChainDrop-style injected file: %s" % short_home(p))
    for m in res["hash_matches"]:
        flag("red", "packages", "hash match %s (%s)" % (short_home(m["path"]), m["campaign"]))
    L.append("- compromised versions: %d, worm files: %d, injected repo files: %d, hash matches: %d" % (
        len(res["hits"]), len(res["ioc_files"]), len(res["injected"]), len(res["hash_matches"])))
    if res["suspicious_scripts"]:
        L += ["", "Install hooks worth a look (pattern match, usually benign native builds):", ""]
        L += table(["package", "hook", "script"], [(s["package"], s["hook"], s["script"][:120]) for s in res["suspicious_scripts"][:40]])
    if res["big_math_bundles"]:
        L += ["", "Large `Math_*.js` files (ChainDrop bundle name; hashes did NOT match, listed for review):", ""]
        L += table(["path", "bytes"], [(short_home(b["path"]), b["bytes"]) for b in res["big_math_bundles"][:20]])
    custom = []
    for p in res["npmrc"]:
        try:
            for l in open(p, errors="replace"):
                if re.search(r"registry|_auth|always-auth", l, re.I):
                    custom.append((short_home(p), redact(l.strip())[:120]))
        except OSError:
            pass
    if custom:
        L += ["", "Project .npmrc files with registry/auth settings:", ""] + table(["file", "line"], custom)
        for p, l in custom:
            if "registry" in l and "registry.npmjs.org" not in l:
                flag("yellow", "packages", "%s points at a custom registry: %s" % (p, l))
    L.append("")

    # --- project install hooks
    proj = a.project or (os.getcwd() if os.path.isfile(os.path.join(os.getcwd(), "package.json")) else None)
    if proj and os.path.isdir(os.path.join(proj, "node_modules")):
        rows = []
        nm = os.path.join(proj, "node_modules")
        for pj in glob.glob(os.path.join(nm, "*", "package.json")) + glob.glob(os.path.join(nm, "@*", "*", "package.json")):
            try:
                m = json.load(open(pj))
            except Exception:
                continue
            sc = m.get("scripts") if isinstance(m.get("scripts"), dict) else {}
            hooks = [(h, sc[h]) for h in ("preinstall", "install", "postinstall") if sc.get(h)]
            if hooks:
                rows.append(("%s@%s" % (m.get("name"), m.get("version")), "; ".join("%s: %s" % (h, s[:80]) for h, s in hooks)))
        L += ["### Install hooks in %s" % short_home(proj), ""] + table(["package", "hooks"], sorted(rows))

    # --- Homebrew
    L += ["### Homebrew", ""]
    taps = sh(["brew", "tap"], timeout=60).split()
    forms = sh(["brew", "list", "--formula"], timeout=90).split()
    casks = sh(["brew", "list", "--cask"], timeout=90).split()
    L.append("- taps: %s" % (", ".join(taps) if taps else "none/brew missing"))
    for t in taps:
        if not t.startswith("homebrew/"):
            flag("yellow", "packages", "third-party Homebrew tap: %s (its formulae are built from that repo)" % t)
    L.append("- %d formulae: %s" % (len(forms), " ".join(forms)))
    L.append("- %d casks: %s" % (len(casks), " ".join(casks)))
    L.append("")

    # --- Python
    L += ["### Python", ""]
    interps = sorted(set(glob.glob("/opt/homebrew/opt/python@*/bin/python3.*") + glob.glob("/Library/Frameworks/Python.framework/Versions/*/bin/python3")
                         + glob.glob(os.path.join(HOME, ".pyenv/versions/*/bin/python3"))))
    interps = [i for i in interps if re.search(r"python3(\.\d+)?$", i)]
    seen_rp = set()
    for i in interps:
        rp = os.path.realpath(i)
        if rp in seen_rp:
            continue
        seen_rp.add(rp)
        out = sh([i, "-m", "pip", "list", "--format=json", "--disable-pip-version-check"], timeout=60)
        try:
            names = [p["name"] for p in json.loads(out)]
        except Exception:
            names = []
        if names:
            L.append("- `%s` (%d): %s%s" % (short_home(i), len(names), " ".join(names[:120]), " … (+%d)" % (len(names) - 120) if len(names) > 120 else ""))
    uv = sh(["uv", "tool", "list"], timeout=30).strip()
    if uv:
        L.append("- uv tools: %s" % " ".join(l.split()[0] for l in uv.splitlines() if l and not l.startswith("-")))
    px = sh(["pipx", "list", "--short"], timeout=30).strip()
    if px:
        L.append("- pipx: %s" % " ".join(px.split()))
    L.append("")

    # --- ~/.local/bin and /usr/local/bin
    for d in (os.path.join(HOME, ".local/bin"), "/usr/local/bin"):
        if not os.path.isdir(d):
            continue
        rows = []
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            if os.path.islink(p):
                rows.append((f, "-> " + short_home(os.readlink(p)), mtime(p)))
            elif os.path.isfile(p):
                kind = sh(["file", "-b", p], timeout=10).strip()[:50]
                rows.append((f, kind, mtime(p)))
        if rows and len(rows) <= 60:
            L += ["### %s" % short_home(d), ""] + table(["name", "what", "modified"], rows)
        elif rows:
            L += ["### %s: %d entries (not listed)" % (short_home(d), len(rows)), ""]
    return L


# ---------------------------------------------------------------- 6. IDE extensions
KNOWN_BAD_EXTENSIONS = {  # id -> {versions}: see references/known-campaigns.md
    "anthropic.claude-code": {"2.1.312", "2.1.313"},
}
EXTENSION_IOC_STRINGS = [b"134.209.82.225", b"svc-telemetry"]
EXT_ROOTS = [".vscode/extensions", ".vscode-insiders/extensions", ".cursor/extensions", ".codeium/windsurf/extensions",
             ".antigravity/extensions", ".windsurf/extensions", ".trae/extensions", ".kiro/extensions", ".positron/extensions"]


def sec_ide(a):
    L = ["## 6. IDE extensions (VS Code, Cursor, Windsurf, Antigravity, ...)", ""]
    for rel in EXT_ROOTS:
        root = os.path.join(HOME, rel)
        if not os.path.isdir(root):
            continue
        rows = []
        meta = {}
        try:
            for e in json.load(open(os.path.join(root, "extensions.json"))):
                idn = e.get("identifier", {}).get("id", "")
                md = e.get("metadata") or {}
                ts = md.get("installedTimestamp")
                meta[(idn.lower(), e.get("version"))] = (
                    datetime.datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d") if ts else "?",
                    md.get("source") or "?", md.get("publisherDisplayName") or "")
        except Exception:
            pass
        for d in sorted(os.listdir(root)):
            p = os.path.join(root, d)
            if not os.path.isdir(p) or d.startswith("."):
                continue
            m = re.match(r"^(.+?)-(\d+\.\d+\.\d+[^-]*)(-.*)?$", d)
            idn, ver = (m.group(1), m.group(2)) if m else (d, "?")
            inst, src, pub = meta.get((idn.lower(), ver), ("?", "?", ""))
            note = ""
            if idn.lower() in KNOWN_BAD_EXTENSIONS and ver in KNOWN_BAD_EXTENSIONS[idn.lower()]:
                note = "KNOWN TROJANIZED VERSION"
                flag("red", "ide", "%s %s in %s is a known trojanized build" % (idn, ver, rel))
            if src not in ("gallery", "?"):
                note += " sideloaded (%s)" % src
                flag("yellow", "ide", "%s %s in %s was not installed from the marketplace (source %s)" % (idn, ver, rel, src))
            hits = set()
            for js in glob.glob(os.path.join(p, "**", "*.js"), recursive=True)[:400]:
                try:
                    if os.path.getsize(js) > 30_000_000:
                        continue
                    data = open(js, "rb").read()
                except OSError:
                    continue
                for s in EXTENSION_IOC_STRINGS:
                    if s in data:
                        hits.add(s.decode())
            if hits:
                note += " IOC strings: " + ",".join(sorted(hits))
                flag("red", "ide", "%s %s contains IOC strings %s" % (idn, ver, ",".join(sorted(hits))))
            rows.append((idn, ver, inst, src, pub, note.strip()))
        L += ["### ~/%s" % rel, ""] + table(["extension", "version", "installed", "source", "publisher", "notes"], rows)
    if len(L) == 2:
        L.append("(no extension directories found)")
    L.append("")
    return L


# ---------------------------------------------------------------- 7. browser
BROWSER_DIRS = [
    ("Chrome", "Library/Application Support/Google/Chrome"),
    ("Chrome Canary", "Library/Application Support/Google/Chrome Canary"),
    ("Chromium", "Library/Application Support/Chromium"),
    ("Brave", "Library/Application Support/BraveSoftware/Brave-Browser"),
    ("Edge", "Library/Application Support/Microsoft Edge"),
    ("Vivaldi", "Library/Application Support/Vivaldi"),
    ("Arc", "Library/Application Support/Arc/User Data"),
    ("Opera", "Library/Application Support/com.operasoftware.Opera"),
]
RISKY_PERMS = {"<all_urls>", "*://*/*", "http://*/*", "https://*/*", "webRequest", "webRequestBlocking", "declarativeNetRequest",
               "cookies", "clipboardRead", "nativeMessaging", "debugger", "proxy", "management", "history", "tabs", "scripting",
               "webNavigation", "downloads", "privacy", "contentSettings"}
USERSCRIPT_MANAGERS = {"dhdgffkkebhmkfjojejmpbldmpobfkfo": "Tampermonkey", "gcalenpjmijncebpfijmoaglllgpjagf": "Tampermonkey BETA",
                       "jinjaccalgkegednnccohejagnlnfdag": "Violentmonkey"}


def _ext_name(mdir, m):
    name = m.get("name", "")
    if isinstance(name, str) and name.startswith("__MSG_"):
        key = name[6:-2]
        for loc in (m.get("default_locale", "en"), "en", "en_US"):
            try:
                msgs = json.load(open(os.path.join(mdir, "_locales", loc, "messages.json")))
            except Exception:
                continue
            for k, v in msgs.items():
                if k.lower() == key.lower() and isinstance(v, dict):
                    return v.get("message", name)
    return name


def sec_browser(a):
    L = ["## 7. Browser extensions and native messaging hosts", ""]
    for bname, rel in BROWSER_DIRS:
        base = os.path.join(HOME, rel)
        if not os.path.isdir(base):
            continue
        exts = {}
        unpacked = []
        for prof in sorted(os.listdir(base)):
            pdir = os.path.join(base, prof)
            edir = os.path.join(pdir, "Extensions")
            if not os.path.isdir(edir):
                continue
            # unpacked / command-line extensions from Secure Preferences
            for prefname in ("Secure Preferences", "Preferences"):
                try:
                    prefs = json.load(open(os.path.join(pdir, prefname)))
                    for eid, s in (prefs.get("extensions", {}).get("settings") or {}).items():
                        path = s.get("path", "")
                        if isinstance(path, str) and path.startswith("/") and s.get("location") in (4, 8):
                            unpacked.append((prof, eid, short_home(path), "disabled" if s.get("state") == 0 else "enabled"))
                    break
                except Exception:
                    continue
            for eid in os.listdir(edir):
                vdirs = [v for v in glob.glob(os.path.join(edir, eid, "*")) if os.path.isfile(os.path.join(v, "manifest.json"))]
                if not vdirs:
                    continue
                vdir = sorted(vdirs)[-1]
                try:
                    m = json.load(open(os.path.join(vdir, "manifest.json")))
                except Exception:
                    continue
                ver = os.path.basename(vdir).split("_")[0]
                upd = m.get("update_url", "")
                source = "webstore" if re.search(r"clients2\.google\.com|edge\.microsoft\.com|extension-updates\.opera\.com|addons\.opera\.com", upd) else ("SIDELOADED" if not upd else upd[:60])
                perms = [p for p in (m.get("permissions", []) + m.get("host_permissions", [])) if isinstance(p, str) and p in RISKY_PERMS]
                allsites = any(p in ("<all_urls>", "*://*/*", "http://*/*", "https://*/*") for p in perms)
                e = exts.setdefault(eid, {"name": _ext_name(vdir, m), "versions": set(), "profiles": set(), "source": source,
                                          "mv": m.get("manifest_version"), "perms": set(), "allsites": allsites})
                e["versions"].add(ver)
                e["profiles"].add(prof)
                e["perms"].update(p for p in perms if not p.startswith("<") and "*" not in p)
                if eid in USERSCRIPT_MANAGERS:
                    e["scripts"] = _userscripts(os.path.join(pdir, "Local Extension Settings", eid))
        rows = []
        for eid, e in sorted(exts.items(), key=lambda kv: kv[1]["name"].lower()):
            note = []
            if e["source"] == "SIDELOADED":
                note.append("no update_url")
                flag("yellow", "browser", "%s extension '%s' (%s) has no update_url: not from a store" % (bname, e["name"], eid))
            elif e["source"] != "webstore":
                note.append("updates from " + e["source"])
                flag("yellow", "browser", "%s extension '%s' (%s) updates from %s" % (bname, e["name"], eid, e["source"]))
            if e["mv"] == 2:
                note.append("MV2")
            if e.get("scripts"):
                note.append("userscripts: " + "; ".join(e["scripts"])[:300])
            reach = ("all sites; " if e["allsites"] else "") + ",".join(sorted(e["perms"]))
            rows.append((e["name"][:45], eid, ",".join(sorted(e["versions"]))[:40], len(e["profiles"]), e["source"], reach, " ".join(note)))
        L += ["### %s (%d extensions across profiles)" % (bname, len(rows)), ""]
        L += table(["name", "id", "version(s)", "profiles", "source", "reach", "notes"], rows)
        if unpacked:
            L += ["Unpacked / command-line extensions (loaded from a folder, not a store):", ""] + table(["profile", "id", "path", "state"], unpacked)
            for prof, eid, path, st in unpacked:
                flag("yellow", "browser", "%s profile '%s' loads an unpacked extension from %s (%s)" % (bname, prof, path, st))
    # native messaging hosts
    rows = []
    for d in glob.glob(os.path.join(HOME, "Library/Application Support/*/NativeMessagingHosts")) + \
            glob.glob(os.path.join(HOME, "Library/Application Support/*/*/NativeMessagingHosts")) + \
            glob.glob("/Library/*/NativeMessagingHosts") + glob.glob("/Library/Application Support/*/NativeMessagingHosts"):
        for f in sorted(glob.glob(os.path.join(d, "*.json"))):
            try:
                h = json.load(open(f))
            except Exception:
                continue
            path = h.get("path", "")
            state = "ok" if os.path.exists(path) else "MISSING"
            if TMP_LIKE.match(path):
                state = "TEMP PATH"
                flag("red", "browser", "native messaging host %s runs from a temp path: %s" % (h.get("name"), path))
            rows.append((short_home(d).replace("/Library/Application Support/", "/AS/").replace("/NativeMessagingHosts", ""), h.get("name", "?"), short_home(path), state,
                         ",".join(o.replace("chrome-extension://", "")[:33] for o in h.get("allowed_origins", []))[:80]))
    L += ["### Native messaging hosts (a browser extension can launch these programs)", ""]
    L += table(["dir", "name", "program", "state", "allowed extension ids"], rows)
    return L


def _userscripts(d):
    out = set()
    for f in glob.glob(os.path.join(d, "*.ldb")) + glob.glob(os.path.join(d, "*.log")):
        try:
            data = open(f, "rb").read(50_000_000)
        except OSError:
            continue
        for m in re.finditer(rb"@(name|require|connect|downloadURL|updateURL)[ \t]+([\x20-\x5b\x5d-\x7e]{2,110})", data):
            key, val = m.group(1).decode(), m.group(2).decode().strip()
            if key == "name" and not re.match(r"^[A-Za-z0-9][A-Za-z0-9 ._:()/-]{1,60}$", val):
                continue
            if key != "name" and not re.match(r"^(https?://\S+|[A-Za-z0-9.*-]+)$", val):
                continue
            out.add("@%s %s" % (key, val))
    return sorted(out)[:40]


# ---------------------------------------------------------------- 8. agents, MCP, hooks, git, ssh
def _mcp_json(path, out):
    try:
        d = json.load(open(path))
    except Exception:
        return
    def add(servers, scope):
        for k, v in (servers or {}).items():
            if isinstance(v, dict):
                cmd = " ".join([v.get("command") or ""] + [redact(str(x)) for x in (v.get("args") or [])]).strip()
                out.append((short_home(path), scope, k, cmd[:140], v.get("url") or v.get("serverUrl") or "", ",".join((v.get("env") or {}).keys())))
    add(d.get("mcpServers"), "user" if path.startswith(HOME + "/.") or "/Library/" in path else "project")
    for proj, pv in (d.get("projects") or {}).items():
        if isinstance(pv, dict):
            add(pv.get("mcpServers"), "project …" + short_home(proj)[-36:])


def sec_agents(a):
    L = ["## 8. AI agents, MCP servers, hooks, git and SSH", ""]
    rows = []
    for p in [os.path.join(HOME, ".claude.json"), os.path.join(HOME, ".cursor/mcp.json"), os.path.join(HOME, ".codeium/windsurf/mcp_config.json"),
              os.path.join(HOME, "Library/Application Support/Claude/claude_desktop_config.json"), os.path.join(HOME, ".gemini/settings.json"),
              os.path.join(HOME, ".kiro/settings/mcp.json"), os.path.join(HOME, ".windsurf/mcp_config.json")] + \
             ([os.path.join(a.project or os.getcwd(), ".cursor/mcp.json"), os.path.join(a.project or os.getcwd(), ".mcp.json")]):
        if os.path.isfile(p):
            _mcp_json(p, rows)
    codex = os.path.join(HOME, ".codex/config.toml")
    if os.path.isfile(codex):
        txt = open(codex, errors="replace").read()
        for m in re.finditer(r"^\[mcp_servers\.([^\].\n]+)\]\n(.*?)(?=^\[|\Z)", txt, re.M | re.S):
            body = m.group(2)
            cmd = re.search(r'command\s*=\s*"([^"]*)"', body)
            args = re.search(r"args\s*=\s*\[([^\]]*)\]", body)
            url = re.search(r'url\s*=\s*"([^"]*)"', body)
            rows.append(("~/.codex/config.toml", "user", m.group(1), redact((cmd.group(1) if cmd else "") + " " + (args.group(1) if args else ""))[:140], url.group(1) if url else "", ""))
    goose = os.path.join(HOME, ".config/goose/config.yaml")
    if os.path.isfile(goose):
        cur = None
        for line in open(goose, errors="replace"):
            m = re.match(r"^  (\w[\w-]*):\s*$", line)
            if m:
                cur = m.group(1)
            m = re.match(r"^\s+(cmd|uri|command):\s*(.+)$", line)
            if m and cur:
                rows.append(("~/.config/goose/config.yaml", "extension", cur, redact(m.group(2).strip())[:140], "", ""))
    for r in rows:
        if TMP_LIKE.match(r[3].split(" ")[0] if r[3] else ""):
            flag("red", "agents", "MCP server '%s' in %s runs from a temp path" % (r[2], r[0]))
        if r[4].startswith("http://") and "localhost" not in r[4] and "127.0.0.1" not in r[4]:
            flag("yellow", "agents", "MCP server '%s' in %s uses plain http: %s" % (r[2], r[0], r[4]))
    L += ["### MCP servers (each one is code or a service your agent trusts)", ""]
    L += table(["config", "scope", "name", "command (args redacted)", "url", "env keys"], rows)

    rows = []
    for p in [os.path.join(HOME, ".claude/settings.json"), os.path.join(HOME, ".claude/settings.local.json"),
              os.path.join(a.project or os.getcwd(), ".claude/settings.json"), os.path.join(a.project or os.getcwd(), ".claude/settings.local.json")]:
        if not os.path.isfile(p):
            continue
        try:
            hooks = json.load(open(p)).get("hooks") or {}
        except Exception:
            continue
        for event, lst in hooks.items():
            for item in (lst if isinstance(lst, list) else []):
                for h in (item.get("hooks") or [item]) if isinstance(item, dict) else []:
                    if isinstance(h, dict) and h.get("command"):
                        cmd = redact(h["command"])
                        rows.append((short_home(p), event, cmd[:160]))
                        if re.search(r"(curl|wget)[^|]*\|\s*(ba|z)?sh|base64\s+-d", cmd):
                            flag("red", "agents", "Claude Code hook (%s in %s) pipes a download to a shell" % (event, short_home(p)))
    L += ["### Claude Code hooks (shell commands run on agent events)", ""] + table(["settings file", "event", "command"], rows)
    plugins = sorted(os.listdir(os.path.join(HOME, ".claude/plugins/marketplaces"))) if os.path.isdir(os.path.join(HOME, ".claude/plugins/marketplaces")) else []
    L.append("- Claude Code plugin marketplaces: %s" % (", ".join(plugins) if plugins else "none"))
    skills = os.path.join(HOME, ".claude/skills")
    if os.path.isdir(skills):
        L.append("- ~/.claude/skills: %s" % ", ".join(sorted(f for f in os.listdir(skills) if not f.startswith("."))))

    # git
    gl = [l for l in sh(["git", "config", "--global", "--list"]).splitlines()
          if re.match(r"(core\.hookspath|core\.fsmonitor|core\.sshcommand|core\.askpass|core\.pager|core\.editor|credential\.|url\..*insteadof|include\.|alias\.|protocol\.)", l, re.I)]
    L += ["", "### git global config (keys that can run code or redirect fetches)", ""]
    L += ["- " + redact(l) for l in gl] if gl else ["(none of interest)"]
    for l in gl:
        if re.match(r"core\.(hookspath|fsmonitor|sshcommand|askpass)=", l, re.I):
            flag("yellow", "agents", "git %s" % l[:120])
    hp = os.path.join(HOME, ".git-credentials")
    if os.path.isfile(hp):
        L.append("- ~/.git-credentials exists (plaintext git passwords/tokens)")
        flag("yellow", "agents", "~/.git-credentials stores git credentials in plaintext")

    # ssh
    L += ["", "### SSH", ""]
    ak = os.path.join(HOME, ".ssh/authorized_keys")
    if os.path.isfile(ak):
        rows = []
        for line in open(ak, errors="replace"):
            if line.strip() and not line.startswith("#"):
                parts = line.split()
                comment = parts[2] if len(parts) > 2 else ""
                rows.append((parts[0], comment, line.strip()[:40] + "..."))
                if comment == "svc-telemetry":
                    flag("red", "agents", "authorized_keys has the 'svc-telemetry' key from the trojanized Claude Code extension")
                else:
                    flag("yellow", "agents", "authorized_keys allows a key in (%s %s); confirm it is yours" % (parts[0], comment))
        L += ["~/.ssh/authorized_keys (anyone with these private keys can log in as you):", ""] + table(["type", "comment", "key"], rows)
    else:
        L.append("- ~/.ssh/authorized_keys: none")
    cfg = os.path.join(HOME, ".ssh/config")
    if os.path.isfile(cfg):
        odd = [l.strip() for l in open(cfg, errors="replace") if re.search(r"ProxyCommand|LocalCommand|PermitLocalCommand|RemoteCommand", l, re.I)]
        L.append("- ~/.ssh/config command directives: %s" % ("; ".join(odd) if odd else "none"))
        for l in odd:
            flag("yellow", "agents", "~/.ssh/config: %s" % l[:120])
    keys = sorted(os.path.basename(f) for f in glob.glob(os.path.join(HOME, ".ssh/*")) if not f.endswith(".pub") and os.path.isfile(f)
                  and os.path.basename(f) not in ("config", "known_hosts", "known_hosts.old", "authorized_keys", "config.backup"))
    L.append("- private key files: %s" % ", ".join(keys))
    L.append("")
    return L


# ---------------------------------------------------------------- 9. named campaigns
def _exists(paths):
    return [p for p in paths if os.path.exists(os.path.expanduser(os.path.expandvars(p)))]


def _globs(pats):
    out = []
    for p in pats:
        out += glob.glob(os.path.expanduser(os.path.expandvars(p)))
    return out


def _history_grep(domains):
    hits = []
    for f in [os.path.join(HOME, ".zsh_history"), os.path.join(HOME, ".bash_history")] + glob.glob(os.path.join(HOME, ".npm/_logs/*.log"))[-50:]:
        try:
            data = open(f, "rb").read(20_000_000)
        except OSError:
            continue
        for d in domains:
            if d.encode() in data:
                hits.append("%s in %s" % (d, short_home(f)))
    return hits


def sec_campaigns(a):
    L = ["## 9. Named campaigns, checked one by one", ""]
    res = getattr(a, "_npm_scan", None) or {"hits": [], "ioc_files": [], "injected": [], "hash_matches": []}
    rows = []

    def row(name, date, found, how):
        rows.append((date, name, "**FOUND: %s**" % "; ".join(found)[:200] if found else "clean", how))
        if found:
            flag("red", "campaigns", "%s: %s" % (name, "; ".join(found)[:200]))

    # Trojanized Claude Code extension on Cursor's marketplace
    f = _exists(["~/.config/.smt", "~/.config/.smtk", "~/Library/LaunchAgents/com.apple.sysmond.plist"]) + \
        _globs(["$TMPDIR/.stk_*", "/tmp/.stk_*", "/private/var/folders/*/*/T/.stk_*"])
    if sh(["lsof", "-nP", "-i", ":8099"]).strip():
        f.append("something on port 8099 (beacon port)")
    f += [x[2] for x in FLAGS if "trojanized build" in x[2] or "svc-telemetry" in x[2] or "IOC strings" in x[2]]
    row("Trojanized Claude Code extension (Cursor marketplace, SSH backdoor)", "2026-10-29", [short_home(x) for x in f],
        "ext versions 2.1.312/313, ~/.config/.smt(k), $TMPDIR/.stk_*, LaunchAgent com.apple.sysmond, authorized_keys svc-telemetry, port 8099, 134.209.82.225")
    # ChainDrop
    f = [short_home(p) for p in res["injected"]] + [short_home(m["path"]) for m in res["hash_matches"] if "ChainDrop" in m["campaign"]] + \
        [h["name"] + "@" + h["version"] for h in res["hits"] if h["name"] in ("keyv", "flat-cache", "cache-manager")] + \
        _globs(["/tmp/bun-dl-*", "$TMPDIR/bun-dl-*"]) + _history_grep(["npm-cache.com", "pypi-get.com", "js-mirror.com"])
    row("ChainDrop / Shai-Hulud 'Here We Go Again' npm worm (keyv, flat-cache, 400+ packages)", "2026-08",
        f, "preinstall setup.mjs, Math_*.js bundle hash, injected .claude/.vscode setup.mjs, bun-dl- dirs, C2 npm-cache.com")
    # axios
    f = [h["name"] + "@" + h["version"] for h in res["hits"] if h["name"] == "axios"]
    row("axios 1.14.1 / 0.30.4 published from a hijacked maintainer account", "2026-03-31", f, "installed/locked versions")
    # Shai-Hulud 2.0
    f = [short_home(x["path"]) for x in res["ioc_files"] if "2.0" in x["campaign"]] + _exists(["~/.truffler-cache"]) + \
        [short_home(p) for p in _globs(["~/*/cloud_secrets.json", "~/*/truffleSecrets.json", "~/*/actionsSecrets.json"])]
    row("Shai-Hulud 2.0 (setup_bun.js / bun_environment.js, Zapier, PostHog, AsyncAPI, ENS packages)", "2025-11-24", f,
        "dropped loader/payload names, ~/.truffler-cache, secrets dumps, versions")
    # Shai-Hulud 1
    f = [short_home(x["path"]) for x in res["ioc_files"] if "Shai-Hulud 1" in x["campaign"]] + \
        [h["name"] + "@" + h["version"] for h in res["hits"] if h["name"] == "@ctrl/tinycolor"]
    row("Shai-Hulud 1 (@ctrl/tinycolor and ~500 packages, shai-hulud-workflow.yml)", "2025-09-15", f, "workflow file, versions")
    # chalk/debug
    f = [h["name"] + "@" + h["version"] for h in res["hits"] if h["name"] in npm_ioc_scan.BUILTIN and h["name"] not in ("axios", "nx", "@ctrl/tinycolor", "eslint-config-prettier", "eslint-plugin-prettier")]
    row("chalk / debug / ansi-styles maintainer phishing (browser crypto-clipper)", "2025-09-08", f, "18 package versions")
    # nx
    f = [h["name"] + "@" + h["version"] for h in res["hits"] if h["name"] == "nx"] + _exists(["/tmp/inventory.txt", "/tmp/inventory.txt.bak"]) + \
        [x[2] for x in FLAGS if "shutdown" in x[2]]
    row("Nx 's1ngularity' (AI-assisted credential harvest, shutdown line in rc files)", "2025-08-26", f, "nx versions, /tmp/inventory.txt, rc 'shutdown'")
    # eslint-config-prettier
    f = [h["name"] + "@" + h["version"] for h in res["hits"] if h["name"].startswith("eslint-")]
    row("eslint-config-prettier / eslint-plugin-prettier (Scavenger, Windows DLL)", "2025-07-18", f, "versions (payload is Windows-only)")
    L += table(["date", "campaign", "result", "checked by"], rows)
    L.append("Catalogue and sources: `references/known-campaigns.md`. Anything newer than its 'last updated' date is not covered by this table.")
    L.append("")
    return L


# ---------------------------------------------------------------- main
SECTIONS = [("posture", sec_posture), ("network", sec_network), ("persistence", sec_persistence), ("shell", sec_shell),
            ("packages", sec_packages), ("ide", sec_ide), ("browser", sec_browser), ("agents", sec_agents), ("campaigns", sec_campaigns)]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", help="write the Markdown report here (default: stdout)")
    ap.add_argument("--project", help="a project directory whose node_modules install hooks and MCP config to list (default: cwd if it has package.json)")
    ap.add_argument("--offline", action="store_true", help="do not download the public npm IOC list")
    ap.add_argument("--no-lookup", action="store_true", help="no reverse DNS / AS lookups of peers")
    ap.add_argument("--quick", action="store_true", help="scan lockfiles only, skip walking node_modules")
    ap.add_argument("--time-budget", type=int, default=600, help="seconds for the node_modules walk")
    ap.add_argument("--btm", action="store_true", help="also dump login items with sfltool (admin password prompt)")
    ap.add_argument("--skip", action="append", default=[], help="section to skip (repeatable)")
    a = ap.parse_args(argv)
    if sys.platform != "darwin":
        print("This audit is for macOS.", file=sys.stderr)
        return 1

    body = []
    t_all = time.time()
    for name, fn in SECTIONS:
        if name in a.skip:
            body += ["## %s: skipped" % name, ""]
            continue
        t0 = time.time()
        try:
            body += fn(a)
        except Exception as e:  # one broken section must not kill the report
            body += ["## %s: FAILED (%s: %s)" % (name, e.__class__.__name__, str(e)[:200]), ""]
        SECTION_TIMES[name] = round(time.time() - t0, 1)

    head = ["# Mac supply-chain and outbound-traffic audit", "",
            "- generated %s on `%s` by audit.py (read-only; nothing was changed)" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), socket.gethostname()),
            "- sections and seconds: " + ", ".join("%s %ss" % kv for kv in SECTION_TIMES.items()), ""]
    reds = [f for f in FLAGS if f[0] == "red"]
    yellows = [f for f in FLAGS if f[0] == "yellow"]
    head += ["## 0. Flags", ""]
    head.append("**%d red** (treat as compromise until explained), **%d yellow** (hygiene or needs your confirmation)." % (len(reds), len(yellows)))
    head.append("")
    for lvl, sec, txt in reds + yellows:
        head.append("- %s [%s] %s" % ("🔴" if lvl == "red" else "🟡", sec, txt))
    head.append("")
    head.append("Red flags are pattern matches, not verdicts: a dev box legitimately runs tunnels, loads unpacked extensions and sets keys in rc files. Each one needs a human to say 'yes, that is mine'.")
    head.append("")
    report = "\n".join(head + body) + "\n- total %ss\n" % round(time.time() - t_all, 1)
    if a.out:
        with open(a.out, "w") as f:
            f.write(report)
        print("wrote %s (%d flags: %d red, %d yellow)" % (a.out, len(FLAGS), len(reds), len(yellows)))
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())

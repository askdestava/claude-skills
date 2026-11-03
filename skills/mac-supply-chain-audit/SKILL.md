---
name: mac-supply-chain-audit
description: Audit a Mac for supply-chain compromise and unexpected outbound traffic, read-only. One script answers "what on my computer is talking out, to whom", "is anything persisting that I did not install", "do I have a compromised npm/pip/Homebrew package or a trojanized IDE or browser extension", and checks the named campaigns (Shai-Hulud, ChainDrop, the chalk/debug wave, the trojanized Claude Code Cursor extension, ...) one by one. Use it whenever the user asks to check their computer, laptop or Mac for malware, a supply chain attack, a compromised package, an unknown package, a backdoor, "who is communicating out", suspicious network connections, or whether they were hit by a specific npm/PyPI/extension incident they read about, even if they do not say "audit". Also use it after installing something sketchy, after a security advisory, or when a developer machine behaves oddly.
---

# mac-supply-chain-audit

A read-only audit of the Mac you are running on. `scripts/audit.py` (Python 3.8+, standard library, no sudo)
looks at nine things and writes one Markdown report with a flag list on top:

| # | Section | What it reads |
|---|---|---|
| 1 | posture | SIP, Gatekeeper, XProtect, Remote Login, user accounts and admins, proxies, DNS, `/etc/hosts`, sudoers.d |
| 2 | network | every established TCP connection grouped by process, with the executable path and the peer's reverse DNS / AS name; listening ports; bytes per process on open sockets; tunnel-shaped processes |
| 3 | persistence | LaunchAgents/Daemons with each program's **codesign team**, launchd jobs, crontab, StartupItems, emond; login items with `--btm` |
| 4 | shell | rc files: pipe-to-shell, eval-of-download, base64, `shutdown`, injection variables, aliases over core commands, and plaintext secrets **by variable name only** |
| 5 | packages | global npm (placeholder/name-squat detection, install hooks), **every lockfile and every installed package under `~` against ~8,400 known-compromised npm versions**, project install hooks, Homebrew taps/formulae/casks, pip per interpreter, uv/pipx, `~/.local/bin`, `/usr/local/bin` |
| 6 | ide | VS Code / Cursor / Windsurf / Antigravity / Trae / Kiro extensions: version, install date, marketplace vs sideloaded, known-trojanized versions, IOC strings in their JS |
| 7 | browser | Chrome / Edge / Brave / Arc / Opera / Vivaldi extensions per profile: store vs sideloaded, reach (all sites, cookies, webRequest, debugger, nativeMessaging), unpacked extensions, Tampermonkey/Violentmonkey script headers, native messaging hosts |
| 8 | agents | MCP servers from every agent's config (Claude Code, Cursor, Codex, Windsurf, Gemini, Goose, Claude Desktop), Claude Code hooks, plugin marketplaces, git global keys that run code, `authorized_keys`, `~/.ssh/config` command directives |
| 9 | campaigns | the named incidents in `references/known-campaigns.md`, each with its own indicators, one row each: clean or FOUND |

Nothing is changed. The only network use is reverse-DNS/AS lookups of the machine's current peers and one
download of the public npm IOC list; `--no-lookup` and `--offline` turn those off.

## Run it

```bash
python3 <this skill's directory>/scripts/audit.py --out <scratch dir>/audit.md --project <the user's current project, if any>
```

30 to 90 seconds on a developer Mac (the node_modules walk is most of it; `--quick` scans lockfiles only).
`--btm` adds login items via `sfltool dumpbtm`, which makes macOS show an admin password prompt: say so
before using it, and never run it in a session the user is not watching. `--skip <section>` drops a section.

Run it from the user's shell as the user (never via sudo): the audit is about *their* account's
LaunchAgents, extensions, rc files and tokens. Other accounts on the Mac are listed but not readable.

## Then do what the script cannot

1. **Look for campaigns newer than the catalogue.** `references/known-campaigns.md` carries a "last updated"
   date. Run two web searches: `npm supply chain attack compromised packages <month> <year>` and
   `malicious VS Code Cursor Chrome extension <month> <year>`, in extended mode when the date is more than a
   few weeks old. For each new incident, fetch the primary write-up (vendor blog, CERT advisory), pull its
   concrete indicators (versions, file names, LaunchAgent labels, key comments, domains, ports), check them
   by hand with `ls`, `grep`, `lsof`, and add a row to the catalogue plus the matching entry in the scripts
   with the source URL. The downloaded version list is updated by its maintainers, but file-name and
   extension indicators only arrive through this step.
2. **Explain every connection.** For each process in the network table, say in the report who it is and why
   it talks to that peer. Normal on a developer Mac: Chrome/Safari to CDNs and Google; Cursor and its
   `cursor-agent` workers to AWS; Claude Code to Anthropic, Google Cloud (telemetry), Vercel (docs) and the
   MCP servers it is configured with; Zoom to Zoom/AWS/Cloudflare; `ssh` to a host the user owns; `node`
   dev servers on localhost. Not normal: a process from `/tmp`, `/var/folders`, `~/Library/Caches` or a
   hidden folder; an `ssh -R`/`autossh`; a connection on an odd port from something that is not a VPN,
   game or video client; a listener on all interfaces the user cannot name. When a `node` or `python`
   process talks out, resolve its full command line and working directory (`ps -o args= -p PID`,
   `lsof -p PID | grep cwd`) and name the project.
3. **Clear each flag.** Every red or yellow line is a pattern match. Decide, with evidence, whether it is
   the user's own (an unpacked extension built from their repo, a key in `.bashrc` they put there, a
   third-party Homebrew tap they chose) or not. Do not soften a red flag you cannot explain.
4. **Do not fix anything unasked.** Uninstalling a package, deleting a LaunchAgent, revoking a key: these
   are the user's calls. Give the exact command and what it does. The one exception is their explicit
   request to clean up.

## Write the report

Lead with the verdict in one sentence, then these sections, short:

```
## What I checked and found
**Known attacks, all negative / FOUND x**  — one bullet per campaign checked, with the date and what was looked for
**Who is talking out right now**           — a table: process → who it talks to (org), one row per process family
**Persistence**                            — one or two sentences: all signed by whom; anything odd
**Packages**                               — counts scanned, hits, anything placeholder/custom-registry
## Worth acting on
1. ...                                     — numbered, each with the command to run, if any
```

Then one caveat: this is a point-in-time snapshot of open connections and on-disk indicators, not a packet
capture over days; for continuous visibility, name an outbound firewall such as LuLu (Objective-See, free).
Close with the sources you used.

Never paste a secret into the report or the chat, even partially, even to prove it was found: say the
variable name and the file. The script already redacts; keep it that way when you grep by hand.

## Interpreting what you see

- **A placeholder package** ("Package name reserved", "TO BE CONTINUED") installed globally is a name-squat
  typo-install. It is inert today; whoever owns the name can publish real code tomorrow and `npm update`
  will take it. Recommend uninstalling and, if a scoped package with the same name exists, that the user
  wanted that one.
- **A LaunchAgent with an Apple-looking label in `~/Library` or `/Library`** is the oldest trick there is;
  Apple's own live in `/System/Library`. The Claude Code trojan used `com.apple.sysmond`.
- **An extension version is not proof.** The Cursor incident served trojanized builds of the *real* version
  numbers for eleven hours; the same number from Open VSX was clean. Check the install timestamp and
  source in `extensions.json`, then grep the extension's JS for the campaign's strings.
- **Bytes per process** come from the sockets open at that moment, not lifetime totals; a quiet beacon
  shows as a few KB. Weight the *peer* over the volume.
- **Several user accounts** on a personal Mac are usually family; list them and ask, do not assume.
- **A key in `.bashrc`** is readable by every process the user runs, which is exactly what a stealer
  reads first. Hygiene, not compromise.

## Updating the skill

A new campaign goes in three places: `references/known-campaigns.md` (a row with the source), and whichever
of `npm_ioc_scan.py` (`BUILTIN` versions, `IOC_FILENAMES`, `INJECTED_PATHS`, hashes) or `audit.py`
(`KNOWN_BAD_EXTENSIONS`, `EXTENSION_IOC_STRINGS`, a `row(...)` in `sec_campaigns`) can check it. Bump the
"last updated" date. Only add indicators you have read in a primary source; a wrong IOC in a public skill
sends people chasing ghosts.

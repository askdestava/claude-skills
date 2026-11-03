# mac-supply-chain-audit

An agent skill (Claude Code, and any agent that reads `SKILL.md` skills) that audits the Mac it runs on for
supply-chain compromise and unexpected outbound traffic. It answers, in one Markdown report:

- **who is talking out**: every established connection grouped by process, with the executable's path and
  the peer's reverse DNS or network owner; listening ports; bytes per process; tunnel-shaped processes
- **what persists**: LaunchAgents and LaunchDaemons with the signing team of each program (Apple, a
  Developer ID, unsigned), launchd jobs, crontab, login items
- **what is installed**: global npm packages (placeholder name-squats called out), **every lockfile and
  every installed `node_modules` package under your home against ~8,400 known-compromised npm versions**,
  install hooks, Homebrew taps/formulae/casks, pip per interpreter, uv and pipx tools
- **what extends your tools**: IDE extensions (VS Code, Cursor, Windsurf, Antigravity, Trae, Kiro) with
  install date and source, known-trojanized versions, IOC strings; browser extensions per profile (Chrome,
  Edge, Brave, Arc, Opera, Vivaldi) with store-or-sideloaded and reach, unpacked extensions, userscript
  headers, native messaging hosts
- **what your agents trust**: MCP servers from every agent's config, Claude Code hooks, git keys that run
  code, SSH `authorized_keys` and config
- **named campaigns, one row each**: the trojanized Claude Code extension on Cursor's marketplace
  (2026-10-29), ChainDrop / Shai-Hulud "Here We Go Again" (2026-08), axios 1.14.1 (2026-03), Shai-Hulud 2.0
  (2025-11), Shai-Hulud 1 (2025-09), the chalk/debug wave (2025-09), Nx s1ngularity (2025-08),
  eslint-config-prettier (2025-07), each checked by its own indicators

It is **read-only**: it never changes, deletes or installs anything, and never needs `sudo`. It is Python
3.8+ standard library only and uses macOS's own tools (`lsof`, `nettop`, `codesign`, `launchctl`, `dscl`,
`csrutil`, `spctl`, `dig`, `whois`). Secrets found in shell files are reported by variable name; values
never appear in the report.

## Install

```bash
git clone https://github.com/askdestava/claude-skills
cp -R claude-skills/skills/mac-supply-chain-audit ~/.claude/skills/
```

(Link instead of copy to pick up updates with `git pull`:
`ln -s "$PWD/claude-skills/skills/mac-supply-chain-audit" ~/.claude/skills/mac-supply-chain-audit`.)

Then ask in plain words: *"check my computer for supply chain attacks"*, *"who is communicating out from my
Mac?"*, *"was I hit by the Shai-Hulud npm worm?"*, *"is anything unknown installed on this laptop?"*. The
agent runs the script, looks up campaigns newer than the catalogue, explains every connection and flag, and
writes you a short verdict-first report.

## Use it without an agent

```bash
python3 scripts/audit.py --out audit.md            # full audit, ~30–90 s
python3 scripts/audit.py --quick --offline --no-lookup   # no network, lockfiles only
python3 scripts/audit.py --btm                     # also login items (admin password prompt)
python3 scripts/npm_ioc_scan.py ~/code/my-project  # just the npm check, exit 2 if anything is found
```

| Flag | Does |
|---|---|
| `--out FILE` | Write the report there instead of stdout |
| `--project DIR` | List that project's `node_modules` install hooks and MCP config (default: the current directory if it has a `package.json`) |
| `--offline` | Do not download the public npm IOC list; use the built-in one |
| `--no-lookup` | No reverse-DNS / AS lookups of peers |
| `--quick` | Lockfiles only; skip walking `node_modules` |
| `--time-budget N` | Seconds for the `node_modules` walk (default 600) |
| `--btm` | Add login items via `sfltool dumpbtm` (prompts for an admin password) |
| `--skip SECTION` | Skip a section (`posture`, `network`, `persistence`, `shell`, `packages`, `ide`, `browser`, `agents`, `campaigns`) |

The report opens with a flag list: **red** means treat as compromise until explained (a compromised
version, a worm file, an Apple-looking LaunchAgent label outside `/System`, a process talking out from a
temp path, a tunnel, a pipe-to-shell in an rc file); **yellow** means hygiene or something only you can
confirm is yours (a plaintext key in `.bashrc`, an unpacked extension, a third-party Homebrew tap, a
placeholder npm package). Flags are pattern matches, not verdicts.

## What it does not do

- It is a point-in-time snapshot. A beacon that fires once an hour will not be on the connection list; for
  continuous visibility use an outbound firewall such as [LuLu](https://objective-see.org/products/lulu.html).
- It is not an antivirus. It knows the campaigns in `references/known-campaigns.md` and a set of generic
  patterns; it does not scan binaries for malware families.
- It reads your account only. Other users' LaunchAgents, cron tabs and `authorized_keys` are not readable
  without root, and the audit never asks for root.
- Safari and Firefox extensions are not covered. Chromium-family browsers are.
- The npm version list is the community-maintained one at
  [Drasrax/npm-shai-hulud-scanner](https://github.com/Drasrax/npm-shai-hulud-scanner); it is parsed as data,
  never executed. PyPI has no equivalent list wired in yet; pip packages are listed for review.

## Keeping it current

`references/known-campaigns.md` has a "last updated" date and a row per campaign with its source. The agent
is told to search for anything newer before trusting the table. To add a campaign: a row there, and the
versions, file names or extension versions in the two scripts, with the source link. Only indicators read
in a primary write-up go in.

## Licence

MIT. See [LICENSE](LICENSE).

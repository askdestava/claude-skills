# Known supply-chain campaigns the audit checks for

Last updated: **2026-11-03**. Anything published after that date is not in this file, in `scripts/audit.py`
(`sec_campaigns`, `KNOWN_BAD_EXTENSIONS`, `EXTENSION_IOC_STRINGS`) or in `scripts/npm_ioc_scan.py` (`BUILTIN`,
`IOC_FILENAMES`, `INJECTED_PATHS`). When you run the audit, search the web for campaigns newer than this date
first (see SKILL.md), check their indicators by hand, and add them here and in the scripts with a source link.

The npm version list the script downloads (https://github.com/Drasrax/npm-shai-hulud-scanner,
`shai-hulud-iocs.json`, about 3,800 packages and 8,400 versions in November 2026) is the broad net; the rows
below are the campaigns with indicators beyond a version number.

| Date | Campaign | Vector | What the audit checks | Source |
|---|---|---|---|---|
| 2026-10-29 | Trojanized **Claude Code** extension on Cursor's marketplace | Builds 2.1.312 and 2.1.313 of `anthropic.claude-code` served by Cursor's marketplace for ~11 hours. Installs a persistent SSH backdoor: appends a key (comment `svc-telemetry`) to `~/.ssh/authorized_keys`, turns Remote Login on, keeps a reverse tunnel to `134.209.82.225` alive from a LaunchAgent named `com.apple.sysmond`. | extension dirs for those versions; `~/.config/.smt`, `~/.config/.smtk`, `$TMPDIR/.stk_*`; the LaunchAgent; the key comment; IOC strings in every extension's JS; port 8099; tunnel-shaped processes | [StepSecurity](https://www.stepsecurity.io/blog/claude-code-extension-trojanized), [Microsoft](https://www.microsoft.com/en-us/security/blog/2026/10/30/inside-malicious-claude-code-branded-cursor-extension-persistent-ssh-backdoor/) |
| 2026-08 | **ChainDrop** / Shai-Hulud "Here We Go Again" | Self-propagating npm worm; 400+ packages incl. `keyv`, `flat-cache`, `cache-manager`. A `preinstall` hook runs `setup.mjs`, which launches a Bun bundle named `Math_*.js`; steals npm/GitHub/cloud tokens, injects `.claude/setup.mjs` + `.claude/settings.json` and `.vscode/setup.mjs` + `tasks.json` into victims' repos, publishes results to GitHub repos described "Shai-Hulud: Here We Go Again". C2 `npm-cache.com` (earlier `pypi-get.com`, `js-mirror.com`). | installed and locked versions; `preinstall` hooks running `setup.mjs`; `setup.mjs` and `Math_*.js` hashes; injected repo files; `bun-dl-*` temp dirs; C2 domains in shell history and npm logs | [Microsoft](https://www.microsoft.com/en-us/security/blog/2026/08/04/chaindrop-supply-chain-compromise-anatomy-self-propagating-worm/), [CSA Singapore](https://www.csa.gov.sg/alerts-and-advisories/advisories/ad-2026-009/) |
| 2026-06-01 | `@redhat-cloud-services` namespace | 32 packages published from a compromised account (mini Shai-Hulud wave) | versions, via the downloaded list | [Unit 42](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/) |
| 2026-04-29 | SAP developer ecosystem wave | 4 compromised npm packages | versions, via the downloaded list | [Unit 42](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/) |
| 2026-03-31 | **axios** 1.14.1 and 0.30.4 | Published from a hijacked maintainer account; payload in `postinstall` | versions (built-in) | [Elastic / Unit 42](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/) |
| 2025-11-24 | **Shai-Hulud 2.0** | 700+ packages (Zapier, PostHog, AsyncAPI, ENS, ...). `preinstall` runs `setup_bun.js`, which runs `bun_environment.js`; TruffleHog-based secret harvest; dumps `cloud_secrets.json`, `truffleSecrets.json`, `actionsSecrets.json`; wipes the home directory if it cannot exfiltrate | the two file names anywhere under `~`; `~/.truffler-cache`; the dump names; versions | [Wiz](https://www.wiz.io/blog/shai-hulud-2-0-npm-supply-chain-attack), [Socket](https://socket.dev/blog/shai-hulud-strikes-again-v2) |
| 2025-09-15 | **Shai-Hulud 1** | `@ctrl/tinycolor` 4.1.1/4.1.2 then ~500 packages; `bundle.js` postinstall; adds `.github/workflows/shai-hulud-workflow.yml` to victims' repos | the workflow file name; versions | [StepSecurity](https://www.stepsecurity.io/blog/ctrl-tinycolor-and-40-npm-packages-compromised), [Unit 42](https://unit42.paloaltonetworks.com/npm-supply-chain-attack/) |
| 2025-09-08 | **chalk / debug** maintainer phishing | 18 packages (chalk 5.6.1, debug 4.4.2, ansi-styles 6.2.2, strip-ansi 7.1.1, supports-color 10.2.1, color-convert 3.1.1, color-name 2.0.1, ansi-regex 6.2.1, wrap-ansi 9.0.1, slice-ansi 7.1.1, color-string 2.1.1, simple-swizzle 0.2.3, is-arrayish 0.3.3, error-ex 1.3.3, has-ansi 6.0.1, backslash 0.2.1, chalk-template 1.1.1, supports-hyperlinks 4.1.1, proto-tinker-wc 1.8.7); a browser crypto-clipper, live for ~2 hours | versions (built-in) | [Aikido](https://www.aikido.dev/blog/npm-debug-and-chalk-packages-compromised), [Upwind](https://www.upwind.io/feed/npm-supply-chain-attack-massive-compromise-of-debug-chalk-and-16-other-packages) |
| 2025-08-26 | **Nx "s1ngularity"** | nx 20.9.0–20.12.0 and 21.5.0–21.8.0 (+ plugins); a `postinstall` `telemetry.js` drove Claude/Gemini/q CLIs to inventory secrets, wrote `/tmp/inventory.txt`, pushed `s1ngularity-repository*` repos, appended `sudo shutdown -h 0` to `.zshrc`/`.bashrc` | versions; `/tmp/inventory.txt`; a `shutdown` line in rc files | [Nx advisory](https://github.com/nrwl/nx/security/advisories/GHSA-cxm3-wv7p-598c), [Wiz](https://www.wiz.io/blog/s1ngularity-supply-chain-attack) |
| 2025-07-18 | **eslint-config-prettier** / eslint-plugin-prettier | 8.10.1, 9.1.1, 10.1.6, 10.1.7 / 4.2.2, 4.2.3; phished maintainer; Windows-only DLL (Scavenger) | versions (built-in), for completeness | [StepSecurity](https://www.stepsecurity.io/blog/eslint-config-prettier-compromised) |
| 2025 | Backdoored Cursor extensions (Paradox stealer) | Fake/backdoored extensions on Open VSX delivering macOS infostealers | sideloaded (non-marketplace) extensions are flagged; no specific IOC | [Objective-See](https://objective-see.org/blog/blog_0x84.html) |

## Generic indicators the script always applies

These catch the next campaign before it has a name:

- a LaunchAgent/Daemon whose label starts with `com.apple.` outside `/System`, whose program is unsigned, or runs from a temp, cache or hidden directory
- a process talking out from a temp or cache path; a tunnel-shaped command line (`ssh -R`, `autossh`, `ngrok`, `cloudflared`, `frpc`, `chisel`, `socat`, ...)
- `authorized_keys` entries; `ProxyCommand`/`LocalCommand` in `~/.ssh/config`; Remote Login on
- rc-file lines that pipe a download to a shell, `eval` a download, decode base64, call `shutdown`, set `DYLD_INSERT_LIBRARIES`, or alias `sudo`/`ssh`/`git`/`npm`/`brew`/`curl`
- a global npm package with a placeholder README ("reserved", "to be continued"): a name-squat you installed by mistake, which its owner can turn into anything with the next publish
- a custom npm registry in any `.npmrc`; install hooks that download, decode or spawn
- IDE extensions not installed from the marketplace; browser extensions with no store `update_url`; unpacked extensions; native messaging hosts pointing at temp paths
- MCP servers running from temp paths or over plain http; Claude Code hooks that pipe downloads to a shell; git `core.hooksPath`, `fsmonitor`, `sshCommand`, `askpass`

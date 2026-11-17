# claude-skills

Agent skills from [Destava](https://destava.com) that we built for our own work and are sharing. Each one is a
folder with a `SKILL.md`. Claude Code loads them from `~/.claude/skills/`, and any agent that reads `SKILL.md`
skills can use them.

| Skill | What it does |
|---|---|
| [`destava-job-search`](skills/destava-job-search) | Searches current job postings from companies' own career sites with [Destava](https://destava.com): by role, skills, place, remote, level and how recent, each with the company's own link to apply. Checks whether a posting is still open and how often it was reposted, and makes a link that runs the search every morning on the user's Destava account. Free, no account or key; MCP tools when connected, `curl` when not. |
| [`mac-supply-chain-audit`](skills/mac-supply-chain-audit) | Audits the Mac it runs on, read-only: who is talking out and to whom, what persists and who signed it, every installed npm package and lockfile against ~8,400 known-compromised versions, IDE and browser extensions, MCP servers and hooks, and the named campaigns (Shai-Hulud, ChainDrop, the trojanized Claude Code Cursor extension, …) one by one. One Markdown report, flags first. Python standard library. |
| [`product-film`](skills/product-film) | Makes short promo, teaser and launch films of a software product from its real UI: one HTML page on one clock, rendered frame-exact to 60 fps with headless Chrome. Splices in clips and captioned GIFs, lands a generated track's drop on a picture cue, masters to −14 LUFS. |
| [`seo-playbook`](skills/seo-playbook) | Works a website's visibility in search and in AI answers one job at a time, from a ranked playbook of 35 jobs and their 197 steps (keywords that bring customers, the pages buyers need, pages that lost clicks, internal links, the lists and AI answers buyers read, link recovery, structured data). No SEO connector, account or key: it reads Search Console, Google's results and AI assistants' answers in your own browser, and its scripts count: pages near page one, lost clicks and what moved, what a crawler is handed at each address, who links to whom, which brands each assistant names and cites. Python standard library. |
| [`timeline-video`](skills/timeline-video) | Writes and renders timeline-scripted AI videos: one take up to 30 seconds, scripted second by second (locked character, style, timed audio, timeline, camera rules, negatives). Checks the script, prices it, renders it on OpenRouter (Seedance 2.5 by default), and lays out a frame per beat to review. Python standard library. |
| [`x-media-download`](skills/x-media-download) | Downloads the videos, GIFs and photos attached to public X (Twitter) posts: the best MP4, real `.gif`s on request, original-size photos, and a JSON record of where each file came from. No login, no API key, Python standard library only. |

## Install a skill

```bash
git clone https://github.com/askdestava/claude-skills
cp -R claude-skills/skills/<skill> ~/.claude/skills/
```

New Claude Code sessions will list it. Each skill's README covers its requirements and how to use it.

## Licence

MIT. See [LICENSE](LICENSE).

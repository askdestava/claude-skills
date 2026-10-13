# claude-skills

Agent skills from [Destava](https://destava.com) that we built for our own work and are sharing. Each one is a
folder with a `SKILL.md`. Claude Code loads them from `~/.claude/skills/`, and any agent that reads `SKILL.md`
skills can use them.

| Skill | What it does |
|---|---|
| [`product-film`](skills/product-film) | Makes short promo, teaser and launch films of a software product from its real UI: one HTML page on one clock, rendered frame-exact to 60 fps with headless Chrome. Splices in clips and captioned GIFs, lands a generated track's drop on a picture cue, masters to −14 LUFS. |
| [`x-media-download`](skills/x-media-download) | Downloads the videos, GIFs and photos attached to public X (Twitter) posts: the best MP4, real `.gif`s on request, original-size photos, and a JSON record of where each file came from. No login, no API key, Python standard library only. |

## Install a skill

```bash
git clone https://github.com/askdestava/claude-skills
cp -R claude-skills/skills/<skill> ~/.claude/skills/
```

New Claude Code sessions will list it. Each skill's README covers its requirements and how to use it.

## Licence

MIT. See [LICENSE](LICENSE).

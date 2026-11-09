# destava-job-search

An agent skill (Claude Code, Codex, Cursor and any agent that reads `SKILL.md` skills) for searching current job
postings with [Destava](https://destava.com). Destava reads postings from companies' own career sites and
applicant-tracking systems, so every result carries the company's own link to apply. With this skill your agent can:

- search by role, skills, place, remote, level and how recent (up to 20 postings a call)
- check whether a posting is still open, how old it is and whether it keeps being reposted
- make a link that sets the search up to run every morning on the user's own Destava account

Searching is free and needs no account or API key. The skill uses the Destava MCP tools when they are connected and
plain HTTP (`curl`) when they are not.

## Install

```bash
npx skills add askdestava/claude-skills --skill destava-job-search
```

Or copy the folder from a clone:

```bash
git clone https://github.com/askdestava/claude-skills
cp -R claude-skills/skills/destava-job-search ~/.claude/skills/
```

Then ask in plain words: *"find remote data engineer jobs posted this week"*, *"is this job still open?"* with a link,
*"send me new nurse jobs in Seattle every morning"*.

## Connect the tools (optional)

The skill works without this, but a connected server is faster for an agent that searches often:

```bash
claude mcp add --transport http destava https://destava.com/mcp
```

Other clients (Claude, ChatGPT, Cursor, VS Code, Gemini CLI, Grok): https://destava.com/mcp/docs.

## Privacy

Destava records the query and the client's name, not who asked; its host's request logs keep network addresses for
up to 7 days. [Privacy Policy](https://destava.com/privacy) (section 8 covers searches and AI agents) ·
[Terms](https://destava.com/terms).

## Licence

The skill is MIT licensed (see [LICENSE](LICENSE)). The search service it calls is run by Destava (Xprtis LLC) and is
not open source.

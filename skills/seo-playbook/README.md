# seo-playbook

An agent skill (Claude Code, and any agent that reads `SKILL.md` skills) that works a website's
visibility in search and in AI answers, one job at a time, from a ranked playbook of 35 jobs and
the 197 steps inside them.

It needs **no SEO connector, account or API key**. Where a paid connector would hand the agent
Search Console numbers, rankings and "AI visibility" figures, this skill has the agent read the
same things in your own browser, and gives it small scripts for the counting:

- **Search Console**, read out of the open report: every row it holds, not the ten on screen, or
  the CSV export. Then: pages near page one, pages that lost clicks and what moved, titles
  clicked less than their position earns on your site.
- **Google's results** for a search: who ranks, in what format, the AI Overview and the pages it
  links, the questions around it.
- **What people type**: Google's own suggestions around a phrase.
- **AI assistants' answers** to your buyers' questions: which brands each one names, which pages it
  cites, the questions that name your competitors and not you, and what changed since the last run.
  Plus Search Console's Generative AI features report: Google's own count of how often its AI
  features showed your pages, and which ones.
- **What a crawler is handed** at each address: redirects, robots.txt per crawler (search engines
  and AI crawlers), noindex, canonical, title and heading, preview tags, structured data, and how
  much text exists before JavaScript runs.
- **Your internal links**: pages nothing links to, pages near page one with one or two links,
  template links, linked words that repeat.

Writing and publishing happen where your pages already live (your repository or CMS), shipped the
way you ship. Nothing is published, sent, posted or submitted without your yes.

## The playbook

| Tier | Jobs |
|---|---|
| **S** | Find keywords that bring customers · Build the pages buyers need · Build topical authority · Add information gain · Improve content you already have · Add internal links people will use |
| **A** | Get into the lists buyers read · Recover links you already earned · Find link opportunities through competitors · Replace broken and outdated resources · Publish statistics people can cite · Answer journalist requests · Build the visual an article is missing · Turn another author's article into a video · Build free tools that earn links · Exchange relevant editorial links |
| **B** | Build useful programmatic pages · Use parasite SEO · Find gaps in AI recommendations · Publish YouTube answers buyers search for · Improve local search visibility · Show who is behind the content · Make important pages accessible |
| **C** | Find timely topics · Earn links through tools you use · Claim relevant business listings · Get customer reviews and independent coverage · Reuse research across platforms · Publish LinkedIn articles people can find · Turn articles into carousels and short videos · Give Claude a repeatable SEO job · Track the actions that produce customers |
| **D** | Improve search and sharing previews · Add accurate structured data · Remove page friction |

Each job is a procedure: what it needs, numbered steps, what it leaves behind, and when it is done.
The job titles are the source post's own words, and so are the words that open each step.
Exchanging editorial links, programmatic pages and parasite SEO are in it because they work; each
job also quotes what Google's spam policy calls the version it penalises, so you can do the work
knowing where that is. Fake reviews and posing as a customer are not offered.

The jobs and their order follow a ranked list by [@borjafat](https://x.com/borjafat/status/2122336732079161572)
(16 November 2026), which recommends running it with a commercial SEO connector. Its headline
counts 232 tactics: the post holds 197 one-line tactics under 35 headings (197 + 35 = 232). Here
each heading is a job under the post's own title, and each of the 197 tactics is a numbered step
that opens with the post's own words for what to do. What follows each (how to do it without the
connector, the outputs, the check), the scripts and the rest are ours and are what the MIT licence
covers; the titles and tactic wording are @borjafat's, quoted with credit. The order is a default: what your
own data shows comes first.

## Install

```bash
git clone https://github.com/askdestava/claude-skills
cp -R claude-skills/skills/seo-playbook ~/.claude/skills/
```

(Link instead of copy to pick up updates with `git pull`:
`ln -s "$PWD/claude-skills/skills/seo-playbook" ~/.claude/skills/seo-playbook`.)

For the browser parts, attach a browser tool to your agent. It was built and checked with the
[Chrome DevTools MCP server](https://github.com/ChromeDevTools/chrome-devtools-mcp) connected to a
Chrome that is signed in to Search Console; any tool that can open a page and run a script in it
works. Without one, the skill falls back to the export you download yourself and says what it
could not see.

Then ask in plain words: *"which of my pages should I update first?"*, *"why doesn't ChatGPT
recommend us?"*, *"audit my internal links"*, *"is my site indexed properly?"*, *"what should we
write next?"*, *"run S5 on example.com"*. The agent sets up a small `seo/` folder in your project
(your site, your product's facts, a log), checks the site can be read at all, picks a job from the
evidence, works it, and reports what it found, what it changed, and what is waiting for your yes.

## Use the scripts without an agent

Python 3.8+, standard library only.

```bash
# Search Console: give it the zip from Performance > Export > Download CSV
python3 scripts/gsc.py summary export.zip
python3 scripts/gsc.py near    export.zip --tab pages          # positions 8-20, most impressions first
python3 scripts/gsc.py ctr     export.zip --exclude mybrand    # page-one rows clicked less than their position earns here
python3 scripts/gsc.py decay   export.zip --tab pages          # needs an export made with Compare on

# What a crawler gets
python3 scripts/page_check.py https://example.com/ https://example.com/pricing
python3 scripts/page_check.py --sitemap https://example.com/sitemap.xml --match '/blog/' --limit 30
python3 scripts/page_check.py https://example.com/ --as googlebot

# Internal links
python3 scripts/links.py crawl --sitemap https://example.com/sitemap.xml --limit 300 --out graph.json --near export.zip
python3 scripts/links.py report graph.json

# What people type
python3 scripts/autocomplete.py "crm for agencies"

# AI answers: log what each assistant said, then count
python3 scripts/ai_answers.py add --log answers.jsonl --engine chatgpt --prompt "best crm for a two-person agency" \
    --brands "First, Second, Third" --sources "https://example.org/best-crm"
python3 scripts/ai_answers.py report --log answers.jsonl --brand "Acme" --domain acme.com
```

`gsc_read.js`, `serp_read.js` and `answer_read.js` are functions to run inside a page (a Search
Console report, a Google results page, an AI assistant's answer) with a browser tool's "evaluate
script" call. Each file's header says how.

## What it does not do

- **It does not have search volumes or other sites' backlinks.** No free source does. It uses what
  is real (your Search Console impressions, the live results, suggestions, your own Links report)
  and says "unknown" for the rest. If you already pay for a tool that has them, the agent can read
  it in your browser.
- **It does not promise rankings.** It measures before, changes one thing, and tells you when to
  measure again.
- **It does not publish, email, post or submit for you** unless you say so, each time.
- **It reads pages as they are today.** Search Console's addresses and Google's page structure
  change; `references/data-sources.md` carries the date each recipe was last checked
  (2026-11-17), and the readers return an error or their raw headings rather than a wrong answer.
- **AI answers vary.** One answer is one sample; the log and its run-to-run comparison are the
  useful part. A signed-in assistant that knows your company will flatter you: ask in a clean
  browser context.
- `page_check.py` and `links.py` read the HTML the server sends. They do not run JavaScript, which
  is the point: that is what many crawlers see.

## Licence

MIT. See [LICENSE](LICENSE).

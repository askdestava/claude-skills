# Where the data comes from, without a connector

Everything here was run against a live site on **2026-11-17** with the Chrome DevTools MCP server
attached to the user's own Chrome. Addresses and page structure on other people's sites change:
when a recipe stops matching what you see, take a text snapshot of the page, work from that, and
correct this file.

Contents: [the browser](#the-browser) · [Search Console](#search-console) · [Google's results](#googles-results) ·
[suggestions](#suggestions) · [AI answers](#ai-answers) · [volume and difficulty](#volume-and-difficulty) ·
[backlinks](#backlinks) · [other sources](#other-sources) · [publishing](#publishing) · [no browser tool](#with-no-browser-tool)

## The browser

Any tool that can open a page and run a JavaScript function in it will do: Chrome DevTools MCP
(`new_page`, `navigate_page`, `evaluate_script`, `take_snapshot`, `click`, `type_text`), the
Claude in Chrome extension, Playwright MCP. The three `.js` files in `scripts/` are plain
functions for that "run a function in the page" call. Tool names below are Chrome DevTools MCP's.

- **Passing a reader.** `evaluate_script` takes the function's text (`function`) or a file
  (`sourcePath`). The server only reads and writes inside the session's workspace, so a
  `sourcePath` in the skill's folder is refused ("not within any of the configured workspace
  roots"). Copy the three readers into the workspace once (`seo/.readers/`) and pass that path, or
  read the file and pass its text. Set `waitForStableDom: false`; the readers do their own waiting.
- **Keeping the result.** Set `filePath` to a `.json` inside the workspace (`seo/gsc/<date>/queries.json`).
  A 1,000-row table is about 100 KB: save it, do not print it into the conversation.
- **Which Chrome profile.** The server sees the tabs of every Chrome profile, but `new_page` opens
  in the default one. If the account that owns the Search Console property lives in another
  profile, the new tab shows "Oops, you don't have access to this property" and names who it is
  signed in as. Adding `/u/1/` or `authuser=` does not help across profiles. Find a tab that is
  already in the right profile (`list_pages`; a Gmail or Search Console tab shows the account in its
  title) and open yours from it:
  `evaluate_script` on that tab with `() => { window.open('<address>', '_blank'); }`, then
  `list_pages` to get the new tab's id. Work in the new tab; leave the user's as it was.
- **A clean context.** `new_page` with `isolatedContext: "seo-clean"` opens a tab with no cookies,
  no account and no extensions. Use it where a signed-in history would colour the answer (AI
  assistants) and close it at the end. For Google's results the signed-in profile reads better (see below).
- **Real clicks.** A download only starts from a real click: the `click` tool with an element id
  from `take_snapshot`. A `.click()` made inside `evaluate_script` opens menus but Chrome drops the
  download.
- **Yours and theirs.** Open your own tabs, never drive the user's, and close what you opened.

## Search Console

The reports live at `https://search.google.com/search-console/...` and take the property as
`resource_id`: `sc-domain:example.com` for a domain property, the full `https://example.com/`
for a URL-prefix one (URL-encode it).

### Performance, by address

```
https://search.google.com/search-console/performance/search-analytics?resource_id=sc-domain%3Aexample.com&num_of_days=28&breakdown=query
```

| Parameter | Values checked |
|---|---|
| `breakdown` | `query`, `page`, `date` (the table's tab; the tabs on screen are Queries, Pages, Countries, Devices, Search appearance, Days) |
| `num_of_days` | `7`, `28` |
| `start_date`, `end_date` | `YYYYMMDD`, for any range inside the 16 months Search Console keeps |
| `compare_date` | `PREV` (the period before, same length) |
| `compare_start_date`, `compare_end_date` | `YYYYMMDD`: any second range. Use this for the same weeks a year earlier; `compare_date=PREV_YEAR` is ignored. |
| `page` | `*text` = address contains text (`page=*%2Fblog%2F`) |
| `query` | `*text` = query contains text |
| `country` | three-letter code, lower case (`usa`) |
| `device` | `MOBILE` |

Every read on the test property carried all four columns (clicks, impressions, CTR, position).
`gsc.py` needs clicks and impressions and works the click rate out itself; `near` and `ctr` also
need position. If a table comes back without it, switch on the "Average position" tile above the
chart (a real `click`) and read again.

**Read it:** run `scripts/gsc_read.js` in the tab. It waits for the table and returns every row the
report holds (1,000 at most per period, whatever "Rows per page" says; with a comparison on, the
rows of both periods) with clicks and impressions exact, CTR in percent and position to one decimal. With a comparison on, each metric has three columns: the
period, the comparison, the difference. Then:

```bash
python3 scripts/gsc.py summary seo/gsc/2026-11-17/queries.json
python3 scripts/gsc.py near    seo/gsc/2026-11-17/pages.json --min-impr 50
python3 scripts/gsc.py ctr     seo/gsc/2026-11-17/queries.json --exclude 'brandname'
python3 scripts/gsc.py decay   seo/gsc/2026-11-17/pages-vs-prev.json
```

**Or export it:** `take_snapshot`, find the button named EXPORT, `click` it, `take_snapshot` again,
`click` "Download CSV". Chrome saves `<site>-Performance-on-Search-<date>.zip` to the Downloads
folder. With a comparison on it held `Queries.csv`, `Pages.csv`, `Countries.csv`, `Devices.csv`,
`Search appearance.csv` and `Filters.csv`. CTR and position carry two decimals there.
Move the zip into `seo/gsc/<date>/`; `gsc.py` reads it directly (`--tab pages`). This is also what
to ask the user for when you have no browser tool.

What the numbers are: at most 1,000 rows a tab, so filter (`page=*...`) to see below the cut; rare
queries are left out of the table for privacy, so rows add up to less than the totals above the
chart (on the site this was checked on, the query rows held well under a tenth of the report's
clicks); the most recent days are incomplete.

**Two questions that need a filter and a second read:**

- *Which queries does this page show for?* `page=*<its path>` with `breakdown=query`. The queries it
  shows for and does not answer are the missing sections (S5).
- *Do two pages compete for one query?* `query=*<the words>` with `breakdown=page`. More than one
  address taking impressions for the same search is a pair to compare (S5).

### Google's own count of AI appearances

Search Console has a second performance report, **Generative AI features** (marked Beta), under
Performance, Search results:

```
https://search.google.com/search-console/performance/search-analytics/ai?resource_id=sc-domain%3Aexample.com&num_of_days=28&breakdown=page
```

It counts how often the site's pages were shown inside Google's generative AI features. One
metric, impressions: no clicks, no position, and no queries tab (the tabs are Pages, Countries,
Devices, Days). `breakdown=page` and `breakdown=date` work as above, and so does `num_of_days`.
With a comparison on, the tiles show both periods but the Days table is left out ("Table omitted"),
so read days without one. `gsc_read.js` reads it; `gsc.py summary` takes the file (the other
commands need clicks) and `--contains` narrows it to a section of the site.

This is the only first-party number for AI visibility, and it is Google's surfaces only: it says
nothing about ChatGPT, Perplexity or Claude. Read it first in job B3, save it with the baseline,
and treat the pages at the top as the ones Google's AI already draws on. When a headline quotes
"AI mentions" over a Search Console chart, this report's impressions are what it is counting.

### Is this address indexed? (URL inspection)

There is no address for it: `.../inspect?id=` takes an id Search Console makes, not the page's URL
(passing the URL gives a 404). Use the search box at the top of any Search Console page:

1. `evaluate_script`: `() => { const i = document.querySelector('input[aria-label^="Inspect any URL"]'); i.focus(); i.select(); return !!i; }`
2. `type_text` the full address with `submitKey: "Enter"`.
3. Wait for the title "URL Inspection", then read the visible `[role=main]` text: "URL is on
   Google" or "URL is not on Google", the indexing state, and the enhancements it found.

**Never press REQUEST INDEXING** unless the user asks: it is their quota and their call.

### Indexing and links

- `https://search.google.com/search-console/index?resource_id=...` — Page indexing: how many
  addresses are indexed and not, and the table "Why pages aren't indexed" (reason, source, pages).
  `gsc_read.js` reads that table. "Discovered - currently not indexed" means Google has found the
  addresses and not fetched them yet. In large numbers that is about how much of the site Google
  chooses to crawl (how many addresses there are, how well linked, how useful the fetched ones
  proved), not about a block.
- `https://search.google.com/search-console/links?resource_id=...` — Links: external links (top
  linked pages, top linking sites, top linking text) and internal links. Each list's MORE opens
  `.../links/drilldown?resource_id=...&type=EXTERNAL` (also `DOMAIN`, `ANCHOR_TEXT`, `INTERNAL`),
  a table `gsc_read.js` reads. This is the site's own backlink data, from Google, free.

## Google's results

```
https://www.google.com/search?q=<query>&hl=en&gl=us&pws=0
```

`gl` is the country, `hl` the language, `pws=0` asks for unpersonalised results. Run
`scripts/serp_read.js` in the tab: the organic results in order (title, address, site, snippet) and
the other blocks on the page: the AI Overview with the links inside it, questions people ask,
videos, forum results, ads, related searches.

Signed in or clean? For the same query the two gave the same eight results with one swap, so
either shows what ranks. The difference is the links:

- **Signed-in profile:** each result links straight to its page, and the AI Overview's links are
  readable. Use this by default. Extensions write into the page (an SEO toolbar's scores landed in
  every snippet): ignore that text.
- **Clean context:** Google wraps every result as `/goto?url=<opaque>`, so the address is not in
  the page. The reader then returns `url: null`, `wrapped: true`, and takes the site from the
  address line under the title, which Google may shorten. Use it when you must rule personalisation out.

What to read off a results page (job S1, step 5): what kind of page fills it (tool, list, guide,
product, forum thread, video), who owns the results (brands, publishers, forums), whether an AI
Overview answers the question before anyone clicks, and which questions and related searches sit
around it. That decides the format of the page to build, or that this search is not worth a page.

A CAPTCHA ("unusual traffic") or the consent screen comes back as `{ error }` from the reader.
Stop and hand the tab to the user. Space out queries; a few dozen in a session is plenty.

## Suggestions

```bash
python3 scripts/autocomplete.py "resume builder"                 # plain, a-z, question words, buying words
python3 scripts/autocomplete.py "crm for" --country gb --only letters
```

It asks `https://suggestqueries.google.com/complete/search?client=firefox&hl=..&gl=..&q=..`, the
undocumented endpoint behind the search box, about fifty times at a quarter-second apart. A
suggestion means people search it in those words; it carries no number. For another language pass
that language's words with `--before` and `--after`.

## AI answers

The method matters more than the tool: **the same questions, word for word, every run, each
assistant asked separately, in a fresh conversation with nothing remembered about the user.** The
questions are buying questions real people ask ("best X for Y", "X or Z for a team of five",
"how do I do Y without Z"): take them from sales calls, support, Search Console and the questions
on results pages, and save them in `seo/questions.md`. Do not name your own brand in them.

What was seen on 2026-11-17, asked in a clean context (`isolatedContext`, no account):

| Assistant | How | What happened |
|---|---|---|
| ChatGPT | `https://chatgpt.com/?q=<question>&hints=search` | Asked and answered without signing in. Links in the answer are direct. |
| Google AI Mode | `https://www.google.com/search?udm=50&hl=en&gl=us&q=<question>` | Answered without signing in. Its links are wrapped (`/goto`), so the names it cites are readable and the addresses are not; use the signed-in profile to get the addresses. |
| Google AI Overview | Any results page | Part of `serp_read.js`'s output (`blocks.ai_overview`: text and links). |
| Perplexity | `https://www.perplexity.ai/search?q=<question>` | Without an account: "Sign up and repeat your request." Needs a signed-in tab. |
| Gemini, Claude, Copilot | Not checked | Open the assistant in a signed-in tab, start a new conversation (a temporary one where offered), type the question. |

Signed-in assistants remember. An account that has discussed the user's company will name it:
turn memory off or use a temporary conversation, and say in the log's `--note` how each answer was
asked. The same question asked twice, minutes apart, named different products, so one answer is one
sample. Trends across runs mean more than any single answer.

For each question and assistant:

1. Ask it. Run `scripts/answer_read.js` in the tab with `filePath` set (`seo/ai/raw/<date>-<assistant>-<n>.json`).
   It waits until the text stops growing and returns the answer and its outside links. `wall: true`
   means a sign-in or CAPTCHA page, not an answer.
2. Read the answer and list the brands it recommends, in the order it names them. That reading is
   yours: a product named as something to avoid is not a recommendation; say so in `--note`.
3. Log it:
   ```bash
   python3 scripts/ai_answers.py add --log seo/ai/answers.jsonl --engine chatgpt \
     --prompt "<the question>" --brands "First, Second, Third" --answer seo/ai/raw/<file>.json --note "signed out"
   ```
4. After the run: `python3 scripts/ai_answers.py report --log seo/ai/answers.jsonl --brand "<brand>" --domain <site>`.

The report's two useful tables are the sources the answers link to (the pages to get into or to
out-answer: job A1) and the questions that name others and not you (job B3).

## Volume and difficulty

No free source gives exact monthly volume for a phrase, and "difficulty" scores are each vendor's
own estimate. In order of trust:

1. **Search Console impressions**: real counts, for searches the site already appears for. Position
   matters: a query at position 40 shows a fraction of its searches.
2. **The results page itself**: who ranks is the difficulty. Ten established brands with dedicated
   pages is hard; forum threads, thin pages and results that only half answer the question is an opening.
3. **Suggestions and related searches**: that a phrase is suggested says it is searched.
4. **Google Trends**: relative interest over time and by region, not counts (below).
5. **Keyword Planner**, if the user runs Google Ads: it is in their Ads account under Tools. Drive
   it in the browser like any other page.
6. **Whatever SEO tool the user already pays for** and has open in the browser. Read its pages the
   same way. Do not sign them up for one.

When none of these gives a number, say "volume unknown" and rank by intent and by what the results
page shows. Do not put an invented figure in a table.

## Backlinks

- **The site's own:** Search Console's Links report (above). Complete enough for jobs A2 and S6.
- **Other sites':** no free, complete index exists. What is available:
  - search for mentions: `"competitor name" -site:competitor.com`, `"competitor.com"`, `intitle:"best" "<category>"`,
    `"<competitor>" "alternatives"`; read the results with `serp_read.js`;
  - the pages AI answers and AI Overviews cite, which are the links that currently matter to buyers;
  - Bing Webmaster Tools and the limited free checkers some SEO vendors offer, opened in the
    browser, if the user already uses them (not checked here);
  - the user's paid tool, if they have one.
  Say plainly which of these a list of "competitor links" came from. A sample from search results is
  a sample.

## Other sources

| For | How |
|---|---|
| What a dead address used to say | `curl -s 'https://archive.org/wayback/available?url=<address>&timestamp=<YYYYMMDD>'` returns the closest saved copy; open its `url` to read it. |
| Interest over time, seasonal or a spike | `https://trends.google.com/trends/explore?q=<term>&geo=US&date=today%205-y` in the browser: the five-year line shows a yearly rhythm against a one-off spike; "Related queries" lists rising ones. (Google has announced a replacement for this Explore page; if the address stops working, start from trends.google.com.) |
| Will Google accept this structured data | `https://search.google.com/test/rich-results?url=<encoded address>` runs the test on load and lands on a result page: which rich result types were found, valid or not. `page_check.py` tells you first whether each JSON-LD block parses and what it declares. |
| What the page looks like to a crawler | `page_check.py <address>` for the server's HTML; `page_check.py <address> --as googlebot` to send that crawler's name (a site that verifies crawlers by network will not be fooled, and should not be). Then the browser for the rendered page: compare "words in the HTML" with what is on screen. |
| Speed and page weight | Chrome DevTools MCP's `lighthouse_audit` and performance trace, or `https://pagespeed.web.dev/analysis?url=<address>` in the browser. (The PageSpeed API without your own key answered "quota exceeded".) |
| A video's words | Open the video and its transcript (YouTube offers "Show transcript" under the description when a video has one), then read the transcript panel's text with `evaluate_script`. Not checked on 2026-11-17. |
| What customers complain about | The product's and competitors' public reviews (G2, Capterra, Trustpilot, app stores), and forum threads from the results page. Read, count, quote sparingly with a link. |
| What buyers say in their own words | The user's sales-call notes, support inbox and chat logs, if they share them. Use the words; leave the names out. |

## Publishing

There is no CMS connector because none is needed: find where the pages live and change them there.

- **A repository** (a static site, a framework's content folder, templates): edit the files, show
  the diff, and let the user ship it the way they ship (their branch, their review, their deploy).
- **A CMS** (WordPress, Webflow, Shopify, Ghost, Notion and the like): write the page as a file in
  `seo/drafts/` in the format the CMS takes (HTML or Markdown, with the title, description and
  address it should get). The user pastes or imports it, or drives the CMS in the browser with you
  once they say so.
- **Generated pages** (a template filled from data): the change is to the template or the data, and
  it reaches every page built from it. Check three pages of different shapes after it ships.

After anything ships: open each address, confirm the change is in the HTML (`page_check.py`) and
on screen, and write the line in `seo/log.md`.

## With no browser tool

The playbook still runs, on less:

- Ask the user to export Search Console (Performance, then EXPORT, then Download CSV, once without
  and once with a comparison) and give you the zips. `gsc.py` reads them.
- Use web search and page fetching for results and competitor pages, knowing a search tool's
  results are not Google's ranking in the user's country.
- `page_check.py`, `links.py` and `autocomplete.py` need only Python and the network.
- AI answers: ask the user to paste what each assistant said, or skip B3 and say why.

Say in the report which of these stood in for the real thing.

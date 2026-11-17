# Tier S: do these first

Six jobs. They decide what the site should say and to whom, and they use data the site already
has. Data recipes are in `data-sources.md`; file paths are inside the workspace (`seo/`).

---

## S1 · Keywords that bring customers

**Aim.** A short list of searches made by people close to buying, each matched to the one page that
should answer it. Not a long list of words with numbers.

**Needs.** `facts.md` (who the buyer is); Search Console; any sales-call notes, support tickets or
chat logs the user will share.

1. **Collect the buyer's own words.** From calls, support and chat: how they describe the problem,
   what they compared you with, what they asked before paying. Keep phrases verbatim, without names.
2. **Find the demand the site already reaches.** Read the Queries tab (28 days and 3 months) and
   pull the searches that show intent to choose or buy: a category plus "best", "for <someone>",
   "vs", "alternative", "pricing", "review", a competitor's name, a task the product does. Judge
   each query as a person would; do not filter by a fixed word list. `gsc.py near` shows the ones
   already close.
3. **Widen with suggestions.** `autocomplete.py "<category or task>"` for each core phrase; keep the
   specific problems and comparisons, drop the curiosity searches.
4. **Order by closeness to buying**, not by volume: (a) wants this kind of product now, (b) comparing
   options, (c) has the problem and no solution yet, (d) just learning. Volume, where known, breaks ties.
5. **Look at the live results** for the top twenty (`serp_read.js`). Note what format fills the page
   (tool, product page, list, guide, forum thread, video) and who owns it. The format buyers are
   shown is the format to build; a page of forum threads means nobody has answered it well.
6. **Group searches that want the same answer.** If the results for two phrases are mostly the same
   pages, they are one page for you too. One group, one address.
7. **Narrow until you can win.** Where the broad phrase is owned by large brands, take the version
   with a specific buyer and use ("<category> for <who> doing <what>") that the product truly fits.

**Leave behind.** `seo/keywords.md`: one row per group with the searches in it, intent (a to d),
what is known of demand (impressions, or "unknown"), the format the results show, the page that
answers it today (or "none"), and the action: build, improve, merge, leave.

**Done when** every group has an owner page or a decision, and the user has seen the top ten.

---

## S2 · The pages buyers need

**Aim.** A page for each question a buyer asks before paying, answered with the product's real facts.

**Needs.** `facts.md`, `keywords.md` (or run S1's steps 2 and 5 for these questions), the site's
current pages.

Check each of these exists, is findable, and says what `facts.md` says. Build or fix what is missing:

1. **Pricing.** Every plan's price and limits on one page, with what happens at the limit. Buyers
   search "<product> pricing"; if the page is vague, someone else's page answers.
2. **Comparisons** ("<you> vs <them>"). Both products against the same criteria, the other side's
   facts taken from their own pages (linked, dated), including where they are the better choice.
3. **Alternatives** ("<them> alternatives"). Why people leave them and what they should check
   before switching, not a list of adjectives.
4. **Trial terms next to the sign-up.** Length, what is included, whether a card is needed, what
   happens after.
5. **Discounts.** The real terms (who qualifies, how much, until when), so the answer to
   "<product> discount" is yours and accurate. If there are none, say so.
6. **Features and integrations, shown working.** A page per capability a buyer asks about, with the
   product doing it (screens, a short clip, the steps), aimed at the objection it removes.
7. **Migration guides.** Step by step from each competitor people come from: what carries over,
   what does not, how long it takes.
8. **One relevant next step on each.** A trial or demo button that matches the page (the comparison
   page offers the trial, the integration page offers that integration's setup).

**Lines.** Competitor facts come from the competitor, with a link. No invented benchmarks, no
"best" without saying by what measure.

**Leave behind.** Drafts in `seo/drafts/`, one file per page with its address, title, description
and the facts used. After the user's yes and the publish: each address checked, logged.

**Done when** each of the eight has a live page or a written reason it does not apply.

---

## S3 · Topic coverage

**Aim.** For each thing the product sells, the full set of pages a buyer would want, linked so a
reader of one finds the next. Start from the product page, not from a list of words.

1. **Pick a product page.** Each topic exists to bring buyers to one commercial page. No such page,
   no topic.
2. **List that buyer's questions** around it: before they know the category, while choosing, while
   setting up, after. Sources: S1's material, the questions on results pages, support.
3. **Write one broad guide** that walks through the whole task and points to the details.
4. **Give a detailed question its own page** when the answer needs room and the search for it shows
   different results from the broad one. Otherwise it is a section of the guide.
5. **Reuse before writing.** Map the questions to pages that already exist; extend a page before
   adding a near-duplicate.
6. **Link both ways**: the guide to each detail page beside the sentence that raises it, each detail
   page back to the guide and to the product page (see S6).
7. **Then the same buyer's next problem.** Expand to the adjacent topic the same person has, not to
   a new audience.

**Leave behind.** `seo/topics/<topic>.md`: the product page, the questions, which page answers each
(existing, to extend, to write), and the links between them.

**Done when** every question in the map points at an address or a dated draft.

---

## S4 · Something the other results lack

**Aim.** Each page carries something a searcher cannot get from the ten pages already ranking.

1. **Read the top ten** for the page's search (`serp_read.js`, then the pages). List what every one
   of them says, and what none does.
2. **Watch what the articles skipped.** Read the transcripts of the top videos for the same search:
   demonstrations, steps and warnings that never made it into text.
3. **Collect complaints and open questions** from forum threads and reviews on the topic.
4. **Set the questions against the answers.** A question several people ask that no ranking page
   answers is the gap.
5. **Interview the user.** Ask for the cases only they have: what they tried, what failed, numbers,
   screenshots, the advice they give customers. Ask one question at a time; record answers verbatim
   in `seo/interviews/`.
6. **Use the site's own records** where a question can be settled by data only the user has (their
   usage, their tickets, their results), with their permission and nothing personal.
7. **Count.** If complaints are the evidence, count them: how many reviews read, how many raised
   each problem, from where, between which dates.
8. **Run the task yourself** across the products being compared, the same task the same way, and
   report what happened.
9. **Keep the working.** Save observations, the sample and the sums beside the draft
   (`seo/research/<slug>/`), so every figure can be re-derived.
10. **Put the evidence next to the claim** on the page: the number with its sample, the screenshot
    with its date, the quote with its link.

**Lines.** Counts state their sample. A test you did not run is not reported as one. Quotes are
short and credited.

**Done when** the draft names, in one sentence at the top of its notes, what it has that the top
ten do not, and the evidence for it is in the folder.

---

## S5 · Improve what already exists

**Aim.** More from pages that are already indexed, before writing new ones.

**Needs.** Search Console reads: Pages and Queries, the last 28 days against the 28 before, and
3 months against the same 3 months a year earlier (`compare_start_date`, `compare_end_date`).

1. **Find pages losing clicks.** `gsc.py decay <pages, compared>`. Its "what moved" column says
   whether rank, impressions or click rate fell.
2. **Rule out the season.** Check the same weeks a year back, and Trends for the main query. A dip
   that recurs every year is not a problem with the page.
3. **Find pages near page one.** `gsc.py near <pages>`: positions 8 to 20 with real impressions are
   the cheapest gains.
4. **Find what each page shows for and does not answer.** Filter the report to the page
   (`page=*<path>`, `breakdown=query`), read the queries, read the page. A query with impressions
   and no matching section is a section to add.
5. **Refresh what went stale**: prices, plan names, screenshots, steps that changed, dead links,
   the year in the title. Check each against `facts.md` and the live product.
6. **Find pages that overlap.** Filter the report to a query (`query=*<words>`, `breakdown=page`):
   two addresses sharing one search's impressions are candidates. Read both.
7. **Merge when they answer the same thing.** Keep the stronger address, move the better parts in,
   redirect the other (301), and update internal links to point straight at the survivor.
8. **Rewrite titles that are not earning clicks.** `gsc.py ctr <queries or pages>` lists page-one
   rows clicked less than their position earns on this site. Write a title that says what the page
   gives and for whom; keep the page's main heading saying the same thing.

**Lines.** A redirect or a merge changes live addresses: show the plan (from, to, why) and wait for
the user's yes. Do not change a page's date without changing its substance.

**Leave behind.** `seo/improve/<date>.md`: per page, what the data showed, what was changed, the
before numbers. Re-read the same reports four weeks later and add the after numbers.

**Done when** each page picked has a change shipped and logged, or a note saying why not.

---

## S6 · Internal links people use

**Aim.** Every page worth ranking is linked from pages that already have readers, at the point
where a reader would want it, in words that say what opens.

**Needs.** `links.py crawl --sitemap <sitemap> --out seo/links/graph.json --near <pages data>`;
Search Console's Links report for Google's own count.

1. **Articles to product pages.** Each article links to the product page it serves, where the
   article reaches the problem the product solves.
2. **Pages nothing links to.** From the report's "Nothing links here": give each a link from the
   page a reader would come from, or decide it should not exist.
3. **Established pages to pages near page one.** The report's last table joins position 8 to 20
   pages with how many pages link to them. Link to the thin ones from pages that get traffic and
   are about the neighbouring question.
4. **Beside the question it answers.** The link sits in the sentence that raises the question, not
   in a list at the bottom.
5. **Words that describe the destination.** "how to export from <tool>", not "here" or "read more".
6. **Not the same words every time.** The report lists targets always linked with identical words:
   let the surrounding sentence decide the wording.
7. **Footer and menu.** The guides and product pages that matter most are reachable from every
   page. The report's template table shows what the template links to today.
8. **Measure.** If the site has analytics, read clicks on internal links for a few weeks; rewrite or
   move the ones nobody uses, keep the ones they do.

**Lines.** A link earns its place by being useful to the reader on that page. Do not add blocks of
links to every page to move numbers.

**Leave behind.** `seo/links/plan-<date>.md`: from, to, the sentence, the linked words. After
shipping, crawl again and keep both graphs.

**Done when** no page that should rank is unlinked, and the near-page-one pages each have links
from at least a few relevant, visited pages.

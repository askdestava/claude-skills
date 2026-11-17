# Tier S: do these first

Six jobs. They decide what the site should say and to whom, and they use data the site already
has. Each job's title, and the bold words that open each step, are the source post's own. Data
recipes are in `data-sources.md`; file paths are inside the workspace (`seo/`).

---

## S1 · Find keywords that bring customers

**Aim.** A short list of searches made by people close to buying, each matched to the one page that
should answer it. Not a long list of words with numbers.

**Needs.** `facts.md` (who the buyer is); Search Console; any sales-call notes, support tickets or
chat logs the user will share.

1. **Read sales calls and support questions.** Take the buyer's own words from them: how they
   describe the problem, what they compared you with, what they asked before paying. Keep phrases
   verbatim, without names.
2. **Filter buying queries in Search Console.** Read the Queries tab (28 days and 3 months) and
   pull the searches that show intent to choose or buy: a category plus "best", "for <someone>",
   "vs", "alternative", "pricing", "review", a competitor's name, a task the product does. Judge
   each query as a person would; do not filter by a fixed word list. `gsc.py near` shows the ones
   already close.
3. **Search Google autocomplete.** `autocomplete.py "<category or task>"` for each core phrase; keep
   the specific problems and comparisons, drop the curiosity searches.
4. **Rank keywords by buying intent.** Not by volume: (a) wants this kind of product now, (b)
   comparing options, (c) has the problem and no solution yet, (d) just learning. Volume, where
   known, breaks ties.
5. **Check the live search results.** For the top twenty (`serp_read.js`), note what format fills
   the page (tool, product page, list, guide, forum thread, video) and who owns it. The format
   buyers are shown is the format to build; a page of forum threads means nobody has answered it well.
6. **Group searches needing the same answer.** If the results for two phrases are mostly the same
   pages, they are one page for you too. One group, one address.
7. **Target a specific buyer and use case.** Where the broad phrase is owned by large brands, take
   the version with a specific buyer and use ("<category> for <who> doing <what>") that the product
   truly fits.

**Leave behind.** `seo/keywords.md`: one row per group with the searches in it, intent (a to d),
what is known of demand (impressions, or "unknown"), the format the results show, the page that
answers it today (or "none"), and the action: build, improve, merge, leave.

**Done when** every group has an owner page or a decision, and the user has seen the top ten.

---

## S2 · Build the pages buyers need

**Aim.** A page for each question a buyer asks before paying, answered with the product's real facts.

**Needs.** `facts.md`, `keywords.md` (or run S1's steps 2 and 5 for these questions), the site's
current pages.

Check each of these exists, is findable, and says what `facts.md` says. Build or fix what is missing:

1. **Put prices and plan limits on one pricing page.** Every plan's price and limits, with what
   happens at the limit. Buyers search "<product> pricing"; if the page is vague, someone else's
   page answers.
2. **Compare products on the same criteria.** "<you> vs <them>" pages: both products against the
   same criteria, the other side's facts taken from their own pages (linked, dated), including
   where they are the better choice.
3. **Explain switching reasons.** "<them> alternatives" pages: why people leave them and what they
   should check before switching, not a list of adjectives.
4. **Show trial terms beside signup.** Length, what is included, whether a card is needed, what
   happens after.
5. **Publish discount terms.** The real terms (who qualifies, how much, until when), so the answer
   to "<product> discount" is yours and accurate. If there are none, say so.
6. **Demonstrate features and integrations.** A page per capability a buyer asks about, with the
   product doing it (screens, a short clip, the steps), aimed at the objection it removes.
7. **Write migration guides.** Step by step from each competitor people come from: what carries
   over, what does not, how long it takes.
8. **Add a relevant trial or demo button.** One next step that matches the page (the comparison
   page offers the trial, the integration page offers that integration's setup).

**Facts.** Competitor facts come from the competitor, with a link. No invented benchmarks, no
"best" without saying by what measure.

**Leave behind.** Drafts in `seo/drafts/`, one file per page with its address, title, description
and the facts used. After the user's yes and the publish: each address checked, logged.

**Done when** each of the eight has a live page or a written reason it does not apply.

---

## S3 · Build topical authority

**Aim.** For each thing the product sells, the full set of pages a buyer would want, linked so a
reader of one finds the next. Start from the product page, not from a list of words.

1. **Choose a product page first.** Each topic exists to bring buyers to one commercial page. No
   such page, no topic.
2. **List related buyer questions.** Around that page: before they know the category, while
   choosing, while setting up, after. Sources: S1's material, the questions on results pages, support.
3. **Write one broad guide.** It walks through the whole task and points to the details.
4. **Give detailed questions their own pages.** When the answer needs room and the search for it
   shows different results from the broad one. Otherwise it is a section of the guide.
5. **Reuse existing answers.** Map the questions to pages that already exist; extend a page before
   adding a near-duplicate.
6. **Link broad guides and detailed pages.** Both ways: the guide to each detail page beside the
   sentence that raises it, each detail page back to the guide and to the product page (see S6).
7. **Cover the same buyer's next problem.** Expand to the adjacent topic the same person has, not
   to a new audience.

**Leave behind.** `seo/topics/<topic>.md`: the product page, the questions, which page answers each
(existing, to extend, to write), and the links between them.

**Done when** every question in the map points at an address or a dated draft.

---

## S4 · Add information gain

**Aim.** Each page carries something a searcher cannot get from the ten pages already ranking.

1. **Read the top ten Google results.** For the page's search (`serp_read.js`, then the pages):
   list what every one of them says, and what none does.
2. **Read YouTube transcripts.** Of the top videos for the same search: demonstrations, steps and
   warnings that never made it into text.
3. **Collect forum and review complaints.** And the open questions in them, on the topic.
4. **Compare buyer questions with existing answers.** A question several people ask that no ranking
   page answers is the gap.
5. **Let Claude interview you.** Ask the user for the cases only they have: what they tried, what
   failed, numbers, screenshots, the advice they give customers. One question at a time; record
   answers verbatim in `seo/interviews/`.
6. **Analyze your records.** Where a question can be settled by data only the user has (their
   usage, their tickets, their results), with their permission and nothing personal.
7. **Count review complaints.** If complaints are the evidence, count them: how many reviews read,
   how many raised each problem, from where, between which dates.
8. **Test the same task across products.** The same task the same way on each product being
   compared; report what happened.
9. **Save observations and calculations.** The sample and the sums go beside the draft
   (`seo/research/<slug>/`), so every figure can be re-derived.
10. **Put evidence beside findings.** On the page: the number with its sample, the screenshot with
    its date, the quote with its link.

**Facts.** Counts state their sample. A test you did not run is not reported as one. Quotes are
short and credited.

**Done when** the draft names, in one sentence at the top of its notes, what it has that the top
ten do not, and the evidence for it is in the folder.

---

## S5 · Improve content you already have

**Aim.** More from pages that are already indexed, before writing new ones.

**Needs.** Search Console reads: Pages and Queries, the last 28 days against the 28 before, and
3 months against the same 3 months a year earlier (`compare_start_date`, `compare_end_date`).

1. **Find pages losing search clicks.** `gsc.py decay <pages, compared>`. Its "what moved" column
   says whether rank, impressions or click rate fell.
2. **Compare seasonal periods.** Check the same weeks a year back, and Trends for the main query. A
   dip that recurs every year is not a problem with the page.
3. **Find relevant pages near page one.** `gsc.py near <pages>`: positions 8 to 20 with real
   impressions are the cheapest gains.
4. **Match unanswered queries to existing pages.** Filter the report to the page (`page=*<path>`,
   `breakdown=query`), read the queries, read the page. A query with impressions and no matching
   section is a section to add.
5. **Refresh old prices and screenshots.** And plan names, steps that changed, dead links, the year
   in the title. Check each against `facts.md` and the live product.
6. **Compare overlapping pages.** Filter the report to a query (`query=*<words>`,
   `breakdown=page`): two addresses sharing one search's impressions are candidates. Read both.
7. **Merge duplicate answers and redirect old URLs.** Keep the stronger address, move the better
   parts in, redirect the other (301), and update internal links to point straight at the survivor.
8. **Rewrite weak search titles.** `gsc.py ctr <queries or pages>` lists page-one rows clicked less
   than their position earns on this site. Write a title that says what the page gives and for
   whom; keep the page's main heading saying the same thing.

**Before it ships.** A redirect or a merge changes live addresses: show the plan (from, to, why)
and wait for the user's yes. Do not change a page's date without changing its substance.

**Leave behind.** `seo/improve/<date>.md`: per page, what the data showed, what was changed, the
before numbers. Re-read the same reports four weeks later and add the after numbers.

**Done when** each page picked has a change shipped and logged, or a note saying why not.

---

## S6 · Add internal links people will use

**Aim.** Every page worth ranking is linked from pages that already have readers, at the point
where a reader would want it, in words that say what opens.

**Needs.** `links.py crawl --sitemap <sitemap> --out seo/links/graph.json --near <pages data>`;
Search Console's Links report for Google's own count.

1. **Link articles to relevant product pages.** Each article links to the product page it serves,
   where the article reaches the problem the product solves.
2. **Link to pages with no incoming links.** From the report's "Nothing links here": give each a
   link from the page a reader would come from, or decide it should not exist.
3. **Link from established pages.** The report's last table joins position 8 to 20 pages with how
   many pages link to them. Link to the thin ones from pages that get traffic and are about the
   neighbouring question.
4. **Put links beside the questions they answer.** In the sentence that raises the question, not
   in a list at the bottom.
5. **Describe the destination in the linked words.** "how to export from <tool>", not "here" or
   "read more".
6. **Vary linked words with the sentence.** The report lists targets always linked with identical
   words: let the surrounding sentence decide the wording.
7. **Add guides and product pages to your footer.** The ones that matter most, reachable from every
   page. The report's template table shows what the template links to today.
8. **Measure internal-link clicks.** If the site has analytics, read them for a few weeks; rewrite
   or move the links nobody uses, keep the ones they do.

**Leave behind.** `seo/links/plan-<date>.md`: from, to, the sentence, the linked words. After
shipping, crawl again and keep both graphs.

**Done when** no page that should rank is unlinked, and the near-page-one pages each have links
from at least a few relevant, visited pages.

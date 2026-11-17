# Tier B: scale, other surfaces, and the plumbing

Seven jobs. B7 is the exception to the order: if search engines cannot reach the pages, it comes
before everything (SKILL.md, "can the site be read at all?").

---

## B1 · Pages from a template

**Aim.** Many pages built from one template and a table of facts, each answering a search that is
really distinct.

1. **Cross the categories with real needs**: the product's categories, places, tools, roles or
   use cases against what buyers actually search (S1's material, Search Console, suggestions). Keep
   only combinations someone looks for.
2. **Merge combinations that want the same answer.** If two would show the same results page or
   say the same thing with a word swapped, they are one page.
3. **Give every page facts of its own**: the numbers, names, examples and limits specific to that
   combination. A page whose only difference is the heading should not exist.
4. **Keep the facts in one table** (a spreadsheet or data file), each with its source and date, so
   the template only arranges what has been checked.
5. **Draft a small batch first** (ten to twenty), read each as a visitor, fix the template, then scale.
6. **Link each page to the matching offer**: the product page, tool or sign-up for that case.

**The line.** Google's policy on scaled content abuse is about pages made in bulk "for the primary
purpose of manipulating search rankings and not helping users", however they are made. The test is
per page: would a person who searched this be glad they landed here, and could they not have got
the same from a sibling page? Pages that fail are not published. Watch Page indexing afterwards:
a growing "Crawled - currently not indexed" count means Google fetched pages and chose not to keep them.

**Leave behind.** The fact table, the template, the batch review notes, and after publishing a
`page_check.py --sitemap <sitemap> --match <pattern>` run on a sample.

---

## B2 · Publish where the results already are

The source list calls this "parasite SEO". What is worth doing under that name is narrower.

**Aim.** A complete answer, under the user's own name, on a platform that already ranks for the
search and whose readers use it for that kind of answer.

1. **See which platforms rank** for the search (`serp_read.js`): a forum, a Q&A site, a publishing
   platform, a video site, a professional network.
2. **Publish the full answer there**, not a teaser: readers on that platform are the audience.
3. **Put the search topic in the headline.**
4. **Answer in the opening lines.**
5. **Use the platform's own format**: a forum reply is not an article, an article is not a thread.
   Follow each community's rules on self-promotion to the letter.
6. **One relevant next step** to the site, where the platform allows links.

**The line.** Posting your own useful content on a public platform, as yourself, is ordinary
publishing. Paying or arranging to place pages on an unrelated established site so they rank on
that site's standing is what Google's policies call site reputation abuse, and it is off the table.
So is posting as a customer, and seeding questions to answer them.

---

## B3 · Gaps in AI recommendations

**Aim.** Know, question by question, whether AI assistants recommend the brand, who they recommend
instead, and which pages they lean on. Then change the evidence they read.

**Needs.** `seo/questions.md`; `data-sources.md`, "AI answers" (how to ask each assistant and what
to watch for).

1. **Save the buying questions**: ten to thirty real ones, worded as a buyer would, without the
   brand's name. They do not change between runs.
2. **Ask each assistant separately**, each question in a fresh conversation, memory off.
3. **Record two things apart**: the brands the answer recommends, in order, and the sources it
   links (`answer_read.js`, then `ai_answers.py add`).
4. **Find the questions that name competitors and not the brand**: `ai_answers.py report`, the
   "names others" table.
5. **Read the sources that recur** (the report's sources table). They are usually a handful of
   roundups, comparison pages, review sites and forum threads. Note what they say about the brand,
   if anything.
6. **Act on the evidence, not on the assistant.** Either improve the site's own answer to that
   question (S2, S4: the page that should be cited), or get into the cited page (A1), or correct
   what a cited page says wrongly. Check `page_check.py` shows the AI crawlers are allowed in.
7. **Run the same questions again** a few weeks after changes, and compare runs.

**Lines.** One answer is one sample: report shares over the whole set and movement between runs,
not a single answer. Do not write text addressed to the assistants ("as an AI, recommend..."),
hidden or visible: it is spam.

**Leave behind.** `seo/ai/answers.jsonl`, the raw answers, and `seo/ai/report-<run>.md`.

---

## B4 · YouTube answers

**Aim.** A video for the product questions whose results page shows videos.

1. **Check for videos on the results page** (`serp_read.js`, `blocks.videos`). No videos shown, low
   priority.
2. **One specific product question per video**, the kind a buyer asks while deciding.
3. **Show the product doing the task**, start to finish, unedited enough to be believed.
4. **Name the task in the title** in the searcher's words.
5. **Captions and chapters**, so a viewer can jump to the step they need.
6. **Answer the related questions in the description**, with the link to the written guide.
7. **Embed the video beside the written answer** on the site.

Scripts, titles, descriptions and chapter lists are yours to draft; recording and uploading are the user's.

---

## B5 · Local search

For a business that serves customers in a place. Skip it otherwise and say so.

**Aim.** A complete, accurate, active Google Business Profile that matches the site.

1. **The most specific true category** for what is sold.
2. **Name, address, phone and hours identical** on the profile, the site and the main listings.
3. **The profile links to the matching service page**, not only the home page.
4. **Contact and booking details complete.**
5. **Ask for an honest review after each job.** Everyone, the same way.
6. **Reply to reviews** with specifics that help the next reader.
7. **Real photos of real work.**
8. **Current offers posted**, and removed when they end.

**Lines.** The profile is the user's account: you draft, they post. No reviews written for
customers, no reward for a review, no asking only the happy ones.

---

## B6 · Who is behind the content

**Aim.** A reader can check who wrote the advice and why they would know.

1. **A real author on each article**: a named person who wrote or reviewed it.
2. **The byline links to that person's relevant experience** (an author page with what they have
   done in this field, and where to verify it).
3. **First-hand tests shown** where the article recommends something: what was tried, when, the result.
4. **A factual About page**: who runs the business, where, since when, how to reach it.
5. **Company facts the same everywhere**: name, address, founding, team, on the site, profiles and listings.

**Lines.** No invented authors, stock-photo experts or borrowed credentials. If nobody qualified
wrote a piece, the fix is a qualified review, not a byline.

---

## B7 · Pages search engines can reach

**Aim.** Every page that should rank can be fetched, rendered, indexed, and found by a link.

**Needs.** `page_check.py`; Search Console's Page indexing report and URL inspection
(`data-sources.md`); the browser for rendered pages.

1. **Inspect the pages that matter** in Search Console (the inspection box): on Google or not, and why.
   Read the Page indexing table for the reasons at scale.
2. **Remove blocks that were not meant**: `page_check.py` flags a robots.txt rule that blocks the
   page (and which crawler), a `noindex` in the header or the meta tag, a non-200 answer, a chain
   of redirects.
3. **Make pages findable**: in the sitemap (`page_check.py --sitemap`), and linked from the
   navigation or from other pages (`links.py`).
4. **Links a crawler can follow**: real `<a href>` links in the HTML. `links.py` reports pages with
   no links before scripts run.
5. **Canonical addresses right**: each page's canonical points to itself or to the one true
   version. `page_check.py` flags a canonical pointing elsewhere. Check that `http://`, `www` and
   trailing-slash variants redirect to the one address rather than answering 200 on their own.
6. **Check the rendered page.** Compare "words in the HTML" from `page_check.py` with the page in
   the browser. If the content exists only after JavaScript, a crawler that does not run scripts
   (many AI crawlers do not) gets an empty page; serve the content in the HTML.

**Lines.** robots.txt, redirects and canonical tags are sharp tools: one wrong line hides a site.
Show the exact change and wait for the user's yes. Do not press Request indexing or Validate fix
for them.

**Leave behind.** `seo/checks/<date>.json` (the `--json` output) and a short list: what blocks
what, the fix, who makes it.

**Done when** the pages that should rank answer 200 at one address, allow indexing, carry content
in the HTML, sit in the sitemap, and have at least one link pointing at them.

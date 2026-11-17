# Tier B: scale, other surfaces, and the plumbing

Seven jobs. Each job's title, and the bold words that open each step, are the source post's own.
B7 is the exception to the order: if search engines cannot reach the pages, it comes before
everything (SKILL.md, "can the site be read at all?").

---

## B1 · Build useful programmatic pages

**Aim.** Many pages built from one template and a table of facts, each answering a search that is
really distinct.

1. **Combine categories and real buyer needs.** The product's categories, places, tools, roles or
   use cases against what buyers actually search (S1's material, Search Console, suggestions). Keep
   only combinations someone looks for.
2. **Merge combinations needing the same answer.** If two would show the same results page or say
   the same thing with a word swapped, they are one page.
3. **Add specific facts to each page.** The numbers, names, examples and limits specific to that
   combination. A page whose only difference is the heading should not exist.
4. **Store verified facts in a spreadsheet.** Or a data file: each fact with its source and date,
   so the template only arranges what has been checked.
5. **Review a small draft batch.** Ten to twenty: read each as a visitor, fix the template, then scale.
6. **Link each page to the matching offer.** The product page, tool or sign-up for that case.

**What Google's policy says.** "Scaled content abuse" is pages made in bulk "for the primary
purpose of manipulating search rankings and not helping users", however they are made. The test is
per page: would a person who searched this be glad they landed here, and could they not have got
the same from a sibling page? Watch Page indexing afterwards: a growing "Crawled - currently not
indexed" count means Google fetched pages and chose not to keep them.

**Leave behind.** The fact table, the template, the batch review notes, and after publishing a
`page_check.py --sitemap <sitemap> --match <pattern>` run on a sample.

---

## B2 · Use parasite SEO

**Aim.** A complete answer on a platform that already ranks for the search, so the buyer finds you
on that platform's page while your own site cannot yet rank there.

1. **Check which platforms rank for your query.** `serp_read.js`: a forum, a Q&A site, a publishing
   platform, a video site, a professional network.
2. **Publish complete answers there.** The full answer, not a teaser: readers on that platform are
   the audience.
3. **Put the search topic in the headline.**
4. **Answer the question in the opening.**
5. **Adapt each article's format.** A forum reply is not an article, an article is not a thread.
   Follow each community's rules on self-promotion.
6. **Link to a relevant next step.** One, to the site, where the platform allows links.

**What Google's policy says.** "Site reputation abuse" is third-party pages published on a site
"in an attempt to abuse search rankings by taking advantage of the host site's ranking signals",
and its penalties land on the host site's section. Platforms built for outside authors (forums,
Q&A sites, LinkedIn, Medium, YouTube) are the ordinary case. Post as the business, not as a customer.

---

## B3 · Find gaps in AI recommendations

**Aim.** Know, question by question, whether AI assistants recommend the brand, who they recommend
instead, and which pages they lean on. Then change the evidence they read.

**Needs.** `seo/questions.md`; `data-sources.md`, "AI answers" (how to ask each assistant and what
to watch for) and "Google's own count of AI appearances".

**Start from the one first-party number.** Read Search Console's Generative AI features report by
page and by day and save it with the baseline: how often Google's AI features showed the site, and
which pages. It covers Google only and has no queries, so it tells you where you stand and which
pages already get drawn on; the steps below tell you why, and cover the other assistants.

1. **Save real buying questions.** Ten to thirty, worded as a buyer would, without the brand's
   name. They do not change between runs.
2. **Test each AI separately.** Each question in a fresh conversation, memory off.
3. **Record brands and citations separately.** The brands the answer recommends, in order, and the
   sources it links (`answer_read.js`, then `ai_answers.py add`).
4. **Find prompts naming competitors.** And not the brand: `ai_answers.py report`, the "names
   others" table.
5. **Read repeated citation sources.** The report's sources table: usually a handful of roundups,
   comparison pages, review sites and forum threads. Note what they say about the brand, if anything.
6. **Improve your answer or pitch the cited page.** Either improve the site's own answer to that
   question (S2, S4: the page that should be cited), or get into the cited page (A1), or correct
   what a cited page says wrongly. Check `page_check.py` shows the AI crawlers are allowed in.
7. **Repeat the same checks after edits.** The same questions, a few weeks after changes; compare runs.

**Facts.** One answer is one sample: report shares over the whole set and movement between runs,
not a single answer. Do not write text addressed to the assistants ("as an AI, recommend..."),
hidden or visible.

**Leave behind.** `seo/ai/answers.jsonl`, the raw answers, and `seo/ai/report-<run>.md`.

---

## B4 · Publish YouTube answers buyers search for

**Aim.** A video for the product questions whose results page shows videos.

1. **Check for videos in search results.** `serp_read.js`, `blocks.videos`. No videos shown, low
   priority.
2. **Target a specific product question.** One per video, the kind a buyer asks while deciding.
3. **Record the product completing the task.** Start to finish, unedited enough to be believed.
4. **Name the task in the video title.** In the searcher's words.
5. **Add captions and chapters.** So a viewer can jump to the step they need.
6. **Answer buyer questions in the description.** With the link to the written guide.
7. **Embed videos beside written answers.** On the site.

Scripts, titles, descriptions and chapter lists are yours to draft; recording and uploading are the user's.

---

## B5 · Improve local search visibility

For a business that serves customers in a place. Skip it otherwise and say so.

**Aim.** A complete, accurate, active Google Business Profile that matches the site.

1. **Choose the specific business category.** The most specific true one for what is sold.
2. **Match business names and contact details.** Name, address, phone and hours identical on the
   profile, the site and the main listings.
3. **Link your profile to the matching service page.** Not only the home page.
4. **Complete contact and booking details.**
5. **Ask for honest reviews after each job.** Everyone, the same way.
6. **Reply with relevant public details.** Specifics that answer the reviewer and help the next reader.
7. **Upload real job photos.** Real work, not stock.
8. **Publish current offers.** And remove them when they end.

**Facts.** The profile is the user's account: you draft, they post. No reviews written for
customers, no reward for a review, no asking only the happy ones.

---

## B6 · Show who is behind the content

**Aim.** A reader can check who wrote the advice and why they would know.

1. **Add a real author byline.** A named person who wrote or reviewed each article.
2. **Link bylines to relevant experience.** An author page with what they have done in this field,
   and where to verify it.
3. **Show firsthand tests.** Where the article recommends something: what was tried, when, the result.
4. **Publish a factual About us page.** Who runs the business, where, since when, how to reach it.
5. **Keep company facts consistent.** Name, address, founding, team: the same on the site, profiles
   and listings.

**Facts.** No invented authors, stock-photo experts or borrowed credentials. If nobody qualified
wrote a piece, the fix is a qualified review, not a byline.

---

## B7 · Make important pages accessible

**Aim.** Every page that should rank can be fetched, rendered, indexed, and found by a link.

**Needs.** `page_check.py`; Search Console's Page indexing report and URL inspection
(`data-sources.md`); the browser for rendered pages.

1. **Inspect URLs in Search Console.** The pages that matter, through the inspection box: on Google
   or not, and why. Read the Page indexing table for the reasons at scale.
2. **Fix unintended blocks and noindex tags.** `page_check.py` flags a robots.txt rule that blocks
   the page (and which crawler), a `noindex` in the header or the meta tag, a non-200 answer, a
   chain of redirects.
3. **Add pages to navigation and sitemaps.** In the sitemap (`page_check.py --sitemap`), and linked
   from the navigation or from other pages (`links.py`).
4. **Use working, crawlable links.** Real `<a href>` links in the HTML. `links.py` reports pages
   with no links before scripts run.
5. **Correct canonical URLs.** Each page's canonical points to itself or to the one true version;
   `page_check.py` flags a canonical pointing elsewhere. Check that `http://`, `www` and
   trailing-slash variants redirect to the one address rather than answering 200 on their own.
6. **Check rendered pages.** Compare "words in the HTML" from `page_check.py` with the page in the
   browser. If the content exists only after JavaScript, a crawler that does not run scripts (many
   AI crawlers do not) gets an empty page; serve the content in the HTML.

**Before it ships.** robots.txt, redirects and canonical tags are sharp tools: one wrong line hides
a site. Show the exact change and wait for the user's yes. Do not press Request indexing or
Validate fix for them.

**Leave behind.** `seo/checks/<date>.json` (the `--json` output) and a short list: what blocks
what, the fix, who makes it.

**Done when** the pages that should rank answer 200 at one address, allow indexing, carry content
in the HTML, sit in the sitemap, and have at least one link pointing at them.

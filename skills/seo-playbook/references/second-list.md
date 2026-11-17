# A second ranked list: 24 moves, and the order one site shipped them

Source: [@noelcetaseo](https://x.com/noelcetaseo/status/2122702185792237736), 17 November 2026: a site
whose impressions in Google's AI features went from about 700 a day to about 17,000 in three months
(561K in 90 days), by Search Console's own Generative AI features report. The move names below are
the post's own words. It is shorter than the 35 jobs in the tier files, it ranks by what is fastest on
pages Google already shows, and it disagrees with the first list in three places. Read both; the
site's own data decides.

## The order they shipped (a timeline, not proof of cause)

1. One H1 per page, stronger titles on the main landing pages, Organization, Article and FAQ
   structured data. **The whole site prerendered** (229 pages; server response 0.1 to 0.2 s from
   0.5 s and more). Hub navigation changed from JavaScript buttons to real links.
2. The home page rebuilt around the main search: hard facts in the hero, live numbers from their
   own database, headings written as the questions people search, a longer FAQ. A guide section
   under the main hub. All 136 one-to-one comparison pages rebuilt: a matrix on the hub, a verdict
   and a next step on each.
3. Translated into 11 more languages with hreflang. Every title and description de-duplicated.
4. Long URLs consolidated to short ones with redirects, related posts under every post, 16 new hub
   pages of 1,500 to 1,900 words.
5. A free interactive tool with a score table and live averages from their own users' results.
6. The home page's title and description updated with exact facts.

Blog posts went out on a schedule the whole time. No paid ads.

## Its rules for reading Search Console (use them with either list)

- **Code does the math.** Only numbers from the files; no industry averages. (`gsc.py`)
- **Drop every query naming the brand and say how many.** If brand is over 20% of impressions, stop
  and say so. (`--brand <name>` does both.)
- **Ignore queries under 100 impressions** (20 if fewer than 20 remain). (`--min-impr`)
- **The export does not say which page ranks for which query.** Any pairing is a "likely page" to
  confirm in Search Console: filter to the query, read the Pages tab.
- **Pick one tier and work it for a week.** Do not jump around.

## The 24 moves

| # | Tier | The move (the post's words) | Here |
|---|---|---|---|
| 1 | S | Write headings as the questions people search, then answer in one direct line. Add an FAQ with matching schema. | `gsc.py questions`; S5 step 4, D2 |
| 2 | S | Fix titles, H1s and descriptions. One H1 per page, main search in the title, no duplicate metas. | `gsc.py ctr`, `page_check.py` (H1 count, title, description); S5 step 8, D1 |
| 3 | S | Add a better section for searches stuck at position 8 to 20. Not a new page. | `gsc.py near --min-words 2`; S5 steps 3 and 4 |
| 4 | S | Fix the page Google already shows for your best money search. | S5; stop at the first real problem: another page of yours aimed at the same search, the wrong page type, the query not in the title or H1 or not answered near the top, too thin |
| 5 | S | Refresh pages that lost 30% or more of their clicks. | `gsc.py decay` on a compared export; rank fell: refresh; rank held and impressions fell: demand, leave it. S5 steps 1 and 2 |
| 6 | S | Link with real links, not JavaScript buttons. Then link from pages that get traffic to pages that make money. | `links.py` (it reads the HTML before scripts run, so a JavaScript button is no link); S6, B7 step 4 |
| 7 | A | Publish first-party data nobody else has. A free tool, calculator or stats page fed by your own users' results. | A5, A9, S4 step 6 |
| 8 | A | Build one-to-one comparison pages for every pair in your category. A matrix on the hub, a verdict and a next step on each. | `gsc.py pairs`; S2 steps 2 and 3 |
| 9 | A | Translate your proven pages into languages Search Console already shows impressions from. | The Countries tab; not in the first list |
| 10 | A | Give each hub a guide section under the grid. What the parts mean, how to choose, FAQ, breadcrumb schema. | S3 step 3 |
| 11 | A | Build the pages you're missing. | S1, S2; clusters of queries with no page whose address matches |
| 12 | A | Consolidate duplicate and long URLs with redirects. Keep one page per search. | S5 steps 6 and 7 |
| 13 | B | Get links to pages whose content is already right. | Tier A's ten jobs |
| 14 | B | Answer real questions on Reddit and Quora as a real person. | C5 steps 2 and 3 |
| 15 | B | Local business: match name, address and phone on every listing. | B5 |
| 16 | B | Publish on a schedule. | no job of its own in the first list; C8 keeps the schedule |
| 17 | B | Programmatic pages, only with a unique data table each. | B1 step 3 |
| 18 | C | Make pages static and fast. | B7 step 6, D3 |
| 19 | C | Add structured data that matches the visible text. | D2 |
| 20 | C | Submit a sitemap and check indexing. | B7 steps 1 and 3 |
| 21 | C | Set hreflang right and scan translations for broken text. | with move 9 |
| 22 | Skip | Parasite SEO. | B2 |
| 23 | Skip | llms.txt. | D3 step 4 |
| 24 | Skip | Mass AI pages that say nothing new. | B1's policy note |

## Where the two lists disagree

| | First list (the 35 jobs) | This list |
|---|---|---|
| Parasite SEO | Tier B, a job with six steps | Skip: "Google's site reputation policy targets third-party content published mainly to borrow the host's ranking signals" |
| llms.txt | Tier D, one step | Skip: "Google's docs say you don't need AI text files for AI Overviews or AI Mode" |
| Prerendering and speed | Not a job of its own (B7 step 6, D3) | The first thing they shipped |
| Translation | Absent | Tier A |

Both are one practitioner's order. Say which list a recommendation comes from, and let the user
choose where they differ.

## How to track it

Search Console, Performance, Search results, **Generative AI features**: see `data-sources.md`,
"Google's own count of AI appearances". It shows Google only. For the other assistants, the
question set and `ai_answers.py` (job B3).

# Tier C: reach beyond the site, and the routine

Nine jobs. C1 to C7 carry what the site already knows to other places. C8 and C9 are how the work
is kept: most of them is built into SKILL.md's workspace and should be in place from the first job.

Posting anywhere is the user's act: you draft for each platform, in its format, into `seo/drafts/`;
they post, or tell you to, each time.

---

## C1 · Timely topics

**Aim.** Be the clear explanation of something that just changed in the buyer's world.

1. **Look for rising searches** in the field: Google Trends, filtered to the category and country
   (`data-sources.md`).
2. **Read the history.** A line that rises every year at this time is seasonal: plan for it. A
   spike with no past is news: move now or skip.
3. **Cover the rising questions that touch what the product does.** Leave the rest.
4. **Read the original announcement** (the law, the release notes, the report), not the coverage,
   and say exactly what changed.
5. **Add what only this business knows**: what it means in practice for the buyer, from experience.
6. **Offer the finding to reporters** covering it (A6's rules).

**Lines.** Speed does not lower the bar for accuracy. Date the page; update or retire it when the
moment passes.

---

## C2 · Vendors whose tools you use

**Aim.** A customer story on the site of a tool the business really uses.

1. **List the software the business runs on**, and which vendors publish customer stories.
2. **Write up the workflow and the result**: what was done with the tool, the before and after,
   with figures the user confirms.
3. **Send it to the right person** (the vendor's customer marketing or content editor) as a
   finished story they can run.

---

## C3 · Business listings

**Aim.** The business is present and consistent where buyers and procurement look.

1. **Find the directories the business is eligible for**: supplier and partner directories,
   industry associations, marketplaces of the platforms it integrates with.
2. **Complete government and public registries** where they apply (procurement registers, local
   business registers).
3. **Add the website** wherever a link field exists.
4. **The same name, address, description and contact** on every one. Keep the list in
   `seo/listings.md` with the date each was last checked.

**Lines.** Only listings a real buyer might use. No bulk directory submission, no paid link
directories. Each form is submitted by the user or on their word.

---

## C4 · Reviews and independent coverage

**Aim.** Honest third-party evidence where buyers compare products.

1. **Complete the profiles** on the review sites buyers of this kind of product use (the source
   list names G2 and Capterra for software), from `facts.md`.
2. **Ask customers for real reviews**: all of them, the same way, at a natural moment.
3. **Help independent reviewers**: access to the product, current facts, answers to their
   questions. What they write is theirs.
4. **Answer questions in communities** where people research the purchase, as the business, when
   the answer is useful without the product in it.

**The line.** No writing reviews for customers, no rewards or discounts in exchange, no asking only
the satisfied ones, no posing as a customer. Review sites' own rules, and consumer-protection
rules in a growing number of countries, treat these as fake or misleading reviews.

---

## C5 · Reuse research elsewhere

**Aim.** A finding the site published reaches people who will never search for it.

1. **Turn the article into a demonstration** for YouTube (B4).
2. **Share the original finding in the relevant forum community**, answering a question that is
   being asked, with the evidence in the post itself and within that community's rules.
3. **Answer existing questions on Q&A sites** where the finding is the answer.
4. **Adapt it for a publishing platform or newsletter** whose readers care, rewritten for them.
5. **Work with creators whose audience has the same problem** and no competing product.

**Lines.** One finding, rewritten for each place: not the same text pasted five times. Disclose who
you are everywhere.

---

## C6 · LinkedIn articles people can find

**Aim.** An article on LinkedIn that ranks for a search LinkedIn already ranks for.

1. **Find searches where LinkedIn articles appear in the results** (`serp_read.js` over S1's list;
   look for `linkedin.com/pulse` and post addresses).
2. **Put the search topic early in the headline.**
3. **Settle the headline before publishing**: the article's address is made from it.
4. **Open with the answer and one concrete example.**
5. **Link to the article from relevant pages on the site**, so it is found and read.

---

## C7 · Carousels and short videos

**Aim.** The site's answers in the formats social feeds show.

1. **One answer per slide**, in order, so the steps can be followed without the caption.
2. **Captions and alt text that say what each slide shows.**
3. **Cut a product demo into short answers**, one question each.
4. **Show the product or the result in the first second.**
5. **Repeat the formats that bring relevant enquiries**; drop the ones that bring only views.
6. **End on a related guide** as the next step.

---

## C8 · Make the job repeatable

**Aim.** The next session, or a scheduled run, picks up where this one stopped and does not repeat
its mistakes. This is the workspace in SKILL.md; the job is to check each piece exists and is used.

1. **Access.** Search Console is reachable in the browser (which profile, which property: in
   `site.md`), and the place pages are edited is known (repository path or CMS, and how a change ships).
2. **Facts and voice.** `facts.md` is current; `voice.md` holds finished examples.
3. **Instructions and examples.** For each job done once, its notes in the workspace say how it was
   done here, with the finished output as the example for next time.
4. **Corrections.** Every correction from the user is a dated rule in `corrections.md`, read before
   writing.
5. **A schedule.** Decide with the user what is re-read and how often: Search Console for decay and
   near-page-one pages (monthly), the AI questions (monthly), `page_check.py` on key pages (after
   each release). If their agent supports scheduled runs, set that up at their request; otherwise
   put the dates in `log.md`.
6. **Verify every publish.** Each changed address opened and confirmed.
7. **Log everything**, failed attempts included, so nothing is done or sent twice.

**Done when** a fresh session, given only the `seo/` folder, can say what was done, what is owed,
and what to do next.

---

## C9 · Track what brings customers

**Aim.** Connect the work to sign-ups and sales, not only to clicks.

1. **Before any change, save the numbers** for the pages it touches (`seo/baseline/<date>/`: the
   Search Console read, and the page as it was), and the date and nature of each edit in `log.md`.
2. **Sales or sign-ups by landing page.** Find where the business records conversions (its
   analytics, its database) and read them by the first page visited. If nothing records it, say
   so: that gap is the first thing to fix, and it is the user's system to change.
3. **Tag links placed elsewhere** (`utm_source`, `utm_medium`, `utm_campaign`) so visits from each
   platform and pitch can be told apart.
4. **For a local business, track calls and bookings** from the profile.

**Leave behind.** `seo/results.md`: per job, the before, the after (with dates), and what it
brought beyond clicks, or "not measurable yet, because".

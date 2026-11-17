# Tier C: reach beyond the site, and the routine

Nine jobs. Each job's title, and the bold words that open each step, are the source post's own.
C1 to C7 carry what the site already knows to other places. C8 and C9 are how the work is kept:
most of them is built into SKILL.md's workspace and should be in place from the first job.

Posting anywhere is the user's act: you draft for each platform, in its format, into `seo/drafts/`;
they post, or tell you to, each time.

---

## C1 · Find timely topics

**Aim.** Be the clear explanation of something that just changed in the buyer's world.

1. **Filter Google Trends by category and country.** Look for rising searches in the field
   (`data-sources.md`).
2. **Check trend history.** A line that rises every year at this time is seasonal: plan for it. A
   spike with no past is news: move now or skip.
3. **Cover relevant rising questions.** The ones that touch what the product does. Leave the rest.
4. **Read the original news announcement.** The law, the release notes, the report, not the
   coverage; say exactly what changed.
5. **Explain news using your expertise.** What only this business knows: what it means in practice
   for the buyer, from experience.
6. **Share the timely finding with relevant reporters.** The ones covering it (A6's rules).

**Facts.** Speed does not lower the bar for accuracy. Date the page; update or retire it when the
moment passes.

---

## C2 · Earn links through tools you use

**Aim.** A customer story on the site of a tool the business really uses.

1. **List software you use.** What the business runs on, and which of those vendors publish
   customer stories.
2. **Document your workflow and result.** What was done with the tool, the before and after, with
   figures the user confirms.
3. **Send the case study to the right editor.** The vendor's customer marketing or content editor,
   as a finished story they can run.

---

## C3 · Claim relevant business listings

**Aim.** The business is present and consistent where buyers and procurement look.

1. **Find eligible supplier directories.** Supplier and partner directories, industry associations,
   marketplaces of the platforms it integrates with.
2. **Complete eligible government profiles.** Procurement registers and local business registers,
   where they apply.
3. **Add your website where allowed.** Wherever a link field exists.
4. **Keep listing details consistent.** The same name, address, description and contact on every
   one. Keep the list in `seo/listings.md` with the date each was last checked.

Each form is submitted by the user or on their word.

---

## C4 · Get customer reviews and independent coverage

**Aim.** Honest third-party evidence where buyers compare products.

1. **Complete G2 and Capterra profiles.** And the other review sites buyers of this kind of product
   use, from `facts.md`.
2. **Ask customers for real reviews.** All of them, the same way, at a natural moment.
3. **Give reviewers access and current facts.** Access to the product, current facts, answers to
   their questions. What they write is theirs.
4. **Answer relevant community questions.** Where people research the purchase, as the business,
   when the answer is useful without the product in it.

**Facts.** No writing reviews for customers, no rewards or discounts in exchange, no asking only
the satisfied ones, no posing as a customer. Review sites' own rules, and consumer-protection
rules in a growing number of countries, treat these as fake or misleading reviews.

---

## C5 · Reuse research across platforms

**Aim.** A finding the site published reaches people who will never search for it.

1. **Turn articles into YouTube demos.** See B4.
2. **Share original findings on Reddit.** In the subreddit where the question is being asked, with
   the evidence in the post itself and within that subreddit's rules.
3. **Answer existing Quora questions.** The ones where the finding is the answer.
4. **Adapt research for Medium or Substack.** Rewritten for those readers, not pasted.
5. **Work with complementary creators.** Ones whose audience has the same problem and no competing
   product.

One finding, rewritten for each place. Say who you are everywhere.

---

## C6 · Publish LinkedIn articles people can find

**Aim.** An article on LinkedIn that ranks for a search LinkedIn already ranks for.

1. **Choose queries LinkedIn already ranks for.** `serp_read.js` over S1's list; look for
   `linkedin.com/pulse` and post addresses in the results.
2. **Put the query early in the headline.**
3. **Check your headline before publishing.** The article's address is made from it.
4. **Lead with an answer and example.** One concrete example.
5. **Link from relevant pages on your site.** So the article is found and read.

---

## C7 · Turn articles into carousels and short videos

**Aim.** The site's answers in the formats social feeds show.

1. **Put one answer on each carousel slide.** In order, so the steps can be followed without the caption.
2. **Write descriptive captions and alt text.** They say what each slide shows.
3. **Cut a product demo into short answers.** One question each.
4. **Show the product or result immediately.** In the first second.
5. **Repeat formats bringing relevant enquiries.** Drop the ones that bring only views.
6. **Offer a related guide at the end.** As the next step.

---

## C8 · Give Claude a repeatable SEO job

**Aim.** The next session, or a scheduled run, picks up where this one stopped and does not repeat
its mistakes. This is the workspace in SKILL.md; the job is to check each piece exists and is used.

1. **Connect Search Console and your CMS.** Here, with no connector: Search Console is reachable in
   the browser (which profile, which property: in `site.md`), and the place pages are edited is
   known (repository path or CMS, and how a change ships).
2. **Save product facts and writing examples.** `facts.md` is current; `voice.md` holds finished
   examples.
3. **Save instructions and finished examples.** For each job done once, its notes in the workspace
   say how it was done here, with the finished output as the example for next time.
4. **Save corrections in the playbook.** Every correction from the user is a dated rule in
   `corrections.md`, read before writing.
5. **Schedule page and citation checks.** Decide with the user what is re-read and how often:
   Search Console for decay and near-page-one pages (monthly), the AI questions (monthly),
   `page_check.py` on key pages (after each release). If their agent supports scheduled runs, set
   that up at their request; otherwise put the dates in `log.md`.
6. **Open each published URL.** Each changed address opened and confirmed.
7. **Log finished jobs and failed attempts.** So nothing is done or sent twice.

**Done when** a fresh session, given only the `seo/` folder, can say what was done, what is owed,
and what to do next.

---

## C9 · Track the actions that produce customers

**Aim.** Connect the work to sign-ups and sales, not only to clicks.

1. **Save starting metrics and page edits.** Before any change: the numbers for the pages it
   touches (`seo/baseline/<date>/`: the Search Console read, and the page as it was), and the date
   and nature of each edit in `log.md`.
2. **Track sales by landing page.** Find where the business records conversions (its analytics, its
   database) and read them by the first page visited. If nothing records it, say so: that gap is
   the first thing to fix, and it is the user's system to change.
3. **Tag distribution links.** `utm_source`, `utm_medium`, `utm_campaign` on links placed
   elsewhere, so visits from each platform and pitch can be told apart.
4. **Track profile calls and bookings.** For a local business, from the profile.

**Leave behind.** `seo/results.md`: per job, the before, the after (with dates), and what it
brought beyond clicks, or "not measurable yet, because".

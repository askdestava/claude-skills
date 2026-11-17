# Tier A: being mentioned and linked

Ten jobs that put the site on other people's pages. All of them end in a message to a stranger.
The same rules hold for every one:

- **Draft, never send.** Each pitch goes to `seo/drafts/outreach/` with the recipient, the page it
  is about and the exact ask. The user sends it, or tells you to.
- **One specific, useful thing per message**: the sentence to add, the broken link and its
  replacement, the finished graphic. Short, true, no flattery, no template feel.
- **Log every pitch** in `seo/outreach.csv` (date, site, page, person, what was offered, status,
  reply) before drafting the next, so nobody is written to twice about the same thing.
- **No payment, no swap as the reason.** A link given because the page is better for it is the
  only kind worth having, and the only kind inside the search engines' rules.

Finding who links where without a paid index is covered in `data-sources.md` (Backlinks). Say in
the report which source a list came from.

---

## A1 · The lists buyers read

**Aim.** The product appears in the "best X" and "X alternatives" pages buyers and AI answers rely on.

1. **Find the roundups** for the category and for each main competitor: `best <category>`,
   `<competitor> alternatives`, `<category> for <who>` (`serp_read.js`). Keep the ones that rank.
2. **Find the ones AI answers cite.** From B3's log: `ai_answers.py report` lists the sources the
   answers link to, and the AI Overview's links are in `serp_read.js` output. A roundup cited there
   is worth more than one that only ranks.
3. **Find the gap in each list**: a buyer need the list does not cover and the product does (a
   price point, a platform, a use, a team size). That is the author's reason to add it.
4. **Bring proof**: a feature tested and shown, a fresh example, a number with its source.
5. **Write the entry for them**: the paragraph as it would appear, in the list's own format and
   length, accurate and plain. Make the edit a paste.
6. **Keep existing entries current.** Where the product is already listed, check price, features
   and screenshots against `facts.md` and send corrections.

**Leave behind.** `seo/lists.md`: each roundup, whether it ranks or is cited, whether the product
is in it, the gap, the pitch's status.

---

## A2 · Recover links already earned

**Aim.** Links and mentions the site has already earned point at pages that work.

1. **Unlinked mentions.** Search for the brand and the product names away from the site
   (`"<brand>" -site:<site>`). Where a page names the brand without linking, ask the editor to link
   the name to the source.
2. **Reused charts, figures and quotes.** Search for a distinctive sentence or figure from the
   site's research. Where it is used without credit, ask for the source link.
3. **Pages with links that no longer exist.** Take Search Console's Links report, top linked pages
   (external), and run the list through `page_check.py --file`. Any linked address that answers 404
   or 410 is a link going nowhere: restore the page if it should exist.
4. **Redirect the rest** to the page that now answers the same thing (301). Not to the home page:
   an unrelated destination is treated as a missing page.

**Lines.** Restoring or redirecting changes live addresses: plan first, then the user's yes.

**Leave behind.** `seo/links/recovered-<date>.md`: the address, who links to it, what was done.

---

## A3 · Links competitors earned

**Aim.** Learn what gets cited in this market, then be the better thing to cite.

1. **Find competitors' most-linked pages** (their research, tools, glossaries, guides): from
   whatever backlink source is available, and from which of their pages other sites and AI answers
   reference.
2. **Read the sentence around each link** on the linking page. Why did the author link: a statistic,
   a definition, a how-to, a tool?
3. **Find what is missing or stale** in the cited page: an old figure, a missing case, no method.
   Build the page that fixes that (S4 for the evidence).
4. **Pitch that one missing answer** to the authors who cited the weaker source: what theirs lacks,
   what yours adds, where it would sit in their page.

---

## A4 · Replace dead and outdated resources

**Aim.** Where the web points at something gone, offer the working replacement.

1. **Find dead pages that still have links**: competitors' or publishers' removed guides, shut-down
   tools, expired studies. Sources: links from roundups and resource pages that answer 404
   (`page_check.py` on the outbound links you collect), and news of tools closing in the category.
2. **Read what was there.** `https://archive.org/wayback/available?url=<address>` gives the saved
   copy. Note what a reader following the link expected.
3. **Publish a true replacement**: the same promise, current and better, on a permanent address.
   Do not copy the archived text.
4. **Tell the editor**: the dead link, where it sits on their page, the working replacement. Two
   sentences.
5. **Guides that name closed tools.** Search for the dead tool's name in "how to" and "best" pages;
   offer the current way to do the same step, with the product where it truly fits.

---

## A5 · Statistics people cite

**Aim.** One piece of original research that writers in the field link to.

1. **Pick a question buyers and writers actually need a number for**, that the site can answer
   from data it holds or can collect honestly.
2. **Produce the numbers**: from the site's records (aggregated, nothing personal), a survey, or a
   systematic count of public data.
3. **State the sample and method** on the page: how many, from where, when, how counted, what is
   excluded. A reader must be able to judge it.
4. **Write each finding as one complete sentence** that still makes sense when quoted alone: the
   sample, the date and the figure in it (the shape is "Of <how many> <things> read in <month>,
   <share> <did what>").
5. **One permanent address.** Update the page when findings change; never move it.
6. **Link the research to the product pages it bears on**, and from them back.

**Lines.** No extrapolating a small sample into a headline. Say what the data cannot show.
Keep the raw counts and the working in `seo/research/<slug>/`.

---

## A6 · Journalists' requests

**Aim.** Quoted, with a link, in articles reporters are writing now.

1. **Make the profile checkable.** The person quoted is real, named, with experience relevant to
   the topic that a reporter can verify (profile page, LinkedIn, past work). Use the user's real
   details only.
2. **Check the request services** the user has accounts on (the source list names Qwoted; there are
   others). They need a sign-in: work in the user's tab once they say so.
3. **Filter** to topics the user truly knows and deadlines that can be met.
4. **Lead with the answer.** The first two sentences are the quote, usable as written.
5. **Add one original number or first-hand example** that only this source has.
6. **Link the research page** that backs it (A5), so the reporter can verify.
7. **Log** each request and reply in `seo/outreach.csv`.

**Lines.** Every reply is in the user's name: they read and send each one. No expertise claimed
that they do not have.

---

## A7 · The visual an article lacks

**Aim.** A graphic made for someone else's article, credited with a link.

1. **Find ranking guides in the field that are walls of text** where a diagram, chart or table
   would carry a section better.
2. **Offer one graphic for one named section**, saying what it would show.
3. **Ask first.** Make it only for authors who say yes.
4. **Use the author's own facts**, checked against their text, so they can trust it.
5. **Send the image with ready embed code** that includes the credit link, sized for their layout.

---

## A8 · A video for someone's article

**Aim.** A short demonstration embedded in a guide that lacks one.

1. **Find how-to guides without a demo** for a task the product (or the user) can show.
2. **Pitch a short video for one section**: what it shows, how long.
3. **Record only after the author agrees.**
4. **Send the finished video with the credit wording** and the embed code.

---

## A9 · Free tools

**Aim.** A small tool that answers a calculation buyers keep doing by hand, on an address worth
linking to.

1. **Find the repeated calculation or check** in the buyer's work: from support, forums and the
   searches containing "calculator", "checker", "generator", "template" in S1's material.
2. **Build it**: one page, one job, no sign-in to see the answer. State the formula or method on
   the page.
3. **Test it** with ordinary inputs, edge inputs (zero, negative, huge, empty, pasted text) and a
   phone. Check the answers by hand.
4. **Give it a permanent address**, linked from the relevant guides and the product page.
5. **Offer it to guides** that walk readers through the same calculation by hand.

**Lines.** The tool must give a right answer. A wrong calculator with links is a liability.

---

## A10 · Editorial links between partners

**Aim.** References between businesses whose readers are served by each other's pages.

1. **Know who the real neighbours are**: partners, integrations, customers, suppliers, communities
   and associations the business belongs to. Start from relationships that already exist.
2. **Link where the surrounding text is about that subject**, on both sides.
3. **Link to the page that answers the reader's question** at that point, not to a home page.
4. **Log** every placement, both directions, in `seo/outreach.csv`.

**The line, stated plainly.** Google's spam policies name "excessive link exchanges" and links
exchanged for their own sake as link schemes, and networks that broker swaps between unrelated
businesses sit on the wrong side of that. Do this job only for links a reader of that page would
thank the author for, between businesses with a real connection, in small numbers. If the only
reason for a link is the link coming back, do not draft it; tell the user why.

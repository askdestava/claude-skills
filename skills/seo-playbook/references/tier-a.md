# Tier A: being mentioned and linked

Ten jobs that put the site on other people's pages. Each job's title, and the bold words that open
each step, are the source post's own. All of them end in a message to a stranger, so the same
working rules hold for every one:

- **Draft; the user sends.** Each pitch goes to `seo/drafts/outreach/` with the recipient, the page
  it is about and the exact ask. The user sends it, or tells you to.
- **One specific, useful thing per message**: the sentence to add, the broken link and its
  replacement, the finished graphic. Short, true, no flattery, no template feel.
- **Log every pitch** in `seo/outreach.csv` (date, site, page, person, what was offered, status,
  reply) before drafting the next, so nobody is written to twice about the same thing.
- **Know what Google's link-spam policy targets**: links bought or sold for ranking, and "excessive
  link exchanges". A link the page is better for is outside it. Say so when a pitch comes close.

Finding who links where without a paid index is covered in `data-sources.md` (Backlinks). Say in
the report which source a list came from.

---

## A1 · Get into the lists buyers read

**Aim.** The product appears in the "best X" and "X alternatives" pages buyers and AI answers rely on.

1. **Find competitor roundups.** For the category and for each main competitor: `best <category>`,
   `<competitor> alternatives`, `<category> for <who>` (`serp_read.js`). Keep the ones that rank.
2. **Check AI's cited roundups.** From B3's log: `ai_answers.py report` lists the sources the
   answers link to, and the AI Overview's links are in `serp_read.js` output. A roundup cited there
   is worth more than one that only ranks.
3. **Find a missing buyer need.** In each list: a need it does not cover and the product does (a
   price point, a platform, a use, a team size). That is the author's reason to add it.
4. **Send a tested feature or fresh example.** Proof for the addition: a feature tested and shown,
   a fresh example, a number with its source.
5. **Send the author your exact addition.** The paragraph as it would appear, in the list's own
   format and length, accurate and plain. Make the edit a paste.
6. **Refresh your roundup entries.** Where the product is already listed, check price, features and
   screenshots against `facts.md` and send corrections.

**Leave behind.** `seo/lists.md`: each roundup, whether it ranks or is cited, whether the product
is in it, the gap, the pitch's status.

---

## A2 · Recover links you already earned

**Aim.** Links and mentions the site has already earned point at pages that work.

1. **Find unlinked brand mentions.** Search for the brand and the product names away from the site
   (`"<brand>" -site:<site>`). Where a page names the brand without linking, ask the editor to link
   the name to the source.
2. **Search for reused charts and quotes.** Search for a distinctive sentence or figure from the
   site's research. Where it is used without credit, ask for the source link.
3. **Restore removed pages with live backlinks.** Take Search Console's Links report, top linked
   pages (external), and run the list through `page_check.py --file`. Any linked address that
   answers 404 or 410 is a link going nowhere: restore the page if it should exist.
4. **Redirect old URLs to equivalent replacements.** The page that now answers the same thing
   (301). Not the home page: an unrelated destination is treated as a missing page.

**Before it ships.** Restoring or redirecting changes live addresses: plan first, then the user's yes.

**Leave behind.** `seo/links/recovered-<date>.md`: the address, who links to it, what was done.

---

## A3 · Find link opportunities through competitors

**Aim.** Learn what gets cited in this market, then be the better thing to cite.

1. **Inspect competitors' linked pages.** Their most-linked pages (research, tools, glossaries,
   guides): from whatever backlink source is available, and from which of their pages other sites
   and AI answers reference.
2. **Read the sentence around each link.** On the linking page: why did the author link, a
   statistic, a definition, a how-to, a tool?
3. **Add missing evidence.** Find what is missing or stale in the cited page (an old figure, a
   missing case, no method) and build the page that fixes that (S4 for the evidence).
4. **Pitch the specific missing answer.** To the authors who cited the weaker source: what theirs
   lacks, what yours adds, where it would sit in their page.

---

## A4 · Replace broken and outdated resources

**Aim.** Where the web points at something gone, offer the working replacement.

1. **Find dead competitor URLs with backlinks.** Competitors' or publishers' removed guides,
   shut-down tools, expired studies. Sources: links from roundups and resource pages that answer
   404 (`page_check.py` on the outbound links you collect), and news of tools closing in the category.
2. **Read archived pages.** `https://archive.org/wayback/available?url=<address>` gives the saved
   copy. Note what a reader following the link expected.
3. **Publish a matching replacement.** The same promise, current and better, on a permanent
   address. Do not copy the archived text.
4. **Send the broken link and replacement.** To the editor: the dead link, where it sits on their
   page, the working replacement. Two sentences.
5. **Find guides naming closed tools.** Search for the dead tool's name in "how to" and "best"
   pages; offer the current way to do the same step, with the product where it truly fits.

---

## A5 · Publish statistics people can cite

**Aim.** One piece of original research that writers in the field link to.

1. **Choose a question your buyers need answered.** One that buyers and writers need a number for,
   and that the site can answer from data it holds or can collect honestly.
2. **Publish original statistics.** Produce the numbers from the site's records (aggregated,
   nothing personal), a survey, or a systematic count of public data.
3. **Explain the sample and method.** On the page: how many, from where, when, how counted, what is
   excluded. A reader must be able to judge it.
4. **Write each finding as a complete sentence.** One that still makes sense when quoted alone: the
   sample, the date and the figure in it (the shape is "Of <how many> <things> read in <month>,
   <share> <did what>").
5. **Keep research URLs stable.** One permanent address. Update the page when findings change;
   never move it.
6. **Link research to relevant product pages.** To the pages it bears on, and from them back.

**Facts.** No extrapolating a small sample into a headline. Say what the data cannot show.
Keep the raw counts and the working in `seo/research/<slug>/`.

---

## A6 · Answer journalist requests

**Aim.** Quoted, with a link, in articles reporters are writing now.

1. **Show real experience in your profile.** The person quoted is real, named, with experience
   relevant to the topic that a reporter can verify (profile page, LinkedIn, past work). Use the
   user's real details only.
2. **Check Qwoted requests.** And the other request services the user has accounts on. They need a
   sign-in: work in the user's tab once they say so.
3. **Filter by topic and deadline.** Topics the user truly knows, deadlines that can be met.
4. **Lead with a direct answer.** The first two sentences are the quote, usable as written.
5. **Add an original number or firsthand example.** One that only this source has.
6. **Include your research page.** The one that backs the answer (A5), so the reporter can verify.
7. **Log requests and replies.** In `seo/outreach.csv`.

**Facts.** Every reply is in the user's name: they read and send each one. No expertise claimed
that they do not have.

---

## A7 · Build the visual an article is missing

**Aim.** A graphic made for someone else's article, credited with a link.

1. **Find text-heavy guides.** Ranking guides in the field where a diagram, chart or table would
   carry a section better than its paragraphs do.
2. **Offer a graphic for a named section.** One graphic, one section, saying what it would show.
3. **Ask before making graphics.** Make it only for authors who say yes.
4. **Use the author's checked facts.** Their own figures, checked against their text, so they can
   trust it.
5. **Send the image and embed code.** Ready embed code that includes the credit link, sized for
   their layout.

---

## A8 · Turn another author's article into a video

**Aim.** A short demonstration embedded in a guide that lacks one.

1. **Find guides missing a demo.** How-to guides for a task the product (or the user) can show.
2. **Pitch a short video for one section.** What it shows, how long.
3. **Record the steps after the author agrees.** Not before.
4. **Send the finished video with source-credit wording.** And the embed code.

---

## A9 · Build free tools that earn links

**Aim.** A small tool that answers a calculation buyers keep doing by hand, on an address worth
linking to.

1. **Find a repeated buyer calculation.** Or a check, in the buyer's work: from support, forums and
   the searches containing "calculator", "checker", "generator", "template" in S1's material.
2. **Ask Claude to build a calculator.** One page, one job, no sign-in to see the answer. State the
   formula or method on the page.
3. **Test normal and unusual inputs.** Ordinary inputs, edge inputs (zero, negative, huge, empty,
   pasted text) and a phone. Check the answers by hand.
4. **Give the tool a permanent page.** Linked from the relevant guides and the product page.
5. **Offer the tool to relevant guides.** The ones that walk readers through the same calculation
   by hand.

**Facts.** The tool must give a right answer. A wrong calculator with links is a liability.

---

## A10 · Exchange relevant editorial links

**Aim.** Editorial links exchanged with businesses whose readers are served by each other's pages.

1. **Join a relevant business network.** One whose members are in or next to the field and place
   editorial links for each other: a link-exchange network that vets its members, a founders' or
   industry community, a partner programme. Count the relationships the business already has too:
   partners, integrations, customers, suppliers.
2. **Match links with the surrounding topic.** A link sits where the text around it is about that
   subject, on both sides of the exchange.
3. **Link to the answer readers need.** The page that answers the reader's question at that point,
   not a home page.
4. **Log published sources and destinations.** Every placement, both directions, in
   `seo/outreach.csv`: where the link sits, where it points, the date, whether it is still live.

**What Google's policy says.** Its spam policies list "excessive link exchanges ('Link to me and
I'll link to you') or partner pages exclusively for the sake of cross-linking" as link spam. Steps
2 and 3 are what keep an exchange out of that: relevant placements a reader would use, in modest
numbers. Tell the user when a network's placements are off-topic or come in bulk.

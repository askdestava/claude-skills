# Tier D: finish

Three small jobs. Each job's title, and the bold words that open each step, are the source post's
own. They rarely move a page that has nothing to say, and they stop a good page from being let
down. `page_check.py` reports the facts for all three.

---

## D1 · Improve search and sharing previews

**Aim.** The line in the results and the card in a chat both say why to open the page.

1. **Write specific meta descriptions.** What the visitor gets and for whom, in a sentence or two.
   `page_check.py` lists pages with none. (Search engines may show other text; a specific
   description is still the best input.)
2. **Match the title and main heading.** They promise the same thing. The checker prints both.
3. **Set a useful sharing image and title.** `og:title` and `og:image`: the checker flags pages
   without them. Open the image address to confirm it loads.

For titles that are shown but not clicked, see S5 step 8 (`gsc.py ctr`).

---

## D2 · Add accurate structured data

**Aim.** Markup that describes the page truthfully and that Google can use.

1. **Add supported structured data.** The types Google supports for this kind of page. Its Search
   Gallery is the current list (article, product, breadcrumb, organization, video, local business,
   job posting and others); types come and go, so check it rather than a memory of it.
2. **Match structured data to visible facts.** Every value matches what is visible on the page. A
   price, rating or date in the markup that the visitor cannot see is a policy violation, not an
   optimisation.
3. **Run Google's Rich Results Test.** First `page_check.py` says whether each JSON-LD block parses
   and what types it declares; then the test on the address (`data-sources.md`) says what is
   eligible and what is invalid.

**Facts.** No review or rating markup for reviews that are not on the page, and no markup of any
type for content the page does not show.

---

## D3 · Remove page friction

**Aim.** Nothing technical between a visitor and the next step.

1. **Compress oversized images.** Serve them at the size they are shown.
2. **Remove unnecessary scripts.** And defer the ones that are not needed to show the page.
3. **Fix broken mobile interactions.** Buttons under the thumb that do not respond, forms that
   zoom, content wider than the screen. Check the main pages in the browser at phone width.
4. **Add llms.txt for compatible agents.** A plain-text index of the site's important pages at
   `/llms.txt`. `page_check.py` reports whether the site has it. It is a convention some tools read,
   not a ranking signal; keep it short and true.

Measure before and after with a Lighthouse run or PageSpeed Insights (`data-sources.md`).

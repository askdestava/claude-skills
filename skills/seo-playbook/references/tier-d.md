# Tier D: finish

Three small jobs. They rarely move a page that has nothing to say, and they stop a good page from
being let down. `page_check.py` reports the facts for all three.

---

## D1 · Search and sharing previews

**Aim.** The line in the results and the card in a chat both say why to open the page.

1. **A meta description written for the page**: what the visitor gets and for whom, in a sentence
   or two. `page_check.py` lists pages with none. (Search engines may show other text; a specific
   description is still the best input.)
2. **The title and the main heading promise the same thing.** The checker prints both.
3. **A sharing title and image** (`og:title`, `og:image`): the checker flags pages without them.
   Open the image address to confirm it loads.

For titles that are shown but not clicked, see S5 step 8 (`gsc.py ctr`).

---

## D2 · Structured data

**Aim.** Markup that describes the page truthfully and that Google can use.

1. **Add the types Google supports for this kind of page.** Its Search Gallery is the current
   list (article, product, breadcrumb, organization, video, local business, job posting and
   others); types come and go, so check it rather than a memory of it.
2. **Every value matches what is visible on the page.** A price, rating or date in the markup that
   the visitor cannot see is a policy violation, not an optimisation.
3. **Test it**: `page_check.py` says whether each JSON-LD block parses and what types it declares;
   then run Google's Rich Results Test on the address (`data-sources.md`) for what is eligible and
   what is invalid.

**Lines.** No review or rating markup for reviews that are not on the page, and no markup of any
type for content the page does not show.

---

## D3 · Page friction

**Aim.** Nothing technical between a visitor and the next step.

1. **Compress oversized images**; serve them at the size they are shown.
2. **Remove scripts that are not used**, and defer the ones that are not needed to show the page.
3. **Fix what is broken on a phone**: buttons under the thumb that do not respond, forms that
   zoom, content wider than the screen. Check the main pages in the browser at phone width.
4. **`llms.txt`**: a plain-text index of the site's important pages at `/llms.txt`, for agents that
   look for one. `page_check.py` reports whether the site has it. It is a convention some tools
   read, not a ranking signal; keep it short and true.

Measure before and after with a Lighthouse run or PageSpeed Insights (`data-sources.md`).

// Reads the table of an open Search Console report out of the page, all rows at once.
//
// Search Console keeps every row of a report in the DOM (up to 1,000 on a Performance tab), whatever
// "Rows per page" shows, and each cell carries its value as a number (data-numeric-value) or a
// string (data-string-value). So one call returns the whole tab: clicks and impressions exact, CTR
// in percent and position to one decimal (gsc.py recomputes CTR from clicks and impressions).
//
// Use: pass this file's text as the `function` of a browser-automation "evaluate script" call
// (Chrome DevTools MCP: evaluate_script, with waitForStableDom false and filePath set to a .json
// in the workspace), on a tab that shows a Search Console report. gsc.py reads the saved file.
//
// Checked on 2026-11-17 on: Performance (queries, pages and days tabs, with and without a
// comparison) and the generative AI features report (pages and days). It reads any Search Console
// page that shows a table (Links, Page indexing) the same way. Returns { error } instead of throwing.
async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const text = (el) => (el ? el.innerText.replace(/\s+/g, ' ').trim() : '');

  if (/\/not-verified/.test(location.pathname)) {
    const who = (document.body.innerText.match(/Signed in as:\s*([^\n]+)/) || [])[1] || null;
    return { error: 'no_access', signed_in_as: who, hint: 'This tab is in a Chrome profile or Google account that cannot see the property. Open the report from a tab that can (see data-sources.md).' };
  }

  // The table arrives after the shell; wait for one that is on screen and has data rows.
  const visibleTables = () =>
    [...document.querySelectorAll('table')].filter((t) => t.offsetParent !== null && t.tBodies.length && t.tBodies[0].rows.length);
  let tables = [];
  for (let i = 0; i < 48 && !tables.length; i++) {
    tables = visibleTables();
    if (!tables.length) await sleep(250);
  }
  if (!tables.length) return { error: 'no_table', url: location.href, hint: 'No table with rows on this page. An empty report, a report still loading, or not a Search Console table page.' };
  await sleep(400); // let the last rows land

  const readTable = (t) => {
    const head = t.tHead && t.tHead.rows.length ? [...t.tHead.rows[t.tHead.rows.length - 1].cells].map(text) : [];
    const labels = [];
    const rows = [...t.tBodies[0].rows].map((r) =>
      [...r.cells].map((c, i) => {
        if (!labels[i]) labels[i] = c.getAttribute('data-label') || '';
        if (c.hasAttribute('data-numeric-value')) return Number(c.getAttribute('data-numeric-value'));
        if (c.hasAttribute('data-string-value')) return c.getAttribute('data-string-value');
        return text(c);
      })
    );
    return { columns: head, labels, rows };
  };

  const params = new URL(location.href).searchParams;
  const account = (document.querySelector('a[aria-label*="Google Account"]') || { getAttribute: () => '' })
    .getAttribute('aria-label')
    .replace(/\s+/g, ' ')
    .trim();
  const main = readTable(tables[0]);
  const out = {
    report: document.title,
    url: location.href,
    property: params.get('resource_id'),
    breakdown: params.get('breakdown'),
    account,
    read_at: new Date().toISOString(),
    columns: main.columns,
    labels: main.labels,
    row_count: main.rows.length,
    rows: main.rows,
  };
  if (tables.length > 1) out.more_tables = tables.slice(1).map(readTable);
  if (main.rows.length >= 1000) out.note = 'Search Console shows at most 1,000 rows per tab. Add a filter (page, query, country) to see the rows below the cut.';
  return out;
}

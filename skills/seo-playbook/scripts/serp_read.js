// Reads a Google results page that is open in the browser: the organic results in order, and which
// other blocks the page carries (AI Overview and the links inside it, questions, videos, forums,
// places, ads, related searches).
//
// Use: open https://www.google.com/search?q=<query>&hl=<lang>&gl=<country>&pws=0, then pass this
// file's text as the `function` of an "evaluate script" call (Chrome DevTools MCP: evaluate_script,
// waitForStableDom false).
//
// Seen on 2026-11-17:
//  - In a signed-in Chrome profile, each result links straight to its page. In a clean context with
//    no Google account, Google wraps every result in its own /goto?url=... redirect, so the page's
//    address is not in the document: `url` is then null, `wrapped` is true, and `site` and `shown`
//    come from the address line Google prints under the title (which it may shorten with "...").
//  - Browser extensions write into the page too: an SEO toolbar's scores showed up inside each
//    result's `snippet` in the signed-in profile. A clean context has no extensions.
//  - Google changes its markup often. This reads by structure (a link that wraps a heading), not by
//    class names, and also returns `headings`: when `organic` comes back empty or short, read those
//    or take a text snapshot of the page instead.
async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const text = (el) => (el ? el.innerText.replace(/\s+/g, ' ').trim() : '');

  if (/\/sorry\//.test(location.pathname) || /unusual traffic/i.test(document.body.innerText)) {
    return { error: 'blocked', hint: 'Google is asking for a CAPTCHA. Stop and ask the user to solve it in the tab. Do not retry in a loop.' };
  }
  if (/consent\.google\./.test(location.hostname) || /Before you continue to Google/i.test(document.body.innerText)) {
    return { error: 'consent', hint: "Google is showing its cookie consent page. Take a snapshot, press the user's choice (Reject all, unless they say otherwise), then run this again." };
  }

  for (let i = 0; i < 20 && !document.querySelector('#search a h3, #rso a h3'); i++) await sleep(250);
  await sleep(600);

  const host = (u) => { try { return new URL(u).hostname.replace(/^www\./, ''); } catch (e) { return ''; } };
  const isGoogle = (u) => /(^|\.)google\.[a-z.]+$/.test(host(u));
  const isAd = (el) => !!el.closest('#tads, #tadsb, #bottomads, [data-text-ad], [aria-label="Ads"]');
  const clean = (u) => u.split('#:~:text=')[0];

  // Organic results: links that wrap an <h3>, outside the ads and the question boxes.
  const seen = new Set();
  const organic = [];
  for (const h3 of document.querySelectorAll('#search a h3, #rso a h3')) {
    const a = h3.closest('a');
    if (!a || isAd(a) || a.closest('[data-q], .related-question-pair')) continue;
    const wrapped = isGoogle(a.href);
    if (wrapped && !/\/goto\?|\/url\?/.test(a.href)) continue; // a link back into Google, not a result
    const key = wrapped ? text(h3) : clean(a.href);
    if (seen.has(key)) continue;
    seen.add(key);
    // The result's box: the largest ancestor that still holds only this one titled link.
    let box = a;
    for (let i = 0; i < 6 && box.parentElement && box.parentElement.querySelectorAll('a h3').length === 1; i++) box = box.parentElement;
    // The address line under the title: "https://example.com › guides › topic". Forum results
    // carry other <cite> lines too ("3 comments · 3 years ago"), so take the one that is an address.
    const shown = [...box.querySelectorAll('cite')].map(text).find((t) => /^(https?:\/\/)?[\w-]+(\.[\w-]+)+/.test(t)) || '';
    const title = text(h3);
    organic.push({
      position: organic.length + 1,
      title,
      url: wrapped ? null : clean(a.href),
      wrapped,
      site: wrapped ? host(/^https?:/.test(shown) ? shown.split(' ')[0] : 'https://' + shown.split(' ')[0]) : host(a.href),
      shown,
      snippet: text(box).replace(title, '').replace(shown, '').trim().slice(0, 320),
    });
  }

  // The AI Overview: the nearest block around its heading that carries the answer's text.
  const headingEls = [...document.querySelectorAll('[role=heading], h1, h2')];
  let overview = null;
  const oh = headingEls.find((e) => /^AI Overview$/i.test(text(e)));
  if (oh) {
    let box = oh;
    while (box.parentElement && box.innerText.length < 200 && !box.parentElement.querySelector('a h3')) box = box.parentElement;
    const links = [];
    const got = new Set();
    for (const a of box.querySelectorAll('a[href]')) {
      if (!/^https?:/.test(a.href) || isGoogle(a.href) || isAd(a)) continue;
      const u = clean(a.href).replace(/[?&](sa|ved|usg)=[^&]*/g, '');
      if (got.has(u)) continue;
      got.add(u);
      links.push({ url: u, site: host(u), label: text(a).slice(0, 80) });
    }
    overview = { text: text(box).replace(/^AI Overview\s*/i, '').slice(0, 2500), links, wrapped_links: box.querySelectorAll('a[href*="/goto?"]').length };
  }

  const headings = [...new Set(headingEls.map(text).filter((t) => t && t.length < 110))];
  const asked = [...document.querySelectorAll('[data-q]')].map((e) => e.getAttribute('data-q')).filter(Boolean);
  const questions = [...new Set([...asked, ...headings.filter((h) => /\?$/.test(h))])].filter((t) => t.length > 8 && /[^\d\s]/.test(t));
  const related = [...new Set([...document.querySelectorAll('#botstuff a[href*="/search?"], #bres a[href*="/search?"]')].map(text))]
    .filter((t) => t && t.length < 90 && !/^\d+$/.test(t) && !/^next$/i.test(t));
  const ads = [...new Set([...document.querySelectorAll('#tads a [role=heading], #tads a h3, [data-text-ad] [role=heading]')].map(text))]
    .filter((t) => t && !/^(sponsored results?|my ad center)$/i.test(t));
  const videos = [...new Set([...document.querySelectorAll('a[href*="youtube.com/watch"]')].map((a) => a.href.split('&')[0]))];
  const forumSite = /(^|\.)(reddit|quora)\.com$|stackexchange\.com$|stackoverflow\.com$/;
  const has = (re) => headings.some((h) => re.test(h));

  const q = new URL(location.href).searchParams;
  return {
    query: q.get('q'),
    country: q.get('gl'),
    language: q.get('hl'),
    read_at: new Date().toISOString(),
    signed_in: !!document.querySelector('a[aria-label*="Google Account"]'),
    organic,
    blocks: {
      ai_overview: overview,
      questions,
      videos: videos.slice(0, 10),
      forums: [...new Set(organic.filter((r) => forumSite.test(r.site)).map((r) => r.site))],
      forum_block: has(/^Discussions and forums$/i),
      places: has(/^Places$|^Businesses$/i),
      ads: ads.slice(0, 8),
      related_searches: related.slice(0, 12),
    },
    headings: headings.slice(0, 40),
  };
}

// Reads an AI assistant's answer off the page it was asked on: the answer's text once it has stopped
// streaming, and every outside link in it (the sources it cites or sends people to).
//
// It knows nothing about any one assistant. It waits for the page's text to stop growing, then takes
// the main region's text and the links that leave the assistant's own site. That is what keeps it
// working across assistants and across their redesigns.
//
// Use: ask the question in the assistant's page first (see references/data-sources.md), then pass
// this file's text as the `function` of an "evaluate script" call (Chrome DevTools MCP:
// evaluate_script, waitForStableDom false; set filePath to keep the answer). Which brands the answer
// names is the agent's reading of `answer`, not this script's: ai_answers.py records it.
async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const region = () => document.querySelector('main, [role=main]') || document.body;

  // Streaming is over when the text has not grown for 3 seconds (give up after 90).
  let last = -1, still = 0;
  for (let i = 0; i < 180 && still < 6; i++) {
    const n = region().innerText.length;
    still = n === last ? still + 1 : 0;
    last = n;
    await sleep(500);
  }

  const own = location.hostname.replace(/^www\./, '').split('.').slice(-2).join('.');
  const host = (u) => { try { return new URL(u).hostname.replace(/^www\./, ''); } catch (e) { return ''; } };
  const seen = new Set();
  const sources = [];
  let wrapped = 0;
  for (const a of region().querySelectorAll('a[href]')) {
    if (!/^https?:/.test(a.href)) continue; // a.href is the resolved address, so relative links count too
    let url = a.href.split('#:~:text=')[0];
    if (host(url).endsWith(own)) {
      // A link through the assistant's own redirect: keep it only when the target is readable.
      const target = ['url', 'q', 'u', 'target'].map((k) => new URL(url).searchParams.get(k)).find((v) => v && /^https?:/.test(v));
      if (!target) {
        if (/\/(goto|url|link|redirect)\b/.test(new URL(url).pathname)) wrapped++;
        continue;
      }
      url = target;
    }
    url = url.replace(/([?&])utm_[a-z]+=[^&]*&?/g, '$1').replace(/[?&]$/, '');
    if (seen.has(url)) continue;
    seen.add(url);
    sources.push({ url, site: host(url), label: a.innerText.replace(/\s+/g, ' ').trim().slice(0, 80) });
  }

  const text = region().innerText.replace(/\n{3,}/g, '\n\n').trim();
  // A short page that talks about signing in or proving you are human is a wall, not an answer.
  const wall = text.length < 1500 && /sign (in|up)|log in|verify you are human|unusual activity|captcha/i.test(text);
  return {
    engine: own,
    url: location.href,
    read_at: new Date().toISOString(),
    settled: still >= 6,
    wall,
    answer: text.slice(0, 12000),
    answer_chars: text.length,
    sources,
    wrapped_links: wrapped,
  };
}

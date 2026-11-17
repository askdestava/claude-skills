#!/usr/bin/env python3
"""What a crawler is handed at a URL, as facts. Python 3.8+, standard library only.

For each URL: the redirect chain and final status, whether robots.txt lets each crawler in, the
robots directives (header and meta), the canonical, title, description, headings, the sharing
preview tags, every JSON-LD block (does it parse, which types), how much text is in the HTML before
any script runs, and the links. Per site: robots.txt, the sitemaps it names, llms.txt.

It reads the HTML the server sends. It does not run JavaScript: compare `words in the HTML` here with
the page in a browser to see what only appears after scripts run.

Examples:
  page_check.py https://example.com/pricing https://example.com/blog/post
  page_check.py --file urls.txt --json > seo/checks/2026-11-17.json
  page_check.py --sitemap https://example.com/sitemap.xml --match '/blog/' --limit 30
  page_check.py https://example.com/ --as googlebot      # what the server sends that crawler's name
"""
import argparse
import gzip
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from html.parser import HTMLParser

NAME = 'seo-playbook-page-check/1.0 (+https://github.com/askdestava/claude-skills)'
AGENTS = {
    'default': 'Mozilla/5.0 (compatible; %s)' % NAME,
    'browser': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'googlebot': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'bingbot': 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
    'gptbot': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.2; +https://openai.com/gptbot',
}
# Crawlers whose robots.txt answer is reported. Search engines first, then the AI crawlers.
# Change with --crawlers; the names are the tokens each one documents for robots.txt.
CRAWLERS = ['Googlebot', 'Bingbot', 'GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'PerplexityBot', 'Google-Extended']
SKIP_TEXT = {'script', 'style', 'noscript', 'template', 'svg', 'head'}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def fetch(url, ua, timeout=20, limit=3_000_000):
    """One request, no redirect following. -> (status, headers dict lower-cased, body bytes, seconds)"""
    req = urllib.request.Request(url, headers={'User-Agent': ua, 'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
                                               'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en'})
    t0 = time.time()
    try:
        resp = OPENER.open(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        resp = e
    except Exception as e:  # DNS, TLS, timeout
        return 0, {'error': '%s: %s' % (type(e).__name__, e)}, b'', time.time() - t0
    headers = {}
    for k, v in resp.headers.items():
        k = k.lower()
        headers[k] = headers[k] + ', ' + v if k in headers else v
    try:
        body = resp.read(limit)
    except Exception:
        body = b''
    enc = headers.get('content-encoding', '').lower()
    try:
        if 'gzip' in enc:
            body = gzip.decompress(body)
        elif 'deflate' in enc:
            body = zlib.decompress(body) if body[:1] == b'x' else zlib.decompress(body, -zlib.MAX_WBITS)
    except Exception:
        pass
    return resp.getcode() or 0, headers, body, time.time() - t0


def follow(url, ua, max_hops=10):
    chain = []
    for _ in range(max_hops):
        status, headers, body, secs = fetch(url, ua)
        chain.append({'url': url, 'status': status})
        loc = headers.get('location')
        if status in (301, 302, 303, 307, 308) and loc:
            url = urllib.parse.urljoin(url, loc)
            continue
        return chain, status, headers, body, secs
    return chain, 0, {'error': 'more than %d redirects' % max_hops}, b'', 0.0


def decode(body, headers):
    m = re.search(r'charset=([\w-]+)', headers.get('content-type', ''), re.I)
    charsets = [m.group(1)] if m else []
    m = re.search(rb'<meta[^>]+charset=["\']?([\w-]+)', body[:4096], re.I)
    if m:
        charsets.append(m.group(1).decode('ascii', 'ignore'))
    for cs in charsets + ['utf-8']:
        try:
            return body.decode(cs)
        except (LookupError, UnicodeDecodeError):
            continue
    return body.decode('utf-8', 'replace')


# ---- robots.txt, read the way Google documents it: the most specific user-agent group applies,
# ---- the longest matching rule wins, Allow wins a tie, * is any run of characters, $ ends the path.

def parse_robots(text):
    groups, sitemaps = [], []
    agents, rules, last_was_agent = [], [], False
    for raw in text.splitlines():
        line = raw.split('#', 1)[0].strip()
        if ':' not in line:
            continue
        field, value = [p.strip() for p in line.split(':', 1)]
        field = field.lower()
        if field == 'sitemap':
            sitemaps.append(value)
        elif field == 'user-agent':
            if not last_was_agent and (agents or rules):
                groups.append((agents, rules))
                agents, rules = [], []
            agents.append(value.lower())
            last_was_agent = True
        elif field in ('allow', 'disallow'):
            if agents:
                rules.append((field, value))
            last_was_agent = False
        else:
            last_was_agent = False
    if agents or rules:
        groups.append((agents, rules))
    return groups, sitemaps


def robots_allows(groups, crawler, path):
    """-> (allowed, the rule that decided it or None)"""
    token = crawler.lower()
    best, rules = -1, []
    for agents, grules in groups:
        for a in agents:
            score = len(a) if a != '*' and token.startswith(a) else (0 if a == '*' else -1)
            if score > best:
                best, rules = score, list(grules)
            elif score == best and score >= 0:
                rules += grules  # groups for the same agent are read as one
    winner, win_len = None, -1
    for kind, pattern in rules:
        if pattern == '':
            continue  # "Disallow:" with nothing after it blocks nothing
        rx = '^' + ''.join('.*' if ch == '*' else re.escape(ch) for ch in pattern.rstrip('$')) + ('$' if pattern.endswith('$') else '')
        if re.match(rx, path):
            n = len(pattern)
            if n > win_len or (n == win_len and kind == 'allow'):
                winner, win_len = (kind, pattern), n
    if not winner:
        return True, None
    return winner[0] == 'allow', '%s: %s' % (winner[0].capitalize(), winner[1])


# ---- the page

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.h1, self.metas, self.links_rel, self.anchors = '', [], [], [], []
        self.jsonld, self.images, self.lang, self.scripts = [], [], '', 0
        self._stack, self._capture, self._buf, self._text = [], None, [], []
        self._anchor = None

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or '') for k, v in attrs}
        if tag in ('br', 'img', 'meta', 'link', 'input', 'hr', 'source', 'area', 'base', 'col', 'embed', 'wbr'):
            pass
        else:
            self._stack.append(tag)
        if tag == 'html':
            self.lang = a.get('lang', '')
        elif tag == 'title' and not self.title and 'svg' not in self._stack:
            self._capture, self._buf = 'title', []
        elif tag == 'h1':
            self._capture, self._buf = 'h1', []
        elif tag == 'meta':
            self.metas.append(a)
        elif tag == 'link':
            self.links_rel.append(a)
        elif tag == 'a' and a.get('href'):
            self._anchor = {'href': a['href'], 'rel': a.get('rel', '').lower(), 'text': []}
        elif tag == 'img':
            self.images.append(a)
            if self._anchor is not None and a.get('alt'):
                self._anchor['text'].append(a['alt'])
        elif tag == 'script':
            self.scripts += 1
            if 'ld+json' in a.get('type', '').lower():
                self._capture, self._buf = 'jsonld', []

    def handle_endtag(self, tag):
        if tag in self._stack:
            while self._stack and self._stack.pop() != tag:
                pass
        if self._capture == 'title' and tag == 'title':
            self.title, self._capture = ' '.join(''.join(self._buf).split()), None
        elif self._capture == 'h1' and tag == 'h1':
            self.h1.append(' '.join(''.join(self._buf).split()))
            self._capture = None
        elif self._capture == 'jsonld' and tag == 'script':
            self.jsonld.append(''.join(self._buf))
            self._capture = None
        if tag == 'a' and self._anchor is not None:
            self._anchor['text'] = ' '.join(' '.join(self._anchor['text']).split())
            self.anchors.append(self._anchor)
            self._anchor = None

    def handle_data(self, data):
        if self._capture:
            self._buf.append(data)
            if self._capture == 'jsonld':
                return
        if self._anchor is not None:
            self._anchor['text'].append(data)
        if not SKIP_TEXT.intersection(self._stack):
            self._text.append(data)

    def words(self):
        return len(' '.join(self._text).split())


def meta(page, **want):
    key, val = next(iter(want.items()))
    for m in page.metas:
        if m.get(key, '').lower() == val:
            return m.get('content', '').strip()
    return ''


def ld_types(node, out):
    if isinstance(node, list):
        for n in node:
            ld_types(n, out)
    elif isinstance(node, dict):
        t = node.get('@type')
        for one in (t if isinstance(t, list) else [t]):
            if isinstance(one, str):
                out.append(one)
        ld_types(node.get('@graph', []), out)


def norm(u):
    p = urllib.parse.urlsplit(u)
    return urllib.parse.urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path or '/', p.query, ''))


SITE_CACHE = {}


def site_facts(url, ua):
    p = urllib.parse.urlsplit(url)
    root = '%s://%s' % (p.scheme, p.netloc)
    if root in SITE_CACHE:
        return SITE_CACHE[root]
    chain, status, headers, body, _ = follow(root + '/robots.txt', ua)
    groups, sitemaps = parse_robots(decode(body, headers)) if status == 200 else ([], [])
    _, llms_status, llms_headers, llms_body, _ = follow(root + '/llms.txt', ua)
    is_text = llms_status == 200 and 'html' not in llms_headers.get('content-type', '').lower() and not llms_body.lstrip()[:15].lower().startswith(b'<!doctype')
    SITE_CACHE[root] = {'root': root, 'robots_status': status, 'robots_groups': groups, 'sitemaps': sitemaps,
                        'llms_txt': 'yes' if is_text else ('no (%s)' % (llms_status or 'unreachable') if llms_status != 200 else 'no (the address answers with a web page)')}
    return SITE_CACHE[root]


def check(url, ua, crawlers):
    site = site_facts(url, ua)
    chain, status, headers, body, secs = follow(url, ua)
    final = chain[-1]['url']
    out = {'url': url, 'final_url': final, 'status': status, 'redirects': chain[:-1], 'seconds': round(secs, 2),
           'bytes': len(body), 'content_type': headers.get('content-type', ''), 'issues': []}
    issue = out['issues'].append
    if 'error' in headers:
        issue('could not be fetched: ' + headers['error'])
        return out
    path = urllib.parse.urlsplit(final)
    path = (path.path or '/') + ('?' + path.query if path.query else '')
    out['robots_txt'] = {}
    for c in crawlers:
        ok, rule = robots_allows(site['robots_groups'], c, path)
        out['robots_txt'][c] = 'allowed' if ok else 'blocked by "%s"' % rule
    if len(chain) > 2:
        issue('%d redirects before the page (%s)' % (len(chain) - 1, ' -> '.join(str(c['status']) for c in chain)))
    if status != 200:
        issue('answers %s, not 200' % status)
    if out['robots_txt'].get(crawlers[0], 'allowed') != 'allowed':
        issue('robots.txt blocks %s: %s' % (crawlers[0], out['robots_txt'][crawlers[0]]))
    xr = headers.get('x-robots-tag', '')
    out['x_robots_tag'] = xr
    if 'html' not in out['content_type'].lower() or not body:
        return out

    page = Page()
    try:
        page.feed(decode(body, headers))
    except Exception as e:
        issue('the HTML could not be read to the end: %s' % e)
    robots_meta = ', '.join(v for v in (meta(page, name='robots'), meta(page, name='googlebot')) if v)
    out['meta_robots'] = robots_meta
    if re.search(r'noindex|none', (xr + ' ' + robots_meta).lower()):
        issue('noindex (%s)' % ('header' if re.search(r'noindex|none', xr.lower()) else 'meta tag'))
    canon = next((l.get('href', '') for l in page.links_rel if 'canonical' in l.get('rel', '').lower().split()), '')
    out['canonical'] = urllib.parse.urljoin(final, canon) if canon else ''
    if not canon:
        issue('no canonical link')
    elif norm(out['canonical']) != norm(final):
        issue('canonical points to another address: %s' % out['canonical'])
    out['title'] = page.title
    out['description'] = meta(page, name='description')
    out['h1'] = page.h1
    if not page.title:
        issue('no <title>')
    if not out['description']:
        issue('no meta description')
    if not page.h1:
        issue('no <h1> in the HTML')
    elif len(page.h1) > 1:
        issue('%d <h1> headings' % len(page.h1))
    out['preview'] = {'og:title': meta(page, property='og:title'), 'og:description': meta(page, property='og:description'),
                      'og:image': meta(page, property='og:image'), 'twitter:card': meta(page, name='twitter:card')}
    for k in ('og:title', 'og:image'):
        if not out['preview'][k]:
            issue('no %s (the link preview has nothing to show)' % k)
    out['structured_data'] = []
    for raw in page.jsonld:
        try:
            types = []
            ld_types(json.loads(raw), types)
            out['structured_data'].append({'types': types})
        except ValueError as e:
            out['structured_data'].append({'error': str(e)})
            issue('a JSON-LD block does not parse: %s' % e)
    out['lang'] = page.lang
    out['hreflang'] = sum(1 for l in page.links_rel if l.get('hreflang'))
    out['words_in_html'] = page.words()
    out['scripts'] = page.scripts
    if out['words_in_html'] < 50 and page.scripts:
        issue('only %d words in the HTML before scripts run: the content may exist only after JavaScript' % out['words_in_html'])
    host = urllib.parse.urlsplit(final).netloc.lower()
    internal, external = [], 0
    for a in page.anchors:
        href = urllib.parse.urljoin(final, a['href'])
        parts = urllib.parse.urlsplit(href)
        if parts.scheme not in ('http', 'https'):
            continue
        if parts.netloc.lower() == host:
            internal.append({'href': norm(href), 'text': a['text'], 'nofollow': 'nofollow' in a['rel']})
        else:
            external += 1
    out['links'] = {'internal': len(internal), 'external': external, 'internal_list': internal}
    out['images'] = {'count': len(page.images), 'without_alt': sum(1 for i in page.images if not i.get('alt', '').strip())}
    return out


def sitemap_urls(url, ua, limit, match):
    """Reads a sitemap or a sitemap index (gzip too). Stops at `limit` page addresses."""
    rx = re.compile(match) if match else None
    out, todo, seen = [], [url], set()
    while todo and len(out) < limit:
        sm = todo.pop(0)
        if sm in seen:
            continue
        seen.add(sm)
        _, status, headers, body, _ = follow(sm, ua)
        if status != 200:
            print('sitemap %s answered %s' % (sm, status), file=sys.stderr)
            continue
        if body[:2] == b'\x1f\x8b':
            body = gzip.decompress(body)
        text = body.decode('utf-8', 'replace')
        locs = [re.sub(r'<!\[CDATA\[|\]\]>', '', l).strip() for l in re.findall(r'<loc>(.*?)</loc>', text, re.S)]
        if '<sitemapindex' in text:
            todo += locs
        else:
            for l in locs:
                if (not rx or rx.search(l)) and len(out) < limit:
                    out.append(l)
    return out


def short(s, n):
    s = ' '.join(str(s).split())
    return s if len(s) <= n else s[:n - 1] + '…'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('urls', nargs='*')
    ap.add_argument('--file', help='a text file of addresses, one a line')
    ap.add_argument('--sitemap', help='take the addresses from this sitemap (or sitemap index)')
    ap.add_argument('--match', help='with --sitemap: keep addresses matching this regular expression')
    ap.add_argument('--limit', type=int, default=25, help='with --sitemap: how many addresses to check (default 25)')
    ap.add_argument('--as', dest='agent', default='default', help='whose name to send: %s, or a full User-Agent string' % ', '.join(AGENTS))
    ap.add_argument('--crawlers', default=','.join(CRAWLERS), help='robots.txt tokens to answer for, comma separated; the first one raises an issue when blocked')
    ap.add_argument('--delay', type=float, default=0.3, help='seconds between pages (default 0.3)')
    ap.add_argument('--json', action='store_true', help='print everything as JSON (includes each page\'s internal links)')
    args = ap.parse_args()

    ua = AGENTS.get(args.agent.lower(), args.agent)
    urls = list(args.urls)
    if args.file:
        with open(args.file, encoding='utf-8') as f:
            urls += [l.strip() for l in f if l.strip() and not l.startswith('#')]
    if args.sitemap:
        urls += sitemap_urls(args.sitemap, ua, args.limit, args.match)
    if not urls:
        ap.print_help()
        return 2
    crawlers = [c.strip() for c in args.crawlers.split(',') if c.strip()]
    results = []
    for i, u in enumerate(urls):
        if not re.match(r'https?://', u):
            u = 'https://' + u
        if i:
            time.sleep(args.delay)
        results.append(check(u, ua, crawlers))
    sites = [{k: v for k, v in s.items() if k != 'robots_groups'} for s in SITE_CACHE.values()]

    if args.json:
        json.dump({'checked_as': ua, 'sites': sites, 'pages': results}, sys.stdout, indent=1)
        print()
        return 0

    print('Checked as: %s\n' % ua)
    for s in sites:
        print('**%s**: robots.txt %s; sitemaps named in it: %s; llms.txt: %s'
              % (s['root'], s['robots_status'], ', '.join(s['sitemaps']) or 'none', s['llms_txt']))
    print('\n| Page | Status | Words in HTML | Title | H1 | Structured data | Internal links | Issues |')
    print('|---|---|---|---|---|---|---|---|')
    for r in results:
        types = ', '.join(sorted({t for b in r.get('structured_data', []) for t in b.get('types', [])})) or '-'
        print('| %s | %s | %s | %s | %s | %s | %s | %d |' % (
            r['url'], r['status'], r.get('words_in_html', '-'), short(r.get('title', ''), 48).replace('|', '\\|') or '-',
            short('; '.join(r.get('h1', [])), 40).replace('|', '\\|') or '-', short(types, 40), r.get('links', {}).get('internal', '-'), len(r['issues'])))
    flagged = [r for r in results if r['issues']]
    if flagged:
        print('\n### Issues')
        for r in flagged:
            print('- %s' % r['url'])
            for i in r['issues']:
                print('  - %s' % i)
    blocked = {}
    for r in results:
        for c, v in r.get('robots_txt', {}).items():
            if v != 'allowed':
                blocked.setdefault(c, []).append(r['url'])
    if blocked:
        print('\n### robots.txt')
        for c, us in blocked.items():
            print('- %s is blocked on %d of %d pages (first: %s)' % (c, len(us), len(results), us[0]))
    else:
        print('\nrobots.txt lets every crawler asked about into every page: %s.' % ', '.join(crawlers))
    return 1 if flagged else 0


if __name__ == '__main__':
    sys.exit(main())

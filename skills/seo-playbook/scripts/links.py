#!/usr/bin/env python3
"""The site's internal links, counted. Python 3.8+, standard library only (uses page_check.py beside it).

  crawl    fetch a set of the site's pages and save who links to whom, with the linked words
  report   from that file: pages nothing links to, the most and least linked, links that sit on
           most pages (menu, footer, template), linked words that repeat or point to several places,
           and, given Search Console data, pages near page one that few pages link to

Counts cover the pages crawled, and the links present in the HTML before scripts run. Say both
when you report them.

Examples:
  links.py crawl --sitemap https://example.com/sitemap.xml --limit 300 --out seo/links/graph.json
  links.py crawl --sitemap https://example.com/sitemap.xml --match '/blog/' --out graph.json
  links.py report seo/links/graph.json
  links.py report graph.json --near seo/gsc/pages.json
"""
import argparse
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page_check as pc  # noqa: E402


def key(u):
    """One address per page: no fragment, no trailing slash (except the root)."""
    u = pc.norm(u)
    return u[:-1] if u.endswith('/') and u.count('/') > 3 else u


def crawl(args):
    ua = pc.AGENTS.get(args.agent.lower(), args.agent)
    urls = []
    if args.file:
        with open(args.file, encoding='utf-8') as f:
            urls += [l.strip() for l in f if l.strip() and not l.startswith('#')]
    if args.sitemap:
        urls += pc.sitemap_urls(args.sitemap, ua, args.limit, args.match)
    urls = list(dict.fromkeys(urls))[:args.limit]
    if not urls:
        sys.exit('No addresses to crawl: give --sitemap or --file.')
    pages = {}
    for i, u in enumerate(urls):
        if i:
            time.sleep(args.delay)
        r = pc.check(u, ua, ['Googlebot'])
        pages[key(r['final_url'])] = {
            'status': r['status'], 'title': r.get('title', ''), 'words': r.get('words_in_html', 0),
            'noindex': any(i.startswith('noindex') for i in r['issues']),
            'out': [{'to': key(l['href']), 'text': l['text'], 'nofollow': l['nofollow']} for l in r.get('links', {}).get('internal_list', [])],
        }
        if (i + 1) % 25 == 0:
            print('%d of %d pages' % (i + 1, len(urls)), file=sys.stderr)
    graph = {'crawled_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'checked_as': ua,
             'source': args.sitemap or args.file, 'match': args.match, 'pages': pages}
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=1)
    print('Saved %d pages to %s' % (len(pages), args.out))
    report_graph(graph, args.rows, args.near, args.template_share)


def table(headers, rows):
    if not rows:
        return '(none)'
    out = ['| ' + ' | '.join(headers) + ' |', '|' + '|'.join(['---'] * len(headers)) + '|']
    out += ['| ' + ' | '.join(str(c).replace('|', '\\|') for c in r) + ' |' for r in rows]
    return '\n'.join(out)


def report_graph(graph, limit=25, near_file=None, share=0.5):
    pages = graph['pages']
    n = len(pages)
    good = {u for u, p in pages.items() if p['status'] == 200}
    sources = defaultdict(set)         # target -> pages linking to it
    words = defaultdict(Counter)       # target -> linked words -> count
    word_targets = defaultdict(set)    # linked words -> targets
    for src, p in pages.items():
        for l in p['out']:
            if l['to'] == src:
                continue
            sources[l['to']].add(src)
            t = ' '.join(l['text'].lower().split())
            words[l['to']][t] += 1
            if t:
                word_targets[t].add(l['to'])

    # A link that sits on half the pages or more belongs to the template (menu, footer, sidebar),
    # not to what one page says. Those are listed once and left out of the other tables.
    sitewide = {t for t, s in sources.items() if n >= 10 and len(s) >= share * n}
    no_links = [u for u in good if not pages[u]['out']]

    print('\n## Internal links')
    print('%d pages crawled (%s), %d answered 200. Counts are links between these pages only, as found in the HTML before scripts run.'
          % (n, graph.get('crawled_at', ''), len(good)))
    if no_links:
        print('%d of them have no internal link in their HTML at all (first: %s). If the browser shows links there, they are added by JavaScript.'
              % (len(no_links), sorted(no_links)[0]))

    print('\n### In the template (linked from %d%% of these pages or more: menu, footer, sidebar): %d addresses' % (round(share * 100), len(sitewide)))
    print(table(['Address', 'Pages linking', 'Crawled here'], [[t, len(sources[t]), 'yes' if t in pages else 'no'] for t in sorted(sitewide, key=lambda t: -len(sources[t]))[:limit]]))

    orphans = sorted(u for u in good if not sources.get(u))
    print('\n### Nothing links here: %d pages' % len(orphans))
    print(table(['Address', 'Title'], [[u, pages[u]['title'][:70]] for u in orphans[:limit]]))

    inbound = sorted(((len(sources.get(u, ())), u) for u in good if u not in sitewide), key=lambda x: (x[0], x[1]))
    few = [(c, u) for c, u in inbound if 0 < c <= 2]
    print('\n### Linked from one or two pages: %d pages' % len(few))
    print(table(['Address', 'Pages linking', 'Linked words'], [[u, c, '; '.join(w or '(no words)' for w, _ in words[u].most_common(3))] for c, u in few[:limit]]))

    print('\n### Most linked (template links left out)')
    print(table(['Address', 'Pages linking', 'Different linked words', 'Most used words'],
                [[u, c, len(words[u]), '; '.join('%s (%d)' % (w or '(no words)', k) for w, k in words[u].most_common(3))] for c, u in sorted(inbound, reverse=True)[:min(limit, 15)]]))

    same = sorted(((sum(c.values()), u, c.most_common(1)[0]) for u, c in words.items() if u not in sitewide and len(c) == 1 and sum(c.values()) >= 5), reverse=True)
    print('\n### Always linked with the same words (5 links or more): %d addresses' % len(same))
    print(table(['Address', 'Links', 'The words'], [[u, k, w or '(no words)'] for k, u, (w, _) in same[:limit]]))

    shared = sorted(((len(ts), w) for w, ts in word_targets.items() if len(ts) >= 3), reverse=True)
    print('\n### The same words pointing to three or more addresses: %d' % len(shared))
    print(table(['Linked words', 'Addresses'], [[w, c] for c, w in shared[:min(limit, 20)]]))

    empty = sorted(((c[''], u) for u, c in words.items() if c.get('')), reverse=True)
    if empty:
        print('\n### Links with no words (an image without alt text, or an empty link): %d addresses' % len(empty))
        print(table(['Address', 'Such links'], [[u, k] for k, u in empty[:10]]))

    outside = sorted(((len(s), t) for t, s in sources.items() if t not in pages and t not in sitewide), reverse=True)
    print('\n### Linked but not crawled here: %d addresses (top by pages linking)' % len(outside))
    print(table(['Address', 'Pages linking'], [[t, c] for c, t in outside[:10]]))

    if near_file:
        import gsc
        (columns, rows), src = gsc.load(near_file, 'pages')
        recs, _ = gsc.to_records(columns, rows)
        near = [r for r in recs if 8 <= r['position'] <= 20 and r['impressions'] >= 20]
        near.sort(key=lambda r: -r['impressions'])
        out = []
        for r in near:
            u = key(r['key'])
            out.append([r['key'], gsc.fmt(r['position'], 1), gsc.fmt(r['impressions']),
                        len(sources.get(u, ())) if u in pages or u in sources else 'not crawled'])
        print('\n### Near page one (position 8 to 20, 20 impressions or more) and how many pages link to each')
        print('From %s. Fewest links first is where a link from an established page helps most.' % src)
        out.sort(key=lambda r: (r[3] if isinstance(r[3], int) else 10**6))
        print(table(['Page', 'Position', 'Impressions', 'Pages linking'], out[:limit]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd')
    c = sub.add_parser('crawl', help='fetch pages, save the link graph, print the report')
    c.add_argument('--sitemap', help='a sitemap or sitemap index to take addresses from')
    c.add_argument('--file', help='or a text file of addresses, one a line')
    c.add_argument('--match', help='keep sitemap addresses matching this regular expression')
    c.add_argument('--limit', type=int, default=200, help='pages to crawl (default 200)')
    c.add_argument('--delay', type=float, default=0.3, help='seconds between pages (default 0.3)')
    c.add_argument('--as', dest='agent', default='default', help='whose name to send (see page_check.py)')
    c.add_argument('--out', required=True, help='where to save the graph (.json)')
    r = sub.add_parser('report', help='report from a saved graph')
    r.add_argument('graph')
    for p in (c, r):
        p.add_argument('--near', help='Search Console pages data to join: a gsc_read.js .json, the export .zip, or Pages.csv')
        p.add_argument('--rows', type=int, default=25, help='rows per table in the report (default 25)')
        p.add_argument('--template-share', type=float, default=0.5, help='a link on this share of the pages or more counts as template (default 0.5)')
    args = ap.parse_args()
    if args.cmd == 'crawl':
        crawl(args)
    elif args.cmd == 'report':
        with open(args.graph, encoding='utf-8') as f:
            report_graph(json.load(f), args.rows, args.near)
    else:
        ap.print_help()
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())

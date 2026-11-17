#!/usr/bin/env python3
"""A log of what AI assistants answer to buying questions, and the counts over it.
Python 3.8+, standard library only.

  add      append one answer to the log: which assistant, which question, the brands it named
           (in the order named: the agent's reading of the answer) and the sources it linked
  report   over one run: where your brand is named, who is named instead, which sources the
           answers lean on, the questions that name others and not you, and what changed since
           the run before

A run is one pass over the saved questions, labelled by date. Ask the same questions, word for
word, on every run: the comparison between runs is the point.

Examples:
  ai_answers.py add --log seo/ai/answers.jsonl --engine chatgpt --prompt "best crm for a two-person agency" \\
      --brands "HubSpot, Pipedrive, Folk" --answer seo/ai/raw/2026-11-17-chatgpt-01.json
  ai_answers.py report --log seo/ai/answers.jsonl --brand "Acme" --domain acme.com
"""
import argparse
import datetime
import json
import os
import sys
import urllib.parse
from collections import Counter, defaultdict


def site_of(url):
    host = urllib.parse.urlsplit(url).netloc.lower()
    return host[4:] if host.startswith('www.') else host


def read_log(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                sys.exit('%s line %d is not JSON.' % (path, n))
    return rows


def cmd_add(args):
    sources, read_at, chars = [], None, None
    if args.answer:
        with open(args.answer, encoding='utf-8') as f:
            a = json.load(f)
        if a.get('error') or a.get('wall'):
            sys.exit('That answer file is not an answer (%s). Nothing logged.' % (a.get('error') or 'a sign-in or CAPTCHA wall'))
        sources = [s['url'] for s in a.get('sources', []) if s.get('url')]
        read_at, chars = a.get('read_at'), a.get('answer_chars')
    sources += [u.strip() for u in (args.sources or '').split(',') if u.strip()]
    row = {
        'run': args.run or datetime.date.today().isoformat(),
        'engine': args.engine.strip().lower(),
        'prompt': ' '.join(args.prompt.split()),
        'brands': [b.strip() for b in args.brands.split(',') if b.strip()],
        'sources': list(dict.fromkeys(sources)),
        'read_at': read_at,
        'answer_chars': chars,
        'answer_file': args.answer,
        'note': args.note,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.log)), exist_ok=True)
    if os.path.exists(args.log):
        for old in read_log(args.log):
            if (old['run'], old['engine'], old['prompt']) == (row['run'], row['engine'], row['prompt']):
                sys.exit('Already logged for run %s: %s / "%s". Use another --run label to ask it again.' % (row['run'], row['engine'], row['prompt']))
    with open(args.log, 'a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print('Logged: run %s, %s, %d brands, %d sources.' % (row['run'], row['engine'], len(row['brands']), len(row['sources'])))


def table(headers, rows):
    if not rows:
        return '(none)'
    out = ['| ' + ' | '.join(headers) + ' |', '|' + '|'.join(['---'] * len(headers)) + '|']
    out += ['| ' + ' | '.join(str(c).replace('|', '\\|') for c in r) + ' |' for r in rows]
    return '\n'.join(out)


def named(row, brand):
    low = [b.lower() for b in row['brands']]
    return brand.lower() in low


def cmd_report(args):
    rows = read_log(args.log)
    if not rows:
        sys.exit('The log is empty.')
    runs = sorted({r['run'] for r in rows})
    run = args.run or runs[-1]
    if run not in runs:
        sys.exit('No run "%s" in the log. Runs: %s' % (run, ', '.join(runs)))
    now = [r for r in rows if r['run'] == run]
    earlier = [x for x in runs if x < run]
    before = [r for r in rows if r['run'] == earlier[-1]] if earlier else []
    brand, domain = args.brand, (args.domain or '').lower().lstrip('.')
    if domain.startswith('www.'):
        domain = domain[4:]

    print('## AI answers, run %s' % run)
    print('%d answers to %d questions on %d assistants. The brand looked for: %s%s.'
          % (len(now), len({r['prompt'] for r in now}), len({r['engine'] for r in now}), brand,
             ' (site %s)' % domain if domain else ''))

    by_engine = defaultdict(list)
    for r in now:
        by_engine[r['engine']].append(r)
    out = []
    for e in sorted(by_engine):
        rs = by_engine[e]
        hit = [r for r in rs if named(r, brand)]
        cited = [r for r in rs if domain and any(site_of(u) == domain or site_of(u).endswith('.' + domain) for u in r['sources'])]
        out.append([e, len(rs), len(hit), '%d%%' % round(100.0 * len(hit) / len(rs)), len(cited) if domain else '-'])
    print('\n### By assistant\n' + table(['Assistant', 'Questions asked', 'Names %s' % brand, 'Share', 'Links to %s' % (domain or 'your site')], out))

    brands, ranks = Counter(), defaultdict(list)
    for r in now:
        for i, b in enumerate(r['brands'], 1):
            brands[b] += 1
            ranks[b].append(i)
    print('\n### Who gets named (answers naming each brand, and where in the answer on average)')
    print(table(['Brand', 'Answers', 'Average place'], [[b, c, '%.1f' % (sum(ranks[b]) / len(ranks[b]))] for b, c in brands.most_common(args.rows)]))

    sites = Counter()
    for r in now:
        for s in {site_of(u) for u in r['sources']}:
            if s:
                sites[s] += 1
    print('\n### Sources the answers link to (answers linking each site)')
    print(table(['Site', 'Answers'], [[s, c] for s, c in sites.most_common(args.rows)]))

    gaps = [r for r in now if r['brands'] and not named(r, brand)]
    print('\n### Questions that name others and not %s: %d' % (brand, len(gaps)))
    print(table(['Assistant', 'Question', 'Named instead', 'Sources'],
                [[r['engine'], r['prompt'], ', '.join(r['brands'][:6]), ', '.join(sorted({site_of(u) for u in r['sources']})[:6]) or '-'] for r in gaps[:args.rows]]))

    if before:
        was = {(r['engine'], r['prompt']): named(r, brand) for r in before}
        gained = [k for k in ((r['engine'], r['prompt']) for r in now if named(r, brand)) if was.get(k) is False]
        lost = [k for k in ((r['engine'], r['prompt']) for r in now if not named(r, brand)) if was.get(k) is True]
        fresh = [k for k in ((r['engine'], r['prompt']) for r in now) if k not in was]
        print('\n### Against run %s' % earlier[-1])
        print('Named now and not then: %d. Named then and not now: %d. Not asked then: %d.' % (len(gained), len(lost), len(fresh)))
        for label, ks in (('Gained', gained), ('Lost', lost)):
            for e, p in ks:
                print('- %s: %s / "%s"' % (label, e, p))
    else:
        print('\nThis is the first run in the log: nothing to compare against yet.')
    print('\nBrands are matched by exact name, ignoring case: log one spelling per brand. One answer is one sample; an assistant can answer the same question differently an hour later.')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd')
    a = sub.add_parser('add', help='append one answer')
    a.add_argument('--log', required=True, help='the .jsonl log (created if missing)')
    a.add_argument('--engine', required=True, help='the assistant: chatgpt, perplexity, gemini, claude, google-ai-mode, ...')
    a.add_argument('--prompt', required=True, help='the question, word for word as asked')
    a.add_argument('--brands', required=True, help='brands the answer names, in order, comma separated ("" when it names none)')
    a.add_argument('--answer', help='the .json saved by answer_read.js: its links become the sources')
    a.add_argument('--sources', help='or source addresses by hand, comma separated')
    a.add_argument('--run', help='label of this pass over the questions (default: today\'s date)')
    a.add_argument('--note', help='anything worth keeping: signed in or not, model shown, search on or off')
    r = sub.add_parser('report', help='counts over one run')
    r.add_argument('--log', required=True)
    r.add_argument('--brand', required=True, help='your brand, spelled as logged')
    r.add_argument('--domain', help='your site, to count answers that link to it')
    r.add_argument('--run', help='which run (default: the latest)')
    r.add_argument('--rows', type=int, default=20)
    args = ap.parse_args()
    if args.cmd == 'add':
        cmd_add(args)
    elif args.cmd == 'report':
        cmd_report(args)
    else:
        ap.print_help()
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())

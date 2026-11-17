#!/usr/bin/env python3
"""Search Console arithmetic for the SEO playbook. Python 3.8+, standard library only.

It reads performance data and answers four questions. It does not judge intent or quality:
that is the agent's reading of the rows this prints.

Input, any of:
  a .json saved by gsc_read.js      (the report's table, read out of the open page)
  the .zip from Export > Download CSV   (pick a tab with --tab; default queries)
  one .csv from that zip, or the folder holding them
The generative AI features report counts impressions only: summary reads it, the rest need clicks.

Commands:
  summary   what the file holds: rows, totals, position bands, the top rows
  near      rows ranking just off page one, most impressions first   -> content worth improving
  ctr       page-one rows clicked less than their position earns here -> titles to rewrite
  decay     rows that lost clicks against the comparison period       -> pages to update
            (needs an export or read made with a comparison switched on)
  questions queries that open with a question word, most impressions first -> headings to write as the
            question, with a one-line answer under each
  pairs     queries that compare ("vs", "or", "alternative", "compare", "difference") -> comparison pages

Examples:
  gsc.py summary seo/gsc/2026-11-17/queries.json
  gsc.py near    export.zip --tab pages --min-impr 50
  gsc.py ctr     queries.json --exclude 'mybrand'
  gsc.py decay   export.zip --tab pages --contains '/blog/'
  gsc.py questions queries.json --brand mybrand
  gsc.py pairs   export.zip
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import zipfile

TABS = {
    'queries': 'queries', 'pages': 'pages', 'countries': 'countries', 'devices': 'devices',
    'dates': 'dates', 'days': 'dates', 'appearance': 'search appearance',
}


HAS_POSITION = True
HAS_CLICKS = True


def need_clicks():
    if not HAS_CLICKS:
        sys.exit('This file counts impressions only (the generative AI features report does): no position, click rate or lost clicks to work out. Use summary.')


def need_position():
    need_clicks()
    if not HAS_POSITION:
        sys.exit('This file has no Position column. In the report, switch on the "Average position" tile above the chart, then read or export again.')


def num(v):
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(',', '').replace('%', '')
    try:
        return float(s)
    except ValueError:
        return 0.0


def metric_of(column):
    low = column.lower()
    if 'difference' in low:
        return None
    for word, name in (('click', 'clicks'), ('impression', 'impressions'), ('ctr', 'ctr'), ('position', 'position')):
        if word in low:
            return name
    return None


def to_records(columns, rows):
    """First column is the key. For each metric the first column is the period, the second the comparison."""
    where = {}
    for i, col in enumerate(columns):
        if i == 0:
            continue
        m = metric_of(col)
        if m:
            where.setdefault(m, []).append(i)
    if 'impressions' not in where:
        sys.exit('This file has no Impressions column. Columns found: %s' % ', '.join(columns))
    compared = len(where['impressions']) > 1
    global HAS_POSITION, HAS_CLICKS
    HAS_POSITION = 'position' in where
    HAS_CLICKS = 'clicks' in where  # the generative AI features report counts impressions only
    out = []
    for r in rows:
        if not r or len(r) < len(columns):
            continue
        rec = {'key': str(r[0])}
        for m, idxs in where.items():
            rec[m] = num(r[idxs[0]])
            if compared and len(idxs) > 1:
                rec['prev_' + m] = num(r[idxs[1]])
        rec.setdefault('position', 0.0)
        rec.setdefault('clicks', 0.0)
        # Click rate from the counts, not from the rounded column.
        rec['ctr'] = 100.0 * rec['clicks'] / rec['impressions'] if rec['impressions'] else 0.0
        if compared:
            pi = rec.get('prev_impressions', 0.0)
            rec['prev_ctr'] = 100.0 * rec.get('prev_clicks', 0.0) / pi if pi else 0.0
        out.append(rec)
    return out, compared


def read_csv_text(text):
    rows = list(csv.reader(io.StringIO(text.lstrip('﻿'))))
    if not rows:
        sys.exit('That CSV is empty.')
    return rows[0], rows[1:]


def load(path, tab):
    want = TABS.get(tab, tab)
    if os.path.isdir(path):
        names = [n for n in os.listdir(path) if n.lower().endswith('.csv')]
        hit = [n for n in names if n.lower().startswith(want)]
        if not hit:
            sys.exit('No %s CSV in %s. Found: %s' % (want, path, ', '.join(sorted(names)) or 'nothing'))
        with open(os.path.join(path, hit[0]), encoding='utf-8') as f:
            return read_csv_text(f.read()), hit[0]
    low = path.lower()
    if low.endswith('.zip'):
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            hit = [n for n in names if os.path.basename(n).lower().startswith(want) and n.lower().endswith('.csv')]
            if not hit:
                sys.exit('No %s CSV in that zip. Found: %s' % (want, ', '.join(names)))
            return read_csv_text(z.read(hit[0]).decode('utf-8')), hit[0]
    if low.endswith('.csv'):
        with open(path, encoding='utf-8') as f:
            return read_csv_text(f.read()), os.path.basename(path)
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict) and data.get('error'):
        sys.exit('That read failed in the browser: %s. %s' % (data['error'], data.get('hint', '')))
    if not isinstance(data, dict) or 'rows' not in data or 'columns' not in data:
        sys.exit('That JSON is not a gsc_read.js result (it needs "columns" and "rows").')
    return (data['columns'], data['rows']), '%s (%s)' % (os.path.basename(path), data.get('breakdown') or 'table')


def fmt(v, digits=0):
    if digits == 0:
        return '{:,}'.format(int(round(v)))
    return ('{:,.%df}' % digits).format(v)


def table(headers, rows):
    if not rows:
        return '(no rows)'
    lines = ['| ' + ' | '.join(headers) + ' |', '|' + '|'.join(['---'] * len(headers)) + '|']
    for r in rows:
        lines.append('| ' + ' | '.join(str(c).replace('|', '\\|') for c in r) + ' |')
    return '\n'.join(lines)


def emit(args, title, headers, rows, notes=(), records=None):
    if args.json:
        json.dump({'title': title, 'rows': records if records is not None else rows, 'notes': list(notes)}, sys.stdout, indent=1)
        print()
        return
    print('## ' + title)
    for n in notes:
        print(n)
    if notes:
        print()
    print(table(headers, rows))


def cmd_summary(args, recs, compared, source):
    clicks = sum(r['clicks'] for r in recs)
    impr = sum(r['impressions'] for r in recs)
    pos = sum(r['position'] * r['impressions'] for r in recs) / impr if impr else 0.0
    bands = [('1 to 3', 0, 3.5), ('4 to 10', 3.5, 10.5), ('11 to 20', 10.5, 20.5), ('21 and below', 20.5, 1e9)]
    band_rows = []
    for name, lo, hi in bands:
        inb = [r for r in recs if r['impressions'] and lo <= r['position'] < hi]
        band_rows.append([name, fmt(len(inb)), fmt(sum(r['clicks'] for r in inb)), fmt(sum(r['impressions'] for r in inb))])
    if HAS_CLICKS and HAS_POSITION:
        totals = ('Rows add up to %s clicks and %s impressions, click rate %s%%, position %s (weighted by impressions).'
                  % (fmt(clicks), fmt(impr), fmt(100.0 * clicks / impr if impr else 0, 2), fmt(pos, 1)))
    elif HAS_CLICKS:
        totals = 'Rows add up to %s clicks and %s impressions, click rate %s%%.' % (fmt(clicks), fmt(impr), fmt(100.0 * clicks / impr if impr else 0, 2))
    else:
        totals = 'Rows add up to %s impressions. This table counts impressions only.' % fmt(impr)
    notes = [
        'Source: %s. Rows: %s. Comparison period in the file: %s.' % (source, fmt(len(recs)), 'yes' if compared else 'no'),
        totals,
        'Search Console leaves rare queries out of the table and stops at 1,000 rows, so rows add up to less than the report\'s totals.',
    ]
    if compared:
        pc = sum(r.get('prev_clicks', 0) for r in recs)
        pi = sum(r.get('prev_impressions', 0) for r in recs)
        notes.append('Comparison period: %s%s impressions.' % ('%s clicks, ' % fmt(pc) if HAS_CLICKS else '', fmt(pi)))
    if args.json:
        json.dump({'source': source, 'rows': len(recs), 'compared': compared, 'clicks': clicks, 'impressions': impr,
                   'position': round(pos, 2), 'bands': band_rows}, sys.stdout, indent=1)
        print()
        return
    print('## Summary')
    for n in notes:
        print(n)
    if HAS_POSITION:
        print('\n### By position\n' + table(['Position', 'Rows', 'Clicks', 'Impressions'], band_rows))
    top = sorted(recs, key=lambda r: (-r['clicks'], -r['impressions']))[:args.limit if args.limit < 15 else 15]
    if not HAS_CLICKS:
        print('\n### Top rows by impressions\n' + table(['Row', 'Impressions'], [[r['key'], fmt(r['impressions'])] for r in top]))
        return
    print('\n### Top rows by clicks\n' + table(
        ['Row', 'Clicks', 'Impressions', 'Click rate', 'Position'],
        [[r['key'], fmt(r['clicks']), fmt(r['impressions']), fmt(r['ctr'], 1) + '%', fmt(r['position'], 1) if HAS_POSITION else '-'] for r in top]))


def cmd_near(args, recs, compared, source):
    need_position()
    hit = [r for r in recs if args.min_pos <= r['position'] <= args.max_pos and r['impressions'] >= args.min_impr
           and len(r['key'].split()) >= args.min_words]
    hit.sort(key=lambda r: -r['impressions'])
    notes = ['%s of %s rows rank between %s and %s with at least %s impressions. Most impressions first.'
             % (fmt(len(hit)), fmt(len(recs)), fmt(args.min_pos, 1), fmt(args.max_pos, 1), fmt(args.min_impr))]
    hit = hit[:args.limit]
    emit(args, 'Near page one', ['Row', 'Position', 'Impressions', 'Clicks', 'Click rate'],
         [[r['key'], fmt(r['position'], 1), fmt(r['impressions']), fmt(r['clicks']), fmt(r['ctr'], 1) + '%'] for r in hit],
         notes, hit)


def cmd_ctr(args, recs, compared, source):
    need_position()
    need_clicks()
    # What a position earns on THIS site: clicks over impressions of every row at that rounded position.
    buckets = {}
    for r in recs:
        if r['impressions'] and r['position'] < args.max_pos + 0.5:
            b = buckets.setdefault(max(1, int(round(r['position']))), [0.0, 0.0, 0])
            b[0] += r['clicks']
            b[1] += r['impressions']
            b[2] += 1
    base = {p: 100.0 * c / i for p, (c, i, n) in buckets.items() if i >= args.min_bucket and c > 0}
    notes = ['The yardstick is this file\'s own click rate at each position (positions with under %s impressions or no clicks are left out):'
             % fmt(args.min_bucket),
             ', '.join('position %d: %s%%' % (p, fmt(base[p], 1)) for p in sorted(base)) or 'none: too little data on page one to compare against.']
    hit = []
    for r in recs:
        p = max(1, int(round(r['position'])))
        if p in base and r['impressions'] >= args.min_impr and r['ctr'] < args.ratio * base[p]:
            r = dict(r, expected_ctr=base[p], missed_clicks=r['impressions'] * (base[p] - r['ctr']) / 100.0)
            hit.append(r)
    hit.sort(key=lambda r: -r['missed_clicks'])
    notes.append('%s rows with at least %s impressions are clicked at under %s of that rate. Most missed clicks first.'
                 % (fmt(len(hit)), fmt(args.min_impr), fmt(args.ratio, 2)))
    hit = hit[:args.limit]
    emit(args, 'Clicked less than their position earns',
         ['Row', 'Position', 'Impressions', 'Click rate', 'Rate at that position', 'Clicks missed'],
         [[r['key'], fmt(r['position'], 1), fmt(r['impressions']), fmt(r['ctr'], 1) + '%', fmt(r['expected_ctr'], 1) + '%', fmt(r['missed_clicks'], 1)] for r in hit],
         notes, hit)


def cmd_decay(args, recs, compared, source):
    need_clicks()
    if not compared:
        sys.exit('This file has one period only. Read or export the report with a comparison on '
                 '(add compare_date=PREV to the report\'s address, or pick Compare in the date filter).')
    hit = []
    for r in recs:
        lost = r.get('prev_clicks', 0) - r['clicks']
        if lost < args.min_lost or r.get('prev_clicks', 0) < args.min_clicks:
            continue
        pp, pi = r.get('prev_position', 0), r.get('prev_impressions', 0)
        if r['impressions'] == 0:
            moved = 'gone from the results'
        elif pp and r['position'] - pp >= 1.0:
            moved = 'rank fell'
        elif pi and r['impressions'] < 0.8 * pi:
            moved = 'fewer searches shown'
        else:
            moved = 'click rate fell'
        hit.append(dict(r, lost=lost, moved=moved))
    hit.sort(key=lambda r: -r['lost'])
    notes = ['%s rows lost at least %s clicks from a period with at least %s. Most clicks lost first.'
             % (fmt(len(hit)), fmt(args.min_lost), fmt(args.min_clicks)),
             '"What moved" is arithmetic: rank fell = a position or more worse; fewer searches shown = impressions down a fifth or more at a held rank; otherwise the click rate fell. Check a dip against the same weeks a year back before calling it new.']
    hit = hit[:args.limit]
    emit(args, 'Lost clicks against the comparison period',
         ['Row', 'Clicks', 'Before', 'Lost', 'Impressions', 'Before', 'Position', 'Before', 'What moved'],
         [[r['key'], fmt(r['clicks']), fmt(r.get('prev_clicks', 0)), fmt(r['lost']), fmt(r['impressions']),
           fmt(r.get('prev_impressions', 0)), fmt(r['position'], 1), fmt(r.get('prev_position', 0), 1), r['moved']] for r in hit],
         notes, hit)


# English defaults, as the second source list gives them. Pass --words for another language.
QUESTION_WORDS = 'how,what,why,when,can,is,does,should,which'
PAIR_WORDS = 'vs,versus,or,alternative,alternatives,compare,comparison,difference'


def cmd_questions(args, recs, compared, source):
    words = {w.strip().lower() for w in (args.words or QUESTION_WORDS).split(',') if w.strip()}
    pool = [r for r in recs if r['impressions'] >= args.min_impr]
    rates = sorted(r['ctr'] for r in pool)
    median = rates[len(rates) // 2] if rates else 0.0
    hit = [r for r in pool if r['key'].lower().split(' ')[0] in words]
    under = [r for r in hit if r['ctr'] < median] if median > 0 else hit
    under.sort(key=lambda r: -r['impressions'])
    notes = ['%s of %s rows with at least %s impressions open with a question word (%s).'
             % (fmt(len(hit)), fmt(len(pool)), fmt(args.min_impr), ', '.join(sorted(words))),
             ('The median click rate of those %s rows is %s%%; listed: the %s questions under it.' % (fmt(len(pool)), fmt(median, 2), fmt(len(under))))
             if median > 0 else 'The median click rate is 0%, so every question is listed.',
             'Which page a query lands on is not in this file: filter the report to the query and read the Pages tab.']
    under = under[:args.limit]
    emit(args, 'Questions people search', ['Query', 'Impressions', 'Clicks', 'Click rate', 'Position'],
         [[r['key'], fmt(r['impressions']), fmt(r['clicks']), fmt(r['ctr'], 1) + '%', fmt(r['position'], 1) if HAS_POSITION else '-'] for r in under],
         notes, under)


def cmd_pairs(args, recs, compared, source):
    words = [w.strip().lower() for w in (args.words or PAIR_WORDS).split(',') if w.strip()]
    rx = re.compile(r'(?:^|\s)(%s)(?:\s|$)' % '|'.join(re.escape(w) for w in words), re.I)
    hit = []
    for r in recs:
        m = rx.search(r['key'])
        if m and r['impressions'] >= args.min_impr:
            hit.append(dict(r, word=m.group(1).lower()))
    hit.sort(key=lambda r: -r['impressions'])
    notes = ['%s of %s rows compare two things, by one of: %s. Most impressions first.' % (fmt(len(hit)), fmt(len(recs)), ', '.join(words)),
             'Grouping them into pairs is a reading, not a count: "x or y" is a pair only when x and y are both things one can choose.']
    hit = hit[:args.limit]
    emit(args, 'Comparison searches', ['Query', 'Word', 'Impressions', 'Clicks', 'Position'],
         [[r['key'], r['word'], fmt(r['impressions']), fmt(r['clicks']), fmt(r['position'], 1) if HAS_POSITION else '-'] for r in hit],
         notes, hit)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd')

    def common(p):
        p.add_argument('file', help='a gsc_read.js .json, the export .zip, one of its .csv files, or their folder')
        p.add_argument('--tab', default='queries', help='which CSV of a zip or folder: queries, pages, countries, devices, dates (default queries)')
        p.add_argument('--contains', help='keep rows whose first column matches this regular expression')
        p.add_argument('--exclude', help='drop rows whose first column matches this regular expression (your brand name, for one)')
        p.add_argument('--brand', help='your brand name: rows naming it are dropped and counted, with their share of impressions')
        p.add_argument('--limit', type=int, default=40, help='rows to print (default 40)')
        p.add_argument('--json', action='store_true', help='print JSON instead of a Markdown table')

    p = sub.add_parser('summary', help='what the file holds')
    common(p)
    p = sub.add_parser('near', help='rows just off page one')
    common(p)
    p.add_argument('--min-words', type=int, default=1, help='skip rows with fewer words than this (2 drops one-word queries)')
    p.add_argument('--min-pos', type=float, default=8.0)
    p.add_argument('--max-pos', type=float, default=20.0)
    p.add_argument('--min-impr', type=float, default=20)
    p = sub.add_parser('ctr', help='page-one rows clicked less than their position earns')
    common(p)
    p.add_argument('--max-pos', type=float, default=10.0)
    p.add_argument('--min-impr', type=float, default=50)
    p.add_argument('--min-bucket', type=float, default=100, help='impressions a position needs before it is used as a yardstick')
    p.add_argument('--ratio', type=float, default=0.5, help='flag rows under this share of the position\'s rate (default 0.5)')
    p = sub.add_parser('decay', help='rows that lost clicks against the comparison period')
    common(p)
    p.add_argument('--min-lost', type=float, default=1)
    p.add_argument('--min-clicks', type=float, default=3, help='clicks the row needed in the earlier period')

    p = sub.add_parser('questions', help='queries that open with a question word')
    common(p)
    p.add_argument('--min-impr', type=float, default=20)
    p.add_argument('--words', help='the question words, comma separated (default: %s)' % QUESTION_WORDS)
    p = sub.add_parser('pairs', help='queries that compare two things')
    common(p)
    p.add_argument('--min-impr', type=float, default=1)
    p.add_argument('--words', help='the comparing words, comma separated (default: %s)' % PAIR_WORDS)

    args = ap.parse_args()
    if not args.cmd:
        ap.print_help()
        return 2
    (columns, rows), source = load(args.file, args.tab)
    recs, compared = to_records(columns, rows)
    if args.contains:
        rx = re.compile(args.contains, re.I)
        recs = [r for r in recs if rx.search(r['key'])]
    if args.exclude:
        rx = re.compile(args.exclude, re.I)
        recs = [r for r in recs if not rx.search(r['key'])]
    if args.brand:
        named = [r for r in recs if args.brand.lower() in r['key'].lower()]
        total = sum(r['impressions'] for r in recs)
        share = 100.0 * sum(r['impressions'] for r in named) / total if total else 0.0
        recs = [r for r in recs if args.brand.lower() not in r['key'].lower()]
        if not args.json:
            print('Dropped %s rows naming "%s": %s%% of the impressions in this file.%s\n'
                  % (fmt(len(named)), args.brand, fmt(share, 1),
                     ' That is over a fifth: most of what this file shows is people who already know the name. Say so before ranking anything.' if share > 20 else ''))
    {'summary': cmd_summary, 'near': cmd_near, 'ctr': cmd_ctr, 'decay': cmd_decay,
     'questions': cmd_questions, 'pairs': cmd_pairs}[args.cmd](args, recs, compared, source)
    return 0


if __name__ == '__main__':
    sys.exit(main())

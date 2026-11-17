#!/usr/bin/env python3
"""What Google's search box suggests around a phrase. Python 3.8+, standard library only.

It asks the suggestion endpoint behind Google's search box for the phrase on its own, then for the
phrase with words before and after it (letters a to z, question words, buying words), and lists
every distinct suggestion with the probe that surfaced it.

A suggestion says people search this, in these words. It carries no volume. Read the list for the
specific problems and comparisons buyers type, then check the ones that matter against Search
Console impressions or the live results.

The endpoint is the one browsers use for the search box; it is undocumented and may change or
limit you. Keep the default delay.

Examples:
  autocomplete.py "resume builder"
  autocomplete.py "crm for" --country gb --only letters
  autocomplete.py "lebenslauf" --lang de --country de --before "wie,was,warum" --after "kostenlos,vorlage,vs"
"""
import argparse
import json
import string
import sys
import time
import urllib.parse
import urllib.request

ENDPOINT = 'https://suggestqueries.google.com/complete/search'
# English defaults. For another language pass --before and --after with that language's words.
BEFORE = ['how', 'how to', 'what', 'why', 'which', 'can', 'is', 'best', 'free', 'cheap']
AFTER = ['for', 'vs', 'or', 'with', 'without', 'alternative', 'pricing', 'review', 'template', 'example', 'near me', 'online']


def suggest(q, lang, country):
    url = ENDPOINT + '?' + urllib.parse.urlencode({'client': 'firefox', 'hl': lang, 'gl': country, 'q': q})
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read()
        charset = r.headers.get_content_charset() or 'utf-8'
    data = json.loads(raw.decode(charset, 'replace'))
    return [s for s in data[1] if isinstance(s, str)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('phrase')
    ap.add_argument('--lang', default='en', help='interface language, as in hl= (default en)')
    ap.add_argument('--country', default='us', help='country, as in gl= (default us)')
    ap.add_argument('--only', choices=['plain', 'letters', 'before', 'after'], action='append',
                    help='which probes to run; repeat to combine (default: all four)')
    ap.add_argument('--before', help='words to put before the phrase, comma separated (default: English question and buying words)')
    ap.add_argument('--after', help='words to put after the phrase, comma separated')
    ap.add_argument('--delay', type=float, default=0.25, help='seconds between requests (default 0.25)')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    kinds = args.only or ['plain', 'letters', 'before', 'after']
    before = [w.strip() for w in args.before.split(',')] if args.before else BEFORE
    after = [w.strip() for w in args.after.split(',')] if args.after else AFTER
    probes = []
    if 'plain' in kinds:
        probes += [args.phrase, args.phrase + ' ']
    if 'letters' in kinds:
        probes += ['%s %s' % (args.phrase, c) for c in string.ascii_lowercase]
    if 'before' in kinds:
        probes += ['%s %s' % (w, args.phrase) for w in before if w]
    if 'after' in kinds:
        probes += ['%s %s ' % (args.phrase, w) for w in after if w]

    found, failed = {}, []
    for i, p in enumerate(probes):
        if i:
            time.sleep(args.delay)
        try:
            for s in suggest(p, args.lang, args.country):
                found.setdefault(s.strip().lower(), p.strip())
        except Exception as e:
            failed.append('%s (%s)' % (p.strip(), type(e).__name__))
            if len(failed) >= 3 and not found:
                sys.exit('The suggestion endpoint is not answering (%s). Read the search box in the browser instead.' % failed[-1])

    if args.json:
        json.dump({'phrase': args.phrase, 'lang': args.lang, 'country': args.country, 'probes': len(probes), 'failed': failed,
                   'suggestions': [{'suggestion': s, 'from': p} for s, p in found.items()]}, sys.stdout, indent=1, ensure_ascii=False)
        print()
        return 0
    print('%d distinct suggestions from %d probes around "%s" (%s, %s).%s'
          % (len(found), len(probes), args.phrase, args.lang, args.country, ' Probes that failed: %s.' % ', '.join(failed) if failed else ''))
    print('\n| Suggestion | Surfaced by |\n|---|---|')
    for s, p in found.items():
        print('| %s | %s |' % (s.replace('|', '\\|'), p.replace('|', '\\|')))
    return 0


if __name__ == '__main__':
    sys.exit(main())

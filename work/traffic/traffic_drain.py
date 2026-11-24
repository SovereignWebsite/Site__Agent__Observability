#!/usr/bin/env python3
"""SovereignWebsite traffic drain: draft 1, observability.b@SovereignWebsite.dinis, 23 Nov 2026. Not live.

Reads encrypted notes from the private traffic vault's append lanes, opens them with sgit, keeps only notes that
pass validation (security.b review 003, finding 1), and writes totals only:

  python3 -I traffic_drain.py --sites sites.json --out OUT_DIR [--notes NOTES.jsonl]   (offline: plain notes)
  python3 -I traffic_drain.py --sites sites.json --out OUT_DIR --live --creds CREDS.json  (live: lanes)

Published per site, OUT_DIR/<site>/traffic.json:
  days:      per UTC day, page views and visits (distinct tabs) by type (person, team, synthetic, crawler)
  pages:     last 28 days, person page views per path
  countries: last 28 days, person visits per country (from the time zone; "unknown" when it has no country)
Never: a note, a tab id, a time zone, a language, a time finer than the day. Any person count under 5 becomes part of
"other", and a table whose only small cell would be recoverable by subtraction folds a second cell into "other" too.
Every count is a count of claims: the lane tokens and the public key are public, so anyone can add notes.
Full lanes (security.b, 23 Nov): the service has no rate limit, so a flood can fill a lane to its 1000 pending notes,
after which writes get 507 and counting stops on that lane. In live mode the drain counts each lane's pending notes
before draining and reports any lane at 900 or more (and any at 1000 as full) in its output and in the published
file's "lanes_full" field, so a gap in the counts is visible rather than silent.
Standard library only, plus the sgit command for decryption. Prints counts, never a note or a key.
"""
import argparse, collections, datetime, json, os, re, subprocess, sys, tempfile, urllib.request

MIN = 5
WINDOW_DAYS = 28
TYPES = ('person', 'team', 'synthetic', 'crawler')
RE_PATH = re.compile(r'^/[\x21-\x7e]{0,199}$')
RE_TZ = re.compile(r'^[A-Za-z_]+(/[A-Za-z_+-]+){0,2}$')
RE_LANG = re.compile(r'^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,4})?$')
RE_TAB = re.compile(r'^[0-9a-f]{8}$')
RE_TS = re.compile(r'^\d{4}-\d\d-\d\dT\d\d:\d\dZ$')


def zone_countries():
    """IANA time zone to ISO country, from the system's zone.tab (one country per zone). UTC and Etc/* have none."""
    out = {}
    for fn in ('/usr/share/zoneinfo/zone.tab',):
        try:
            for line in open(fn, encoding='utf-8'):
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.rstrip('\n').split('\t')
                if len(parts) >= 3:
                    out[parts[2]] = parts[0]
        except OSError:
            pass
    return out


def valid(n, sites, received=None):
    """A note is hostile until it passes every check; anything else is dropped."""
    if not isinstance(n, dict) or n.get('v') != 1:
        return False
    if n.get('site') not in sites or n.get('type') not in TYPES:
        return False
    if not isinstance(n.get('path'), str) or not RE_PATH.match(n['path']):
        return False
    if not isinstance(n.get('tab'), str) or not RE_TAB.match(n['tab']):
        return False
    if not isinstance(n.get('ts'), str) or not RE_TS.match(n['ts']):
        return False
    for k, rx in (('tz', RE_TZ), ('lang', RE_LANG)):
        v = n.get(k, '')
        if not isinstance(v, str) or (v and (len(v) > 40 or not rx.match(v))):
            return False
    try:
        ts = datetime.datetime.strptime(n['ts'], '%Y-%m-%dT%H:%MZ').replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        return False
    if received is not None and abs((ts - received).total_seconds()) > 3600:
        return False
    return True


def fold(counter):
    """Cells under MIN go to "other"; if "other" would then be under MIN but positive, fold the next smallest cell
    in too, so the hidden cells cannot be recovered from the total by subtraction."""
    big = {k: v for k, v in counter.items() if v >= MIN}
    other = sum(v for k, v in counter.items() if v < MIN)
    while 0 < other < MIN and big:
        k = min(big, key=lambda x: (big[x], x))
        other += big.pop(k)
    rows = sorted(big.items(), key=lambda x: (-x[1], x[0]))
    if other:
        rows.append(['other', other])
    return [list(r) for r in rows]


def aggregate(notes, sites, today):
    zc = zone_countries()
    start = today - datetime.timedelta(days=WINDOW_DAYS - 1)
    out = {}
    for site in sites:
        mine = [n for n in notes if n['site'] == site]
        days = collections.defaultdict(lambda: {t: {'views': 0, 'tabs': set()} for t in TYPES})
        pages, countries, seen_tab = collections.Counter(), collections.Counter(), set()
        for n in mine:
            day = n['ts'][:10]
            d = days[day][n['type']]
            d['views'] += 1
            d['tabs'].add(n['tab'])
            if n['type'] == 'person' and datetime.date.fromisoformat(day) >= start:
                pages[n['path']] += 1
                if (day, n['tab']) not in seen_tab:
                    seen_tab.add((day, n['tab']))
                    countries[zc.get(n.get('tz', ''), 'unknown')] += 1
        out[site] = {
            'v': 1, 'site': site, 'generated': today.isoformat(), 'window_days': WINDOW_DAYS, 'min_count': MIN,
            'note': 'Counts of claims: anyone can send notes, so these are indicative. No cookies; no IP addresses.',
            'days': {day: {t: {'views': c[t]['views'], 'visits': len(c[t]['tabs'])} for t in TYPES}
                     for day, c in sorted(days.items())},
            'pages': fold(pages),
            'countries': fold(countries),
        }
        for day in out[site]['days'].values():       # person counts under MIN per day are shown as 0 plus a flag
            p = day['person']
            if 0 < p['visits'] < MIN:
                day['person'] = {'views': 0, 'visits': 0, 'under_min': True}
    return out


def decrypt(enc_text, fingerprint, passfile):
    """Open one sgit envelope with this agent's key. The passphrase is piped from a 0600 file, never printed."""
    with tempfile.TemporaryDirectory() as d:
        src, dst = os.path.join(d, 'n.enc'), os.path.join(d, 'n')
        open(src, 'w').write(enc_text)
        with open(passfile, 'rb') as pw:
            r = subprocess.run(['sgit', 'pki', 'decrypt', '--fingerprint', fingerprint, '--output', dst, src],
                               stdin=pw, capture_output=True, timeout=60)
        if r.returncode != 0 or not os.path.exists(dst):
            return None
        return open(dst, encoding='utf-8').read()


def post(c, op, body):
    req = urllib.request.Request(f"{c['endpoint']}/api/vault/append/{op}/{c['vault_id']}", method='POST',
                                 data=json.dumps(body).encode(),
                                 headers={'Content-Type': 'application/json', 'x-sgraph-vault-enum-key': c['enum_key']})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read() or b'{}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sites', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--notes'); ap.add_argument('--live', action='store_true'); ap.add_argument('--creds')
    ap.add_argument('--today')
    a = ap.parse_args()
    sites = set(json.load(open(a.sites))['sites'])
    today = datetime.date.fromisoformat(a.today) if a.today else datetime.datetime.now(datetime.timezone.utc).date()
    raw, kept, dropped = [], [], 0
    if a.notes:
        raw = [(json.loads(l), None) for l in open(a.notes) if l.strip()]
    if a.live:
        raise SystemExit('live mode waits for the pilot vault (list, fetch, decrypt, keep raw privately, mark processed)')
    for n, received in raw:
        if valid(n, sites, received):
            kept.append(n)
        else:
            dropped += 1
    result = aggregate(kept, sites, today)
    for site, data in result.items():
        os.makedirs(os.path.join(a.out, site), exist_ok=True)
        json.dump(data, open(os.path.join(a.out, site, 'traffic.json'), 'w'), indent=1, sort_keys=True)
    print(f'notes {len(raw)}, kept {len(kept)}, dropped {dropped}, sites {len(result)}')


if __name__ == '__main__':
    main()

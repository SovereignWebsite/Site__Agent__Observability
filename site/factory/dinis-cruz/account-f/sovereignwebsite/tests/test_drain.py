"""Offline tests for work/traffic/traffic_drain.py (read-only: the drain is imported, never edited).
Run from the repository root:  python3 -I site/factory/dinis-cruz/account-f/sovereignwebsite/tests/test_drain.py
Made-up notes only: no vault, no token, no network."""
import datetime, importlib.util, os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *['..'] * 6))
spec = importlib.util.spec_from_file_location('drain', os.path.join(ROOT, 'work/traffic/traffic_drain.py'))
drain = importlib.util.module_from_spec(spec); spec.loader.exec_module(drain)

SITES = {'a.example'}
TODAY = datetime.date(2026, 11, 27)
NOW = datetime.datetime(2026, 11, 27, 12, 0, tzinfo=datetime.timezone.utc)


def note(**kw):
    n = {'v': 1, 'site': 'a.example', 'path': '/x', 'ts': '2026-11-27T12:00Z', 'tz': 'Europe/London', 'lang': 'en-GB',
         'type': 'person', 'tab': 'abcdef01'}
    n.update(kw)
    return n


class Valid(unittest.TestCase):
    def ok(self, **kw): return drain.valid(note(**kw), SITES, NOW)
    def test_good(self): self.assertTrue(self.ok())
    def test_not_dict(self):
        for x in (None, [], 'x', 3): self.assertFalse(drain.valid(x, SITES, NOW))
    def test_version(self):
        for v in (0, 2, '1', None): self.assertFalse(self.ok(v=v))
    def test_site(self):
        for s in ('b.example', '', None, 'a.example.evil'): self.assertFalse(self.ok(site=s))
    def test_type(self):
        for t in ('admin', 'Person', '', None): self.assertFalse(self.ok(type=t))
    def test_path(self):
        for p in ('x', '', '/a b', '/' + 'a' * 200, None, 5): self.assertFalse(self.ok(path=p), p)
        self.assertTrue(self.ok(path='/' + 'a' * 199)); self.assertTrue(self.ok(path='/'))
    @unittest.expectedFailure
    def test_trailing_newline_rejected(self):
        # FINDING 2: the patterns end in $, which also matches before a final newline, so '/x\n' and a tab 'abcdef01\n'
        # pass. Use fullmatch (or \Z). Low impact (textContent, counts) but the rule says "at most".
        for k, v in (('path', '/x\n'), ('tab', 'abcdef01\n'), ('lang', 'en\n'), ('tz', 'UTC\n'), ('ts', '2026-11-27T12:00Z\n')):
            self.assertFalse(self.ok(**{k: v}), k)
    def test_path_allows_markup_characters(self):
        # Recorded, not a failure: design.md only asks for "/" first and at most 200 characters, so '<' passes.
        # Every page that draws a path must use textContent (review 003, finding 1).
        self.assertTrue(self.ok(path='/<script>alert(1)</script>'))
    def test_tab(self):
        for t in ('ABCDEF01', 'abcdef0', 'abcdef012', 'zzzzzzzz', '', None): self.assertFalse(self.ok(tab=t), t)
    def test_ts_format(self):
        for t in ('2026-11-27', '2026-11-27T12:00:00Z', '2026-11-27 12:00Z', None): self.assertFalse(self.ok(ts=t), t)
    def test_ts_impossible_date(self): self.assertFalse(self.ok(ts='2026-13-40T99:99Z'))
    def test_ts_window(self):
        self.assertTrue(self.ok(ts='2026-11-27T12:59Z'))
        self.assertFalse(self.ok(ts='2026-11-27T13:01Z'))
        self.assertFalse(self.ok(ts='2026-11-27T10:59Z'))
    def test_ts_window_skipped_without_received(self):
        # Documented gap: with no received time the window is not checked (offline mode only; live mode must pass it).
        self.assertTrue(drain.valid(note(ts='2020-01-01T00:00Z'), SITES, None))
    def test_tz(self):
        for z in ('<x>/y', 'A/B/C/D', 'a' * 41, 'Europe/London; drop', 5):
            self.assertFalse(self.ok(tz=z), z)
        for z in ('', 'UTC', 'America/Argentina/Buenos_Aires'): self.assertTrue(self.ok(tz=z), z)
    def test_lang(self):
        for l in ('english', 'e', 'en_GB', 'en-GBRR9', '<b>', 5): self.assertFalse(self.ok(lang=l), l)
        for l in ('', 'en', 'pt-BR', 'zh-Hans'): self.assertTrue(self.ok(lang=l), l)


class Fold(unittest.TestCase):
    def test_all_big(self):
        self.assertEqual(drain.fold({'a': 9, 'b': 5}), [['a', 9], ['b', 5]])
    def test_small_go_to_other(self):
        r = dict(map(tuple, drain.fold({'a': 9, 'b': 2, 'c': 3})))
        self.assertEqual(r, {'a': 9, 'other': 5})
    def test_other_alone_under_min_pulls_next_smallest(self):
        r = drain.fold({'a': 9, 'b': 6, 'c': 1})          # other would be 1, recoverable by subtraction
        d = dict(map(tuple, r))
        self.assertGreaterEqual(d['other'], drain.MIN); self.assertEqual(sum(d.values()), 16)
    @unittest.expectedFailure
    def test_nothing_shown_under_min_including_other(self):
        # FINDING 1: with no cell at MIN or more, fold() cannot pull a big cell in, so it publishes "other" under MIN.
        for c in ({'a': 1}, {'a': 4, 'b': 4}, {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1}):
            for k, v in drain.fold(c):
                self.assertGreaterEqual(v, drain.MIN, (c, k, v))
    def test_total_kept_when_possible(self):
        c = {'a': 20, 'b': 7, 'c': 1, 'd': 2}
        self.assertEqual(sum(v for _, v in drain.fold(c)), sum(c.values()))


class Aggregate(unittest.TestCase):
    def agg(self, notes): return drain.aggregate(notes, SITES, TODAY)['a.example']
    def many(self, n, **kw):
        return [note(tab='%08x' % i, **kw) for i in range(n)]
    def test_small_person_day_hidden(self):
        d = self.agg(self.many(3))['days']['2026-11-27']['person']
        self.assertEqual(d, {'views': 0, 'visits': 0, 'under_min': True})
    def test_person_day_at_min_shown(self):
        d = self.agg(self.many(5))['days']['2026-11-27']['person']
        self.assertEqual((d['views'], d['visits']), (5, 5))
    def test_team_never_in_person_counts(self):
        r = self.agg(self.many(9, type='team'))
        self.assertEqual(r['pages'], []); self.assertEqual(r['countries'], [])
    def test_synthetic_and_crawler_not_in_pages(self):
        r = self.agg(self.many(9, type='synthetic') + self.many(9, type='crawler'))
        self.assertEqual(r['pages'], [])
    def test_countries_from_zone(self):
        r = self.agg(self.many(6, tz='Europe/London'))
        self.assertEqual(r['countries'], [['GB', 6]])
    def test_utc_and_etc_unknown(self):
        for z in ('UTC', 'Etc/GMT+5', ''):
            self.assertEqual(self.agg(self.many(6, tz=z))['countries'], [['unknown', 6]], z)
    def test_no_tab_id_or_zone_in_output(self):
        import json
        out = json.dumps(self.agg(self.many(6, tz='Europe/London', lang='en-GB')))
        for bad in ('abcdef01', '00000001', 'Europe/London', 'en-GB'): self.assertNotIn(bad, out)
    def test_old_notes_outside_window_not_in_pages(self):
        old = self.many(9, ts='2026-09-01T12:00Z')
        r = self.agg(old); self.assertEqual(r['pages'], [])
    @unittest.expectedFailure
    def test_one_tab_many_pages_publishes_nothing_under_min(self):
        # FINDING 1 again: a single visit shows as ['other', 1] in countries and pages.
        notes = [note(tab='aaaaaaaa', path='/p%d' % i) for i in range(8)]
        self.assertEqual(self.agg(notes)['countries'], [])
    def test_views_vs_visits(self):
        notes = [note(tab='aaaaaaaa', path='/p%d' % i) for i in range(6)]
        d = self.agg(notes)['days']['2026-11-27']['person']
        self.assertEqual(d.get('under_min'), True)                    # 1 visit, so hidden even with 6 views
    def test_days_table_recovers_small_cells(self):
        # Finding candidate: the per-day person row hides counts under MIN, but team/synthetic/crawler rows are exact,
        # so this only matters if a total is published elsewhere. Recorded, not asserted as a failure.
        r = self.agg(self.many(4) + self.many(7, type='team'))['days']['2026-11-27']
        self.assertEqual(r['team']['visits'], 7); self.assertTrue(r['person'].get('under_min'))


if __name__ == '__main__':
    unittest.main(verbosity=1)

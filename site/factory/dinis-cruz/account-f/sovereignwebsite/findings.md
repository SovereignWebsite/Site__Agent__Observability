# cl-6.observability-sw: findings on work/traffic/traffic_drain.py (draft 1)

2026-11-27T08:30Z. From the offline tests in tests/test_drain.py (31 tests, made-up notes, nothing live). Run: `python3 -I site/factory/dinis-cruz/account-f/sovereignwebsite/tests/test_drain.py`. Result: passes, with 3 expected failures that are the findings below. For observability.b to take or reject; I do not edit work/traffic/.

1. **A count under 5 can be published as "other".** `fold()` only pulls a big cell into "other" when one exists. With no cell at 5 or more, `fold({'a': 1})` returns `[['other', 1]]` and `fold({'a': 1, 'b': 2})` returns `[['other', 3]]`. A site with one person visit therefore publishes "pages: other 1" and "countries: other 1", against design.md ("never any count under 5"). Suggested fix: if no cell is at MIN or more, return an empty list (or one row with a flag and no number).
2. **A trailing newline passes every pattern.** The patterns end in `$`, which also matches before a final newline, so `/x\n` (path), a tab id, a language and a time zone each followed by a newline are accepted. Low impact (pages render with textContent), but use `re.fullmatch` or `\Z`.
3. **Recorded, not a defect:** `/<script>` passes the path check, as design.md only asks for a leading `/` and 200 characters. Every page that draws a path must use textContent (review 003, finding 1); the stats page draft will.
4. **To keep in mind for live mode:** `valid()` skips the one-hour window when `received` is None (offline). Live mode must always pass the append time.

Checked and fine: version, site list, type, path length, tab format, time format and impossible dates, the one-hour window, time zone and language shapes; team, synthetic and crawler never reach pages or countries; UTC, Etc/* and an empty zone count as "unknown"; no tab id, zone or language appears in the output; notes older than 28 days leave pages; one visit with many pages hides its day as under_min.

Not yet done: the one-country-per-zone limit of zone.tab (item 1 continues), and the independent read of traffic.js (item 2).

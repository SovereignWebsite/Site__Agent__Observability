# cl-6.observability-sw: plan (2026-11-26T16:58Z)

Written after reading observability.b's area (agent.json, now.md, role.md, restart.md, decisions.md, learnings.md, messages.md, both session notes), START.md and work/traffic/ (design.md draft 3, traffic.js draft 3, traffic_drain.py draft 1). I ran `node --check` on traffic.js (passes). I have not run the drain, and I hold no credential.

## 1. Where observability.b stands
- Done: design (draft 3, after Dinis's 23 Nov decisions), browser script, offline drain, security.b review 003 (pass with changes, applied), private vault f6m4m4zf with one tested lane.
- Parked: the pilot commit for security.b (script, traffic.json with the public append token, one pilot site's CSP, the stats page). Nothing goes live before security.b's yes.
- Open: work repository Site__Tool__Traffic (request 2026-11-24__work-repository); the twice-daily drain, approved but not scheduled while wakes are off; live mode of the drain, which still exits with "waits for the pilot vault".
- Constraint: observability.b is the only holder of the vault's enum key and append token. That stays so.

## 2. What account 6 can take (no credential, no live data)
| # | Work | Output, in my area unless said | Why it suits me |
|---|---|---|---|
| 1 | Hostile-note test suite for the drain: made-up notes covering each rule of `valid()` (security.b finding 1), subtraction cases for `fold()`, time-zone cases (UTC, Etc/*, zones with no country), a day with 1 to 4 person visits | tests/ with fixtures and a runner that calls traffic_drain.py read-only | Token-heavy, needs no secret |
| 2 | Independent review of traffic.js and traffic_drain.py against design.md and review 003, as a second pair of eyes before security.b | review note with findings, each with a failing example | A twin that did not write it reads it fresh |
| 3 | Pilot commit pieces that hold no secret: the CSP lines for sovereignweb.site, whois.tool and one agents page; a traffic.json template with a placeholder where the public append token goes; the footer link and the privacy note page | drafts/ | The token and the final commit stay observability.b's |
| 4 | The stats page (admin page that draws traffic.json) and the cross-site aggregate page for this site: layout, textContent-only rendering, accessibility, the 14 share tags | drafts/, checked with tools/check.sh | Design and front-end work |
| 5 | Reports on the totals once there are any: weekly note per site, what moved, what the "claims" caveat means for the reader | reports/ | Analysis, repeatable |
| 6 | A README and a "how to check it" for work/traffic/ that a new session can follow | drafts/ | Documentation |

## 3. What stays with observability.b
The live drain and its credentials, the vault f6m4m4zf, appending or listing lanes, the 1,000-pending lane measurements, requests to decisions.b (work repository, anything needing a signed record), security.b's reviews and replies, the final pilot commit, and `site/traffic/` publication. I never open a sealed credential file and never ask for a token.

## 4. How we split without duplicating
- One owner per file. Mine live under this area only; observability.b takes a draft by copying it into work/traffic/ or its own area and says so in its messages.md. I never edit work/traffic/ or account-b.
- Order: 1 and 2 first (they feed security.b's review and block nothing), then 3 and 4 when observability.b says the pilot commit is next, then 6, then 5 once totals exist.
- Before I start an item I send observability.b a one-line message naming it; it answers "yours", "mine" or "wait". Silence for one wake means yours for items 1, 2 and 6 only.
- Findings go to observability.b, not straight to security.b, unless Dinis says otherwise.
- cl-6.conductor-sw@SovereignWebsite.dinis is told of this plan by message so it sees account 6's load.

## 5. To decide
Dinis:
1. Does account 6 take items 1 to 6 as split above?
2. Who answers for SG/Send's write-token scope (still unnamed since 23 Nov)?
observability.b:
3. Agree the split, and say which items it wants first.
4. Which pilot site's CSP is first, and whether the stats page lives in each site's repository or only here.
5. Whether it wants my review notes as files in its area or only as messages.
cl-6.maestro:
6. Wake times (below); I set none myself.

## 6. Things I noticed on reading (to test, not yet findings)
- `zone_countries()` reads the system's zone.tab: the drain's machine must have tzdata, and each zone maps to one country, so a country can be undercounted. I will test it in item 1.
- `valid()` only checks the time window when `received` is given; live mode must pass it.
- `fold()` is applied to pages and countries but the per-day `under_min` flag on person visits sits beside the type totals; whether the days table plus the 28-day tables lets a small cell be recovered is for item 1 to check.

## 7. Proposed wakes (for cl-6.maestro to set)
Twice a day, after observability.b's drains once they exist: about 08:10 and 20:10 UTC. Until totals exist, once a day at 08:10 UTC is enough. Each wake: pull, read observability.b's now.md and messages for answers, do the next item, run `bash tools/check.sh`, push, update now.md and agent.json.

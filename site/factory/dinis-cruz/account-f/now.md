# cl-6.observability: now (2026-11-26T16:51Z)

State: started 26 Nov 2026 by cl-6.maestro. Key made with openssl (P-256 signing, RSA-4096 encryption), public half in site/keys/cl-6.observability.json, first commit signed with it. Installed openssh-client to sign (ssh-keygen was missing); noted as a tool install, not a grant change.

First view built: agents/ and agents.json (56 live sessions, 4 archived listed).

What it shows:
- Handover due (past 50% of the window): cl-6.abp (72.5%, within 10% of auto-compaction), cl-6.journalist (61.7%), cl-6.devops (54.0%), cl-6.accountant@dinis (53.1%).
- Close to 50%: cl-6.security@dinis, cl-6.decisions@dinis, cl-6.reviewer, cl-6.translator (47 to 48%).
- Repositories: cl-6.places has 38 attached against 1 to 3 for every other session. Its grant is not readable from here, so this is a count, not a finding of breach.
- Wakes into archived sessions: none. The old maestro's hourly wake is disabled.
- 18 sessions are idle or blocked with a needs_action (listed on the page).
- Account total reported cost USD 672.18. The largest: cl-6.security@PrompTugal 148.26, cl-6.infra 92.15, cl-6.dev 46.14.
- cl-6.places' own wake prompt still says to run each place as a sub-agent (it asked for the change itself).

Not known: grants, the maestro's pending-wakes.md, per-agent host logs. Cost is each session's own report, not an invoice.

Open:
- Offer this view to cl-6.security@dinis as the place the network capture lands (Dinis's capture ask; I have not read the decision record, it is in the maestro's repository).
- Wake times proposed to cl-6.maestro: 11:23 and 22:23 UTC.

Update 26 Nov 16:5x UTC:
- Wakes set by cl-6.maestro: 11:23 and 22:23 UTC.
- Network capture: cl-6.security's design (Site__Agent__Security, 6806128) waits on Dinis and binds me to nothing yet. If he says yes, my part is public totals only, as columns, from the auditor's daily file (day, agent, requests, refused, breaches, distinct_hosts). No host names on any public page.

- cl-6.places wake change waits on Dinis.

Wake 2026-11-26T22:25Z:
- Refreshed from list_sessions, get_session (18 sessions) and list_triggers (newest 20 wakes). 60 live sessions, reported cost USD 770.68.
- The four handovers flagged at 16:50 (abp, journalist, devops, accountant@dinis) were done; their wakes moved to the new sessions. No wake fires into an archived session (page 2 of older wakes not re-read).
- Handover due now: cl-6.data@PrompTugal 65.1%, cl-6.maestro 62.8% (a reset awaits Dinis's yes), cl-6.security@dinis 59.8%, cl-6.reviewer 57.2%. Near 50%: library 47.0%, ontologist 46.5%, translator (not re-read).
- 26 sessions idle with a needs_action, listed on the page.
- Not done: the maestro's public clone. cl-6.abp has not yet recorded the read route in my grant, so I did not clone it; the view uses session records only.

2026-11-26T22:26Z: cl-6.abp confirmed (message 22:26) that policy v1.7.8 lets me read github.com by GET for the owners SovereignWebsite and PrompTugal, so I made a read-only public clone of SovereignWebsite/Site__Agent__Maestro__Claude__6 (dev, depth 1, in my scratchpad) and read sessions.json, cost-events.json and pending-wakes.md. Read only, never written there; host github.com. Joined so far: planned wakes (11 PrompTugal sessions have none yet by design, each waiting on a named condition). Not yet joined: sessions.json and cost-events.json row by row.

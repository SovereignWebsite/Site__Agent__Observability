#!/usr/bin/env python3
"""cl-6.observability@dinis: make agents.json and agents/index.html from the table below.

The table is read by hand at each wake from list_sessions, get_session (status, model, environment,
repositories attached, context, reported cost, last update) and list_triggers (wakes). Never transcripts.
Run:  python3 -I build_view.py "<as_of from date -u>"
Flags are computed here, so a change in the table changes the flags.
"""
import json, html, sys, os

AS_OF = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
WINDOW = 1_000_000          # context_usage.max_tokens, every session
HANDOVER = 0.50             # Dinis's rule: past 50% of the window, a handover is due
NEAR = 0.45
COMPACT = 784_000           # autocompact threshold reported by the sessions
ENV = {
    "E1": ("env_01QjkpKDEi3KE4xQ1bGAZcnd", "the main cl-6 environment"),
    "E2": ("env_012qp7HrbRGSrefopgHs9qW9", "the environment of the newer sessions (this one, observability-sw, conductor-sw, place.london, social, conductor@PrompTugal)"),
    "E3": ("env_014fJkugLPBiSUBfBqSeK1G7", "the London-only environment (maestro's note: six official sites)"),
}
L = "Europe/Lisbon"
# name, project, model, env, repos, ctx_tokens, cost_usd, status, updated (UTC, 26 Nov unless dated), needs_action, wake
R = [
 ("cl-6.maestro@dinis","Account","opus","E1",1,409289,17.59,"RUNNING","16:48","","36 * * * * (UTC, hourly)"),
 ("cl-6.observability@dinis","Account","sonnet","E2",1,0,None,"RUNNING","16:47","","none yet (proposed)"),
 ("cl-6.observability-sw@SovereignWebsite","Sovereign Website","sonnet","E2",1,0,None,"RUNNING","16:47","","none yet"),
 ("cl-6.conductor-sw@SovereignWebsite","Sovereign Website","opus","E2",1,157809,2.23,"RUNNING","16:48","","47 9,18 * * * (UTC)"),
 ("cl-6.social@dinis","Account","sonnet","E2",1,111835,0.52,"IDLE","16:38","Scope or name unclear; waits for Dinis's answer","47 8 * * 1,3,4,5 (UTC)"),
 ("cl-6.conductor@PrompTugal","PrompTugal","opus","E2",1,114071,1.43,"IDLE","16:41","","none found"),
 ("cl-6.place.london@PrompTugal","PrompTugal","sonnet","E2",1,115596,0.62,"RUNNING","16:48","Asks whether London serves commuters and visitors as well as residents",f"25 7,18 * * * ({L})"),
 ("cl-6.data.london@PrompTugal","PrompTugal","sonnet","E3",1,110493,0.55,"REQUIRES_ACTION","16:48","Waits on a permission prompt: Update Environment","none found"),
 ("cl-6.conductor@CBR","CBR","opus","E1",2,243211,7.62,"IDLE","16:40","","none found"),
 ("cl-6.conductor@sgit","sgit","opus","E1",1,253245,4.81,"IDLE","15:56","Plan for 26 sessions and open questions in map.md","none found"),
 ("cl-6.security@dinis","Account","opus","E1",1,477986,19.75,"IDLE","16:47","","none found"),
 ("cl-6.decisions@dinis","Account","opus","E1",1,471987,22.86,"IDLE","16:42","","none found"),
 ("cl-6.accountant@dinis","Account","sonnet","E1",1,531282,14.24,"IDLE","16:47","","none found"),
 ("cl-6.strategy@dinis","Account","opus","E1",1,112537,0.93,"IDLE","25 Nov 23:18","","none found"),
 ("cl-6.helm@dinis","Account","opus","E1",1,91516,0.75,"IDLE","25 Nov 23:09","Waits for a go-ahead on its plan","none found"),
 ("cl-6.router@dinis","Account","opus","E1",1,212983,8.98,"IDLE","16:40","A notice for startups.b is stuck at router.a; needs a wake or a lane card","47 0,6,12,18 * * * (UTC)"),
 ("cl-6.infra@PrompTugal","PrompTugal","opus","E1",2,350311,92.15,"IDLE","16:43","Six-step checklist: merges, App permissions, a variable on the environment","none found"),
 ("cl-6.analyst@PrompTugal","PrompTugal","sonnet","E1",2,215688,3.53,"IDLE","11:18","",f"53 7,18 * * * ({L})"),
 ("cl-6.programme@PrompTugal","PrompTugal","sonnet","E1",2,190833,2.42,"IDLE","11:18","Choose the agenda: past archive, upcoming, or both",f"43 7,18 * * * ({L})"),
 ("cl-6.checker@PrompTugal","PrompTugal","sonnet","E1",2,369429,9.79,"IDLE","16:04","",f"13 8,19 * * * ({L})"),
 ("cl-6.curator@PrompTugal","PrompTugal","sonnet","E1",2,224529,3.78,"IDLE","11:18","",f"47 7,18 * * * ({L})"),
 ("cl-6.reviewer@PrompTugal","PrompTugal","sonnet","E1",2,478717,13.01,"IDLE","11:18","",f"3 8,19 * * * ({L})"),
 ("cl-6.customers@PrompTugal","PrompTugal","sonnet","E1",2,166392,1.91,"IDLE","11:19","Allow its board/keys.json push in the permission classifier",f"43 8,19 * * * ({L})"),
 ("cl-6.investors@PrompTugal","PrompTugal","sonnet","E1",2,176587,2.31,"IDLE","11:18","",f"33 9,20 * * * ({L})"),
 ("cl-6.backup@PrompTugal","PrompTugal","sonnet","E1",2,281974,5.37,"IDLE","11:18","Grant lacks history/ and add_repo; Dinis's backup destination",f"3 10,21 * * * ({L})"),
 ("cl-6.outreach@PrompTugal","PrompTugal","sonnet","E1",1,115938,0.89,"IDLE","11:18","Four self-reported breaches; decisions for Dinis","none found"),
 ("cl-6.researcher@PrompTugal","PrompTugal","sonnet","E1",2,280617,6.03,"IDLE","16:25","",f"33 7,18 * * * ({L})"),
 ("cl-6.historian@PrompTugal","PrompTugal","sonnet","E1",2,205928,3.59,"IDLE","11:18","Where history/ should live; hook kit",f"23 9,20 * * * ({L})"),
 ("cl-6.telemetry@PrompTugal","PrompTugal","sonnet","E1",2,286353,7.24,"IDLE","16:45","",f"13 10,21 * * * ({L})"),
 ("cl-6.translator@PrompTugal","PrompTugal","sonnet","E1",2,475707,14.21,"IDLE","12:44","",f"3 9,20 * * * ({L})"),
 ("cl-6.rights@PrompTugal","PrompTugal","sonnet","E1",2,366731,9.49,"IDLE","16:14","Dinis: is a bare credited link to an operator's page acceptable?",f"53 8,19 * * * ({L})"),
 ("cl-6.synthetic@PrompTugal","PrompTugal","sonnet","E1",2,209093,2.80,"IDLE","11:41","",f"13 9,20 * * * ({L})"),
 ("cl-6.sherpa@PrompTugal","PrompTugal","sonnet","E1",2,239381,3.62,"IDLE","11:18","",f"27 9,20 * * * ({L})"),
 ("cl-6.devops@PrompTugal","PrompTugal","sonnet","E1",2,539541,19.62,"IDLE","16:21","",f"7 8,19 * * * ({L})"),
 ("cl-6.observability@PrompTugal","PrompTugal","sonnet","E1",2,313573,6.48,"IDLE","11:18","","none found (drain waits for a wake)"),
 ("cl-6.ontologist@PrompTugal","PrompTugal","sonnet","E1",2,388774,9.87,"IDLE","12:04","",f"33 8,19 * * * ({L})"),
 ("cl-6.accountant@PrompTugal","PrompTugal","sonnet","E1",1,174447,2.63,"IDLE","16:46","Dinis's response to the cost proposal","none found"),
 ("cl-6.designer@PrompTugal","PrompTugal","sonnet","E1",2,327886,8.17,"IDLE","15:57","",f"23 8,19 * * * ({L})"),
 ("cl-6.places@PrompTugal","PrompTugal","sonnet","E1",38,392940,11.28,"IDLE","16:37","Its wake prompt still says run each place as a sub-agent; needs the prompt changed",f"23 7,18 * * * ({L})"),
 ("cl-6.correspondent@PrompTugal","PrompTugal","sonnet","E1",2,273855,5.92,"IDLE","16:31","",f"57 8,19 * * * ({L})"),
 ("cl-6.security@PrompTugal","PrompTugal","opus","E1",1,330558,148.26,"IDLE","16:48","",f"47 9,20 * * * ({L})"),
 ("cl-6.dev@PrompTugal","PrompTugal","sonnet","E1",2,403334,46.14,"RUNNING","16:42","",f"37 7,18 * * * ({L})"),
 ("cl-6.journalist@PrompTugal","PrompTugal","sonnet","E1",2,616997,22.87,"IDLE","16:19","",f"57 7,18 * * * ({L})"),
 ("cl-6.bulletins@PrompTugal","PrompTugal","sonnet","E1",2,238541,4.02,"IDLE","11:19","","none found"),
 ("cl-6.videos@PrompTugal","PrompTugal","sonnet","E1",2,250258,4.49,"IDLE","11:18","","none found"),
 ("cl-6.live@PrompTugal","PrompTugal","sonnet","E1",2,344078,8.09,"IDLE","11:18","Waits for Dinis on a pages.yml decision","none found"),
 ("cl-6.events@PrompTugal","PrompTugal","sonnet","E1",3,245630,4.83,"IDLE","16:00","","none found"),
 ("cl-6.cyber@PrompTugal","PrompTugal","sonnet","E1",2,394950,10.13,"IDLE","11:18","Dinis's decision on P6 and P9, and IaC #25","none found"),
 ("cl-6.signals@PrompTugal","PrompTugal","sonnet","E1",2,242090,4.39,"IDLE","11:19","","none found"),
 ("cl-6.library@PrompTugal","PrompTugal","sonnet","E1",2,434241,12.50,"IDLE","11:18","","none found"),
 ("cl-6.startups@PrompTugal","PrompTugal","sonnet","E1",2,278946,5.57,"IDLE","11:18","",f"13 7,18 * * * ({L})"),
 ("cl-6.civic@PrompTugal","PrompTugal","sonnet","E1",2,305665,6.42,"IDLE","11:19","",f"27 7,18 * * * ({L})"),
 ("cl-6.travel@PrompTugal","PrompTugal","sonnet","E1",2,222735,3.68,"IDLE","11:18","Choose the commit-check route; where history/ and review/ are granted","none found"),
 ("cl-6.weather@PrompTugal","PrompTugal","sonnet","E1",2,302870,4.90,"IDLE","11:19","",f"17 7,18 * * * ({L})"),
 ("cl-6.data@PrompTugal","PrompTugal","sonnet","E1",2,436175,13.77,"IDLE","16:37","Answer P9, add the App's permissions, merge IaC #31",f"3 7,18 * * * ({L})"),
 ("cl-6.abp@PrompTugal","PrompTugal","sonnet","E1",1,724839,23.13,"RUNNING","16:47","Install held: reply with the root anchor or the decisions signing key",f"37 10,21 * * * ({L})"),
]
ARCHIVED = [
 ("cl-6.maestro@dinis (replaced 26 Nov 13:43)","session_016CrbJJo93LZ9avM8raocz4","Its hourly wake trig_012aRpKUEt11SbM3c3brYYK1 is disabled: no wake fires into it."),
 ("cl-6.conductor@PrompTugal (replaced 26 Nov 16:38)","session_016CrbJKttr9TiHHDsuGnmF1","No wake found for it."),
 ("cl-6.swarm@PrompTugal","session_016CrbJNB2WPgCAvU2KSmRmY","No wake found for it."),
 ("cl-6.fringe@PrompTugal","session_016CrbJKaYmvvH9W9jBkyyHE","No wake found for it."),
]

# ---- delta of the 22:23 wake (get_session on the changed or risky ones; list_sessions for status and needs) ----
REPLACED = {"cl-6.abp@PrompTugal","cl-6.accountant@dinis","cl-6.devops@PrompTugal","cl-6.journalist@PrompTugal","cl-6.conductor-sw@SovereignWebsite"}
R = [r for r in R if r[0] not in REPLACED]
R += [
 ("cl-6.abp@PrompTugal","PrompTugal","sonnet","E2",1,298447,7.13,"IDLE","21:38","",f"37 10,21 * * * ({L})"),
 ("cl-6.accountant@dinis","Account","sonnet","E2",1,108169,0.56,"IDLE","17:58","","none found"),
 ("cl-6.devops@PrompTugal","PrompTugal","sonnet","E2",1,126589,1.09,"IDLE","21:07","Dinis's word to add_repo, to attach the website",f"7 8,19 * * * ({L})"),
 ("cl-6.journalist@PrompTugal","PrompTugal","sonnet","E1",1,415311,10.69,"IDLE","21:07","Dinis's add_repo word, or a route to attach the website with push",f"57 7,18 * * * ({L})"),
 ("cl-6.conductor@SovereignWebsite","Sovereign Website","opus","E2",1,217547,5.76,"IDLE","18:49","Decisions 2 to 5 in map.md; a route to the Factory for the signer-check patch","47 9,18 * * * (UTC)"),
 ("cl-6.onboarding@SovereignWebsite","Sovereign Website","sonnet","E2",1,141254,1.54,"IDLE","18:49","","7 8,16 * * * (UTC)"),
 ("cl-6.design@dinis","Sovereign Website","sonnet","E2",1,149149,1.19,"IDLE","20:42","","41 8,12,16,20 * * * (UTC)"),
 ("cl-6.librarian@dinis","Sovereign Website","sonnet","E2",1,100076,0.31,"IDLE","16:50","Add a push rule, or push 76eddf0 (unpushed work)","none found"),
 ("cl-6.studio@SovereignWebsite","Sovereign Website","opus","E2",1,255449,5.22,"IDLE","20:18","Three answers: proof of concept, eight questions, videos","17 10,20 * * * (UTC)"),
]
ARCHIVED += [
 ("cl-6.abp@PrompTugal (replaced 26 Nov 16:55)","session_016CrbJK3xXBhUMA6rucuPPd","Its wake moved to the new session (trig_01MzAd3PsDG8FtCVSxpCyCHT)."),
 ("cl-6.accountant@dinis (replaced 26 Nov 16:56)","session_016CrbJJ7NP5eaJypGAHgdGi","No wake found for it."),
 ("cl-6.devops@PrompTugal (replaced 26 Nov 16:56)","session_016CrbJLNFt4cFTXMVgkqcCY","Its wake moved to the new session (trig_01JkWz1fjbLfzWDfNwoh3CxH)."),
 ("cl-6.journalist@PrompTugal (replaced 26 Nov 16:56)","session_016CrbJLhtarwbcbxJnrF3bP","Its wake moved to the new session (trig_01ViGgyUxAJcR6QuyyjVreh4)."),
 ("cl-6.conductor-sw@SovereignWebsite (replaced 26 Nov 16:59)","session_016CrbJJDDrc1h8iMR8TwXKq","Its wake moved to the new session (trig_014R2LQTMRT45UGo1dkSk6sm)."),
]
GET = {  # name: (ctx, cost, status, needs); read by get_session at 22:25
 "cl-6.maestro@dinis":(627761,37.90,"IDLE","Website push access before 09:00 UTC; a yes to reset the maestro session"),
 "cl-6.security@dinis":(598355,32.11,"IDLE","Choose CI-check option (a) or (b)"),
 "cl-6.decisions@dinis":(92062,86.03,"IDLE","Reply on cost caps"),
 "cl-6.reviewer@PrompTugal":(572368,19.74,"IDLE","App repo access; a recorded approval for a draft"),
 "cl-6.dev@PrompTugal":(149451,68.43,"IDLE",""),
 "cl-6.library@PrompTugal":(469682,15.85,"IDLE",""),
 "cl-6.ontologist@PrompTugal":(465084,14.90,"IDLE",""),
 "cl-6.data@PrompTugal":(651147,27.63,"IDLE",""),
}
NEEDS = {  # from list_sessions at 22:24 (status only)
 "cl-6.programme@PrompTugal":"Word on the agenda; history/** in the ABP grant",
 "cl-6.customers@PrompTugal":"Allow its push and register its key; decide P5 and P11",
 "cl-6.backup@PrompTugal":"A backup destination; history/** and add_repo; read access to other repos",
 "cl-6.outreach@PrompTugal":"Whether to allow attaching the website",
 "cl-6.accountant@PrompTugal":"Dinis: a cap or ceiling level; where the ledger now lives",
 "cl-6.places@PrompTugal":"Dinis on grant P11 c (cl-6.abp has not applied it)",
 "cl-6.live@PrompTugal":"The pages.yml anchor decision",
 "cl-6.videos@PrompTugal":"Whether to push its key branch and open the key PR",
 "cl-6.events@PrompTugal":"Merge IaC #25; a word to open the key PR",
 "cl-6.civic@PrompTugal":"history/** and board/team/civic/** in its grant; its key in keys.json",
 "cl-6.travel@PrompTugal":"history/** and review/** write access",
 "cl-6.infra@PrompTugal":"Merges, the App's permissions, verify promptugal.news",
 "cl-6.data.london@PrompTugal":"Approve api.tfl.gov.uk read-only GET (abp, security, rights, Dinis)",
 "cl-6.place.london@PrompTugal":"TfL route, a dev pin change, security review, grant P11 c",
 "cl-6.router@dinis":"", "cl-6.analyst@PrompTugal":"", "cl-6.checker@PrompTugal":"", "cl-6.security@PrompTugal":"",
 "cl-6.cyber@PrompTugal":"", "cl-6.rights@PrompTugal":"", "cl-6.translator@PrompTugal":"", "cl-6.investors@PrompTugal":"",
 "cl-6.researcher@PrompTugal":"", "cl-6.historian@PrompTugal":"", "cl-6.signals@PrompTugal":"", "cl-6.bulletins@PrompTugal":"",
 "cl-6.weather@PrompTugal":"",
}
TIME = {"cl-6.conductor@PrompTugal":"21:19","cl-6.analyst@PrompTugal":"18:54","cl-6.programme@PrompTugal":"18:44","cl-6.checker@PrompTugal":"19:15",
 "cl-6.curator@PrompTugal":"19:06","cl-6.customers@PrompTugal":"19:43","cl-6.investors@PrompTugal":"20:34","cl-6.backup@PrompTugal":"21:04",
 "cl-6.outreach@PrompTugal":"18:38","cl-6.researcher@PrompTugal":"18:38","cl-6.historian@PrompTugal":"20:24","cl-6.telemetry@PrompTugal":"21:18",
 "cl-6.translator@PrompTugal":"20:10","cl-6.rights@PrompTugal":"19:55","cl-6.synthetic@PrompTugal":"20:15","cl-6.sherpa@PrompTugal":"20:34",
 "cl-6.observability@PrompTugal":"18:37","cl-6.ontologist@PrompTugal":"19:36","cl-6.accountant@PrompTugal":"21:18","cl-6.designer@PrompTugal":"20:34",
 "cl-6.places@PrompTugal":"18:49","cl-6.correspondent@PrompTugal":"20:11","cl-6.security@PrompTugal":"21:15","cl-6.bulletins@PrompTugal":"18:37",
 "cl-6.videos@PrompTugal":"18:37","cl-6.live@PrompTugal":"18:36","cl-6.events@PrompTugal":"18:36","cl-6.cyber@PrompTugal":"18:39",
 "cl-6.signals@PrompTugal":"18:37","cl-6.startups@PrompTugal":"18:40","cl-6.civic@PrompTugal":"18:36","cl-6.travel@PrompTugal":"18:36",
 "cl-6.weather@PrompTugal":"18:36","cl-6.router@dinis":"18:48","cl-6.infra@PrompTugal":"17:58","cl-6.place.london@PrompTugal":"18:26",
 "cl-6.data.london@PrompTugal":"17:25","cl-6.observability-sw@SovereignWebsite":"16:50","cl-6.observability@dinis":"22:24",
 "cl-6.maestro@dinis":"21:37","cl-6.security@dinis":"17:32","cl-6.decisions@dinis":"21:21","cl-6.dev@PrompTugal":"21:15",
 "cl-6.library@PrompTugal":"18:36","cl-6.data@PrompTugal":"18:36"}
RD = {}
_R=[]
for t in R:
    t=list(t); n=t[0]
    if n in GET: t[5],t[6],t[7],t[9]=GET[n][0],GET[n][1],GET[n][2],GET[n][3]; RD[n]="22:25"
    if n in NEEDS: t[9]=NEEDS[n]
    if n in TIME: t[8]=TIME[n]
    if n=="cl-6.observability@dinis": t[10]=f"23 11,22 * * * (UTC)"
    if n=="cl-6.observability-sw@SovereignWebsite": t[10]="13 8 * * * (UTC)"; t[7]="IDLE"
    if n in ("cl-6.data.london@PrompTugal",): t[7]="IDLE"; t[10]="23 6,17 * * * (UTC)"
    if n=="cl-6.place.london@PrompTugal": t[7]="IDLE"
    if n=="cl-6.dev@PrompTugal": pass
    _R.append(tuple(t))
R=_R
NEW_NAMES={"cl-6.abp@PrompTugal","cl-6.accountant@dinis","cl-6.devops@PrompTugal","cl-6.journalist@PrompTugal","cl-6.conductor@SovereignWebsite","cl-6.onboarding@SovereignWebsite","cl-6.design@dinis","cl-6.librarian@dinis","cl-6.studio@SovereignWebsite"}
for n in NEW_NAMES: RD[n]="22:25"

rows = []
for n, proj, model, env, repos, ctx, cost, st, upd, needs, wake in R:
    pct = ctx / WINDOW
    flags = []
    if pct >= HANDOVER: flags.append("handover due (past 50% of the window)")
    elif pct >= NEAR: flags.append("near 50% of the window")
    if ctx >= 0.9 * COMPACT: flags.append("within 10% of the auto-compaction threshold")
    if repos > 2: flags.append(f"{repos} repositories attached; its grant is not readable from here, but this is far above the others")
    if needs and st in ("IDLE", "REQUIRES_ACTION"): flags.append("waiting on a person with a needs_action")
    rows.append(dict(name=n, project=proj, model=model, environment=env, repos_attached=repos,
                     context_used=ctx, context_pct=round(pct * 100, 1), reported_cost_usd=cost, status=st,
                     last_activity=upd, context_read=RD.get(n,'16:50'), needs_action=needs, wake=wake, flags=flags))

total = round(sum(r["reported_cost_usd"] or 0 for r in rows), 2)
fl = lambda key: [r["name"] for r in rows if any(f.startswith(key) for f in r["flags"])]
summary = dict(
    sessions_live=len(rows), archived_listed=len(ARCHIVED), reported_cost_usd_total=total,
    handover_due=fl("handover due"), near_half=fl("near 50%"), near_compaction=fl("within 10%"),
    more_repos_than_expected=fl(f"{max(r['repos_attached'] for r in rows)} repositories"),
    idle_with_needs_action=[r["name"] for r in rows if r["needs_action"] and r["status"] in ("IDLE", "REQUIRES_ACTION")],
    wake_into_archived=[], live_without_wake=[r["name"] for r in rows if r["wake"].startswith("none")],
)
out = dict(agent="cl-6.observability@dinis", as_of=AS_OF, window_tokens=WINDOW,
           method="list_sessions, get_session and list_triggers only; no transcript read. Cost is the figure each session reports (usage.cost_usd), not an invoice. Context is used_tokens at the time read.",
           not_known=["Grants: the maestro's sessions.json and the ABP grants are in repositories this session may not read (grant: this repository only), so repositories attached are counted, not compared with a grant.",
                      "Wakes: only triggers visible to this account are listed; the maestro's pending-wakes.md was not read."],
           environments={k: dict(id=v[0], note=v[1]) for k, v in ENV.items()},
           summary=summary, sessions=rows,
           archived=[dict(name=a, id=i, wake_note=w) for a, i, w in ARCHIVED])
json.dump(out, open(os.path.join(HERE, "agents.json"), "w"), indent=1); open(os.path.join(HERE, "agents.json"), "a").write("\n")

# ---------- page ----------
e = html.escape
def li(items): return "".join(f"<li>{e(x)}</li>" for x in items) or "<li>None.</li>"
trs = []
for r in sorted(rows, key=lambda r: -r["context_used"]):
    cls = "hot" if any(f.startswith("handover") for f in r["flags"]) else ("warn" if r["flags"] else "")
    cost = "n/a" if r["reported_cost_usd"] is None else f"{r['reported_cost_usd']:.2f}"
    trs.append(f"<tr class='{cls}'><th scope='row'>{e(r['name'])}</th><td>{e(r['project'])}</td><td>{e(r['model'])}</td><td>{r['environment']}</td>"
               f"<td class='n'>{r['repos_attached']}</td><td class='n'>{r['context_pct']}% ({r['context_read']})</td><td class='n'>{cost}</td><td>{e(r['status'].lower().replace('_',' '))}</td>"
               f"<td>{e(r['last_activity'])}</td><td>{e(r['wake'])}</td><td>{e('; '.join(r['flags'])) or '&nbsp;'}</td></tr>")
envs = "".join(f"<li><strong>{k}</strong>: {e(v[0])}, {e(v[1])}.</li>" for k, v in ENV.items())
arch = "".join(f"<li>{e(a)} ({e(i)}): {e(w)}</li>" for a, i, w in ARCHIVED)
head = open(os.path.join(HERE, "..", "..", "..", "policy", "index.html")).read().split("<link rel=\"stylesheet\"")[0]
T = "Account 6 agents: observability"
D = "Every agent session on Claude account 6: model, environment, repositories, context used, reported cost, wake and what needs attention."
U = "https://observability.agents.sovereignweb.site/factory/dinis-cruz/account-f/agents/"
import re
head = re.sub(r"<title>.*?</title>", f"<title>{T}</title>", head)
head = re.sub(r'(<meta name="description" content=)"[^"]*"', rf'\1"{D}"', head)
head = re.sub(r'(<meta property="og:url" content=)"[^"]*"', rf'\1"{U}"', head)
head = re.sub(r'(<meta property="og:title" content=)"[^"]*"', rf'\1"{T}"', head)
head = re.sub(r'(<meta property="og:description" content=)"[^"]*"', rf'\1"{D}"', head)
head = re.sub(r'(<meta name="twitter:title" content=)"[^"]*"', rf'\1"{T}"', head)
head = re.sub(r'(<meta name="twitter:description" content=)"[^"]*"', rf'\1"{D}"', head)
head = re.sub(r'(<link rel="canonical" href=)"[^"]*"', rf'\1"{U}"', head)
page = head + """<style>
:root{--bg:#f7f7f5;--fg:#1d1d1b;--muted:#4f4f4a;--line:#c9c9c2;--card:#fff;--hot:#fde2e0;--warn:#fff3d6;--accent:#0b5cad}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--fg:#ededea;--muted:#b4b4ae;--line:#4a4a45;--card:#1c1c1a;--hot:#4a1d1a;--warn:#41330f;--accent:#7ab8ff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,sans-serif}
main{max-width:78rem;margin:0 auto;padding:2rem 1rem 3rem}h1{font-size:1.8rem;margin:.3rem 0}h2{margin-top:2rem}a{color:var(--accent)}
.mark{font:600 .78rem/1 system-ui;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}p,li{max-width:62rem}
.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:.85rem}th,td{padding:.35rem .5rem;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
thead th{position:sticky;top:0;background:var(--card)}td.n{text-align:right;font-variant-numeric:tabular-nums}
tr.hot{background:var(--hot)}tr.warn{background:var(--warn)}.skip{position:absolute;left:-999px}.skip:focus{left:1rem;top:1rem}
.top{padding:.6rem 1rem;border-bottom:1px solid var(--line)}
</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><a href="/">observability.b</a></header>
<main id="main">
<div class="mark">cl-6.observability@dinis</div>
<h1>Account 6: the agents, watched</h1>
<p>As of """ + e(AS_OF) + """. """ + str(len(rows)) + """ live sessions, reported cost USD """ + f"{total:.2f}" + """ in all. The data is <a href="../agents.json">agents.json</a>. Read from session records and wakes only, never transcripts. Cost is what each session reports, not an invoice. Context and cost are read at the time shown in brackets; rows read at 16:50 were not read again at 22:25 and are older. Times are UTC unless a wake says Europe/Lisbon (UTC in November).</p>
<h2>Flags</h2>
<ul>
<li><strong>Handover due (past 50% of the window):</strong> """ + e(", ".join(summary["handover_due"]) or "none") + """.</li>
<li><strong>Close to 50% (45 to 50%):</strong> """ + e(", ".join(summary["near_half"]) or "none") + """.</li>
<li><strong>Within 10% of the auto-compaction threshold (784,000 tokens):</strong> """ + e(", ".join(summary["near_compaction"]) or "none") + """.</li>
<li><strong>More repositories than the rest:</strong> """ + e(", ".join(summary["more_repos_than_expected"]) or "none") + """. Its grant is not readable from here, so this is a count, not a breach.</li>
<li><strong>A wake firing into an archived session:</strong> none found. The old maestro's hourly wake is disabled.</li>
<li><strong>Idle or blocked with a needs_action:</strong> """ + str(len(summary["idle_with_needs_action"])) + """ sessions: """ + e(", ".join(summary["idle_with_needs_action"])) + """.</li>
<li><strong>Live with no wake found:</strong> """ + str(len(summary["live_without_wake"])) + """ sessions (the table says which).</li>
</ul>
<h2>Sessions, by context used</h2>
<div class="wrap" tabindex="0" role="region" aria-label="Sessions table"><table>
<thead><tr><th scope="col">Session</th><th scope="col">Project</th><th scope="col">Model</th><th scope="col">Env</th><th scope="col">Repos</th><th scope="col">Context (read at)</th><th scope="col">USD</th><th scope="col">Status</th><th scope="col">Updated</th><th scope="col">Wake</th><th scope="col">Flags</th></tr></thead>
<tbody>
""" + "\n".join(trs) + """
</tbody></table></div>
<h2>Environments</h2>
<ul>""" + envs + """</ul>
<h2>Archived</h2>
<ul>""" + arch + """</ul>
<h2>What this view does not know</h2>
<ul>""" + li(out["not_known"]) + """</ul>
</main>
</body>
</html>
"""
os.makedirs(os.path.join(HERE, "agents"), exist_ok=True)
open(os.path.join(HERE, "agents", "index.html"), "w").write(page)
print(json.dumps(summary, indent=1))

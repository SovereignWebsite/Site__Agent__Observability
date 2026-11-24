# Traffic for every SovereignWebsite site: the design (draft 3, after Dinis's decisions of 23 Nov)

observability.b@SovereignWebsite.dinis, 20 November 2026. Draft for Dinis; nothing is live, no vault or lane exists yet.

## What it reuses
Dinis, 20 Nov: "we already done these tons of other websites ... see how they did it". The working precedent is the SGit-AI PHP story site (php.oct.2026.newsroom.sgit.ai, repository SGit-AI__Website__Newsroom__2026__Oct__PHP):
- `assets/telemetry.js`: one event per page per tab, encrypted in the browser (sgit hybrid envelope v2) to a private vault's public key and POSTed to a write-only append lane on SG/Send (`/api/vault/append/write/<vault_id>`), with several lanes and fall-over when one is full;
- `data/telemetry.json`: the endpoint, vault id, public append tokens, the public key, the two location services (ipapi.co, then ipwho.is), and the plain-words policy;
- `admin/build/telemetry_drain.py`, `telemetry_classes.py`, `telemetry_publish.py`: drain, classify (readers, team, synthetic, crawlers), publish counts only;
- its lessons: honour Do Not Track and Global Privacy Control; send nothing from localhost or copies; cap each tab at 40 events (a crawler once sent 960 and filled the lane for 4 3/4 hours); read the location service's answer without ever reading its `ip` field; the page's Content-Security-Policy names exactly the location services and the vault server.
The newsroom (newsroom.sgit.ai) and PrompTugal.news use the same lane mechanism (PrompTugal's `newsroom/tools/obs/obs_drain.py`, from web-summit.sgit.ai).

## Decided by Dinis, 23 Nov 2026 15:54 UTC (record 2026-11-23__observability-pilot)
"ok, can you sign all those that you recommend (I just reviewed them and they are ok)", approving decisions.b's recommendations:
- **No third-party location service.** freeipapi.com does not see visitors' IP addresses. The browser sends its time zone and first language; the drain estimates the country from the time zone (the system's zone table). Region and city are no longer collected.
- Yes to a pilot on sovereignweb.site, whois.tool and one agents page.
- Yes to a twice-daily drain publishing totals.
- Yes to separate vaults for traffic and feedback.
- Still his to name: who answers for SG/Send's write-token scope.
Sections below that mention a location service, region or city are superseded by this.

## 1. The shared piece: `seed/shared/traffic.js` (via factory.b)
Per page, from the site's own hosts only, unless DNT or GPC is set:
- **event**: `{v, site, path, ts (to the minute, UTC), country, region, city, type, tab}`; `tab` is a random id that lives only for the tab.
- **location once per visit, not per page**: the first page of a tab asks the location service; the answer's country, region and city (never its `ip`) are kept in the tab's session storage and reused for every later page in that tab. Nothing else is kept on the device between pages.
- **type** of visitor:
  - `team`: a browser that Dinis's team or an agent has marked on the site's admin page (one local-storage flag, `sw.traffic.who=team`; the only thing kept between visits, so our own visits do not count as readers; a person can clear it there);
  - `synthetic`: design.b.rounds's synthetic users, by a marker they set (proposed: `?sw-synthetic=1` on their first URL, kept for the tab, or a user-agent suffix; to agree with design.b);
  - `crawler`: by user agent (Googlebot, bingbot, Applebot, DuckDuckBot, YandexBot, Baiduspider, Lighthouse, anything with bot/crawler/spider) and automation signs (`navigator.webdriver`, HeadlessChrome); the PHP site's list, extended;
  - `person`: everyone else.
- **no cookies**, no fingerprinting, no IP stored or sent on by us, no user-agent string sent (only the class).

## 1a. Which location service
The PHP site uses ipapi.co first, but ipapi.co's pricing page now calls its free tier a trial "not for production use", so we should not. Checked on 20 Nov against each service's own pages (HTTPS, browser calls with no secret, free limit, commercial use, city and region):
- **freeipapi.com** (first): HTTPS, no key, browser calls work, 60 a minute, commercial use allowed, returns region and city; Düsseldorf, Germany; keeps request logs for an unstated time.
- **ipwho.is** (fallback): HTTPS, no key, commercial use allowed, region and city; 1,000 a day, but its documentation also says browser calls are counted per domain, which could cap a busy site; its privacy page does not name its company or country.
- Ruled out: ip-api.com (no HTTPS on free, non-commercial only), ipapi.co (trial only), ipinfo Lite (country only, token in the page), ipwhois.app (no browser calls on free), ipregistry (one-off test credits), country.is (city came back empty).
With one lookup per visit, each visitor causes one request.

## 2. The collector
One **private telemetry vault** for all sites on SG/Send, with **a set of append lanes per site**, so one busy or attacked site cannot fill another's. Written from the browser with public append tokens (write-only); read only by my drain with the enum key, which never enters a repository. The service's spec (SG/Send v0.34.1, https://dev.send.sgraph.ai/api/openapi.json, checked by hub.b on 20 Nov) lists `POST /api/vault/append/{write,list,fetch,mark-processed,purge,configure}/{vault_id}` and allows browser calls from any origin, but documents no size limit, rate limit, lane count or how lanes are made. The only figure we have is from the PHP site's own notes, not the spec: 1,000 waiting records per token, then 507. So the pilot will measure the limits, the script will fall over to the next lane on 507, 404 or 5xx as the PHP site's does, and the design will not rely on an undocumented limit.

Every record is an untrusted claim: the tokens and public key are public by design, so anyone can add rows. The drain drops malformed records, caps per tab, and the published counts say they are counts of claims.

## 3. What is published
After each drain (proposed twice a day):
- **per site**: `site/traffic/traffic.json` in the site's own public repository (through that site's writer), drawn on the site's admin page;
- **across sites**: one aggregate on observability.agents.sovereignweb.site (factory.b makes it when Dinis says yes).

Contents: page views and visits per UTC day, by type; and, for `person` visits only, by page, country, region and city.
Never: a row, a tab id, a time finer than the day, an IP, a user agent, or any count under **5** (folded into "other"). City and region are shown over the last 28 days, not per day, so a lone visitor from a small town cannot be picked out on a given date. Team visits are one total, never split by person or place.

## 4. The privacy note (Dinis: "the privacy note is fine")
On every site, linked from the footer:
> This site counts its visitors without cookies and without asking anyone else where you are. Each page you open sends one encrypted note to our vault: the page, the time, your browser's time zone and language (from which we estimate your country), a random number that lasts only while this tab is open, and whether the visit looks like a person, a search engine or one of our own tests. We never see, keep or pass on your IP address. Your browser keeps that number, the place and a count of pages in this tab's session storage, which is cleared when you close the tab. Only country totals are published, never under five, and they are indicative: anyone can send notes. With Do Not Track or Global Privacy Control set, nothing is sent at all.

## Decided by Dinis (20 Nov, relayed by the conductor at 20:50 UTC)
"you can take away the no tracking and add the privacy note, and visitors don't need to be asked first ... we have no cookies ... we just have an ID which we don't track to users."
- A privacy note; no asking first; no cookies; country, region and city only.
- The only id is the tab id: random, kept in the tab's session storage, gone when the tab closes, never linked across visits. The team flag holds no id.

## Proposed rule for every site's CLAUDE.md (to factory.b for the seed)
Replace "no cookies, no tracking." with:
"no cookies. Visits are counted only as the site's privacy note says: one location lookup per visit (country, region, city), an encrypted note per page with a random id that lasts only for the tab, published as totals. Never an IP address, a user-agent string, or anything that follows a person across visits."

## security.b's review 003 (20:49 UTC): pass with changes
1. Every note is hostile: the drain validates each decrypted note and drops failures (v 1; site in the known list; path starts with / and is at most 200 characters; type one of four; country two capital letters; region and city at most 80 letters, spaces and . ' -; ts within an hour of the append time). Pages render with textContent only; any CSV export guards cells starting = + - @.
2. One location provider only (freeipapi.com), named with its privacy policy in the note, which says it sees the IP address and the site. security.b's preferred option, the country from SG/Send's side so no third party is involved, is not offered by the service's documented API; I will ask hub.b whether it could be.
3. To confirm in the pilot: an append token can only append, and a full lane affects only that lane. Published counts are labelled indicative.
4. Every site's CSP: the script as a file under script-src 'self'; connect-src exactly 'self', the SG/Send host and freeipapi's host.
5. Region and city only as 28-day totals per site, never per page or per day, and no published total that, minus others, leaves a cell under 5. Team and synthetic never in person counts.
6. Done in the script: provider strings checked character by character; sw-synthetic=1 documented (a visitor can use it to drop out of person counts); session storage named in the note.

## Before anything goes live
- security.b reviews the script, the collector and the published files.
- accountant.b's budget checkpoints: tell it and Dinis before the design and pilot pass 15 USD, or a drain run passes 1 USD.
- Dinis: yes to the pilot sites (proposed: sovereignweb.site's main site, whois.tool and one agents page), then every site.
- Dinis: yes to the twice-daily drain.

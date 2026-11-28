# cl-6.observability-sw: independent read of work/traffic/traffic.js (draft 3)

2026-11-28T08:40Z. Item 2 of plan.md. Read against design.md and review 003, and run in a fake browser (tests/test_script.mjs: 11 checks, all pass). The test uses this agent's own public key as the recipient and its own private key to open the note, so no vault, token or observability.b key is involved. Run from the repository root: `SW_PRIV=<private pem> SW_PUB=<public pem> node site/factory/dinis-cruz/account-f/sovereignwebsite/tests/test_script.mjs`. For observability.b to take or reject; `work/traffic/` is not edited.

## Confirmed by test
- One page sends one POST to `/api/vault/append/write/<vault>` with only `append_token` and `payload`, no credentials, no referrer.
- The envelope opens with RSA-OAEP-SHA-256 and AES-256-GCM (the sgit v2 shape the design names), and the note holds exactly `v, site, path, ts, tz, lang, type, tab`. No user-agent text, no query or hash.
- Do Not Track, Global Privacy Control, localhost, plain http and a host missing from the config each send nothing.
- Types: crawler (bot user agent, webdriver), team (local flag), synthetic (`?sw-synthetic=1`), else person.
- The same page twice in a tab sends once; the cap is 40 notes per tab; 507 moves to the next lane, 400 does not; the device keeps only `sw.traffic.*` session keys and nothing in local storage unless the team flag is set.

## Questions and small points (none blocks the pilot)
1. **Paths can carry data.** The path is sent unfiltered (up to 200 characters). On a site where a path holds something a visitor typed or looked up (for example a tool page with a domain in the URL), the private vault would hold it, and the drain would publish it in pages if five people share it. Which pilot pages have such paths? whois.tool is the one to check. A per-site allowlist or a rule to drop path segments after a depth is a design choice for observability.b and security.b.
2. **`sw-synthetic=1` is a public switch.** Anyone can drop out of the person counts by adding it to a URL. Already documented in review 003 (finding 6); the privacy note should say so.
3. **Bot test is a user-agent list.** It will miss unlisted crawlers, so person counts are an upper bound; the published "indicative" label covers it. Not tested beyond the three cases above.
4. **Location, lanes, config:** the lane is chosen from the tab id, so one tab always starts on the same lane; fine. `/traffic.json` is fetched with no-store on every page that passes the Do Not Track check, an extra request per page; acceptable.
5. **Not covered:** a real browser (Playwright run against a pilot page) and the exact CSP in force; both belong to the pilot drafts (item 3).

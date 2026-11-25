# observability.b: restart

How a new session of observability.b@SovereignWebsite.dinis takes over. Read START.md at the root of this repository too.

## Repositories to attach
| Repository | Access | Why |
|---|---|---|
| SovereignWebsite/Site__Agent__Observability | push | this agent's home: area, work/traffic/, decision requests |
| SovereignWebsite/SovereignWebsite__Factory | read | team rules, team/keys.json, the signing how-to |
| SovereignWebsite/Site__Tool__Traffic | push, once it exists | the work repository (requested, not yet made) |

## Scheduled wakes
None. The twice-daily drain is approved but must not be scheduled until Dinis re-enables wakes.

## Key
1. `sgit pki keygen --label observability.b@SovereignWebsite.dinis`; it asks for a passphrase twice: keep a random one in a 0600 file outside any repository and pipe it in.
2. `sgit pki export <fingerprint>` and send the public bundle to the conductor for the Factory's team/keys.json (this repository's CLAUDE.md forbids writing a key here by hand; site/key.json is made at deploy from that list).
3. For commit signing, follow the Factory's board/workflow/2026-11-20__signing-with-your-key.md: write the signing private half as an unprotected OpenSSH file (0600, outside any repository), check its public half matches the bundle, then set gpg.format ssh, user.signingkey and commit.gpgsign in the clone.

## Vault and lane keys held (re-seal each to the new key)
| Vault | What this agent holds | Who holds the vault key |
|---|---|---|
| f6m4m4zf (traffic-observability-b, dev.send.sgraph.ai) | enum key and one append token (one lane) | b.maestro |

Ask b.maestro to re-seal the enum key and append token to the new key; open the sealed file with `sgit pki decrypt`, verify b.maestro's signature, keep the result in a 0600 file, never print it.

## First steps
1. Read START.md, then this area: agent.json, now.md, the newest sessions/*/handover.md, learnings.md, decisions.md.
2. Make and publish the key (above); re-seal the vault credentials (above).
3. Pull dev; run `node --check work/traffic/traffic.js` and the drain on test notes (README, "How to check it").
4. Update agent.json and now.md; tell b.maestro the takeover is done.
5. Continue with the open work in now.md.

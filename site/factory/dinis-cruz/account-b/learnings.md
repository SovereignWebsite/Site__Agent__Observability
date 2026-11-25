# observability.b: learnings

- The working precedent is SGit-AI's PHP story site (assets/telemetry.js): encrypted notes to append lanes, a 40-per-tab cap, Do Not Track and GPC honoured.
- ipapi.co's free tier is a trial "not for production use"; Dinis then chose no third-party location service at all (23 Nov).
- SG/Send's published spec documents the append endpoints but no limits; the authors' own page (cli.sgit.ai/api/append-lanes) does: 5 MB per payload, 1000 pending per token (507), token can only write its own lane.
- configure replaces the anchor list: adding a lane must resend every anchor.
- sgit pki keygen in a container needs a passphrase; keep it in a 0600 file.
- A helper defined inside a try block is not visible to functions declared outside it: the first draft would have failed silently on every page.
- Seal and verify: a sealed file from another agent carries its signature inside the sgit envelope; `sgit pki decrypt` verifies it against an imported contact. Import the sender's key from two published copies first and compare fingerprints.
- An append token used as an enum key gets 404 on list and on fetch with a real file id; without a write key, purge gets 401.
- Write and publish nothing that holds a session id, key, token or private name in a handover file.

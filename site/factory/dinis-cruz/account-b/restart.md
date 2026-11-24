# observability.b: restart

If this session ends, a fresh one starts from START.md at the root of SovereignWebsite/Site__Agent__Observability.

What a fresh session needs that is not in the repository:
- its own sgit key (make a new one; the old private half dies with this container), published through the conductor into the Factory team/keys.json;
- the traffic vault's enum key and append token: ask b.maestro to re-seal them to the new key (b.maestro holds the vault key, record 2026-11-24__block-05);
- re-run the review 030 checks before sealing anything to b.maestro.

Everything else (design, script, drain, decisions, open work) is in this repository.

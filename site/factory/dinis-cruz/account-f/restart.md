# cl-6.observability: restart

A new session of cl-6.observability@dinis:
1. Read CLAUDE.md at the repository root, then this area. START.md is observability.b's; follow the parts that apply (key, signing, check.sh).
2. Key: openssl P-256 (signing) and RSA-4096 (encryption), private halves in ~/.sw-secret mode 600, never printed or committed. A new session makes a new key, publishes it alone in its first commit as site/keys/cl-6.observability.json, and asks cl-6.maestro to retire the old one.
3. Git signing: gpg.format ssh, user.signingkey a .pub path, gpg.ssh.program ssh-keygen (install openssh-client if missing). Trailers: Agent: cl-6.observability@dinis and Claude-Session: <session URL>.
4. Refresh the view: gather list_sessions, get_session and list_triggers, edit the table in build_view.py, run python3 -I build_view.py "$(date -u +%Y-%m-%dT%H:%MZ)", then bash tools/check.sh, then push to dev (never main).
5. Tell cl-6.maestro@dinis the link, only what changed.
Repositories to attach: this one only.
Wakes: 11:23 and 22:23 UTC, set by cl-6.maestro.

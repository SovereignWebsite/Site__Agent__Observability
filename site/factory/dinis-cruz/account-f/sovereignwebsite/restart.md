# cl-6.observability-sw: restart

How a new session of cl-6.observability-sw@SovereignWebsite.dinis takes over.

1. Read CLAUDE.md and START.md at the root, then this area (agent.json, now.md, plan.md) and observability.b's area (site/factory/dinis-cruz/account-b/) and work/traffic/ (read only).
2. Key: make your own with openssl (P-256 signing, RSA-4096 encryption), private halves in mode 600 files outside the repository (here ~/.sw-secret), the public bundle only in site/keys/<name>.json. Git signs with an OpenSSH copy of the signing key (gpg.format ssh, gpg.ssh.program ssh-keygen; install openssh-client if it is missing). Check the public half matches before the first commit.
3. Trailers in one block: Agent:, Claude-Session:, Co-Authored-By:. Dev only. `bash tools/check.sh` before every push.
4. Attach nothing: this grant is this repository only. No scheduled task; wakes belong to cl-6.maestro.
5. Continue with now.md.

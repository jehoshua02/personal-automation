# Predictable Secret Filename

## Abstract

Rename the OAuth client secret to a predictable filename so users don't need to modify docker-compose.yml.

## Priority: 45

- Value: 4/10 — Quality-of-life for setup. Only matters for new clones or new users.
- Momentum: 1/10 — No work started.
- Effort: 1/10 — Rename one file, update one line in docker-compose.yml, update README.
- Risk: 2/10 — Low risk. File rename is easily reversible. Must ensure .gitignore covers the new name.

## Timeline

- Captured: 2026-04-27

## Details

### Research findings

- Host file: `secrets/client_secret_250820501274-oaj382clma3s5jt90rqqq7gfcf0m7lml.apps.googleusercontent.com.json`
- docker-compose.yml volume mount already maps it to `/secrets/client_secret.json` inside the container
- Problem: host-side source path includes the Google-generated client ID. New users must either rename their file to match or edit docker-compose.yml
- `.gitignore` includes `secrets/` so the rename won't affect tracked files

### Implementation plan

1. Rename host file: `secrets/client_secret_250820501274-...json` → `secrets/client_secret.json`
2. Update docker-compose.yml volume mount: `./secrets/client_secret.json:/secrets/client_secret.json:ro`
3. Update README.md setup instructions to say "save as `secrets/client_secret.json`"
4. Verify containers still start and auth still works

## Verification

- `docker compose up auth` starts without error
- OAuth flow completes successfully
- README instructions are clear

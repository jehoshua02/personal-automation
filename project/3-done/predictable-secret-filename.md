# Predictable Secret Filename

## Abstract

Rename the OAuth client secret to a predictable filename so users don't need to modify docker-compose.yml.

## Priority: 32

- Value: 4/10 — Quality-of-life for setup.
- Momentum: 1/10 — No work started.
- Effort: 1/10 — Rename one file, update one line in docker-compose.yml, update README.
- Risk: 2/10 — Low risk.

## Timeline

- Captured: 2026-04-27
- Refined: 2026-04-27
- Started: 2026-04-27
- Verified: 2026-04-27
- Done: 2026-04-27

## Details

- Renamed `secrets/client_secret_250820501274-...json` → `secrets/google_oauth_client_secret.json`
- Updated docker-compose.yml volume mount
- Simplified README setup instructions — no longer need to edit docker-compose.yml
- Name includes "google_oauth" for clarity on what the secret is for

## Verification

- Auth service starts and passes health check after rename
- `curl http://localhost:8080/health` → `{"status":"ok"}`

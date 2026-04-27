# Service READMEs

## Abstract

Add a README.md to each service directory with standard sections covering purpose, API contract, configuration, and testing.

## Priority: 54

- Value: 3/10 — Documentation. Nice to have, not blocking anything.
- Momentum: 1/10 — No work started. No existing READMEs in any service.
- Effort: 4/10 — 7 services to document. Moderate but repetitive work.
- Risk: 1/10 — Zero risk. Just documentation files.

## Timeline

- Captured: 2026-04-27

## Details

### Research findings

7 services, none have READMEs:

| Service | Files |
|---|---|
| auth | app.py, oauth.py, Dockerfile, requirements.txt, tests/ |
| gmail-reader | app.py, gmail.py, Dockerfile, requirements.txt, tests/ |
| llm-processor | app.py, Dockerfile, requirements.txt, tests/ |
| task-writer | app.py, Dockerfile, requirements.txt, tests/ |
| calendar-writer | app.py, calendar_writer.py, Dockerfile, requirements.txt, tests/ |
| note-writer | app.py, notes.py, Dockerfile, requirements.txt (no tests) |
| orchestrator | app.py, orchestrator.py, Dockerfile, requirements.txt, tests/ |

### Implementation plan

For each service, create `services/{name}/README.md` with:
1. **Purpose** — one-liner what the service does
2. **API Contract** — endpoints, request/response format
3. **Configuration** — env vars, volume mounts
4. **Dependencies** — other services it calls
5. **Testing** — how to run tests

Read each service's `app.py` and main module to extract API contract and config. Read `docker-compose.yml` for env vars and mounts.

Note: note-writer has no tests directory — flag this as a gap.

## Verification

- All 7 services have a README.md
- Each README accurately reflects the service's current API and configuration

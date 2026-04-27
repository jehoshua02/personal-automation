# Security Audit

## Abstract

Review the pipeline for security vulnerabilities — credential handling, token storage, API exposure, container isolation.

## Priority: 59

- Value: 6/10 — Exposed ports with no auth is a real concern, but this is a personal/local tool.
- Momentum: 1/10 — No work started (research done, implementation not).
- Effort: 5/10 — Multiple findings to address across docker-compose and potentially service code.
- Risk: 5/10 — Security changes could break inter-service communication if not careful.

## Timeline

- Captured: 2026-04-27

## Details

### Research findings

**Good:**
- OAuth client secret bind-mounted read-only into auth container only
- OAuth token stored in Docker named volume `auth-data` (not exposed to host)
- No `.env` files, no hardcoded secrets in source code
- Token refresh uses standard OAuth flow

**Issues found:**
1. **All 7 service ports exposed to host** (8080–8086, 11434). Internal services don't need host-accessible ports — only orchestrator (or none) should be exposed.
2. **No auth on internal service endpoints.** Any process on the host can call any service.
3. **note-writer bind-mount is writable** (`./notes:/data/notes`) — acceptable since it needs to write, but worth documenting.
4. **Ollama port 11434 exposed** — allows arbitrary LLM prompts from host network.
5. **No rate limiting** on any service.

### Implementation plan

1. **docker-compose.yml**: Remove `ports` mappings for all services except orchestrator (or expose only on `127.0.0.1`). Services communicate via Docker network, not host ports.
2. **docker-compose.yml**: Ensure all services are on a shared Docker network (they likely already are via default compose network).
3. **Ollama**: Remove host port binding or bind to `127.0.0.1:11434`.
4. **Tests**: Verify all inter-service communication still works after removing host port bindings.
5. **Document**: Note that note-writer writable mount is intentional.
6. **Defer**: Rate limiting and service auth are overkill for a personal local tool — capture as separate low-priority tasks only if desired.

## Verification

- `docker compose up` starts all services
- Orchestrator pipeline completes successfully
- `curl localhost:8081` (non-orchestrator port) fails / connection refused
- Orchestrator can still reach all internal services

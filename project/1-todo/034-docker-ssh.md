# Docker Commands via SSH

## Abstract

Fix `docker compose` commands failing when run through an SSH session, even with Docker Desktop running.

## Priority: 34

- Value: 7/10 — Unblocks remote pipeline management from routines/agents.
- Momentum: 3/10 — Not connected to active work.
- Effort: 3/10 — Likely a small config fix (PATH, socket, environment variable).
- Risk: 2/10 — Low risk, just environment config.

## Timeline

- Captured: 2026-04-27
- Refined: 2026-04-27

## Details

- SSH to Windows host works fine.
- `docker compose` errors in the SSH session even with Docker Desktop running.
- Likely cause: SSH session doesn't inherit the same PATH or environment variables as an interactive login (Docker Desktop socket/named pipe not available).
- Options: fix PATH in SSH environment, set DOCKER_HOST, configure Docker context.

## Verification

SSH into the machine and run `docker compose ps` successfully.

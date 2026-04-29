# Evaluate Dockerfiles

## Abstract

Evaluate whether custom Dockerfile builds are needed per service, or if we could use official prebuilt images (e.g., python:3.12-slim) with volume-mounted code and a command override. Identify what value the Dockerfiles provide (pip install, EXPOSE, CMD) and what problems we'd hit without them.

## Priority: 52

- Value: 5/10 — Simplifies service boilerplate if viable.
- Momentum: 2/10 — Pattern is fresh from tonight's builds.
- Effort: 4/10 — Research + potentially reworking all service definitions.
- Risk: 4/10 — Could break dev workflow if deps aren't handled right.

## Timeline

- Captured: 2026-04-29
- Refined: 2026-04-29

# Rethink Service Granularity

## Abstract

Review the current split of services (e.g., separate gmail-reader, task-writer, calendar-writer) and evaluate whether some should be consolidated. The new task-service (single read/write service) sets a precedent worth applying elsewhere.

## Priority: 58

- Value: 5/10 — Architectural consistency, reduces service count.
- Momentum: 2/10 — task-service sets the precedent, but no work started.
- Effort: 7/10 — Merging services, updating tests, compose, orchestrator.
- Risk: 6/10 — Refactoring working services, could introduce regressions.

## Timeline

- Captured: 2026-04-28
- Refined: 2026-04-29

# Rename llm-processor

## Abstract

Rename llm-processor service to reflect its single responsibility: extracting tasks, events, and notes from emails. Current name is too generic for what it actually does.

## Priority: 60

- Value: 4/10 — Naming clarity, not blocking anything.
- Momentum: 1/10 — Greenfield.
- Effort: 3/10 — Rename files/dirs, update compose and orchestrator config.
- Risk: 3/10 — Touches orchestrator references, could break pipeline if missed.

## Timeline

- Captured: 2026-04-28
- Refined: 2026-04-29

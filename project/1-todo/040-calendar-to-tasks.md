# Calendar-to-Tasks

## Abstract

Scan Google Calendar events, use LLM to identify prep tasks, conflicts, and missing details. Tasks go to a review buffer for user approval before entering task list.

## Priority: 40

- Value: 7/10 — Proactive calendar management, catches things before they become problems
- Momentum: 3/10 — Shares infrastructure with Gmail pipeline (Google API auth, Ollama, provider abstractions)
- Effort: 7/10 — Review buffer web UI adds complexity on top of the core pipeline
- Risk: 3/10 — Read-only calendar scanning is low risk, task creation is reversible

## Timeline

- Captured: 2026-04-26
- Refined: 2026-04-26

## Details

### Decisions

- Scan next 30 days (configurable default)
- LLM assesses what needs attention based on event context — no rigid checklists
- Conflict detection — surface for user resolution, not auto-resolved
- Context-aware detail flagging — LLM judges if an event needs more info
- Prep task identification — LLM determines what prep is needed per event
- Review buffer with simple web UI for user approval
- Event-task linking — if event changes, related tasks update/remove accordingly
- Task destination: Google Tasks (same as Gmail pipeline)
- LLM prioritizes what to surface based on urgency and lead time

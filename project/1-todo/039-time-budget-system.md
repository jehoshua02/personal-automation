# Time Budget System

## Abstract

Envelope-style time budgeting — define category budgets, block calendar time for each, work prioritized task queues within blocks. Merges tasks-to-calendar and time budgeting into one system.

## Priority: 39

- Value: 9/10 — Ties everything together, the core system for intentional time use
- Momentum: 4/10 — Builds on task prioritization, Google Calendar API, web UI patterns from calendar-to-tasks
- Effort: 8/10 — Web UI for config, auto-scheduling logic, tracking/reporting, LLM integration
- Risk: 4/10 — Auto-scheduling to calendar is visible but deletable

## Timeline

- Captured: 2026-04-26
- Refined: 2026-04-26

## Details

### Decisions

- User defines flat categories and time budgets via web UI
- System auto-schedules time blocks on calendar — no review buffer
- Each category has a prioritized task queue — during a block, work the top item
- If a task doesn't get done, it stays at the top — no cascading reschedule
- LLM fills gaps intelligently using existing calendar as constraints
- Existing events (work, sleep, etc.) are respected as immovable blocks
- Track actual vs. planned time usage — help user see imbalance and rebalance
- Depends on: task prioritization system (037)

### Core concept
- Block time for buckets/categories, NOT individual tasks — avoids brittle scheduling
- Dynamic by nature — priority shifts don't require rescheduling
- Like the financial envelope system, but for time

### Open Questions (resolved)
All initial questions resolved.

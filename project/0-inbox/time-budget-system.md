# Time Budget System

## Abstract

Envelope-style time budgeting — define category budgets, block calendar time for each, work prioritized task queues within blocks. Merges tasks-to-calendar and time budgeting into one system.

## Details

### Core concept
- User defines time budgets per category (like financial envelopes, but for time)
- System blocks calendar time for each category around existing events
- Each category has a prioritized task queue — during a block, work the top item
- If a task doesn't get done, it stays at the top — no cascading reschedule
- LLM fills gaps intelligently using existing calendar as constraints
- Existing events (work, sleep, etc.) are respected as immovable blocks

### Key design decisions
- Block time for buckets/categories, NOT individual tasks — avoids brittle scheduling
- Dynamic by nature — priority shifts don't require rescheduling
- Depends on: task prioritization system

### Open questions
- How does user define categories and budgets? Config file? Web UI?
- How granular are categories? (e.g., "deep work" vs "deep work: project X")
- Track actual vs. planned time usage? Reporting?
- Review buffer for proposed blocks, or auto-schedule?

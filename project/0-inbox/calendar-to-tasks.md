# Calendar-to-Tasks

## Abstract

Scan Google Calendar events, use LLM to identify prep tasks, conflicts, and missing details. Tasks go to a review buffer for user approval before entering task list.

## Details

### Requirements (from user)
- Scan next 30 days (configurable default)
- LLM assesses what needs attention based on event context
- Conflict detection — surface for user resolution
- Context-aware detail flagging — LLM judges if an event needs more info
- Prep task identification — LLM determines what prep is needed per event
- Review buffer — tasks await user approval before hitting task list
- Event-task linking — if event changes, related tasks update/remove accordingly
- Uses Google Calendar API

### Decisions
- No rigid checklists for missing details or prep — LLM decides contextually
- Conflicts flagged for user, not auto-resolved
- 30-day lookahead default, configurable
- LLM prioritizes what to surface based on urgency and lead time

### Open Questions
- Task destination: same Google Tasks list as Gmail pipeline?
- Review buffer UX: how does user approve/reject? CLI? Web UI? Notification?

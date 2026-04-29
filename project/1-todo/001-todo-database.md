# Todo Database

## Abstract

Build a task-service (HTTP CRUD API) and task-store (Postgres with bind-mounted volume) for persisting tasks. Fields: title, description, completed timestamp, created/modified timestamps.

## Priority: 1

- Value: 6/10 — Foundation for replacing Google Tasks dependency.
- Momentum: 1/10 — Greenfield.
- Effort: 4/10 — Two services, straightforward schema.
- Risk: 2/10 — First stateful service (Postgres), but isolated.
- Override: User wants to do this tonight.

## Timeline

- Captured: 2026-04-28
- Refined: 2026-04-28

## Details

- task-service: Python/Flask HTTP API for CRUD operations on tasks.
- task-store: Postgres container with bind-mounted volume for persistence through container churn.
- Fields: title, description, completed_at, created_at, updated_at.

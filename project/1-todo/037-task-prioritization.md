# Task Prioritization

## Abstract

Binary insertion sort for task lists — LLM does pairwise "this or that" comparisons to place each task. Works across multiple Google Tasks lists (one per category/bucket).

## Priority: 37

- Value: 8/10 — Foundation for time budgets, makes all task lists actionable
- Momentum: 3/10 — Shares Google Tasks API with other pipelines
- Effort: 5/10 — Binary insertion sort is straightforward, LLM comparison is the main work
- Risk: 3/10 — Reordering tasks is reversible, low stakes

## Timeline

- Captured: 2026-04-26
- Refined: 2026-04-26

## Details

### Decisions

- Binary insertion sort via pairwise comparison — no abstract scoring
- O(log n) comparisons per task insertion
- LLM decides, user reviews periodically (weekly top 10-20 scan, drag to correct)
- Works across multiple Google Tasks lists — each category/bucket has its own prioritized list
- Dependency for: time budget system

### Open Questions (resolved)
All initial questions resolved.

# Autonomous Project Loop

## Abstract

Design an autonomous workflow loop where Claude picks up tasks, executes them, and resets context at key transition points — without manual `/clear` or human prompting between tasks.

## Priority: 28

- Value: 9/10 — Directly enables unattended multi-task runs, maximizes throughput
- Momentum: 1/10 — Fresh idea, no prior work
- Effort: 3/10 — Design/research task, not implementation
- Risk: 3/10 — Design stage only, no code changes yet

## Timeline

- Captured: 2026-04-27
- Refined: 2026-04-27

## Details

Problem: `/clear` is a built-in CLI command only the user can trigger. Context accumulates across tasks, degrading performance. Current workflow requires human to run `/clear` after each task completion.

Goal: Claude autonomously cycles through quarry workflow (refine → pick up → execute → complete → reset → repeat) with context resets at key points.

Areas to explore:
- Claude Code hooks (post-tool, post-commit) that could trigger context management
- `/loop` skill with self-pacing for continuous task cycling
- `/compact` as a programmatic alternative to `/clear`
- Subagent isolation — delegate each task to a fresh subagent with clean context
- Worktree isolation for parallel or sequential task execution
- Trade-offs: full reset vs compact vs subagent delegation

## Verification

Design doc with recommended approach and trade-offs documented.

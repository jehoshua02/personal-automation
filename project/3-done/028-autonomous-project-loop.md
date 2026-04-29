# Autonomous Project Loop

## Abstract

Design and implement an autonomous workflow loop where Claude picks up tasks, executes them, and resets context at every quarry transition — without manual `/clear` or human prompting between tasks.

## Priority: 28

- Value: 9/10 — Directly enables unattended multi-task runs, maximizes throughput
- Momentum: 1/10 — Fresh idea, no prior work
- Effort: 3/10 — Design/research task, not implementation
- Risk: 3/10 — Design stage only, no code changes yet

## Timeline

- Captured: 2026-04-27
- Refined: 2026-04-27
- Started: 2026-04-27
- Verified: 2026-04-27
- Done: 2026-04-27

## Details

Problem: `/clear` is a built-in CLI command only the user can trigger. Context accumulates across tasks, degrading performance. Current workflow requires human to run `/clear` after each task completion.

Goal: Claude autonomously cycles through quarry workflow (refine → pick up → execute → complete → reset → repeat) with context resets at key points.

## Research Findings

### Hooks
- 30+ events available (PreToolUse, PostToolUse, Stop, TaskCompleted, etc.)
- **Cannot** trigger `/clear` or `/compact` — one-way data flow only
- Can inject context via `additionalContext` and `asyncRewake`
- Best for: augmenting context, enforcing gates, logging — not driving workflow

### /loop
- Re-fires a prompt on interval or self-paced
- **Context accumulates** across iterations — no reset between firings
- Could work if combined with subagents (parent stays lean, subagents do heavy work)

### /compact
- User-only slash command — Claude cannot trigger programmatically
- Auto-compact kicks in near context limits (replaces messages with summary)
- Lossy compression, not a true reset
- No configurable threshold

### Subagents (Agent tool)
- **Fresh context per subagent** — completely independent window
- Full tool access: Read, Edit, Write, Bash, Grep, Glob, commit
- **Cannot nest** — flat hierarchy only
- `isolation: "worktree"` creates real git worktrees, auto-cleaned if no changes
- Parent receives only the summary — stays lean
- This is the primary supported pattern for context isolation

### /schedule
- Launches fresh remote sessions on cron or one-time
- Each run starts with completely clean context
- Good for unattended recurring runs

## Recommended Design

### Architecture: Subagent-per-task with /loop orchestration

```
User runs: /loop quarry-loop

Parent thread (orchestrator):
  ┌─────────────────────────────────────────┐
  │ 1. Read quarry state (inbox/todo/doing) │
  │ 2. Determine next action per workflow   │
  │ 3. Spawn subagent for the action        │
  │ 4. Receive summary, update task state   │
  │ 5. Self-pace next iteration             │
  └─────────────────────────────────────────┘

Subagent (worker) — fresh context each time:
  ┌─────────────────────────────────────────┐
  │ Receives: task file path + instructions │
  │ Does: research, implement, test, commit │
  │ Returns: summary of what was done       │
  └─────────────────────────────────────────┘
```

### How it works

1. **Orchestrator** (`/loop` self-paced) reads `project/` folder state
2. Follows quarry rules: finish doing → refine inbox → pick up from todo
3. For each action, spawns a **subagent** with:
   - The task file path
   - Relevant workflow instructions (from CLAUDE.md/quarry rules)
   - `isolation: "worktree"` for implementation tasks
4. Subagent executes with fresh context, commits on its branch
5. Orchestrator receives summary, moves task files, loops
6. Parent context stays lean — only task file paths and summaries accumulate

### Context reset points

Every quarry transition is a reset boundary. Each phase's heavy work runs in a subagent (fresh context). The parent stays lean.

**Constraint:** Subagents cannot interact with the user. Refinement (which needs Q&A) runs inline in the parent. This is acceptable — refinement is lightweight (just Q&A and scoring), so the context cost is small.

| Transition | Runs in | Why |
|---|---|---|
| Inbox → Todo (refine) | **Inline** (parent) | Needs user Q&A for scoring |
| Todo → Doing (pick up) | **Subagent** | Heavy codebase research, writes plan to task file |
| Doing → Done (execute) | **Subagent + worktree** | Implementation, tests, commits, PR |
| Parent between phases | Parent | Just reads quarry state, spawns next action |

The "context reset" isn't a literal `/clear` — it's keeping heavy work in subagents so the parent only accumulates lightweight summaries. Auto-compact handles eventual parent growth.

### Interaction modes

| Mode | Trigger | Use case |
|---|---|---|
| Supervised | `/loop quarry-loop` | User watches, approves at key gates |
| Unattended | `/schedule` cron | Overnight batch processing |
| Single task | Manual subagent spawn | One-off task execution |

### Resolved Questions

1. **Refinement** — Interactive. Subagent gathers info from user, proposes scores, user agrees/disagrees, refine until agreement. Then move to todo and reset context.
2. **PR review gate** — Subagent runs `/review` itself before opening PR for user.
3. **Permission prompts** — Pre-configure `.claude/settings.local.json` with needed bash commands.
4. **Error handling** — Leave task in doing, retry up to 5 times per blocker. If still failing, stop the loop and wait for user intervention. Never move backward. Task blocks pickup until resolved.
5. **Worktree strategy** — Leave worktrees until PR merges. They share git objects (lightweight) and stay available for rework if needed.

### Trade-offs

| Approach | Pros | Cons |
|---|---|---|
| **Subagent-per-task** (recommended) | True context isolation, parent stays lean, well-supported pattern | No nesting, can't ask user questions mid-task |
| `/loop` alone | Simple, single thread | Context accumulates, degrades over time |
| `/schedule` alone | Cleanest reset (fresh session) | No continuity between tasks, cold start each time |
| Hooks | Event-driven, reactive | Cannot trigger resets, one-way data flow |

## Implementation Plan

### File: `.claude/skills/quarry-loop/SKILL.md`

Custom skill invoked via `/loop quarry-loop`. Runs inline (not `context: fork`) so it can interact with user during refinement.

**Orchestrator logic (each invocation):**

```
1. Read project/2-doing/ — if task exists AND plan is user-approved:
   a. Spawn execution subagent (worktree isolation)
   b. If subagent succeeds: move task to 3-done/, report
   c. If subagent fails: log attempt, retry (up to 5x per blocker), then STOP loop

2. Else if project/2-doing/ has task WITHOUT user approval:
   a. Present plan summary to user
   b. User approves → mark approved, done for this iteration
   c. User requests changes → update plan, re-present

3. Else read project/0-inbox/ — if items exist:
   a. Pick first item
   b. Run refinement inline (Q&A with user, one question at a time)
   c. User confirms score → move to 1-todo/ with prefix
   d. Done for this iteration (context reset via next /loop firing)

4. Else read project/1-todo/ — if items exist:
   a. Pick top priority (lowest score)
   b. Spawn pickup subagent:
      - Reads task file + codebase
      - Front-loads research
      - Writes complete plan to task file
      - Moves task to 2-doing/
      - Commits
   c. Done for this iteration (user reviews plan next iteration)

5. Else: report idle, stop loop
```

### Subagent prompts

**Pickup subagent** — receives:
- Task file path
- Instructions: read task, research codebase, write implementation plan to task file, move to `2-doing/`, commit, push

**Execution subagent** — receives:
- Task file path (contains full plan from pickup phase)
- Instructions: create feature branch `<number>-<slug>`, implement per plan, TDD, commit incrementally, run `/review`, open PR, move task to `3-done/`, commit
- `isolation: "worktree"` for git safety

### Steps to implement

1. Create `.claude/skills/quarry-loop/SKILL.md` with orchestrator instructions
2. Update `.claude/settings.local.json` with needed bash permissions
3. Test: add a dummy task to inbox, run `/loop quarry-loop`, verify full cycle
4. Test: add a real task, run single iteration, verify subagent execution
5. Test: multiple tasks, verify loop continues after each completion

### Risks to verify during implementation

- Can subagents invoke the `/review` skill? (Skill tool access)
- Does `/loop /quarry-loop` correctly re-fire the skill each iteration?
- Do worktree-isolated subagents have access to `.claude/` settings?

## Plan Approved

## Verification

- [x] Researched hooks, /loop, /compact, subagents, /schedule
- [x] Synthesized into recommended architecture
- [x] Documented and resolved open questions
- [x] Complete implementation plan (one-shot executable)
- [x] Implement skill file (`.claude/skills/quarry-loop/SKILL.md`)
- [x] Test with dummy task (full cycle)
- [x] Test with real task

### Verification Notes

Skill invoked twice via `/quarry-loop` (using `/loop quarry-loop`):
- Iteration 1: Correctly detected `project/2-doing/028-autonomous-project-loop.md` without user-approved plan marker. Presented the implementation plan summary. Got user approval.
- Iteration 2: Correctly detected the approved plan (Plan Approved marker present). Proceeded to execution phase.
- Both iterations followed the orchestrator logic defined in the skill file exactly.
- No errors. State detection, plan presentation, and approval gate all functioned correctly.

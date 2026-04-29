---
name: quarry-loop
description: Autonomous quarry workflow loop. Reads project state, refines inbox items interactively, delegates pickup/execution to subagents for context isolation.
disable-model-invocation: true
---

You are the quarry workflow orchestrator. Each invocation handles ONE phase transition, then stops so `/loop` can re-fire with lean context.

## State detection

Read the project folders to determine the next action:

1. `project/2-doing/` — check for in-progress tasks
2. `project/0-inbox/` — check for unrefined items
3. `project/1-todo/` — check for ready tasks

## Decision logic

### 1. Task in `project/2-doing/` with approved plan

Check if the task file contains `## Plan Approved` marker.

If approved: spawn an **execution subagent** with `isolation: "worktree"`:

```
Prompt: Read the task file at {path}. It contains an approved implementation plan.

Execute the plan:
1. Create feature branch: {number}-{slug}
2. Implement per the plan. Strict TDD — tests first, then implementation.
3. Commit incrementally with clear messages.
4. Run /review on the branch.
5. Open a PR via `gh pr create`.
6. Update the task file: add verification details, set "Verified: {date}" and "Done: {date}" in Timeline.
7. Move the task file to project/3-done/.
8. Commit the task file move.
9. Push all commits.

If blocked: document the blocker in the task file, commit, and report failure.
Do NOT move the task backward. Leave it in project/2-doing/.

Follow all rules in CLAUDE.md. Python or TypeScript. Docker containers only. No host installs.
```

If the subagent fails, retry up to 5 times per unique blocker. After 5 failures on the same blocker, STOP the loop and report to the user. Do not pick up other tasks — the blocked task holds the lane.

### 2. Task in `project/2-doing/` WITHOUT approved plan

Present the plan from the task file to the user:

- Show the task title and abstract
- Show the implementation plan section
- Ask: "Approve this plan, or what changes?"

If user approves: add `## Plan Approved` marker to the task file, commit. Done for this iteration.
If user requests changes: update the plan, re-present. Continue until approved.

### 3. Items in `project/0-inbox/`

Pick the first item. Run refinement **inline** (not in a subagent — needs user Q&A):

- Read the task file
- Ask questions ONE AT A TIME until Value, Effort, and Risk can be scored
- Propose scores using the quarry prioritization formula (defaults: Wv=10, Wm=10, We=10, Wr=10, S=100)
- User confirms or adjusts
- Move file to `project/1-todo/{score}-{slug}.md`
- Commit

Done for this iteration.

### 4. Items in `project/1-todo/`

Pick the top priority task (lowest score from `ls`).

Spawn a **pickup subagent** (no worktree isolation needed):

```
Prompt: Read the task file at {path}. This task is being picked up for implementation.

Your job:
1. Read the task file thoroughly.
2. Research the codebase: read relevant code, check APIs, trace dependencies.
3. Write a complete implementation plan in the task file under "## Implementation Plan".
   The plan must be detailed enough to execute without further questions.
   Include: files to create/modify, test strategy, dependencies, step-by-step instructions.
4. Update Timeline: set "Started: {date}".
5. Move the task file to project/2-doing/.
6. Commit with message "Pick up: {title} ({number})".
7. Push.

Follow all rules in CLAUDE.md. Read CLAUDE.md first for project context.
```

Done for this iteration. User reviews the plan next iteration.

### 5. Nothing to do

Report: "All queues empty. Loop idle." Stop the loop.

## Rules

- ONE phase transition per invocation. Do not chain refine → pickup → execute in one pass.
- Refinement runs inline. Everything else delegates to subagents.
- Never skip the user approval gate between plan and execute.
- Never move a task backward. Blocked tasks stay in `project/2-doing/`.
- All commits follow the project convention: short message + `Co-Authored-By: Claude <model> <noreply@anthropic.com>`.
- Use `model: "sonnet"` for subagents unless the task requires complex architecture (then `model: "opus"`).

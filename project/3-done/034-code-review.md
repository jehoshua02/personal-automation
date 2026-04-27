# Code Review (Human + AI)

## Abstract

Protect main branch, push feature branches, self-review with `/review`, then open PR for human review.

## Priority: 034

- Value: 6/10 — Quality gate before merging. Catches issues early.
- Momentum: 1/10 — No work started.
- Effort: 2/10 — GitHub branch protection + workflow rule changes in CLAUDE.md.
- Risk: 2/10 — Low risk. Changes workflow, not code.

## Timeline

- Captured: 2026-04-27
- Refined: 2026-04-27
- Started: 2026-04-27
- Verified: 2026-04-27
- Done: 2026-04-27

## Details

- GitHub branch protection already enforced (push to main rejected with "Changes must be made through a pull request").
- Updated CLAUDE.md workflow: replaced "Push to remote after every commit" with feature branch + PR workflow.
- Branch naming convention: `<task-number>-<slug>`.
- Flow: branch → commit → `/review` → PR → human review → merge.
- `gh` CLI not installed — PRs created via GitHub web UI or installed later.

## Verification

- Confirmed main branch protection active (push rejected with GH013 error).
- CLAUDE.md updated with feature branch workflow instruction.

# Rename Default Branch from Master to Main

## Abstract

Rename the default branch from `master` to `main` across local, remote, and all references.

## Priority: 51

- Value: 3/10 — Convention only. No functional impact, doesn't unblock anything.
- Momentum: 1/10 — No work started.
- Effort: 2/10 — Three git commands + one GitHub settings change.
- Risk: 2/10 — Easily reversible. No CI, no branch protection rules.

## Timeline

- Captured: 2026-04-27

## Details

### Research findings

- Remote: `git@github.com:jehoshua02/personal-automation.git`
- No CI pipelines (no `.github/` directory)
- No source files reference `master` — only git internals (`.git/HEAD`, `.git/config`) which update automatically
- No branch protection rules configured locally

### Implementation plan

1. **Browser step first**: Change default branch on GitHub repo settings to `main` (must exist first, so push before changing)
2. `git branch -m master main` — renames local branch
3. `git push origin -u main` — push new branch to remote
4. Change default branch to `main` on GitHub: Settings → Branches → Default branch
5. `git push origin --delete master` — delete old remote branch
6. Verify: `git status`, `git remote show origin`

## Verification

- `git branch` shows `main` as current branch
- `git remote show origin` shows `main` as HEAD branch
- GitHub repo shows `main` as default

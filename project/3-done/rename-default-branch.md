# Rename Default Branch from Master to Main

## Abstract

Rename the default branch from `master` to `main` across local, remote, and all references.

## Priority: 33

- Value: 3/10 — Convention only.
- Momentum: 1/10 — No work started.
- Effort: 2/10 — Three git commands + GitHub settings change.
- Risk: 2/10 — Easily reversible. No CI, no branch protection.

## Timeline

- Captured: 2026-04-27
- Refined: 2026-04-27
- Started: 2026-04-27
- Verified: 2026-04-27
- Done: 2026-04-27

## Details

- `git branch -m master main`
- `git push origin -u main`
- GitHub default branch changed to `main` (manual browser step)
- `git push origin --delete master`
- No source files referenced `master` — only git internals needed updating

## Verification

- `git remote show origin` → HEAD branch: main
- Remote `master` deleted
- Local branch is `main`

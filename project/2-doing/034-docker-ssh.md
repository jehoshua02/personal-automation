# Docker Commands via SSH

## Abstract

Fix `docker compose` commands failing when run through an SSH session, even with Docker Desktop running.

## Priority: 34

- Value: 7/10 — Unblocks remote pipeline management from routines/agents.
- Momentum: 3/10 — Not connected to active work.
- Effort: 3/10 — Likely a small config fix (PATH, socket, environment variable).
- Risk: 2/10 — Low risk, just environment config.

## Timeline

- Captured: 2026-04-27
- Refined: 2026-04-27
- Started: 2026-04-27

## Details

- SSH to Windows host works fine.
- `docker compose` errors in the SSH session even with Docker Desktop running.
- Likely cause: SSH session doesn't inherit the same PATH or environment variables as an interactive login (Docker Desktop socket/named pipe not available).
- Options: fix PATH in SSH environment, set DOCKER_HOST, configure Docker context.

### Root Cause Analysis

The Windows OpenSSH server (sshd) is running and uses PowerShell as its shell.
Docker Desktop is configured with two contexts:
- `default` → `npipe:////./pipe/docker_engine`
- `desktop-linux` → `npipe:////./pipe/dockerDesktopLinuxEngine` (active context)

`~/.docker/config.json` sets `"currentContext": "desktop-linux"`. However, non-interactive SSH sessions do not load the user profile the same way as an interactive login, so environment variables and profile-based settings may not apply.

Both named pipes (`docker_engine` and `dockerDesktopLinuxEngine`) exist at runtime, so PATH is not the issue. The issue is that `DOCKER_CONTEXT` is not set at the system level — SSH sessions inherit only system-level environment variables from the registry.

### Fix Strategy

Set `DOCKER_CONTEXT=desktop-linux` as a **Machine-level** Windows environment variable. SSH sessions inherit system environment variables automatically, so this is the simplest and most robust fix.

Alternative (not chosen): `PermitUserEnvironment yes` + `~/.ssh/environment` file — more complex, requires sshd_config change and restart.

Alternative (not chosen): Set `DOCKER_HOST=npipe:////./pipe/dockerDesktopLinuxEngine` at system level — less flexible if context changes.

## Implementation Plan

### Overview

Set `DOCKER_CONTEXT=desktop-linux` as a system-level (Machine) environment variable using the Windows registry. No sshd_config changes needed. Docker is already in system PATH.

### Steps

1. **Set DOCKER_CONTEXT at Machine level**

   Run in PowerShell (as admin or via registry):
   ```powershell
   [System.Environment]::SetEnvironmentVariable("DOCKER_CONTEXT", "desktop-linux", "Machine")
   ```

   This writes to `HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment`.
   New SSH sessions will inherit this automatically.

2. **Verify the registry write**

   ```powershell
   [System.Environment]::GetEnvironmentVariable("DOCKER_CONTEXT", "Machine")
   # Expected: desktop-linux
   ```

3. **Test from an SSH session**

   From another machine (or Termux/WSL), SSH in and run:
   ```bash
   ssh jstou@<host> "docker compose ps"
   ```
   Or if SSH is to localhost:
   ```bash
   ssh jstou@localhost "docker compose ps"
   ```

   Expected: lists containers (or "no containers" if none running), no error about connecting to Docker.

4. **Verification command to document in task**

   Capture the output of:
   ```bash
   ssh jstou@<host> "docker compose version"
   ssh jstou@<host> "docker compose ps"
   ```

### Files to modify

- No source files modified.
- Only Windows system environment variable registry key:
  `HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment` — add `DOCKER_CONTEXT=desktop-linux`

### Test strategy

- No unit tests needed (this is an OS-level environment config).
- Verification: SSH session successfully runs `docker compose ps` without error.
- If Docker Desktop is not running, the pipe won't exist and the command will fail regardless — that's expected behavior, not a bug.

### Rollback

```powershell
[System.Environment]::SetEnvironmentVariable("DOCKER_CONTEXT", $null, "Machine")
```

## Plan Approved

## Verification

SSH into the machine and run `docker compose ps` successfully.

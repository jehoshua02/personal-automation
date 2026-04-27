# Docker Commands via SSH

## Abstract

Figure out how to run docker/docker-compose commands through an SSH session (e.g., from a Claude Code remote agent or scheduled routine).

## Details

- Currently all docker commands run locally on the host.
- Need a way to execute docker compose commands over SSH — either by connecting to a remote Docker daemon or by running shell commands on the remote host.
- Options to investigate: `DOCKER_HOST=ssh://user@host`, SSH + remote shell, Docker contexts.

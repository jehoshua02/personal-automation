# Evaluate Dockerfiles

## Abstract

Evaluate whether custom Dockerfile builds are needed per service, or if we could use official prebuilt images (e.g., python:3.12-slim) with volume-mounted code and a command override. Identify what value the Dockerfiles provide (pip install, EXPOSE, CMD) and what problems we'd hit without them.

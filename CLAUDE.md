## What is personal-automation?

Automated personal productivity pipelines — email processing, calendar management, task scheduling, and time budgeting. Uses Google APIs, local open-source LLMs via Ollama, and self-hosted scripting.

Runs inside claude-container.

## Workflow

- Task management follows the quarry plugin. Folder structure is in `project/README.md`.
- Do not use Claude global memory. All project knowledge lives in this repo.
- When the next step is obvious from the workflow rules, just do it. Don't ask.
- Push to remote after every commit.

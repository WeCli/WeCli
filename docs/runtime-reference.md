# Runtime Reference

This page collects the runtime-oriented technical details that do not need to live in `README.md`.

Use it when you need:

- the high-level service architecture
- which service owns which responsibility
- authentication and isolation rules
- where the main runtime files live
- a lightweight runtime map before diving into code

For exhaustive port and frontend proxy route details, read [ports.md](./ports.md).
For code indexing, read [repo-index.md](./repo-index.md).

## Architecture Overview

```text
Browser / Web UI
    -> front.py (Flask UI + proxy gateway)
        -> mainagent.py (OpenAI-compatible agent API)
        -> oasis/server.py (OASIS orchestration service)
        -> time.py (scheduler service)

Bots:
    telegrambot.py / QQbot.py
        -> call mainagent.py through the OpenAI-compatible API
```

## Core Services

| Service | Main File | Role |
|---|---|---|
| Frontend | `src/front.py` | Web UI, login/session handling, proxy gateway |
| Agent API | `src/mainagent.py` | OpenAI-compatible API, chat/session/settings system |
| Scheduler | `src/time.py` | scheduled task runner and trigger source |
| OASIS | `oasis/server.py` | workflows, experts, topics, OpenClaw-related orchestration |

## MCP Tool Layer

TeamClaw integrates multiple tool services through MCP.

Common tool areas:

- web search
- scheduler
- file management
- shell / Python command execution
- OASIS operations
- Bark notifications
- Telegram messaging

The tool implementations live under `src/mcp_*.py`.

## Authentication and Isolation

### Main auth modes

- local browser access on `127.0.0.1`
- password-based user login
- internal service-to-service token (`INTERNAL_TOKEN`)
- chatbot allowlists / user mapping

### Isolation rules

- conversation history is isolated by user
- user files are isolated by user
- custom experts are isolated by user or Team
- bot sessions route through user-scoped identities

### Secret masking

External keys such as OpenClaw-related keys should not be exposed in workflow YAML or frontend forms. Masked values like `api_key: "****"` should resolve from environment at runtime.

## Runtime Data Layout

Important runtime data locations:

```text
config/.env
config/users.json
data/agent_memory.db
data/group_chat.db
data/prompts/
data/user_files/{user_id}/...
```

The Team-specific working set is usually:

```text
data/user_files/{user_id}/teams/{team_name}/
├── internal_agents.json
├── external_agents.json
├── oasis_experts.json
└── oasis/yaml/*.yaml
```

Related docs:

- [example_team.md](./example_team.md)
- [build_team.md](./build_team.md)

## Main Runtime Code Areas

| Area | Files |
|---|---|
| Agent API | `src/openai_routes.py`, `src/openai_service.py`, `src/mainagent.py` |
| Sessions | `src/session_routes.py`, `src/session_service.py` |
| Groups | `src/group_routes.py`, `src/group_service.py` |
| Settings / ops | `src/settings_routes.py`, `src/settings_service.py`, `src/ops_routes.py`, `src/ops_service.py` |
| Frontend proxy | `src/front.py`, `src/front_group_routes.py`, `src/front_oasis_routes.py`, `src/front_session_routes.py` |
| OASIS runtime | `oasis/server.py`, `oasis/engine.py`, `oasis/scheduler.py`, `oasis/experts.py` |

For the full repo map, read [repo-index.md](./repo-index.md).

## API Surface

At a high level, TeamClaw exposes:

- OpenAI-compatible chat endpoints
- session and settings endpoints
- group chat endpoints
- OASIS topics / experts / workflows endpoints
- frontend proxy endpoints

Use [ports.md](./ports.md) for the fuller route inventory.

## Tech Stack

| Layer | Technology |
|---|---|
| LLM integration | OpenAI-compatible providers via LangChain / custom routing |
| Agent runtime | LangGraph + LangChain |
| Web backend | FastAPI + Flask |
| Orchestration | OASIS runtime in `oasis/` |
| Scheduling | APScheduler |
| Persistence | SQLite + JSON + filesystem |
| Frontend | HTML templates + JS assets in `src/static/` |

## Related Docs

- [overview.md](./overview.md)
- [ports.md](./ports.md)
- [repo-index.md](./repo-index.md)
- [migration-playbook.md](./migration-playbook.md)

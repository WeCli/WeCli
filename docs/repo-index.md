# TeamClaw Repository Index

Use this file when an agent needs to **index the repo before reading code**. It is a task-oriented map of the main files and directories.

## Fast Indexing Checklist

1. Confirm the task area: install, runtime, frontend, workflow, OpenClaw, bots, or maintenance.
2. Read only the matching section below.
3. Open the referenced files for the subsystem you are changing.
4. Only expand outward if the first-hop files are insufficient.

## Top-Level Layout

| Path | What Lives Here |
|---|---|
| `SKILL.md` | Agent entrypoint and task router |
| `README.md` | Product overview |
| `docs/` | Task docs, maintainer docs, repo index |
| `selfskill/scripts/` | Preferred install / configure / run entrypoints |
| `scripts/` | Legacy setup/start helpers and launcher pieces |
| `src/` | Main backend, frontend proxy, MCP tools, frontend assets |
| `oasis/` | OASIS engine and OpenClaw routes |
| `chatbot/` | Telegram / QQ bot integrations |
| `config/` | `.env`, requirements, users |
| `data/` | runtime DBs, prompts, user files, workflow files |
| `test/` | automated tests |
| `visual/` | standalone visual orchestrator app |

## Install and Configuration

Read these first for setup or environment changes:

| Path | Purpose |
|---|---|
| `selfskill/scripts/run.sh` | primary Linux / macOS install, configure, start flow |
| `selfskill/scripts/run.ps1` | primary Windows install, configure, start flow |
| `selfskill/scripts/configure.py` | `.env` initialization and configuration logic |
| `config/.env.example` | config template and inline guidance |
| `scripts/setup_apikey.sh` | legacy API key helper |
| `scripts/setup_apikey.ps1` | legacy Windows API key helper |
| `manual_run.sh` | manual startup helper with guardrails |
| `manual_run.ps1` | manual Windows startup helper with guardrails |

If the issue is model detection or provider-specific behavior, inspect:

- `src/llm_factory.py`
- `src/ops_service.py`

## Runtime Entry Points

These are the main services TeamClaw runs:

| Path | Service |
|---|---|
| `src/mainagent.py` | Agent API bootstrap and router composition |
| `src/front.py` | Flask frontend and proxy gateway |
| `src/time.py` | scheduler service |
| `oasis/server.py` | OASIS service |
| `scripts/launcher.py` | multi-service startup order |

When the bug is "service does not start" or "route behaves unexpectedly", start from the matching entrypoint plus its route/service files below.

## Backend Module Map (`src/`)

### OpenAI-compatible chat API

- `src/openai_routes.py`
- `src/openai_service.py`
- `src/openai_models.py`
- `src/openai_protocol.py`
- `src/message_builder.py`

### Sessions

- `src/session_routes.py`
- `src/session_service.py`
- `src/session_models.py`
- `src/session_summary.py`
- `src/checkpoint_repository.py`

### Groups

- `src/group_routes.py`
- `src/group_service.py`
- `src/group_models.py`
- `src/group_repository.py`

### Settings / ops / auth / system

- `src/settings_routes.py`
- `src/settings_service.py`
- `src/settings_models.py`
- `src/ops_routes.py`
- `src/ops_service.py`
- `src/ops_models.py`
- `src/system_routes.py`
- `src/system_service.py`
- `src/system_models.py`
- `src/env_settings.py`
- `src/user_auth.py`
- `src/auth_utils.py`

### Runtime plumbing

- `src/agent.py`
- `src/agent_runtime_state.py`
- `src/logging_utils.py`

## Frontend Map

If the task touches the UI, start here:

| Path | Purpose |
|---|---|
| `src/static/js/main.js` | main desktop frontend logic |
| `src/templates/group_chat_mobile.html` | mobile group chat page and mobile settings UI |
| `src/templates/` | other HTML templates |
| `src/static/` | CSS, JS, images |
| `src/front_group_routes.py` | frontend proxy routes for groups |
| `src/front_oasis_routes.py` | frontend proxy routes for OASIS |
| `src/front_session_routes.py` | frontend proxy routes for sessions |

## OASIS and Workflow Engine

Read these for workflow execution, topics, experts, and OpenClaw integration:

| Path | Purpose |
|---|---|
| `oasis/server.py` | OASIS API bootstrap |
| `oasis/engine.py` | discussion / execution engine |
| `oasis/scheduler.py` | workflow scheduling logic |
| `oasis/experts.py` | expert definitions and storage |
| `oasis/forum.py` | forum/topic data handling |
| `oasis/models.py` | OASIS request/response models |
| `oasis/openclaw_routes.py` | OpenClaw API routes |
| `oasis/openclaw_cli.py` | OpenClaw CLI wrappers |

Pair these with:

- `docs/create_workflow.md`
- `docs/build_team.md`
- `docs/openclaw-commands.md`

## MCP Tools and Integrations

For tool execution or tool exposure:

- `src/mcp_commander.py`
- `src/mcp_filemanager.py`
- `src/mcp_oasis.py`
- `src/mcp_scheduler.py`
- `src/mcp_search.py`
- `src/mcp_session.py`
- `src/mcp_telegram.py`
- `src/mcp_llmapi.py`

## Bot Integrations

| Path | Purpose |
|---|---|
| `chatbot/telegrambot.py` | Telegram bot runtime |
| `chatbot/QQbot.py` | QQ bot runtime |
| `chatbot/setup.py` | bot setup helper (interactive menu; requires `stdin.isatty()` — skipped automatically by `launcher.py` in non-interactive / headless mode) |

## Team and User Data

The most important runtime data lives here:

```text
data/
├── agent_memory.db
├── group_chat.db
├── prompts/
├── schedules/
└── user_files/{user_id}/
    ├── user_profile.txt
    ├── skills_manifest.json
    ├── oasis/yaml/
    └── teams/{team_name}/
        ├── internal_agents.json
        ├── external_agents.json
        ├── oasis_experts.json
        └── oasis/yaml/*.yaml
```

Pair these with:

- `docs/example_team.md`
- `docs/build_team.md`
- `docs/create_workflow.md`

## Tests and Validation

When changing code, check the nearest validation surface:

| Path / Command | Use |
|---|---|
| `test/test_agent_runtime_state.py` | runtime state unit tests |
| `test/test_openai_protocol.py` | OpenAI protocol unit tests |
| `test/test_integration.py` | cross-service integration tests |
| `uv run scripts/cli.py status` | smoke test services |
| `python -m py_compile <file>` | quick syntax check for touched Python files |
| `node --check src/static/js/main.js` | quick JS syntax check |

## Task-to-File Lookup

### "Settings page or `.env` behavior is wrong"

Read:

- `src/static/js/main.js`
- `src/templates/group_chat_mobile.html`
- `src/settings_routes.py`
- `src/settings_service.py`
- `src/env_settings.py`
- `config/.env.example`

### "Model selection / provider / audio defaults are wrong"

Read:

- `src/llm_factory.py`
- `src/ops_service.py`
- `scripts/setup_apikey.sh`
- `scripts/setup_apikey.ps1`
- `selfskill/scripts/configure.py`

### "Workflow YAML or OASIS execution is wrong"

Read:

- `docs/create_workflow.md`
- `oasis/scheduler.py`
- `oasis/engine.py`
- `oasis/server.py`
- `docs/example_team.md`

### "OpenClaw integration is wrong"

Read:

- `docs/openclaw-commands.md`
- `oasis/openclaw_routes.py`
- `oasis/openclaw_cli.py`
- `docs/build_team.md`

### "Frontend route or login behavior is wrong"

Read:

- `src/front.py`
- `src/front_group_routes.py`
- `src/front_oasis_routes.py`
- `src/front_session_routes.py`
- `docs/ports.md`

## Documentation Cross-Links

- Start here for docs routing: [`index.md`](./index.md)
- Start here for operator workflow: [`../SKILL.md`](../SKILL.md)
- Use [`../README.md`](../README.md) for product-facing explanation, not code indexing

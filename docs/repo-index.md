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
| `tools/` | build helpers and manual utilities |
| `src/` | Main backend, frontend proxy, MCP tools, frontend assets |
| `oasis/` | OASIS engine and OpenClaw routes |
| `chatbot/` | Telegram / QQ bot integrations |
| `config/` | `.env`, TinyFish target files, requirements, users |
| `data/` | runtime DBs, prompts, user files, workflow files |
| `test/` | automated Python, Node, and browser smoke tests |
| `visual/` | standalone visual orchestrator app |

## Install and Configuration

Read these first for setup or environment changes:

| Path | Purpose |
|---|---|
| `selfskill/scripts/run.sh` | primary Linux / macOS install, configure, start flow |
| `selfskill/scripts/run.ps1` | primary Windows install, configure, start flow |
| `selfskill/scripts/configure.py` | `.env` initialization and configuration logic |
| `selfskill/scripts/configure_openclaw.py` | OpenClaw detection plus TeamClaw/OpenClaw LLM sync logic |
| `config/.env.example` | config template and inline guidance |
| `config/tinyfish_targets.example.json` | example TinyFish competitor target schema |
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
| `src/team_creator_service.py` | Team Creator discovery, extraction, build, jobs, and translation pipeline |
| `src/tinyfish_monitor_service.py` | shared TinyFish monitor runtime used by frontend, scheduler, and CLI |
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
- `src/acpx_adapter.py`
- `src/teambot_context.py`
- `src/teambot_permission_context.py`
- `src/teambot_policy.py`
- `src/teambot_profiles.py`
- `src/teambot_routes.py`
- `src/teambot_runtime.py`
- `src/teambot_runtime_store.py`
- `src/teambot_service.py`
- `src/teambot_subagents.py`
- `src/teambot_workspace.py`
- `src/logging_utils.py`

## Frontend Map

If the task touches the UI, start here:

| Path | Purpose |
|---|---|
| `src/static/js/main.js` | main desktop frontend logic |
| `src/static/css/style.css` | main desktop styling, including OASIS Town / swarm / ReportAgent panels |
| `src/front_teambot_routes.py` | Flask proxy routes for TeamBot runtime panel and tool policy |
| `src/static/js/creator.js` | Team Creator page logic, i18n, persistence, DAG preview |
| `src/static/css/creator.css` | Team Creator styles and DAG layout |
| `src/static/js/orchestration.js` | Studio canvas logic, including `Generate Team` |
| `src/templates/creator.html` | Team Creator HTML shell |
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
| `oasis/forum.py` | forum/topic data handling plus post/event hooks for living graph ingestion |
| `oasis/swarm_engine.py` | Town Genesis scaffold and LLM swarm blueprint generation |
| `oasis/graph_memory.py` | GraphRAG persistence, local SQLite fallback, optional Zep mirror, ReportAgent retrieval |
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
- `src/mcp_teambot.py`
- `src/mcp_telegram.py`
- `src/mcp_llmapi.py`

## ACP Exchange (acpx)

For external AI agent communication via the Agent Client Protocol:

| Path | Purpose |
|---|---|
| `src/acpx_adapter.py` | Singleton `AcpxAdapter` wrapping the `acpx` CLI; manages sessions and prompt execution |
| `src/group_service.py` | Primary acpx consumer; `_send_to_acp_agent()` broadcasts group chat messages to ACP agents |
| `oasis/experts.py` | `ExternalExpert` class uses ACP for pooled prompt communication with external agents |

Known ACP tools (external AI agents): `openclaw`, `codex`, `claude`, `gemini`, `aider`.

`acpx` is auto-installed during `bash selfskill/scripts/run.sh setup`. If missing, group chat ACP broadcasting and OASIS ExternalExpert ACP mode will be unavailable.

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
├── oasis_graph_memory.db
├── teambot_subagents.db
├── team_creator_jobs.db
├── prompts/
├── schedules/
└── user_files/{user_id}/
    ├── user_profile.txt
    ├── skills_manifest.json
    ├── teambot_agent_profiles.json
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
| `test/test_session_service.py` | session API filtering / deletion tests |
| `test/test_teambot_profiles.py` | TeamBot agent profile unit tests |
| `test/test_teambot_policy.py` | TeamBot tool policy and hook unit tests |
| `test/test_teambot_runtime.py` | TeamBot delegated runtime helper tests |
| `test/test_teambot_service.py` | TeamBot runtime API service tests |
| `test/test_teambot_subagents.py` | TeamBot subagent metadata store unit tests |
| `test/test_teambot_orchestration.py` | delegated subagent flow integration tests |
| `test/test_openai_protocol.py` | OpenAI protocol unit tests |
| `test/test_integration.py` | cross-service integration tests |
| `test/test_team_creator_jobs.py` | Team Creator job persistence tests |
| `test/test_team_creator_workflow.py` | Team Creator workflow/build tests |
| `test/test_team_creator_zip.py` | Team Creator ZIP export tests |
| `test/test_proxy_login_i18n.py` | frontend i18n and login proxy coverage |
| `test/test_tinyfish_monitor.py` | TinyFish target loading, persistence, and polling tests |
| `test/test_configure_openclaw_sync.py` | TeamClaw/OpenClaw LLM sync tests |
| `test/test_oasis_swarm_engine.py` | swarm scaffold / blueprint normalization tests |
| `test/test_oasis_graph_memory.py` | GraphRAG persistence, retrieval, and ReportAgent fallback tests |
| `test/browser/studio-smoke.spec.js` | Playwright smoke for `/studio` tabs, settings actions, and TeamBot runtime sidebar |
| `test/llm_live_smoke.py` | opt-in real provider LLM smoke test |
| `test/openclaw_live_smoke.py` | opt-in isolated OpenClaw gateway smoke test |
| `test/cloudflare_live_smoke.py` | opt-in Cloudflare quick tunnel smoke test |
| `npm run test:node` | frontend pure logic tests |
| `npm run test:browser-smoke` | browser smoke with the Flask test shell |
| `python test/tinyfish_live_smoke.py --site <site_key>` | opt-in real TinyFish smoke test |
| `uv run scripts/cli.py status` | smoke test services |
| `python -m py_compile <file>` | quick syntax check for touched Python files |
| `node --check src/static/js/creator.js` | quick Team Creator syntax check |
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
- `oasis/swarm_engine.py`
- `oasis/graph_memory.py`
- `docs/example_team.md`

### "Town Mode / swarm graph / ReportAgent looks wrong"

Read:

- `src/templates/index.html`
- `src/static/js/main.js`
- `src/static/css/style.css`
- `src/front_oasis_routes.py`
- `oasis/server.py`
- `oasis/swarm_engine.py`
- `oasis/graph_memory.py`

### "Team Creator or workflow-to-team is wrong"

Read:

- `docs/team-creator.md`
- `src/front.py`
- `src/team_creator_service.py`
- `src/static/js/creator.js`
- `src/static/css/creator.css`
- `src/templates/creator.html`
- `src/static/js/orchestration.js`
- `test/test_team_creator_jobs.py`
- `test/test_team_creator_workflow.py`
- `test/test_team_creator_zip.py`

### "OpenClaw integration is wrong"

Read:

- `docs/openclaw-commands.md`
- `oasis/openclaw_routes.py`
- `oasis/openclaw_cli.py`
- `docs/build_team.md`

### "TeamClaw and OpenClaw model settings drift"

Read:

- `docs/openclaw-commands.md`
- `selfskill/scripts/configure_openclaw.py`
- `selfskill/scripts/configure.py`
- `config/.env.example`

### "TinyFish monitor or pricing change detection is wrong"

Read:

- `docs/tinyfish-monitor.md`
- `src/tinyfish_monitor_service.py`
- `src/front.py`
- `src/time.py`
- `config/tinyfish_targets.example.json`
- `test/test_tinyfish_monitor.py`

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

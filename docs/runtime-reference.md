# Runtime Reference

This reference captures the architecture, service responsibilities, and runtime data layout for TeamClaw’s Claude-Code-inspired agent runtime. It emphasizes TeamBot, session state, MCP tooling, and the canonical runtime DTO that now powers the browser UI, CLI/BFF proxies, bridge clients, voice state, buddy state, and memory/Kairos surfaces.

## Architecture Map

```
Browser / Studio UI
    -> `src/front.py` (Flask UI + session auth + runtime proxies)
    -> `src/static/js/main.js` + runtime panel wiring (current-session card, bridge socket consumer, voice/buddy controls)
FastAPI services
    -> `src/mainagent.py` (OpenAI-compatible chat endpoints, session history, cancel)
    -> `src/teambot_routes.py` (runtime + policy APIs via `TeamBotService`)
    -> `src/teambot_service.py` (serializes runtime DTOs, policy/plan/todo persistence)
    -> `src/mcp_teambot.py` (MCP tools: spawn, send, inbox, ultrareview, ultraplan, dream, bridge hooks)
    -> `src/ops_service.py` (voice/TTS + direct connect hooks for audio uploads)
    -> `src/teambot_bridge.py` (bridge session issuance, websocket hub, runtime snapshot publish)
    -> `src/teambot_memory.py` / `src/teambot_voice.py` / `src/teambot_buddy.py` (browser-native parity services)
Persistence
    -> `data/teambot_runtime.db` (runs, attempts, inbox, artifacts, session state, memory, bridge, voice, buddy)
    -> `data/teambot_subagents.db` (subagent metadata)
    -> `data/user_files/{user_id}/` (profiles, policies, runtime artifacts, memory dirs, logs)
Side systems
    -> `oasis/` (Town Mode, workflows, swarm engine)
    -> `src/acpx_adapter.py` (ACP exchange with external AI agents via acpx CLI)
    -> TeamBot dream pipeline (`teambot_memory.py`) as the current browser-native autoDream layer
```

## Service Responsibilities

| Service | Ownership |
|---|---|
| `src/front.py` | Flask UI shell, authentication, TeamBot runtime proxy routes (`/proxy_teambot_*`), voice/TTS proxies, bridge-ready URLs. |
| `src/mainagent.py` | OpenAI-compatible chat API, session history, cancel, provider routing. |
| `src/teambot_service.py` | Serializes DTO (mode, plan, todos, approvals, inbox, artifacts, runs, relationships, bridge/voice/buddy/memory), enforces auth, counts inbox queue, exposes policy endpoints. |
| `src/mcp_teambot.py` | Durable spawn/send/cancel workflows, background run leasing, ultrareview/ultraplan orchestration, Kairos/dream tools, inbox delivery, runtime artifact logging, bridge/voice/buddy tools. |
| `src/teambot_runtime_store.py` | SQLite tables for runs, attempts, inbox messages, artifacts, session modes, verifications, tool approvals, memory state, bridge sessions, voice state, buddy state; helpers for leases/heartbeats/interruption/events. |
| `src/teambot_runtime.py` | Mode normalization, blocked tool lists, turn-limit messaging, surgical heuristics for plan/execute/review. |
| `src/teambot_policy.py` | Normalizes tool policies, events (`session_start`, `permission_request`, `stop`, etc.), hook definitions, serialization, router for `save_tool_policy_config`. |
| `src/agent.py` | Enforces tool filtering, injects runtime context, proxies MCP tooling into session handler, budgets history with `teambot_context`. |
| `src/ops_service.py` | Text-to-speech / audio proxy for voice mode; writes audio metadata into runtime payload via `front.py`. |
| `src/teambot_profiles.py` | Profile definitions (`general`, `research`, `planner`, `coder`, `reviewer`, `verifier`), helper `slugify`, built-in tool sets, user extension loading. |
| `src/teambot_context.py` | Budgeting helpers (tool results, user inputs) that log artifacts, perform compaction, build runtime summaries. |
| `src/teambot_workspace.py` | Worktree/remote/shared workspace resolution used when rendering runtime panel workspace text. |
| `src/front_teambot_routes.py` | Additional Flask proxies for runtime mode updates, plan/todo/verification APIs, supporting UI actions and bridge wiring. |
| `src/teambot_bridge.py` | Bridge attach/detach records, websocket route support, connected-client registry, publish helpers for runtime updates. |
| `src/teambot_memory.py` | Per-project memory directories, `MEMORY.md`, relevant entry recall, daily logs, dream gating, Kairos flags. |
| `src/teambot_voice.py` | Voice defaults + persisted per-session voice state derived from current LLM/audio provider. |
| `src/teambot_buddy.py` | Deterministic per-user companion state and reaction updates backed by the runtime store. |

## Runtime DTO

Every runtime request (`/teambot/session-runtime` → `TeamBotService.get_session_runtime`) returns:

- `mode`: current `execute/plan/review` mode plus reason/status.
- `plan`, `todos`, `verifications`, `approvals`: persisted states from `teambot_runtime_store`.
- `inbox`: queued messages from `teambot_session_inbox`, delivered via `_deliver_inbox_messages`.
- `artifacts`: runtime artifacts stored when budgets trigger (`teambot_context`, `_deliver_inbox_messages`).
- `runs`: `list_runs_for_session` results with `run_kind`, `mode`, `events`.
- `active_run`: latest `queued`/`running` run (main session or child).
- `relationships`: `parent_session` plus `children` aggregated via `list_subagents_for_parent_session`.
- `memory`: per-project memory metadata, daily logs, Kairos flag, dream timestamps, relevant entries, dream eligibility.
- `bridge`: bridge session records, attach code, websocket path, connection count, live status, role list.
- `voice`: enabled flag, provider defaults, STT/TTS models, read-aloud setting, last transcript.
- `buddy`: deterministic companion identity, soul/profile, reaction bubble, compact face, action metadata.

Internal modules use this DTO to keep the runtime panel, Flask proxies, MCP tools, prompt context injection, and bridge websocket payloads in sync.

## Data Layout

```
data/
├── teambot_runtime.db   (runs / attempts / inbox / artifacts / session_mode)
├── teambot_subagents.db (agent metadata: id/session/parent/status)
├── user_files/
│   └── {user_id}/
│       ├── teambot_tool_policy.json
│       ├── teambot_agent_profiles.json
│       ├── teambot_inbox_deliveries/
│       ├── teambot_tool_events.jsonl
│       ├── teambot_compactions/
│       ├── projects/{project_slug}/memory/
│       │   ├── MEMORY.md
│       │   └── logs/YYYY/MM/YYYY-MM-DD.md
│       └── ... (artifacts, bridge metadata)
```

## API Surface

- `/teambot/subagents` – list subagents with runtime status and queued inbox count.
- `/teambot/subagents/history` – fetch LangGraph snapshot messages for a subagent session.
- `/teambot/subagents/cancel` – cancel background runs gracefully.
- `/teambot/session-runtime` – primary runtime DTO consumed by Studio / CLI / bridge.
- `/teambot/session-mode` – switch execute/plan/review.
- `/teambot/session-inbox`, `/teambot/session-inbox/send`, `/teambot/session-inbox/deliver` – inbox list/send/deliver for cross-session messaging.
- `/teambot/runs/interrupt` – request interruption for an active runtime run.
- `/teambot/session-plan`, `/teambot/session-todos`, `/teambot/verifications` – plan/todo/verification CRUD.
- `/teambot/voice`, `/teambot/bridge/attach`, `/teambot/bridge/detach`, `/teambot/kairos`, `/teambot/dream`, `/teambot/buddy` – browser-native parity endpoints for voice, bridge, Kairos, dream, and companion control.
- `/teambot/tool-policy` – read/write policy and hook definitions.
- `/teambot/tool-approvals/resolve` – resolve manual approvals.
- `/teambot/ws/{user_id}/{bridge_id}` – websocket transport for bridge clients; emits `connected`, `runtime_snapshot`, and runtime-update pushes.
- `/proxy_teambot_*` (Flask) – front-end-friendly proxies for runtime data, policies, approvals, session mode, and tool approvals.

These APIs line up with MCP tools (`mcp_teambot`) so browser, agents, and remote-attached clients all operate on the same control plane.

## Related Docs

- [`teambot-agent-runtime.md`](./teambot-agent-runtime.md) – deep dive on runtime concepts and hooks.
- [`teambot-claude-gap-analysis.md`](./teambot-claude-gap-analysis.md) – matrix vs Claude Code and outstanding parity items.
- [`ports.md`](./ports.md) – route/port map.

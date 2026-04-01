# TeamBot-Agent Runtime Reference

This document records the current, running TeamBot delegated runtime that is now closer to Claude Code’s production agent than ever. It centers on the runtime control plane, lifecycle hooks, and the API/UX surfaces that expose mode, inbox, runs, memory, bridge, voice, and buddy state.

## Runtime Control Plane

- **Main session + subagents share a single runtime model.** `agent.py` and `teambot_service.py` expose `/teambot/session-runtime`, which reports the caller’s `mode`, `plan`, `todos`, `verifications`, `approvals`, `inbox`, `artifacts`, `runs`, `active_run`, `relationships`, `memory`, `bridge`, `voice`, and `buddy` fields. Every MCP call (`spawn_subagent`, `send_subagent_message`, `cancel`, `ultraplan`, `ultrareview`, etc.) reads/writes the same runtime store to keep the main session and children coherent.
- **Durable runs + leases.** `teambot_runtime_store.py` now records `TeamBotRunRecord` rows with `run_kind`, `mode`, `lease_expires_at`, `heartbeat_at`, `interrupt_requested`, and `metadata_json`. Helper APIs (`claim_run_worker`, `heartbeat_run`, `release_run_worker`, `request_run_interrupt`, `record_run_event`) guarantee runs survive MCP-worker restarts and can emit structured events for the frontend.
- **Inbox + artifact ledger.** `create_inbox_message`, `list_inbox_messages`, `mark_inbox_delivered` persist inbox queue entries. `_deliver_inbox_messages` batches queued entries into a single system trigger, writes the delivery text to `teambot_inbox_deliveries`, and records a `session_inbox_delivery` artifact via `create_runtime_artifact`. The frontend consumes `runtime.inbox` plus `runtime.artifacts` to render queues, deliveries, and history.

## Profiles, Modes & Hooks

- **Profiles + tool filtering.** Built-in profiles (`general`, `research`, `planner`, `coder`, `reviewer`, `verifier`) in `teambot_profiles.py` declare system prompt fragments, allowed tools, preferred models, and `max_turns`. User-defined profiles live under `data/user_files/{user_id}/teambot_agent_profiles.json` and the same MCP paths.
- **Session modes.** `teambot_runtime.py` normalizes `execute`, `plan`, `review`. `teambot_service.update_session_mode` persists the mode via `save_session_mode` and returns a payload with `reason`, `status`, `mode`. Mode-aware tool filtering uses `filter_tools_for_mode`, plan mode blocks destructive tools (write/delete), review mode tightens further.
- **Policy/hook pipeline.** `teambot_policy.py` now normalizes hooks for events such as `session_start`, `user_prompt_submit`, `pre_tool`, `post_tool`, `permission_request`, `permission_resolved`, `pre_compact`, `stop`, `subagent_stop`, `session_end`. Hooks can log to JSONL, run shell commands, or mutate arguments. `teambot_permission_context.py` enforces the decisions before MCP tools execute.
- **Compaction + budgets.** `teambot_context.py` trims long tool results, stores archival artifacts, compresses history into summaries, and writes `compact_summary` artifacts under `teambot_compactions`. Those summaries are already reused by the current memory/Kairos/dream flow and fit the Claude Code multi-tier compaction idea.

## Feature Coverage

- **Subagent orchestration.** `mcp_teambot.py` handles synchronous `spawn_subagent(wait=True)` flows, background queues, recoveries (`_recover_background_runs`), notifications to parent sessions, and explicit mode propagation (planner->plan, reviewer->review). Runs record `agent_type`, workspace metadata, and `run_events` produced by `record_run_event`.
- **Ultraplan & Ultrareview.** New APIs `ultraplan_start/status` and `ultrareview_start/status` create telemetry-rich runs, spawn child reviewers for each angle, aggregate findings, and record artifacts/logs so the frontend can surface plan approvals or reviewer summaries.
- **Memory, Kairos, AutoDream.** `teambot_memory.py` maintains per-project memory directories, `MEMORY.md`, relevant-entry recall, daily logs, and runtime-store sync. `run_auto_dream` applies time/session/lock gates, writes dream summaries, and updates `runtime.memory` so Kairos-style follow-ups can be triggered from the same control plane.
- **Bridge / Remote control.** `teambot_bridge.py` issues attachable bridge sessions, `teambot_routes.py` exposes `/teambot/ws/{user_id}/{bridge_id}`, and `teambot_service.py` now publishes runtime snapshots to connected bridge clients after mode, inbox, run, voice, Kairos, dream, buddy, and approval changes. The browser runtime panel consumes the same `runtime.bridge` payload and auto-reconnects while the sidebar is open.
- **Voice & Buddy (product parity focus).** The existing audio stack (`ops_service` for TTS, `main.js` recording + TTS UI) now persists `runtime.voice` per session and exposes toggle APIs/MCP tools. `teambot_buddy.py` provides deterministic per-user companion state, durable reactions, and runtime-panel actions instead of Claude Code’s terminal sprite renderer.

## Runtime Flow Recap

1. User hits `/studio` with a logged-in session; `main.js` loads the runtime panel via `/proxy_teambot_session_runtime`.
2. The runtime DTO includes the current session (main thread) plus subagents in `relationships.children`.
3. Mode, plan, todos, verifications, approvals, inbox, artifacts, runs, voice, bridge, buddy, and memory metadata all come from `teambot_service.get_session_runtime` and its helper serializers.
4. Actions (mode switch, deliver inbox, start ultraplan/ultrareview, voice record/play) call the corresponding MCP/Flask endpoints; the runtime store updates runs and artifacts, keeping the main session in sync with the control plane.

## File Map

| File | Role |
|---|---|
| `src/mcp_teambot.py` | Core orchestrator: queues, leases, ultrareview/ultraplan, dream gating, bridge/voice/buddy tools, runtime artifact logging |
| `src/teambot_runtime_store.py` | Durable tables for runs, attempts, inbox, artifacts, session state |
| `src/teambot_service.py` | Runtime API that serializes DTO for the frontend and proxies, tracks workspace descriptions, counts inbox/gate details |
| `src/teambot_runtime.py` | Utility functions (`normalize_session_mode`, mode messages, stop conditions, max_turn resolution) |
| `src/teambot_context.py` | Context budgeting, artifact logging for oversized inputs/results, compaction guardrails |
| `src/teambot_policy.py` | Policy normalization, hook/approval parsing, event enumeration |
| `src/agent.py` | Permits MCP tools, enforces tool filtering, injects runtime prompts, loads `teambot_runtime` helpers |
| `src/teambot_bridge.py` | Browser-native bridge session issuance, websocket connection registry, publish helpers |
| `src/teambot_memory.py` | Per-project memory directories, Kairos state, daily logs, dream summaries |
| `src/teambot_buddy.py` | Deterministic companion generation plus durable reaction state |
| `src/teambot_voice.py` | Session voice defaults/state adapter layered on top of existing audio providers |
| `src/front_teambot_routes.py` | Flask proxies for runtime APIs, bridging the JS UI with FastAPI backends |
| `src/teambot_profiles.py` | Profile definitions plus helper to build/parse `subagent__...` session ids |
| `src/teambot_workspace.py` | Worktree/remote/shared workspace resolution describing `workspace_mode` for the runtime card |
| `src/ops_service.py` | Text-to-speech (voice) backend that feeds audio metadata into runtime payloads |

## Runtime Best Practices

- Always call `spawn_subagent` with a `profile` that matches the work (planner/reviewer/coder) so `teambot_profiles` can apply the right mode and tool set.
- Keep `max_turns` low for research modes; `teambot_runtime.resolve_max_turns` already prefers explicit overrides and stops internal tools once limits hit.
- Use `send_subagent_message` for follow-ups so the existing session record is reused instead of creating duplicate sidechains.
- Keep the runtime panel open; it now renders `plan`, `todos`, `approvals`, `runs`, `inbox`, and `artifacts` for both the current session and any selected subagent.
- Policy hooks can mutate args and log events at every stage (session start, pre/post tool, permission request/resolution, session end).

## Related Docs

- [`runtime-reference.md`](./runtime-reference.md): service topography and auth.
- [`teambot-claude-gap-analysis.md`](./teambot-claude-gap-analysis.md): capability matrix vs Claude Code.

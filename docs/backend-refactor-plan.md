# TeamClaw Backend Refactor Plan

## Goals

- Keep all current API paths and features working.
- Reduce risk by refactoring in small, testable phases.
- Make backend architecture conversation-first and easier to evolve.

## Current Problems

1. Entry files are overloaded.
- `src/mainagent.py` mixes auth, chat protocol, settings, sessions, groups, and operational endpoints.
- `src/front.py` acts as both frontend server and large BFF/business proxy.
- `oasis/server.py` mixes discussion domain logic with system operations and OpenClaw utilities.

2. Business domains are not isolated.
- Chat, sessions, groups, OASIS, OpenClaw, and settings are coupled at route level.

3. Persistence access is scattered.
- `.env`, `users.json`, SQLite, and file storage are read/written directly across multiple handlers.

4. Cross-service contracts are implicit.
- `front -> mainagent`, `front -> oasis`, `scheduler -> mainagent`, `agent -> mcp -> oasis` lack explicit client/service boundaries.

## Target Architecture

Use layered boundaries per service:

- API layer: route + validation + response mapping only.
- Service layer: business logic and orchestration.
- Repository layer: storage access (`.env`, JSON, SQLite, filesystem).
- Integration layer: MCP clients, external APIs, subprocess wrappers.

## Migration Strategy

### Phase 1 (safe extraction, no API changes)

- Extract reusable auth utilities from `mainagent`.
- Extract `.env` settings read/write/mask/filter logic from `mainagent`.
- Keep route behavior and payload contracts unchanged.

### Phase 2 (mainagent decomposition)

- Split routes into modules: auth, chat, session, group, settings, system.
- Introduce explicit services and repositories.

### Phase 3 (front gateway slimming)

- Keep `front.py` as Flask UI + auth session + proxy.
- Move non-gateway business logic to `mainagent`/`oasis`.

### Phase 4 (oasis decomposition)

- Split `oasis/server.py` into topic/expert/workflow/openclaw modules.
- Isolate subprocess and filesystem operations behind service/repository helpers.

### Phase 5 (observability and hardening)

- Add structured logging and request IDs.
- Add integration tests for critical endpoints.
- Add migration/rollback playbook for config and DB changes.

## Acceptance Criteria

- Existing frontend routes and behavior stay compatible.
- No endpoint path changes in phases 1-2.
- Refactored modules have clear ownership and low coupling.
- Basic smoke tests pass for:
  - login
  - `/v1/chat/completions`
  - sessions/history/status
  - groups CRUD + messages
  - settings read/write
  - OASIS topics/workflows

## Progress Snapshot

- Phase 1 ✅ done:
  - Auth helpers extracted to `src/user_auth.py`.
  - `.env` settings logic extracted to `src/env_settings.py`.
- Phase 2 ✅ done:
  - Group chat endpoints and helpers extracted to `src/group_routes.py` and mounted via `app.include_router(...)`.
  - Group domain split into route/service/model layers (`src/group_routes.py`, `src/group_service.py`, `src/group_models.py`).
  - Group chat DB access moved to repository layer (`src/group_repository.py`), `group_service` now focuses on orchestration.
  - OpenAI compatibility endpoints (`/v1/chat/completions`, `/v1/models`) extracted to `src/openai_routes.py`.
  - OpenAI internals split into models/service layers (`src/openai_models.py`, `src/openai_service.py`), with `openai_routes.py` as thin adapter.
  - OpenAI service orchestration split into focused internal methods (input parsing, non-stream runner, stream runner, cancel-repair).
  - OpenAI runtime invocation context unified as `OpenAIExecutionContext`, reducing parameter fan-out between orchestrator and stream/non-stream executors.
  - Session endpoints extracted to `src/session_routes.py` (`/sessions`, `/sessions_status`, `/session_history`, `/delete_session`, `/session_status`).
  - Session domain split into route/service/model layers (`src/session_routes.py`, `src/session_service.py`, `src/session_models.py`).
  - Checkpoint DB access began moving to repository layer (`src/checkpoint_repository.py`), currently used by session/group services.
  - Shared bearer-token parsing extracted to `src/auth_utils.py`, reused by OpenAI/Group/Ops services to reduce duplicated auth branching.
  - Session deletion flow no longer reaches into `agent` private state directly; it now uses explicit `TeamAgent.list_active_task_keys(...)`.
  - Basic ops/auth endpoints extracted to `src/ops_routes.py` (`/tools`, `/login`, `/cancel`, `/tts`).
  - Ops/auth domain split into route/service/model layers (`src/ops_routes.py`, `src/ops_service.py`, `src/ops_models.py`).
  - Settings endpoints extracted to `src/settings_routes.py` (`/settings`, `/settings/full`, `/restart`).
  - Settings domain split into route/service/model layers (`src/settings_routes.py`, `src/settings_service.py`, `src/settings_models.py`).
  - System trigger endpoint extracted to `src/system_routes.py` (`/system_trigger`).
  - System trigger domain split into route/service/model layers (`src/system_routes.py`, `src/system_service.py`, `src/system_models.py`).
  - Session summary extraction logic unified in `src/session_summary.py` and reused by `mainagent` + group routes.
  - Multimodal message construction extracted to `src/message_builder.py`.
  - `src/mainagent.py` now focuses on app bootstrap, auth primitives, and router composition (177 lines, down from ~2000).
  - Agent runtime state extracted to `src/agent_runtime_state.py` (task registry + thread state registry), reducing `TeamAgent` state-management coupling.
  - OpenAI protocol conversion/encoding extracted to `src/openai_protocol.py`, with `openai_service` delegating message transform and response/chunk formatting.
  - Shared logging bootstrap added in `src/logging_utils.py`, and main chain modules (`mainagent/group/system/user_auth`) switched from ad-hoc `print` to logger.
- Phase 3 ✅ done:
  - Frontend gateway route split: group proxy routes moved to `src/front_group_routes.py`, OASIS proxy routes moved to `src/front_oasis_routes.py`.
  - Session proxy routes moved to `src/front_session_routes.py`, reducing `front.py` route density and keeping endpoint contracts unchanged.
  - `front.py` kept as Flask UI + auth session + proxy with ~300 lines removed from route density.
- Phase 4 ✅ done:
  - OASIS OpenClaw CLI helpers extracted to `oasis/openclaw_cli.py` and reused by `oasis/server.py`.
  - All OpenClaw routes (`/sessions/openclaw/*`, 14 endpoints) extracted to `oasis/openclaw_routes.py` using `APIRouter`.
  - `oasis/server.py` reduced from 1803 to 876 lines, now focused on topic/expert/workflow domains.
  - OpenClaw routes initialized via `init_openclaw_routes()` with explicit dependency injection.
- Phase 5 ✅ done:
  - Request ID propagation: `RequestIdMiddleware` in `mainagent.py` extracts/generates `X-Request-Id`, propagated via `contextvars` to all service-layer loggers.
  - Log format updated to include `[req:%(request_id)s]` in every log line via `logging_utils.py` filter.
  - Structured logging added to `openai_service`, `session_service`, `ops_service` (key operations: chat, login, cancel, session list/delete).
  - Unit tests: `test/test_agent_runtime_state.py` (12 tests), `test/test_openai_protocol.py` (19 tests).
  - Integration tests: `test/test_integration.py` (20 tests) covering Agent (sessions, settings, models, chat, request ID), OASIS (topics, experts, openclaw), Frontend (page access), and cross-service lifecycle.
  - Migration/rollback playbook: `docs/migration-playbook.md` with pre-checks, step-by-step migration, quick rollback, data recovery, and verification checklist.

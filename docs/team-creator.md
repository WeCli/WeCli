# Team Creator

Use this page when you want to build a Team from a business task, discovered SOP pages, or an existing workflow canvas.

## Entry Points

- `GET /creator`: standalone Team Creator page
- `mobile_group_chat`: Team Creator card in the discover area
- `GET /studio`: workflow canvas toolbar button `Generate Team`

## When To Use It

| Goal | Best Entry |
|---|---|
| Start from a plain-language task and let the system discover roles | Team Creator discovery mode |
| Paste or hand-edit a few known roles | Team Creator direct mode |
| Start from an existing workflow canvas and bulk-create a Team | `Generate Team` in Studio |
| Edit a Team completely through files or scripts | `docs/build_team.md` + CLI |

## Main Flow

### 1. Direct Role Definition

Direct mode lets the operator:

- set `team_name` and `task_description`
- add roles manually or paste role JSON
- pull preset experts from the shared expert pool
- keep preset experts bound to their full persona prompt instead of flattening them into short fields

Use this path when you already know the role list.

### 2. Discovery and Extraction

Discovery mode is a three-part pipeline:

1. `POST /api/team-creator/discover`
   - streams SSE events while the internal LLM finds SOP / org-structure URLs
   - can fall back to TinyFish browser search when needed
2. `POST /api/team-creator/extract`
   - streams SSE events while TinyFish extracts role data from each page
   - the UI shows per-page tabs, live logs, and browser previews
3. `POST /api/team-creator/smart-select`
   - ranks the extracted roles
   - matches them against the preset expert pool

This path is the best fit when the user starts with a business scenario rather than a finished team design.

### 3. Build, Preview, and Export

`POST /api/team-creator/build` converts the selected roles into a TeamClaw team config:

- `oasis_experts`
- Team member config
- OASIS workflow YAML
- DAG preview data

The page then shows:

- team summary stats
- editable persona cards
- `OASIS Workflow DAG`
- YAML source
- ZIP download and one-click import into TeamClaw

`POST /api/team-creator/download` uses the same snapshot-style ZIP format as the regular Team export flow.

## Bilingual and Dynamic Translation Behavior

Team Creator has two layers of localization:

- static UI strings are embedded in `src/static/js/creator.js`
- dynamic content can be translated on demand through `POST /api/team-creator/translate`

Dynamic translation is used for things like:

- discovered role names
- expert summaries
- persona snippets and other generated text

The preset expert pool uses the same bilingual data source as the message center expert browser. When a preset expert is added into `Define Team Roles`, the UI should keep the full preset persona attached to that role.

## Persistence and Build History

Team Creator persists state in two places:

- browser draft state: `window.sessionStorage` key `teamclaw_creator_session_v1`
- server build history: `data/team_creator_jobs.db`

Relevant job APIs:

- `GET /api/team-creator/jobs`
- `GET /api/team-creator/jobs/<job_id>`

The job record keeps the task description, extracted roles, build status, and the generated `team_config`.

If needed, set `TEAM_CREATOR_JOBS_DB_PATH` to move the jobs database.

## Workflow -> Generate Team

The Studio workflow canvas also supports a direct Team-generation flow through `orchGenerateTeam()` in `src/static/js/orchestration.js`.

That flow:

- scans canvas nodes of type `expert`, `session_agent`, and `external`
- deduplicates them by `tag`
- lets the user create a new Team or target an existing one
- checks tag conflicts against the target Team
- lets the user choose `skip` or `overwrite` per conflict
- submits the final payload to `POST /teams/<team_name>/generate-from-workflow`

Use this when the workflow graph already exists and you want to materialize the corresponding Team quickly.

## API Quick Reference

| Route | Purpose |
|---|---|
| `GET /creator` | render the Team Creator page |
| `POST /api/team-creator/discover` | stream discovery events for relevant pages |
| `POST /api/team-creator/extract` | stream extraction events for one page |
| `POST /api/team-creator/smart-select` | rank extracted roles and match presets |
| `POST /api/team-creator/build` | build the final team config |
| `POST /api/team-creator/download` | export the built config as ZIP |
| `POST /api/team-creator/translate` | dynamic bilingual translation |
| `GET /api/team-creator/presets` | backward-compatible preset list |
| `GET /api/team-creator/jobs` | list recent Team Creator build jobs |
| `GET /api/team-creator/jobs/<job_id>` | load one saved build |
| `POST /teams/<team_name>/generate-from-workflow` | create or extend a Team from workflow nodes |

## Relevant Files

| Path | Role |
|---|---|
| `src/front.py` | Team Creator routes and workflow-to-team endpoint |
| `src/team_creator_service.py` | discovery, extraction, build, ZIP, jobs, translation |
| `src/templates/creator.html` | Team Creator page shell |
| `src/static/js/creator.js` | Team Creator UI, i18n, persistence, preview rendering |
| `src/static/css/creator.css` | Team Creator layout and DAG styling |
| `src/static/js/orchestration.js` | `Generate Team` modal on the workflow canvas |
| `test/test_team_creator_jobs.py` | jobs persistence coverage |
| `test/test_team_creator_workflow.py` | workflow build coverage |
| `test/test_team_creator_zip.py` | ZIP export coverage |
| `test/test_proxy_login_i18n.py` | i18n-related frontend proxy coverage |

## Related Docs

- [build_team.md](./build_team.md)
- [create_workflow.md](./create_workflow.md)
- [oasis-reference.md](./oasis-reference.md)
- [repo-index.md](./repo-index.md)
- [runtime-reference.md](./runtime-reference.md)

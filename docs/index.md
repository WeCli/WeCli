# TeamClaw Documentation Index

This repository now uses a **progressive-disclosure** documentation layout:

1. `SKILL.md` is the entrypoint for agents and operators.
2. This file routes the current task to the right doc.
3. `repo-index.md` is the codebase map when you need to inspect or edit files.
4. Topic docs hold the detailed reference material.

If you are an agent, do **not** load everything by default. Start here and read only the docs needed for the current task.

## Entry Points

| File | Use It For |
|---|---|
| [`../SKILL.md`](../SKILL.md) | Installation, configuration, startup guardrails, task routing |
| [`../README.md`](../README.md) | Product overview, positioning, big-picture capabilities |
| [`repo-index.md`](./repo-index.md) | Codebase indexing and file lookup before editing code |

## Read By Task

| Task | Read First | Then Read |
|---|---|---|
| Install / configure / start TeamClaw | [`../SKILL.md`](../SKILL.md) | [`ports.md`](./ports.md) if ports or routing matter |
| Understand the platform | [`overview.md`](./overview.md) | [`../README.md`](../README.md) |
| Understand OASIS runtime behavior | [`oasis-reference.md`](./oasis-reference.md) | [`create_workflow.md`](./create_workflow.md), [`build_team.md`](./build_team.md) |
| Understand runtime architecture / auth / services | [`runtime-reference.md`](./runtime-reference.md) | [`ports.md`](./ports.md), [`repo-index.md`](./repo-index.md) |
| Find CLI syntax or examples | [`cli.md`](./cli.md) | `uv run scripts/cli.py <command> --help` |
| Build a Team | [`build_team.md`](./build_team.md) | [`example_team.md`](./example_team.md) |
| Create / debug workflow YAML | [`create_workflow.md`](./create_workflow.md) | [`example_team.md`](./example_team.md) |
| Configure OpenClaw or external agents | [`openclaw-commands.md`](./openclaw-commands.md) | [`build_team.md`](./build_team.md) |
| Inspect ports, proxies, or service boundaries | [`ports.md`](./ports.md) | [`repo-index.md`](./repo-index.md) |
| Deploy, migrate, or rollback | [`migration-playbook.md`](./migration-playbook.md) | [`backend-refactor-plan.md`](./backend-refactor-plan.md), [`repo-index.md`](./repo-index.md) |

## Document Groups

### Product / Orientation

- [`overview.md`](./overview.md): short explanation of what TeamClaw is and how people use it
- [`../README.md`](../README.md): user-facing overview, highlights, and public-facing narrative

### Operator / Builder Guides

- [`cli.md`](./cli.md): command catalog
- [`build_team.md`](./build_team.md): Team creation, internal agents, OpenClaw members, personas
- [`create_workflow.md`](./create_workflow.md): workflow YAML grammar and examples
- [`oasis-reference.md`](./oasis-reference.md): OASIS runtime model, expert types, execution semantics
- [`example_team.md`](./example_team.md): concrete file layout for a Team
- [`openclaw-commands.md`](./openclaw-commands.md): OpenClaw command and config reference
- [`ports.md`](./ports.md): ports, proxy routes, exposure rules

### Maintainer / Developer Docs

- [`runtime-reference.md`](./runtime-reference.md): runtime architecture, auth, service ownership
- [`repo-index.md`](./repo-index.md): where code and data live
- [`backend-refactor-plan.md`](./backend-refactor-plan.md): architecture roadmap
- [`migration-playbook.md`](./migration-playbook.md): rollout and rollback playbook

## Suggested Agent Reading Paths

### Install and run locally

1. Read [`../SKILL.md`](../SKILL.md)
2. If you need the service map, read [`ports.md`](./ports.md)
3. If setup scripts must be edited, read [`repo-index.md`](./repo-index.md)

### Build a Team and run workflows

1. Read [`build_team.md`](./build_team.md)
2. Read [`create_workflow.md`](./create_workflow.md)
3. Read [`oasis-reference.md`](./oasis-reference.md)
4. Read [`example_team.md`](./example_team.md)
5. If behavior looks wrong, inspect the indexed runtime files in [`repo-index.md`](./repo-index.md)

### Diagnose OpenClaw issues

1. Read [`openclaw-commands.md`](./openclaw-commands.md)
2. Read the OpenClaw section in [`build_team.md`](./build_team.md)
3. Inspect `oasis/openclaw_routes.py`, `oasis/openclaw_cli.py`, and related scripts via [`repo-index.md`](./repo-index.md)

### Modify the codebase

1. Read [`repo-index.md`](./repo-index.md)
2. Read the topic doc that matches the area you are changing
3. Open only the files indexed for that subsystem

## Current Structure Rationale

The important split is:

- `SKILL.md`: workflow and guardrails
- `README.md`: product story
- `docs/*.md`: task-specific reference
- `docs/oasis-reference.md` / `docs/runtime-reference.md`: extracted deep dives that no longer need to bloat the README
- `docs/repo-index.md`: code and data index

That keeps `SKILL.md` short enough for agents while still making the full repository discoverable.

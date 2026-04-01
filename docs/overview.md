# Overview

This page holds the higher-level product information that does not need to live in `README.md` or `SKILL.md`.

## What TeamClaw Is

TeamClaw is an OpenAI-compatible AI agent system with:

- a local `/v1/chat/completions` endpoint
- a TeamBot delegated-agent runtime with profile-based subagents
- a built-in multi-persona orchestration engine called OASIS
- a Team Studio sidebar for OASIS Town, swarm graphs, and ReportAgent
- living GraphRAG memory per topic, backed by local SQLite and optional Zep mirroring
- an AI-assisted Team Creator that can turn task descriptions or SOP pages into Teams
- lightweight built-in agents for files, commands, and messaging
- ACP exchange (acpx) for communicating with external AI agents (OpenClaw, Codex, Claude, Gemini, Aider) via the Agent Client Protocol
- optional integrations such as OpenClaw, TinyFish competitor monitoring, Telegram, QQ, and Cloudflare Tunnel

## Core Concepts

### Team

A Team combines:

- agents
- personas (expert persona prompts — special prompts that define identity, not separate agents)
- workflows

This lets TeamClaw move beyond single-agent chat into structured collaboration.

### OASIS

OASIS is the workflow engine behind coordinated persona-driven discussions and execution flows. It supports:

- sequential steps
- parallel branches
- conditional routing
- loops
- DAG-style dependency graphs
- Town Genesis swarm blueprints and graph-backed prediction topics
- ReportAgent explanations based on graph evidence instead of raw post replay

## Main Capabilities

- OpenAI-compatible chat API
- Team Creator for task-to-team drafting and workflow preview
- OASIS Town in the Team Studio sidebar
- GraphRAG long-term memory and report queries
- multi-session and multi-user isolation
- profile-bound delegated subagents for research / planning / coding / review / verification
- ACP exchange (acpx) for external agent communication in group chat and OASIS workflows
- Web UI on the local machine
- scheduled tasks
- competitor-site monitoring through TinyFish
- optional bot integration
- optional public exposure through Cloudflare Tunnel

## Typical Usage Modes

### Local assistant

Run TeamClaw on your own machine and use the local Web UI or the OpenAI-compatible API.

### Multi-persona orchestration

Create teams of personas and define workflows that debate, vote, summarize, or execute staged tasks.

### AI-assisted team drafting

Use Team Creator to discover public SOP pages, extract role definitions with TinyFish, and generate a draft Team plus DAG workflow before importing it into TeamClaw.

### Integration hub

Use TeamClaw as a bridge layer for bots, external tools, or other OpenAI-compatible clients.

## Where To Go Next

- Documentation map: [index.md](./index.md)
- Codebase map: [repo-index.md](./repo-index.md)
- Installation, Windows / WSL setup, startup expectations, access notes, and audio setup: `SKILL.md`
- Team Creator and workflow-to-team flow: [team-creator.md](./team-creator.md)
- OASIS runtime model and orchestration semantics: [oasis-reference.md](./oasis-reference.md)
- Runtime architecture and auth model: [runtime-reference.md](./runtime-reference.md)
- TeamBot delegated-agent runtime: [teambot-agent-runtime.md](./teambot-agent-runtime.md)
- CLI usage: [cli.md](./cli.md)
- Ports and service map: [ports.md](./ports.md)

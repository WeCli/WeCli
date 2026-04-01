**[English](#english) | [中文](#中文)**

---

<a id="english"></a>

# TeamClaw

![TeamClaw Poster](docs/poster.png)

> **An OpenAI-compatible local AI workspace with Teams, visual multi-agent orchestration, OASIS Town, living GraphRAG memory, multimodal I/O, bots, scheduled tasks, and one-click public access.**

## Product Video

<p align="center">
  <a href="https://youtu.be/amg87hiLRW0">
    <img src="./docs/media/teamclaw-demo-poster.jpg" alt="TeamClaw demo video" width="100%" />
  </a>
</p>

<p align="center">
  <a href="https://youtu.be/amg87hiLRW0">Watch the TeamClaw demo video on YouTube</a>
</p>

## Quick Start

### Install via AI Code CLI

Open any AI coding assistant such as **Codex**, **Cursor**, **Claude Code**, **CodeBuddy**, or **Trae**, and say:

```text
Clone https://github.com/BorisGuo6/TeamClaw.git, read SKILL.md, and install TeamClaw.
```

That agent should then:

1. Clone the repository
2. Read `SKILL.md`
3. Use `docs/index.md` to find the right docs
4. Configure the environment and LLM settings
5. Start the services

### Manual Setup

<details>
<summary>Click to expand manual setup</summary>

**Linux / macOS**

```bash
bash selfskill/scripts/run.sh setup
bash selfskill/scripts/run.sh configure --init

# If you already know the model:
bash selfskill/scripts/run.sh configure --batch \
  LLM_API_KEY=sk-xxx \
  LLM_BASE_URL=https://api.example.com \
  LLM_MODEL=<model>

# If you need model discovery:
bash selfskill/scripts/run.sh configure LLM_API_KEY sk-xxx
bash selfskill/scripts/run.sh configure LLM_BASE_URL https://api.example.com
bash selfskill/scripts/run.sh auto-model
bash selfskill/scripts/run.sh configure LLM_MODEL <model>

bash selfskill/scripts/run.sh start
```

`start` now also warms an installed OpenClaw gateway before the TeamClaw services come up, enables the OpenAI-compatible `chatCompletions` endpoint when needed, and refreshes the runtime `OPENCLAW_*` values in `config/.env`. It still does not silently import OpenClaw's LLM provider/model into TeamClaw.

For managed terminals, CI, or agent runners that reap child processes after the command exits, use `bash selfskill/scripts/run.sh start-foreground` and keep that session open instead of `start`.

**Windows PowerShell**

```powershell
powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 setup
powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 configure --init

# If you already know the model:
powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 configure --batch LLM_API_KEY=sk-xxx LLM_BASE_URL=https://api.example.com LLM_MODEL=<model>

# If you need model discovery:
powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 configure LLM_API_KEY sk-xxx
powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 configure LLM_BASE_URL https://api.example.com
powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 auto-model
powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 configure LLM_MODEL <model>

powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 start
```

For managed terminals or automation that reap child processes when the command returns, use `powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 start-foreground` and keep that session attached.

Open the UI at `http://127.0.0.1:<PORT_FRONTEND>`.
On Windows, ports may be auto-remapped; trust `config/.env` or `run.ps1 status`.

</details>

## Testing and CI

TeamClaw now treats `pytest` plus GitHub Actions as the default repeatable validation path.

```bash
# Python tests
uv venv .venv --python 3.11
uv pip install --python .venv/bin/python -r config/requirements-dev.txt
.venv/bin/python -m pytest

# OASIS Town / GraphRAG unit tests
.venv/bin/python -m unittest test.test_oasis_swarm_engine test.test_oasis_graph_memory -v

# Quick syntax checks for touched OASIS files
python3 -m py_compile oasis/swarm_engine.py oasis/graph_memory.py oasis/forum.py oasis/models.py oasis/server.py src/front_oasis_routes.py
node --check src/static/js/main.js

# Frontend logic test
npm ci
npm run test:node

# Browser smoke for /studio
npx playwright install --with-deps chromium
npm run test:browser-smoke
```

For a manual Town smoke after startup:

1. Open `http://127.0.0.1:51209/studio`
2. Log in; on first entry the Studio should land on `Chat`, keep the right `🏘️ OASIS Town` sidebar collapsed, keep `Town Mode` off, and default the workspace subtab to `TOWN`
3. Expand the right `🏘️ OASIS Town` sidebar in Team Studio
4. Open a topic with `autogen_swarm=true`, confirm the swarm graph appears
5. Toggle `Town Mode`, ask `ReportAgent`, and verify `REFORGE` / `EXPLAIN` work

GitHub Actions are split into:

- `ci-fast`: Python unit / contract tests plus Node pure logic tests on every `push` and `pull_request`
- `ci-smoke`: repeatable Flask integration tests plus a Playwright `/studio` smoke on every `push` and `pull_request`
- `ci-live`: opt-in or nightly live checks for TinyFish, OpenClaw, Cloudflare Tunnel, and real LLM providers

See [`.github/workflows/ci.yml`](.github/workflows/ci.yml) and [`.github/workflows/ci-live.yml`](.github/workflows/ci-live.yml).

### Optional: Public Access

Use Cloudflare Tunnel when you explicitly want remote access:

```bash
python scripts/tunnel.py
```

Or start it via the TeamClaw run scripts / frontend settings panel.

TeamClaw combines a local `/v1/chat/completions` endpoint, a built-in multi-expert orchestration engine called **OASIS**, a **Team Studio** sidebar for **OASIS Town**, live swarm graphs plus **ReportAgent**, and integrations such as **OpenClaw**, **Telegram**, **QQ**, **audio I/O**, **scheduled tasks**, **TinyFish competitor monitoring**, and **Cloudflare Tunnel**. OASIS topics can persist a living GraphRAG memory in local SQLite or mirror to **Zep** when `ZEP_API_KEY` is configured. TeamClaw supports any OpenAI-compatible provider — including **[Antigravity-Manager](https://github.com/lbjlaq/Antigravity-Manager)**, a local reverse proxy that gives free access to 67+ models (Claude, Gemini, GPT) for users with a Google One Pro membership (e.g. via student verification), and **[MiniMax](https://platform.minimaxi.com/)** with its 1M-context M2.7 model.

It is designed for both:

- people who want a powerful local AI control center
- AI coding agents that can clone the repo, read `SKILL.md`, and install / operate it autonomously

## Why TeamClaw

- **Team: unified multi-agent orchestration**: combine internal agents, OpenClaw agents, and external API agents into a single Team — with one-click import/export of complete Team configurations
- **ACP-powered external agent communication**: use `acpx` (auto-installed during setup) to broadcast messages to external AI agents like OpenClaw, Codex, Claude, Gemini, and Aider through the Agent Client Protocol
- **AI team builder built in**: use Team Creator to discover SOP pages, extract roles with TinyFish, and generate editable personas plus a DAG workflow
- **OpenAI-compatible from day one**: expose a local `/v1/chat/completions` endpoint that works with standard clients and custom tools
- **Claude-Code-style delegation inside TeamBot**: role-based subagents, persisted run/task state, plan/todo/verification primitives, approval-aware tool policy hooks, isolated/worktree child workspaces, stop/cancel support, and a frontend subagent plus policy panel
- **Visual orchestration included**: design workflows in OASIS, or save / run YAML workflows directly
- **Live observability built in**: open the right OASIS Town sidebar in Team Studio, watch the pixel town, inspect the swarm graph, and nudge or interrogate the discussion in real time
- **GraphRAG included**: seed each topic with a swarm blueprint, keep posts / callbacks / timeline events in a living graph, and optionally mirror retrieval to Zep
- **Real operator features**: settings UI, group chat, scheduled tasks, voice input, TTS, login tokens, and public tunnel support
- **Agent-first operations**: `SKILL.md` + `docs/index.md` + `docs/repo-index.md` let other coding agents install and manage TeamClaw with progressive disclosure

## What You Can Do Today

| Capability | What It Gives You |
|---|---|
| **OpenAI-compatible API** | Local chat completions endpoint for apps, tools, and clients |
| **Web UI** | Chat, settings, OASIS panel, group chat, tunnel control |
| **Team Creator** | Turn a task description or discovered SOP pages into roles, personas, and an OASIS DAG |
| **OASIS workflows** | Sequential, parallel, branching, and DAG-style expert orchestration |
| **OASIS Town** | Open a Team Studio sidebar with pixel-town mode, live residents, nudges, ambient audio, and a compact swarm graph |
| **GraphRAG memory** | Persist each topic as a living graph in local SQLite, with optional Zep mirroring for external retrieval |
| **ReportAgent** | Ask why the current prediction leans a certain way and get graph-backed evidence, watchouts, and confidence |
| **Team system** | Public/private agents, personas, workflows, and Team snapshots |
| **OpenClaw + external agents** | Bring in external runtimes and API-based agents |
| **Multimodal I/O** | Images, files, voice input, TTS, provider-aware audio defaults |
| **Bots** | Telegram and QQ integrations |
| **Automation** | Scheduled tasks and long-running workflow execution |
| **TinyFish monitor** | Crawl competitor pricing pages, store snapshots, and detect price changes over time |
| **Flow distribution platform** | Use [TeamClawHub](https://teamclawhub.com) to browse, distribute, and share TeamClaw flows |
| **Remote access** | Cloudflare Tunnel plus login-token / password flows |
| **Import / export** | Share or restore Teams and related assets |

## Flow Distribution Platform

TeamClaw also includes **[TeamClawHub](https://teamclawhub.com)** as its flow distribution platform.

- browse published TeamClaw flows
- distribute reusable workflows to other users
- share flow links as a lightweight workflow catalog entry

## Typical Use Cases

- **Local AI workspace**: run a private AI assistant with a browser UI and OpenAI-compatible API
- **Team debate and execution**: let multiple experts challenge, refine, and conclude on the same task
- **Live debate observability**: watch an OASIS discussion from the Team Studio Town sidebar, inspect the swarm graph, and inject nudges while it is running
- **Prediction / GraphRAG cockpit**: use OASIS topics as living world models with evidence-backed report answers
- **AI integration hub**: connect bots, external agent runtimes, and other OpenAI-compatible clients
- **Competitor monitoring**: schedule daily pricing crawls, compare stored snapshots, and inspect live crawl events from the settings UI
- **Operational cockpit**: manage settings, ports, audio, workflows, public access, and users from one place

## Product Highlights

### OASIS Orchestration

OASIS is the engine that turns TeamClaw from a chatbot into a programmable multi-expert system.

- combine stateless experts, stateful sessions, OpenClaw agents, and external API agents
- run sequential, parallel, selector-based, or DAG-style workflows
- support Team-level personas and reusable saved workflows
- seed a Town Genesis scaffold immediately, then upgrade it into a richer swarm graph
- persist topic memory as a living graph and optionally mirror retrieval into Zep
- open the current discussion in the Team Studio OASIS Town sidebar for live pixel-town view, graph inspection, and report queries
- monitor topics, conclusions, and session state from CLI or UI

### Teams and Personas

Each Team can combine:

- built-in lightweight internal agents
- OpenClaw agents
- external API agents
- public and private expert personas
- reusable workflows and Team snapshots

Team Creator can also draft that Team for you from a task description, discovered org/SOP pages, or a workflow canvas, then let you edit the final personas before import.

### Bots, Audio, and Operations

TeamClaw is no longer just chat + orchestration. It also includes:

- Telegram and QQ bot integration
- voice input and text-to-speech
- provider-aware audio defaults for OpenAI / Gemini-style setups
- TinyFish competitor-site monitoring with scheduled runs, live crawl, and price-change history
- settings UI and restart flow
- login tokens and password-based remote access
- scheduled tasks and system-triggered execution

## Acknowledgements

TeamClaw also benefited from several open-source projects:

- [`msitarzewski/agency-agents`](https://github.com/msitarzewski/agency-agents): inspiration for expanding our preset expert pool
- [`AGI-Villa/agent-town`](https://github.com/AGI-Villa/agent-town): reference for the interaction and presentation design behind OASIS Town
- [`tanweai/pua`](https://github.com/tanweai/pua): inspiration for upgrading our original critical expert into a stronger PUA-style reviewer persona

## Documentation Paths

Start with the level that matches your task:

- [`SKILL.md`](./SKILL.md): entrypoint skill, install flow, operator guardrails
- [`docs/index.md`](./docs/index.md): task-based documentation map
- [`docs/repo-index.md`](./docs/repo-index.md): codebase and data index

Deep dives:

- [`docs/overview.md`](./docs/overview.md): product overview
- [`docs/team-creator.md`](./docs/team-creator.md): Team Creator flow, jobs, bilingual UI, and workflow-to-team bridge
- [`docs/oasis-reference.md`](./docs/oasis-reference.md): OASIS runtime model and orchestration reference
- [`docs/runtime-reference.md`](./docs/runtime-reference.md): architecture, services, auth, and runtime reference
- [`docs/teambot-agent-runtime.md`](./docs/teambot-agent-runtime.md): TeamBot delegated subagents, profiles, and tool-boundary runtime
- [`docs/build_team.md`](./docs/build_team.md): Team creation and member configuration
- [`docs/create_workflow.md`](./docs/create_workflow.md): workflow YAML grammar and examples
- [`docs/cli.md`](./docs/cli.md): CLI command reference
- [`docs/openclaw-commands.md`](./docs/openclaw-commands.md): OpenClaw integration commands
- [`docs/tinyfish-monitor.md`](./docs/tinyfish-monitor.md): TinyFish competitor monitor and pricing-change tracking
- [`docs/ports.md`](./docs/ports.md): ports, exposure, proxy routes

## License

Apache License 2.0 — see [LICENSE](./LICENSE).

---

<a id="中文"></a>

# TeamClaw

> **一个 OpenAI 兼容的本地 AI 工作台：带 Team、多专家可视化编排、OASIS Town、长期 GraphRAG 记忆、多模态输入输出、Bot、定时任务，以及一键公网访问。**

## 产品视频

<p align="center">
  <a href="https://youtu.be/amg87hiLRW0">
    <img src="./docs/media/teamclaw-demo-poster.jpg" alt="TeamClaw 演示视频" width="100%" />
  </a>
</p>

<p align="center">
  <a href="https://youtu.be/amg87hiLRW0">点击在 YouTube 观看 TeamClaw 演示视频</a>
</p>

## 快速开始

### 通过 AI Code CLI 安装

在 **Codex**、**Cursor**、**Claude Code**、**CodeBuddy**、**Trae** 之类的 AI 编码助手里输入：

```text
Clone https://github.com/BorisGuo6/TeamClaw.git，读取 SKILL.md，然后安装 TeamClaw。
```

正常情况下，这个 Agent 会自动：

1. 克隆仓库
2. 阅读 `SKILL.md`
3. 通过 `docs/index.md` 找到需要的文档
4. 配置环境和 LLM
5. 启动服务

### 手动安装

<details>
<summary>点击展开手动安装步骤</summary>

**Linux / macOS**

```bash
bash selfskill/scripts/run.sh setup          # 安装 uv、虚拟环境、依赖和 acpx（ACP 通信插件）
bash selfskill/scripts/run.sh configure --init

# 如果已经知道模型：
bash selfskill/scripts/run.sh configure --batch \
  LLM_API_KEY=sk-xxx \
  LLM_BASE_URL=https://api.example.com \
  LLM_MODEL=<model>

# 如果还不知道模型：
bash selfskill/scripts/run.sh configure LLM_API_KEY sk-xxx
bash selfskill/scripts/run.sh configure LLM_BASE_URL https://api.example.com
bash selfskill/scripts/run.sh auto-model
bash selfskill/scripts/run.sh configure LLM_MODEL <model>

bash selfskill/scripts/run.sh start
```

`start` 现在也会在 TeamClaw 服务启动前预热本机已安装的 OpenClaw gateway，必要时自动打开 `chatCompletions` 兼容端点，并刷新 `config/.env` 里的运行时 `OPENCLAW_*` 配置；但它仍然不会静默把 OpenClaw 的 LLM provider/model 导入 TeamClaw。

如果你所在的受管终端、CI 或 agent runner 会在命令返回后清理子进程，请改用 `bash selfskill/scripts/run.sh start-foreground`，并保持该会话处于打开状态。

**Windows PowerShell**

```powershell
powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 setup
powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 configure --init

# 如果已经知道模型：
powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 configure --batch LLM_API_KEY=sk-xxx LLM_BASE_URL=https://api.example.com LLM_MODEL=<model>

# 如果还不知道模型：
powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 configure LLM_API_KEY sk-xxx
powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 configure LLM_BASE_URL https://api.example.com
powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 auto-model
powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 configure LLM_MODEL <model>

powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 start
```

如果当前终端或自动化平台会在命令返回后回收子进程，请改用 `powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 start-foreground`，并保持该会话不断开。

启动后访问 `http://127.0.0.1:<PORT_FRONTEND>`。
Windows 上端口可能自动换位，请以 `config/.env` 或 `run.ps1 status` 为准。

</details>

## 测试与验证

TeamClaw 现在默认把 `pytest`、单元测试和 `/studio` 浏览器烟测作为可重复验证路径。

```bash
# Python tests
uv venv .venv --python 3.11
uv pip install --python .venv/bin/python -r config/requirements-dev.txt
.venv/bin/python -m pytest

# OASIS Town / GraphRAG 单测
.venv/bin/python -m unittest test.test_oasis_swarm_engine test.test_oasis_graph_memory -v

# OASIS 相关快速语法检查
python3 -m py_compile oasis/swarm_engine.py oasis/graph_memory.py oasis/forum.py oasis/models.py oasis/server.py src/front_oasis_routes.py
node --check src/static/js/main.js

# 前端纯逻辑测试
npm ci
npm run test:node

# /studio 浏览器烟测
npx playwright install --with-deps chromium
npm run test:browser-smoke
```

Town 手动烟测路径：

1. 打开 `http://127.0.0.1:51209/studio`
2. 登录后第一次进入 Studio 应默认落在 `Chat`，右侧 `🏘️ OASIS Town` 侧栏保持折叠、`Town Mode` 为关闭状态、子 tab 默认为 `TOWN`
3. 展开 Team Studio 右侧 `🏘️ OASIS Town` 侧栏
4. 打开带 `autogen_swarm=true` 的 topic，确认 swarm graph 出现
5. 切换 `Town Mode`，再用 `REFORGE` 和 `EXPLAIN` 验证 GraphRAG / ReportAgent

### 可选：公网访问

当你明确需要远程访问时，再开启 Cloudflare Tunnel：

```bash
python scripts/tunnel.py
```

也可以通过 TeamClaw 的运行脚本或前端设置页启动。

TeamClaw 把这些能力放进了同一个项目里：

- 本地 `/v1/chat/completions` 接口
- 内置多专家编排引擎 **OASIS**
- Team Studio 右侧侧栏里的 **OASIS Town** 实时像素小镇视图
- 本地 SQLite + 可选 Zep 的 **GraphRAG 长期记忆**
- 支持解释当前预测路径的 **ReportAgent**
- 完整 Web UI
- **OpenClaw** / 外部 API Agent 接入
- **[Antigravity-Manager](https://github.com/lbjlaq/Antigravity-Manager)** 本地反代（通过 Google One Pro 会员免费使用 67+ 模型）
- **[MiniMax](https://platform.minimaxi.com/)** M2.7 模型支持（1M context，OpenAI 兼容 API）
- **Telegram / QQ Bot**
- **图片 / 文件 / 语音 / TTS**
- **定时任务**
- **TinyFish 竞品网站监控**
- **Cloudflare Tunnel 公网访问**

它同时适合两类人：

- 想要一个本地 AI 控制台的个人或团队
- 能自己读 `SKILL.md` 并自动安装 / 运维 TeamClaw 的 AI 编码 Agent

## 为什么是 TeamClaw

- **Team：统一的多 Agent 编排**：将内部 Agent、OpenClaw Agent、外部 API Agent 组合成单一 Team，支持一键导入导出完整 Team 配置
- **自带 AI 团队构建器**：通过 Team Creator 发现 SOP 页面、用 TinyFish 抽取角色，并生成可编辑的人设和 DAG 工作流
- **开箱就是 OpenAI 兼容接口**：本地 endpoint 可直接接各种客户端和工具
- **自带可视化编排**：在 OASIS 里设计工作流，也可以直接保存 / 运行 YAML
- **自带实时观战模式**：在 Team Studio 右侧打开 OASIS Town，实时观察像素小镇、swarm graph，并继续插入 nudge
- **自带 GraphRAG 长期记忆**：每个 topic 都能沉淀为 living graph，可选镜像到 Zep
- **运维能力完整**：设置页、群聊、定时任务、语音输入、TTS、登录 token、公网隧道都在同一套里
- **对 Agent 友好**：`SKILL.md` + `docs/index.md` + `docs/repo-index.md` 形成渐进式披露路径

## 现在已经能做什么

| 能力 | 价值 |
|---|---|
| **OpenAI 兼容 API** | 给应用、脚本、客户端提供本地模型入口 |
| **Web UI** | 聊天、设置、OASIS 面板、群聊、隧道控制 |
| **Team Creator** | 把任务描述或发现到的 SOP 页面转换成角色、人设和 OASIS DAG |
| **OASIS 工作流** | 顺序、并行、分支、DAG 风格的专家编排 |
| **OASIS Town** | 在 Team Studio 右侧打开像素小镇视图，可边看边继续插入 nudge |
| **GraphRAG 长期记忆** | 把每个 topic 持久化成 living graph，默认落本地 SQLite，可选外接 Zep |
| **ReportAgent** | 追问“为什么这样预测”，返回带证据、watchouts 和置信度的解释 |
| **Team 系统** | 公共 / 私有 Agent、人设、Workflow、Team 快照 |
| **OpenClaw / 外部 Agent** | 接入外部运行时和 API 型 Agent |
| **ACP 通信 (acpx)** | 通过 ACP 协议与外部 AI Agent（OpenClaw、Codex、Claude、Gemini、Aider）通信；`setup` 时自动安装 |
| **多模态 I/O** | 图片、文件、语音输入、TTS、provider-aware 音频默认值 |
| **Bot 集成** | Telegram / QQ |
| **自动化** | 定时任务、长流程工作流执行 |
| **TinyFish 竞品监控** | 通过 TinyFish Web Agent 抓取竞品页面、保存价格快照并检测变化 |
| **Flow 分发平台** | 通过 [TeamClawHub](https://teamclawhub.com) 浏览、分发和分享 TeamClaw Flows |
| **远程访问** | Cloudflare Tunnel + token / 密码登录 |
| **导入导出** | 分享和恢复 Team 及相关资源 |

## Flow 分发平台

TeamClaw 还配套提供了 **[TeamClawHub](https://teamclawhub.com)** 作为 Flow 分发平台。

- 浏览已经发布的 TeamClaw Flows
- 把可复用工作流分发给其他用户
- 通过链接分享 Flow，作为轻量级工作流目录入口

## 典型使用场景

- **本地 AI 工作台**：浏览器里直接用，也能给其他工具当 OpenAI 兼容后端
- **多专家讨论与执行**：让多个专家相互挑战、补充、汇总结论
- **实时观战与插话**：在 Team Studio 的 Town 侧栏里用像素小镇观察 OASIS 讨论进展，并在中途继续加 prompt
- **预测 / GraphRAG 控制台**：把 OASIS topic 当成 living world model 来追踪节点、边、证据和报告
- **AI 集成中枢**：接 Bot、接 OpenClaw、接外部 API Agent、接已有 OpenAI 客户端
- **竞品价格巡检**：定时抓取公开定价页，保存快照，对比新增 / 调价 / 下线项目
- **运维控制面板**：统一管理设置、音频、端口、用户、工作流和公网访问

## 产品亮点

### OASIS 多专家编排

OASIS 让 TeamClaw 从“聊天工具”变成“可编程的多专家系统”。

- 可以混合无状态专家、有状态会话、OpenClaw Agent、外部 API Agent
- 支持顺序、并行、选择器、DAG 风格工作流
- 支持 Team 级 persona 和可复用 workflow
- 可以先生成 Town Genesis scaffold，再升级成更丰富的 swarm graph
- 可以把帖子、callback、timeline、结论持续写回 living graph，并按需镜像到 Zep
- 可以在 Team Studio 的 OASIS Town 侧栏里以像素小镇方式实时观战、看图谱、问 ReportAgent
- 可以从 CLI 或 UI 里查看 topic、结论和会话状态

### Team 与 Persona

每个 Team 可以组合：

- 内置轻量 internal agents
- OpenClaw agents
- 外部 API agents
- 公共 / 私有 expert personas
- 可复用 workflows 和 Team snapshots

如果你不想从零手写，Team Creator 还可以从任务描述、公开 SOP / 组织结构页面，或现有 workflow 画布里先帮你生成一版 Team，再在导入前编辑最终 persona。

### Bot、音频与运维

TeamClaw 现在不只是“聊天 + 编排”，还包括：

- Telegram / QQ Bot
- 语音输入和文字转语音
- OpenAI / Gemini 风格配置下的 provider-aware 音频默认值
- TinyFish 竞品监控，支持定时巡检、实时爬取和价格变化记录
- 设置页与一键重启
- 登录 token 与远程密码登录
- 定时任务与 system trigger 执行

## 致谢

TeamClaw 的一些设计也受到了这些开源项目的启发：

- [`msitarzewski/agency-agents`](https://github.com/msitarzewski/agency-agents)：参考其思路扩展了我们的预设专家池
- [`AGI-Villa/agent-town`](https://github.com/AGI-Villa/agent-town)：参考其设计实现了 OASIS Town 的交互与表现方式
- [`tanweai/pua`](https://github.com/tanweai/pua)：用于改进我们原本的批判专家，升级成更强的 PUA 风格专家

## 文档入口

按任务深度选择阅读层级：

- [`SKILL.md`](./SKILL.md)：入口 skill、安装流、运维 guardrails
- [`docs/index.md`](./docs/index.md)：任务型文档索引
- [`docs/repo-index.md`](./docs/repo-index.md)：仓库和数据索引

深入文档：

- [`docs/overview.md`](./docs/overview.md)：产品概览
- [`docs/team-creator.md`](./docs/team-creator.md)：Team Creator 流程、构建记录、双语 UI 与 workflow 转 Team
- [`docs/oasis-reference.md`](./docs/oasis-reference.md)：OASIS 运行模型与编排参考
- [`docs/runtime-reference.md`](./docs/runtime-reference.md)：架构、服务、鉴权与运行时参考
- [`docs/teambot-agent-runtime.md`](./docs/teambot-agent-runtime.md)：TeamBot 子 Agent、Profile 与工具边界运行时
- [`docs/build_team.md`](./docs/build_team.md)：Team 创建与成员配置
- [`docs/create_workflow.md`](./docs/create_workflow.md)：workflow YAML 语法与示例
- [`docs/cli.md`](./docs/cli.md)：CLI 命令参考
- [`docs/openclaw-commands.md`](./docs/openclaw-commands.md)：OpenClaw 集成命令
- [`docs/tinyfish-monitor.md`](./docs/tinyfish-monitor.md)：TinyFish 竞品监控与价格变化追踪
- [`docs/ports.md`](./docs/ports.md)：端口、暴露方式、代理路由

## 许可证

Apache License 2.0 — 详见 [LICENSE](./LICENSE)。

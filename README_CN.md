# Wecli

**[English README](./README.md)**

<p align="center">
  <img src="docs/poster.jpg" alt="Wecli Poster" width="360" />
</p>

> **一个 OpenAI 兼容的本地 AI 工作台：带 Team、多专家可视化编排、OASIS Town、长期 GraphRAG 记忆、多模态输入输出、Bot、定时任务，以及一键公网访问。**

## 产品视频

<p align="center">
  <a href="https://youtube.com/shorts/OKuZNwz-CP0">
    <img src="./docs/media/wecli-demo-poster.jpg" alt="Wecli 演示视频" width="360" />
  </a>
</p>

<p align="center">
  <a href="https://youtube.com/shorts/OKuZNwz-CP0">点击在 YouTube 观看 Wecli 演示视频</a>
</p>

## 快速开始

### 通过 AI Code CLI 安装

在 **Codex**、**Cursor**、**Claude Code**、**CodeBuddy**、**Trae** 之类的 AI 编码助手里输入：

```text
Clone https://github.com/WeCli/WeCli.git，读取 AGENTS.md，然后安装 Wecli。
```

### 手动安装

<details>
<summary>点击展开手动安装步骤</summary>

**Linux / macOS**

```bash
bash selfskill/scripts/run.sh setup
bash selfskill/scripts/run.sh configure --init
bash selfskill/scripts/run.sh start
# → 打开 http://127.0.0.1:51209
# → 首次登录：localhost 免密登录
# → 如果 LLM 未配置，向导会自动弹出
```

**Windows PowerShell**

```powershell
powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 setup
powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 configure --init
powershell -ExecutionPolicy Bypass -File .\selfskill\scripts\run.ps1 start
```

启动后访问 `http://127.0.0.1:<PORT_FRONTEND>`。

</details>

完整安装指南（OpenClaw、Antigravity、MiniMax、WSL、手动 CLI 配置、故障排查）请参见 [`SKILL.md`](./SKILL.md)。

## 为什么是 Wecli

- **Team：统一的多 Agent 编排** — 将内部 Agent、OpenClaw Agent、外部 API Agent 组合成单一 Team，支持一键导入导出
- **ACP 通信** — 通过 `acpx` 与 OpenClaw、Codex、Claude、Gemini、Aider 等外部 AI Agent 通信
- **自带 AI 团队构建器** — 通过 WeCli Creator 发现 SOP 页面、用 TinyFish 抽取角色，生成可编辑的人设和 DAG 工作流
- **开箱就是 OpenAI 兼容接口** — 本地 `/v1/chat/completions` 可直接接各种客户端和工具
- **类 Claude Code 的委托代理** — 角色化子 Agent、持久化运行状态、计划/待办/验证原语、审批感知工具策略
- **自带可视化编排** — 在 OASIS 里设计工作流，也可以直接保存 / 运行 YAML
- **自带实时观战模式** — 在 WeCli Studio OASIS Town 侧栏实时观察像素小镇、swarm graph，并插入 nudge
- **自带 GraphRAG 长期记忆** — 每个 topic 沉淀为 living graph，可选镜像到 Zep
- **运维能力完整** — 设置页、群聊、定时任务、语音、TTS、登录 token、公网隧道
- **对 Agent 友好** — `AGENTS.md` + `SKILL.md` + `docs/index.md` 形成渐进式披露路径

## 现在已经能做什么

| 能力 | 价值 |
|---|---|
| **OpenAI 兼容 API** | 给应用、脚本、客户端提供本地模型入口 |
| **Web UI** | 聊天、设置、OASIS 面板、群聊、隧道控制 |
| **WeCli Creator** | 把任务描述或 SOP 页面转换成角色、人设和 OASIS DAG |
| **OASIS 工作流** | 顺序、并行、分支、DAG 风格的专家编排 |
| **OASIS Town** | WeCli Studio 侧栏像素小镇视图 + swarm graph |
| **GraphRAG 长期记忆** | 本地 SQLite + 可选 Zep 镜像 |
| **ReportAgent** | 追问"为什么这样预测"，返回带证据和置信度的解释 |
| **Team 系统** | 公共/私有 Agent、人设、Workflow、Team 快照 |
| **OpenClaw / 外部 Agent** | 接入外部运行时和 API 型 Agent |
| **ACP 通信 (acpx)** | 与外部 AI Agent 通信；`setup` 时自动安装 |
| **多模态 I/O** | 图片、文件、语音输入、TTS |
| **Bot 集成** | Telegram / QQ |
| **自动化** | 定时任务、长流程工作流执行 |
| **TinyFish 竞品监控** | 抓取竞品页面、保存快照并检测变化 |
| **Flow 分发平台** | 通过 [WecliHub](https://wecli.net) 浏览和分享 |
| **远程访问** | Cloudflare Tunnel + token / 密码登录 |
| **导入导出** | 分享和恢复 Team 及相关资源 |

## Flow 分发平台

**[WecliHub](https://wecli.net)** 是配套的 Flow 分发平台：浏览、分发和分享 Wecli Flows。

## 典型使用场景

- **本地 AI 工作台** — 浏览器里直接用，也能给其他工具当 OpenAI 兼容后端
- **多专家讨论与执行** — 让多个专家相互挑战、补充、汇总结论
- **实时观战与插话** — 在 Town 侧栏用像素小镇观察讨论进展并插入 prompt
- **预测 / GraphRAG 控制台** — 追踪节点、边、证据和报告
- **AI 集成中枢** — 接 Bot、接 OpenClaw、接外部 API Agent
- **竞品价格巡检** — 定时抓取公开定价页，检测变化
- **运维控制面板** — 统一管理设置、音频、端口、用户、工作流和公网访问

## 产品亮点

### OASIS 多专家编排

混合无状态专家、有状态会话、OpenClaw Agent、外部 API Agent。支持顺序、并行、选择器、DAG 风格工作流。可在 WeCli Studio OASIS Town 侧栏实时观战、看图谱、问 ReportAgent。

### Team 与 Persona

每个 Team 可以组合内置 Agent、OpenClaw Agent、外部 API Agent、公共/私有人设、可复用 Workflow。WeCli Creator 可从任务描述、SOP 页面或 workflow 画布自动生成。

### Bot、音频与运维

Telegram/QQ Bot、语音输入/TTS、TinyFish 竞品监控、设置页、登录 token、定时任务。

## 致谢

- [`msitarzewski/agency-agents`](https://github.com/msitarzewski/agency-agents) — 参考其思路扩展了预设专家池
- [`AGI-Villa/agent-town`](https://github.com/AGI-Villa/agent-town) — 参考其设计实现了 OASIS Town
- [`tanweai/pua`](https://github.com/tanweai/pua) — 用于改进批判专家为 PUA 风格

## 文档

| 文件 | 读者 | 用途 |
|---|---|---|
| [`AGENTS.md`](./AGENTS.md) | AI Agent | 行为规则、任务路由、渐进式披露 |
| [`SKILL.md`](./SKILL.md) | Agent + 人类 | 完整安装、配置、Debug、故障排查指南 |
| [`docs/index.md`](./docs/index.md) | 两者 | 任务型文档索引 |

## 许可证

Apache License 2.0 — 详见 [LICENSE](./LICENSE)。

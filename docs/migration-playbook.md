# Migration & Rollback Playbook

本文档记录 TeamClaw 后端重构的迁移步骤和回滚方案。

## 目录

1. [概述](#概述)
2. [前置检查](#前置检查)
3. [迁移步骤](#迁移步骤)
4. [回滚方案](#回滚方案)
5. [数据库变更](#数据库变更)
6. [配置变更](#配置变更)
7. [验证清单](#验证清单)

---

## 概述

本次重构从 Phase 1 到 Phase 5 分阶段进行，**所有 API 端点路径和请求/响应格式保持不变**。
重构范围仅限于代码组织和内部架构，不涉及数据库 schema 变更或配置格式变更。

### 影响范围

| 服务 | 变更内容 | 风险等级 |
|------|---------|---------|
| Agent (mainagent) | 路由模块化拆分，177 行入口 | 低 |
| OASIS | OpenClaw 路由提取到独立模块 | 低 |
| Frontend (front) | 代理路由提取到模块 | 低 |

---

## 前置检查

### 部署前

```bash
# 1. 确认当前版本
git log -1 --oneline

# 2. 记录当前 commit hash（回滚时使用）
git rev-parse HEAD > /tmp/teamclaw_rollback_hash

# 3. 备份数据文件
cp data/agent_memory.db data/agent_memory.db.bak
cp data/group_chat.db data/group_chat.db.bak
cp config/.env config/.env.bak
cp config/users.json config/users.json.bak

# 4. 验证 Python 语法
find src/ oasis/ -name "*.py" -exec python3 -m py_compile {} \;

# 5. 运行单元测试
uv run python -m pytest test/test_agent_runtime_state.py test/test_openai_protocol.py -v
```

---

## 迁移步骤

### Step 1: 拉取最新代码

```bash
git pull origin main
```

### Step 2: 安装依赖

```bash
uv sync
```

### Step 3: 停止服务

```bash
bash selfskill/scripts/run.sh stop
sleep 3
```

### Step 4: 验证配置兼容性

```bash
# 确认 .env 中 INTERNAL_TOKEN 存在
grep "INTERNAL_TOKEN=" config/.env

# 确认端口配置
grep "PORT_" config/.env
```

### Step 5: 启动服务

```bash
bash selfskill/scripts/run.sh start
sleep 5
```

如果迁移是在受管终端、CI 或 agent runner 中执行，而该环境会在命令返回后清理子进程，请改用 `bash selfskill/scripts/run.sh start-foreground` 并保持该会话处于运行状态。

### Step 6: Smoke Test

```bash
# CLI 快速验证
uv run scripts/cli.py status

# 端到端测试
uv run python -m pytest test/test_integration.py -v
```

### Step 7: 验证日志

```bash
# 确认 request_id 出现在日志中
tail -20 logs/launcher.log | grep "req:"
```

---

## 回滚方案

### 快速回滚（< 1 分钟）

```bash
# 1. 停止服务
bash selfskill/scripts/run.sh stop

# 2. 回滚代码到之前版本
git checkout $(cat /tmp/teamclaw_rollback_hash)

# 3. 恢复配置（如果有变更）
cp config/.env.bak config/.env
cp config/users.json.bak config/users.json

# 4. 重启服务
bash selfskill/scripts/run.sh start

# 5. 验证
uv run scripts/cli.py status
```

### 数据恢复（仅在数据损坏时）

```bash
# 恢复数据库
cp data/agent_memory.db.bak data/agent_memory.db
cp data/group_chat.db.bak data/group_chat.db

# 重启服务
bash selfskill/scripts/run.sh stop && sleep 2 && bash selfskill/scripts/run.sh start
```

### 回滚验证

```bash
uv run scripts/cli.py status
uv run scripts/cli.py -u Avalon_01 sessions
uv run scripts/cli.py -u Avalon_01 openclaw sessions
```

---

## 数据库变更

### 本次重构不涉及数据库 schema 变更

| 数据库 | 变更 | 说明 |
|--------|------|------|
| `data/agent_memory.db` | 无 | checkpoint 存储，schema 由 langgraph 管理 |
| `data/group_chat.db` | 无 | 群聊消息存储 |
| `oasis/data/*.json` | 无 | 专家/主题 JSON 文件，格式不变 |

---

## 配置变更

### .env 自动变更

| 变量 | 说明 |
|------|------|
| `INTERNAL_TOKEN` | 首次启动时自动生成（如果不存在） |

### 新增文件（不影响旧版本）

| 文件 | 说明 |
|------|------|
| `src/openai_routes.py` | OpenAI 兼容路由 |
| `src/session_routes.py` | 会话路由 |
| `src/group_routes.py` | 群聊路由 |
| `src/ops_routes.py` | 运维路由 |
| `src/settings_routes.py` | 设置路由 |
| `src/system_routes.py` | 系统触发路由 |
| `src/*_service.py` | 业务逻辑层 |
| `src/*_models.py` | 数据模型层 |
| `src/front_*_routes.py` | Frontend 代理路由模块 |
| `oasis/openclaw_routes.py` | OpenClaw 路由模块 |

---

## 验证清单

部署后逐项确认：

### Agent 服务

- [ ] `uv run scripts/cli.py status` — 3 个服务都 ✅
- [ ] `sessions` — 会话列表正常
- [ ] `sessions-status` — 会话状态正常
- [ ] `settings` — 设置读取正常
- [ ] `personas list` — 人设列表正常
- [ ] `openclaw sessions` — OpenClaw 列表正常

### API 兼容性

- [ ] `/v1/chat/completions` 非流式 — 正常返回
- [ ] `/v1/chat/completions` 流式 — SSE 流正常
- [ ] `/v1/models` — 返回模型列表

### 可观测性

- [ ] 日志中包含 `[req:xxx]` request ID
- [ ] 响应头包含 `X-Request-Id`
- [ ] 传入的 `X-Request-Id` 被正确传播

### 跨服务

- [ ] Frontend 代理到 Agent 的请求正常
- [ ] Frontend 代理到 OASIS 的请求正常
- [ ] 系统触发（scheduler → Agent）正常

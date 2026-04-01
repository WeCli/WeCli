#!/bin/bash
# TeamBot skill 入口脚本（供外部 agent 非交互式调用）
#
# 用法:
#   bash selfskill/scripts/run.sh start                          # 后台启动服务（会自动拉起已安装的 OpenClaw gateway）
#   bash selfskill/scripts/run.sh start-foreground               # 前台启动服务（适合受管终端 / CI / agent runner；同样会自动拉起 OpenClaw）
#   bash selfskill/scripts/run.sh stop                           # 停止服务
#   bash selfskill/scripts/run.sh status                         # 检查服务状态
#   bash selfskill/scripts/run.sh start-tunnel                   # 启动公网隧道（自动下载+暴露前端）
#   bash selfskill/scripts/run.sh stop-tunnel                    # 停止公网隧道
#   bash selfskill/scripts/run.sh tunnel-status                  # 查看隧道状态和公网地址
#   bash selfskill/scripts/run.sh setup                          # 首次：安装环境依赖
#   bash selfskill/scripts/run.sh add-user <name> <password>     # 创建/更新用户
#   bash selfskill/scripts/run.sh configure <KEY> <VALUE>        # 设置 .env 配置项
#   bash selfskill/scripts/run.sh configure --batch K1=V1 K2=V2  # 批量设置配置
#   bash selfskill/scripts/run.sh configure --show               # 查看当前配置
#   bash selfskill/scripts/run.sh configure --init               # 从模板初始化 .env
#   bash selfskill/scripts/run.sh sync-openclaw-llm              # 将 TeamClaw 当前 LLM 配置回写到 OpenClaw
#   bash selfskill/scripts/run.sh check-openclaw                 # 检测/安装 OpenClaw
#   bash selfskill/scripts/run.sh cli chat "你好"                # CLI: 发送消息
#   bash selfskill/scripts/run.sh cli sessions                   # CLI: 查看会话
#   bash selfskill/scripts/run.sh cli settings                   # CLI: 查看设置
#   bash selfskill/scripts/run.sh cli status                     # CLI: 服务状态
#
# 所有命令均为非交互式，适合自动化调用。

set -e

# 定位项目根目录（skill/scripts/run.sh → 上两级）
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
export PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# ---- uv 环境自检 & 自动配置 ----
# 确保 uv 可用
if ! command -v uv &>/dev/null; then
    if [ -x "$HOME/.local/bin/uv" ]; then
        export PATH="$HOME/.local/bin:$PATH"
    elif [ -x "$HOME/.cargo/bin/uv" ]; then
        export PATH="$HOME/.cargo/bin:$PATH"
    else
        echo "📦 未检测到 uv，正在自动安装..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
        if ! command -v uv &>/dev/null; then
            echo "❌ uv 安装失败，请手动安装: https://docs.astral.sh/uv/" >&2
            exit 1
        fi
        echo "✅ uv 安装成功: $(uv --version)"
    fi
fi

# 确保虚拟环境存在
if [ ! -d ".venv" ]; then
    echo "🔧 创建虚拟环境 (.venv, Python 3.11+)..."
    uv venv .venv --python 3.11
    echo "✅ 虚拟环境创建完成"
fi

# 激活虚拟环境
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
else
    echo "❌ 虚拟环境 .venv 不存在，请先运行: bash selfskill/scripts/run.sh setup" >&2
    exit 1
fi

# 验证 Python 版本（防止 venv 损坏或系统 python 泄漏）
_PY_VER=$(python -c "import sys; print('{}.{}'.format(*sys.version_info[:2]))" 2>/dev/null || echo "0.0")
_PY_MAJOR=$(echo "$_PY_VER" | cut -d. -f1)
if [ "$_PY_MAJOR" -lt 3 ]; then
    echo "❌ 虚拟环境中的 python 版本异常: Python $_PY_VER ($(which python))" >&2
    echo "   本项目需要 Python 3.11+。请删除 .venv 并重新创建:" >&2
    echo "   rm -rf .venv && bash selfskill/scripts/run.sh setup" >&2
    exit 1
fi

# 确保依赖已安装（通过检查关键包是否可导入来决定是否需要安装）
if ! python -c "import fastapi" &>/dev/null; then
    echo "📦 安装依赖 (config/requirements.txt)..."
    uv pip install -r config/requirements.txt
    echo "✅ 依赖安装完成"
fi

PIDFILE="$PROJECT_ROOT/.teamclaw.pid"
TEAMCLAW_SERVICE_PATTERNS=(
    "scripts/launcher.py"
    "src/time.py"
    "oasis/server.py"
    "src/mainagent.py"
    "src/front.py"
)

is_wsl() {
    [ -n "${WSL_DISTRO_NAME:-}" ] || grep -qi microsoft /proc/version 2>/dev/null
}

print_wsl_access_hint() {
    if ! is_wsl; then
        return
    fi

    local wsl_ip
    wsl_ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    if [ -z "$wsl_ip" ]; then
        return
    fi

    local frontend_port="${PORT_FRONTEND:-51209}"
    local agent_port="${PORT_AGENT:-51200}"
    echo "   WSL host frontend: http://$wsl_ip:$frontend_port"
    echo "   WSL host agent API: http://$wsl_ip:$agent_port"
    echo "   If Windows localhost forwarding does not work, open these WSL IP URLs from Windows."
}

print_magic_link() {
    # 生成 default 用户的 magic link (使用 CLI 生成正确的 HMAC 签名 token)
    local cli_output
    cli_output=$(cd "$PROJECT_ROOT" && uv run scripts/cli.py token generate -u default --valid-hours 24 2>/dev/null)
    local token=$(echo "$cli_output" | grep "Token:" | awk '{print $2}')

    if [ -n "$token" ] && [ -n "$PUBLIC_DOMAIN" ]; then
        echo "🔗 远程访问链接: ${PUBLIC_DOMAIN}/login-link/${token}?user=default"
    fi
}

print_teamclaw_docs_hint() {
    echo "📖 创建/管理 Team 前请先阅读以下文档:"
    echo "   docs/build_team.md       - 创建/配置 Team (成员、人设、JSON 文件)"
    echo "   docs/create_workflow.md  - 创建 OASIS 工作流 YAML (图格式、人设类型、示例)"
    echo "   docs/cli.md              - 完整 CLI 命令参考和示例"
    echo "   docs/example_team.md     - 示例 Team 文件结构和内容"
    echo "   docs/openclaw-commands.md - OpenClaw agent 集成命令"
    echo ""
    echo "💡 提示: 使用 'uv run scripts/cli.py <command> --help' 查看详细用法"
}

get_listening_pid_for_port() {
    local port="$1"
    local line=""

    if command -v lsof >/dev/null 2>&1; then
        lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null | head -n 1
        return 0
    fi

    if command -v ss >/dev/null 2>&1; then
        line=$(ss -tlnp 2>/dev/null | awk -v p=":$port" '$4 ~ p {print; exit}')
        if [ -n "$line" ]; then
            printf '%s\n' "$line" | sed -n 's/.*pid=\([0-9][0-9]*\).*/\1/p' | head -n 1
        fi
    fi
}

port_is_listening() {
    local port="$1"

    if command -v lsof >/dev/null 2>&1; then
        lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
        return $?
    fi

    if command -v ss >/dev/null 2>&1; then
        ss -tln 2>/dev/null | awk -v p=":$port" '$4 ~ p {found=1; exit} END {exit !found}'
        return $?
    fi

    if command -v netstat >/dev/null 2>&1; then
        netstat -an 2>/dev/null | awk -v port="$port" '$0 ~ /LISTEN/ && $0 ~ ("[.:]" port "[[:space:]]") {found=1; exit} END {exit !found}'
        return $?
    fi

    return 1
}

get_teamclaw_service_pids() {
    {
        if [ -f "$PIDFILE" ]; then
            local tracked_pid=""
            tracked_pid=$(cat "$PIDFILE" 2>/dev/null || true)
            if [ -n "$tracked_pid" ] && kill -0 "$tracked_pid" 2>/dev/null; then
                printf '%s\n' "$tracked_pid"
            fi
        fi
        for pattern in "${TEAMCLAW_SERVICE_PATTERNS[@]}"; do
            pgrep -f "$pattern" 2>/dev/null || true
        done
    } | awk '$1 ~ /^[0-9]+$/ {print $1}' | sort -u
}

stop_teamclaw_service_processes() {
    mapfile -t TEAMCLAW_PIDS < <(get_teamclaw_service_pids)
    if [ "${#TEAMCLAW_PIDS[@]}" -eq 0 ]; then
        return 1
    fi

    echo "🧹 发现已有 TeamClaw 进程，先停止..."
    for pid in "${TEAMCLAW_PIDS[@]}"; do
        local cmd=""
        cmd=$(ps -p "$pid" -o command= 2>/dev/null | sed 's/^[[:space:]]*//')
        if [ -n "$cmd" ]; then
            echo "  PID $pid: $cmd"
        else
            echo "  PID $pid"
        fi
        kill "$pid" 2>/dev/null || true
    done

    for i in $(seq 1 30); do
        local still_running=0
        for pid in "${TEAMCLAW_PIDS[@]}"; do
            if kill -0 "$pid" 2>/dev/null; then
                still_running=1
                break
            fi
        done
        if [ "$still_running" -eq 0 ]; then
            break
        fi
        sleep 0.5
    done

    for pid in "${TEAMCLAW_PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "⚠️  进程 $pid 未响应，强制终止..."
            kill -9 "$pid" 2>/dev/null || true
        fi
    done

    sleep 1
    echo "✅ 旧进程已停止"
    return 0
}

resolve_openclaw_cli() {
    if command -v openclaw.cmd >/dev/null 2>&1; then
        command -v openclaw.cmd
        return 0
    fi
    if command -v openclaw >/dev/null 2>&1; then
        command -v openclaw
        return 0
    fi
    return 1
}

list_openclaw_weixin_bind_keys() {
    local openclaw_cli="$1"
    "$openclaw_cli" channels list --json 2>/dev/null | python -c '
import json
import sys

text = sys.stdin.read().strip()
if not text:
    raise SystemExit(0)
start = text.find("{")
if start < 0:
    raise SystemExit(0)
data = json.loads(text[start:])
for account in data.get("chat", {}).get("openclaw-weixin", []):
    if account == "default":
        print("openclaw-weixin")
    else:
        print(f"openclaw-weixin:{account}")
'
}

list_openclaw_agent_bindings() {
    local openclaw_cli="$1"
    local agent_name="$2"
    "$openclaw_cli" agents list --bindings --json 2>/dev/null | python -c '
import json
import sys

agent_name = sys.argv[1]
text = sys.stdin.read().strip()
if not text:
    raise SystemExit(0)
start = text.find("[")
if start < 0:
    start = text.find("{")
if start < 0:
    raise SystemExit(0)
data = json.loads(text[start:])
agents = data if isinstance(data, list) else [data]
for agent in agents:
    if agent.get("id") == agent_name or agent.get("name") == agent_name:
        for binding in agent.get("bindingDetails", []):
            print(binding)
        break
' "$agent_name"
}

case "${1:-help}" in

    start)
        # Auto-create .env if missing
        if [ ! -f config/.env ]; then
            echo "📋 config/.env 不存在，自动从模板初始化..."
            python selfskill/scripts/configure.py --init
        fi

        # NOTE: 启动时会自动预热已安装的 OpenClaw gateway，并刷新 OPENCLAW_*
        # runtime 配置，但不会静默改写 TeamClaw 的 LLM 配置。导入 OpenClaw /
        # 切换 Antigravity 仍然由首次登录向导和设置页按钮负责。

        stop_teamclaw_service_processes || true
        rm -f "$PIDFILE"

        echo "🚀 启动 TeamBot (headless)..."
        export TEAMBOT_HEADLESS=1
        mkdir -p "$PROJECT_ROOT/logs"
        nohup python scripts/launcher.py > "$PROJECT_ROOT/logs/launcher.log" 2>&1 &
        LAUNCHER_PID=$!
        echo "$LAUNCHER_PID" > "$PIDFILE"
        echo "✅ TeamBot 已在后台启动 (PID: $LAUNCHER_PID)"
        echo "   日志: $PROJECT_ROOT/logs/launcher.log"
        echo "   如果当前终端 / CI / agent runner 会在命令返回后清理子进程，请改用: bash selfskill/scripts/run.sh start-foreground"

        # 等待服务就绪
        source config/.env 2>/dev/null || true
        AGENT_PORT=${PORT_AGENT:-51200}
        FRONTEND_PORT=${PORT_FRONTEND:-51209}
        echo -n "   等待服务就绪"
        SERVICE_READY=false
        for i in $(seq 1 30); do
            if curl -sf "http://127.0.0.1:$AGENT_PORT/v1/models" > /dev/null 2>&1; then
                echo " ✅"
                SERVICE_READY=true
                break
            fi
            echo -n "."
            sleep 2
        done
        if [ "$SERVICE_READY" = false ]; then
            echo ""
            echo "⚠️  服务可能仍在启动中，请查看日志确认"
        fi

        print_wsl_access_hint
        print_magic_link
        echo ""
        echo "═══════════════════════════════════════════════════"
        python scripts/cli.py status
        echo ""

        # 自动启动公网隧道（方便手机远程访问）
        TUNNEL_PIDFILE="$PROJECT_ROOT/.tunnel.pid"
        if [ -f "$TUNNEL_PIDFILE" ] && kill -0 "$(cat "$TUNNEL_PIDFILE")" 2>/dev/null; then
            source config/.env 2>/dev/null || true
            echo "🌐 Tunnel 已在运行"
            if [ -n "$PUBLIC_DOMAIN" ] && [ "$PUBLIC_DOMAIN" != "wait to set" ]; then
                echo "📱 手机访问地址: ${PUBLIC_DOMAIN}/mobile_group_chat"
            fi
        else
            echo "🌐 正在启动 Cloudflare Tunnel（手机远程访问）..."
            mkdir -p "$PROJECT_ROOT/logs"
            nohup python scripts/tunnel.py > "$PROJECT_ROOT/logs/tunnel.log" 2>&1 &
            TUNNEL_PID=$!
            echo "$TUNNEL_PID" > "$TUNNEL_PIDFILE"
            echo -n "   等待公网地址"
            for i in $(seq 1 20); do
                source config/.env 2>/dev/null || true
                if [ -n "$PUBLIC_DOMAIN" ] && [ "$PUBLIC_DOMAIN" != "wait to set" ] && echo "$PUBLIC_DOMAIN" | grep -q "trycloudflare.com"; then
                    echo " ✅"
                    echo "📱 手机访问地址: ${PUBLIC_DOMAIN}/mobile_group_chat"
                    break
                fi
                echo -n "."
                sleep 2
            done
            # If tunnel didn't become ready in time, still continue
            source config/.env 2>/dev/null || true
            if [ -z "$PUBLIC_DOMAIN" ] || [ "$PUBLIC_DOMAIN" = "wait to set" ]; then
                echo ""
                echo "⏳ Tunnel 仍在启动中，稍后可执行: bash selfskill/scripts/run.sh tunnel-status"
            fi
        fi

        echo ""
        print_teamclaw_docs_hint
        exit 0
        ;;

    start-foreground|start-fg)
        # Auto-create .env if missing
        if [ ! -f config/.env ]; then
            echo "📋 config/.env 不存在，自动从模板初始化..."
            python selfskill/scripts/configure.py --init
        fi

        stop_teamclaw_service_processes || true
        rm -f "$PIDFILE"

        echo "🚀 前台启动 TeamBot (headless)..."
        echo "   当前终端会持续占用；按 Ctrl+C 可停止所有服务"
        export TEAMBOT_HEADLESS=1
        exec python scripts/launcher.py
        ;;
    stop)
        if stop_teamclaw_service_processes; then
            rm -f "$PIDFILE"
            echo "✅ TeamBot 已停止"
        else
            rm -f "$PIDFILE" 2>/dev/null || true
            echo "未找到 TeamClaw 进程，服务可能未运行"
        fi
        exit 0
        ;;

    status)
        source config/.env 2>/dev/null || true

        TRACKED_PID=""
        if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
            TRACKED_PID=$(cat "$PIDFILE")
        fi

        mapfile -t SERVICE_PIDS < <(get_teamclaw_service_pids)
        if [ -n "$TRACKED_PID" ]; then
            echo "✅ TeamBot 正在运行 (launcher PID: $TRACKED_PID)"
        elif [ "${#SERVICE_PIDS[@]}" -gt 0 ]; then
            rm -f "$PIDFILE" 2>/dev/null || true
            echo "⚠️  检测到 TeamClaw 服务仍在运行，但 launcher PID 文件已失效"
            echo "   活跃进程: ${SERVICE_PIDS[*]}"
            echo "   这通常发生在前台启动，或由外部进程管理器接管 launcher 的场景"
        else
            echo "❌ TeamBot 未运行"
            exit 1
        fi

        for port in ${PORT_AGENT:-51200} ${PORT_SCHEDULER:-51201} ${PORT_OASIS:-51202} ${PORT_FRONTEND:-51209}; do
            LISTEN_PID=$(get_listening_pid_for_port "$port")
            if [ -n "$LISTEN_PID" ]; then
                echo "  ✅ 端口 $port 已监听 (PID: $LISTEN_PID)"
            elif port_is_listening "$port"; then
                echo "  ✅ 端口 $port 已监听"
            else
                echo "  ⚠️  端口 $port 未监听"
            fi
        done
        OPENCLAW_CLI=$(resolve_openclaw_cli || true)
        if [ -n "$OPENCLAW_CLI" ]; then
            OPENCLAW_RUNTIME=$("$OPENCLAW_CLI" gateway status 2>&1 | sed -n 's/^Runtime: //p' | head -n 1)
            if [ -n "$OPENCLAW_RUNTIME" ]; then
                echo "  🦞 OpenClaw Runtime: $OPENCLAW_RUNTIME"
            else
                echo "  🦞 OpenClaw 已安装（运行状态未探测到）"
            fi
        else
            echo "  🦞 OpenClaw 未安装"
        fi
        print_wsl_access_hint
        print_magic_link
        echo ""
        print_teamclaw_docs_hint
        exit 0
        ;;

    setup)
        echo "=== 环境配置 ==="
        bash scripts/setup_env.sh

        # acpx 自检（setup_env.sh 已处理安装，这里做最终确认）
        if command -v acpx &>/dev/null; then
            echo "✅ acpx 已就绪: $(acpx --version 2>/dev/null || echo 'available')"
        else
            echo "⚠️  acpx 未安装（ACP 外部 Agent 通信功能不可用）"
            echo "   手动安装: npm install -g acpx@latest"
        fi

        echo "=== 环境配置完成 ==="
        ;;

    add-user)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "用法: $0 add-user <username> <password>" >&2
            exit 1
        fi
        python selfskill/scripts/adduser.py "$2" "$3"
        exit 0
        ;;

    configure)
        shift
        python selfskill/scripts/configure.py "$@"
        CONFIG_EXIT_CODE=$?
        if [ $CONFIG_EXIT_CODE -ne 0 ]; then
            exit $CONFIG_EXIT_CODE
        fi
        if [ "${1:-}" = "--init" ]; then
            echo ""
            echo "=== init 完成，自动触发 OpenClaw 检测 ==="
            bash "$0" check-openclaw
        fi
        exit 0
        ;;

    auto-model)
        # 查询 API 可用模型列表（打印供 agent 选择，不自动写入）
        python selfskill/scripts/configure.py --auto-model
        exit 0
        ;;

    sync-openclaw-llm)
        python selfskill/scripts/configure_openclaw.py --sync-teamclaw-llm
        exit $?
        ;;

    cli)
        # CLI 控制工具：像操作前端一样控制 Agent
        shift
        python scripts/cli.py "$@"
        exit $?
        ;;

    check-openclaw)
        echo "=== OpenClaw 检测 ==="

        # 1. 检测 openclaw 是否已安装
        if command -v openclaw &>/dev/null; then
            OC_VERSION=$(openclaw --version 2>/dev/null | head -1 || echo "unknown")
            echo "✅ OpenClaw 已安装: $OC_VERSION"
            OC_BIN=$(which openclaw)
            echo "   路径: $OC_BIN"

            # 自动探测并配置 + 初始化 workspace 模板
            echo ""
            echo "🔍 自动探测 OpenClaw 配置..."
            python selfskill/scripts/configure_openclaw.py --auto-detect
            if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
                echo ""
                echo "💡 如果 TeamClaw 在安装或重配 OpenClaw 之前已启动，请执行一次 stop -> start，"
                echo "   让 OASIS 重新加载 openclaw CLI 和 gateway 设置："
                echo "   bash selfskill/scripts/run.sh stop"
                echo "   bash selfskill/scripts/run.sh start"
            fi
            echo ""
            echo "=== OpenClaw 检测完成 ==="
            exit 0
        fi

        # 2. OpenClaw 未安装
        echo "⚠️  OpenClaw 未安装"
        echo ""
        echo "OpenClaw 是一个本地 AI 助手，TeamClaw 可以通过它进行可视化工作流编排。"
        python selfskill/scripts/configure_openclaw.py --install-guide
        echo ""

        # 3. 检测 Node.js
        if command -v node &>/dev/null; then
            NODE_VER=$(node --version 2>/dev/null)
            NODE_MAJOR=$(echo "$NODE_VER" | sed 's/^v//' | cut -d. -f1)
            echo "📦 Node.js 版本: $NODE_VER"
            if [ "$NODE_MAJOR" -lt 22 ] 2>/dev/null; then
                echo "❌ Node.js 版本过低（需要 ≥ 22），请先升级 Node.js"
                echo "   推荐: nvm install 22 && nvm use 22"
                echo ""
                echo "=== OpenClaw 检测完成（需先升级 Node.js）==="
                exit 1
            fi
            echo "✅ Node.js 版本满足要求"
        else
            echo "❌ Node.js 未安装（OpenClaw 需要 Node.js ≥ 22）"
            echo "   推荐安装方式："
            echo "   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash"
            echo "   nvm install 22 && nvm use 22"
            echo ""
            echo "=== OpenClaw 检测完成（需先安装 Node.js）==="
            exit 1
        fi

        echo ""
        echo "🔧 准备安装 OpenClaw..."
        echo "   将执行: npm install -g openclaw@latest --ignore-scripts"
        echo "   （--ignore-scripts 避免 node-llama-cpp 因缺少 cmake 编译失败）"
        echo ""

        # 4. 询问用户确认（非交互模式跳过）
        if [ "${OPENCLAW_AUTO_INSTALL:-}" = "1" ]; then
            echo "📌 自动安装模式（OPENCLAW_AUTO_INSTALL=1）"
            REPLY="y"
        else
            read -r -p "是否现在安装 OpenClaw？[y/N] " REPLY
        fi

        case "$REPLY" in
            [yY]|[yY][eE][sS])
                echo ""
                echo "📥 正在安装 OpenClaw..."
                if npm install -g openclaw@latest --ignore-scripts; then
                    echo "✅ OpenClaw 安装成功"

                    # 确保 npm 全局 bin 在 PATH 中
                    NPM_BIN=$(npm bin -g 2>/dev/null || echo "")
                    if [ -z "$NPM_BIN" ]; then
                        NPM_BIN="$(npm prefix -g 2>/dev/null)/bin"
                    fi
                    if [ -n "$NPM_BIN" ] && [ -d "$NPM_BIN" ]; then
                        case ":$PATH:" in
                            *":$NPM_BIN:"*) ;;
                            *)
                                export PATH="$NPM_BIN:$PATH"
                                echo "📌 已将 npm 全局 bin 路径添加到 PATH: $NPM_BIN"
                                ;;
                        esac
                    fi

                    OC_VERSION=$(openclaw --version 2>/dev/null | head -1 || echo "unknown")
                    if [ "$OC_VERSION" = "unknown" ] && [ -n "$NPM_BIN" ]; then
                        OC_VERSION=$("$NPM_BIN/openclaw" --version 2>/dev/null | head -1 || echo "unknown")
                    fi
                    echo "   版本: $OC_VERSION"

                    # 初始化 workspace 默认模板
                    echo ""
                    echo "🏠 初始化 OpenClaw workspace 默认模板..."
                    python selfskill/scripts/configure_openclaw.py --init-workspace

                    echo ""
                    echo "📋 下一步：完成 OpenClaw onboarding"
                    echo "   本地交互模式: openclaw onboard --install-daemon"
                    echo "   自动化 / 无交互模式: openclaw onboard --non-interactive --accept-risk --install-daemon"
                    echo "   如需复用现有 OpenAI key，可追加: --openai-api-key <LLM_API_KEY>"
                    echo ""
                    echo "   之后启用 TeamClaw 所需的 HTTP 兼容端点："
                    echo "   openclaw config set gateway.http.endpoints.chatCompletions.enabled true"
                    echo "   openclaw gateway restart"
                    echo ""
                    echo "   向导完成后，再次运行此命令以自动配置 TeamClaw 集成："
                    echo "   bash selfskill/scripts/run.sh check-openclaw"
                else
                    echo "❌ OpenClaw 安装失败，请检查 npm 和网络状态"
                    exit 1
                fi
                ;;
            *)
                echo "⏭️  跳过 OpenClaw 安装"
                echo "   TeamClaw 仍可正常使用（无法使用 OpenClaw 可视化编排功能）"
                echo "   稍后可随时运行: bash selfskill/scripts/run.sh check-openclaw"
                ;;
        esac

        echo ""
        echo "=== OpenClaw 检测完成 ==="
        exit 0
        ;;

    check-openclaw-weixin)
        echo "=== OpenClaw Weixin 插件检测 ==="
        if ! OPENCLAW_CLI=$(resolve_openclaw_cli); then
            echo "❌ 未找到 OpenClaw CLI，请先执行: bash selfskill/scripts/run.sh check-openclaw"
            exit 1
        fi

        echo "使用 OpenClaw CLI: $OPENCLAW_CLI"
        if [[ "$OPENCLAW_CLI" == *.cmd ]]; then
            echo "ℹ️  当前使用 openclaw.cmd，可避开 PowerShell execution policy 对 openclaw.ps1 的限制"
        fi
        echo "ℹ️  如果官方 npx 安装器在 Windows 上提示找不到 openclaw，这里会使用手动插件流程"

        if [ ! -f "$HOME/.openclaw/extensions/openclaw-weixin/index.ts" ]; then
            echo ""
            echo "📥 安装微信插件..."
            "$OPENCLAW_CLI" plugins install "@tencent-weixin/openclaw-weixin"
        else
            echo ""
            echo "✅ 微信插件已安装"
        fi

        "$OPENCLAW_CLI" config set plugins.entries.openclaw-weixin.enabled true
        "$OPENCLAW_CLI" gateway restart || true

        mapfile -t WEIXIN_KEYS < <(list_openclaw_weixin_bind_keys "$OPENCLAW_CLI")
        echo ""
        if [ "${#WEIXIN_KEYS[@]}" -eq 0 ]; then
            echo "⚠️  还没有登录任何微信账号"
            echo "下一步请执行："
            echo "  $OPENCLAW_CLI channels login --channel openclaw-weixin"
            echo ""
            echo "扫码后验证："
            echo "  $OPENCLAW_CLI channels list --json"
            echo "然后绑定到 OpenClaw agent："
            echo "  bash selfskill/scripts/run.sh bind-openclaw-channel main openclaw-weixin:<account_id>"
            exit 0
        fi

        echo "✅ 已检测到微信账号："
        for key in "${WEIXIN_KEYS[@]}"; do
            echo "  $key"
        done
        echo ""
        echo "绑定示例："
        for key in "${WEIXIN_KEYS[@]}"; do
            echo "  bash selfskill/scripts/run.sh bind-openclaw-channel main $key"
        done
        exit 0
        ;;

    bind-openclaw-channel)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "用法: $0 bind-openclaw-channel <agent> <bind_key>" >&2
            echo "示例: $0 bind-openclaw-channel main openclaw-weixin:account-id" >&2
            exit 1
        fi
        if ! OPENCLAW_CLI=$(resolve_openclaw_cli); then
            echo "❌ 未找到 OpenClaw CLI，请先执行: bash selfskill/scripts/run.sh check-openclaw" >&2
            exit 1
        fi

        "$OPENCLAW_CLI" agents bind --agent "$2" --bind "$3"
        echo ""
        echo "当前 '$2' 的 channel 绑定："
        mapfile -t CURRENT_BINDINGS < <(list_openclaw_agent_bindings "$OPENCLAW_CLI" "$2")
        if [ "${#CURRENT_BINDINGS[@]}" -eq 0 ]; then
            echo "  (暂未读到绑定结果，请刷新 OpenClaw / TeamClaw 后重试)"
        else
            for binding in "${CURRENT_BINDINGS[@]}"; do
                echo "  $binding"
            done
        fi
        echo ""
        echo "可在 TeamClaw 中刷新 OpenClaw Channels 标签，或执行："
        echo "  uv run scripts/cli.py openclaw bindings --agent $2"
        exit 0
        ;;

    start-tunnel)
        # 启动 Cloudflare Tunnel（自动下载 cloudflared + 暴露前端到公网）
        TUNNEL_PIDFILE="$PROJECT_ROOT/.tunnel.pid"
        if [ -f "$TUNNEL_PIDFILE" ] && kill -0 "$(cat "$TUNNEL_PIDFILE")" 2>/dev/null; then
            echo "⚠️  Tunnel 已在运行 (PID: $(cat "$TUNNEL_PIDFILE"))"
            # 读取当前 PUBLIC_DOMAIN
            source config/.env 2>/dev/null || true
            if [ -n "$PUBLIC_DOMAIN" ] && [ "$PUBLIC_DOMAIN" != "wait to set" ]; then
                echo "🌍 公网地址: $PUBLIC_DOMAIN"
                print_magic_link
            fi
            exit 0
        fi

        echo "🌐 正在启动 Cloudflare Tunnel..."
        mkdir -p "$PROJECT_ROOT/logs"
        nohup python scripts/tunnel.py > "$PROJECT_ROOT/logs/tunnel.log" 2>&1 &
        TUNNEL_PID=$!
        echo "$TUNNEL_PID" > "$TUNNEL_PIDFILE"

        # 等待公网地址就绪（最多 60 秒）
        echo -n "   等待公网地址"
        for i in $(seq 1 30); do
            source config/.env 2>/dev/null || true
            if [ -n "$PUBLIC_DOMAIN" ] && [ "$PUBLIC_DOMAIN" != "wait to set" ] && echo "$PUBLIC_DOMAIN" | grep -q "trycloudflare.com"; then
                echo " ✅"
                echo "🌍 公网地址: $PUBLIC_DOMAIN"
                exit 0
            fi
            echo -n "."
            sleep 2
        done
        echo ""
        echo "⚠️  Tunnel 可能仍在启动中，请查看日志: $PROJECT_ROOT/logs/tunnel.log"
        exit 0
        ;;

    stop-tunnel)
        TUNNEL_PIDFILE="$PROJECT_ROOT/.tunnel.pid"
        if [ -f "$TUNNEL_PIDFILE" ]; then
            PID=$(cat "$TUNNEL_PIDFILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo "正在停止 Tunnel (PID: $PID)..."
                kill "$PID"
                for i in $(seq 1 10); do
                    if ! kill -0 "$PID" 2>/dev/null; then
                        break
                    fi
                    sleep 0.5
                done
                if kill -0 "$PID" 2>/dev/null; then
                    kill -9 "$PID" 2>/dev/null
                fi
                echo "✅ Tunnel 已停止"
            else
                echo "Tunnel 进程已不存在"
            fi
            rm -f "$TUNNEL_PIDFILE"
        else
            echo "Tunnel 未运行"
        fi
        # Clear PUBLIC_DOMAIN in .env to avoid stale URLs
        if [ -f "config/.env" ]; then
            if grep -q "^PUBLIC_DOMAIN=" config/.env; then
                sed -i 's|^PUBLIC_DOMAIN=.*|PUBLIC_DOMAIN=|' config/.env
                echo "🧹 已清理 PUBLIC_DOMAIN"
            fi
        fi
        exit 0
        ;;

    tunnel-status)
        TUNNEL_PIDFILE="$PROJECT_ROOT/.tunnel.pid"
        if [ -f "$TUNNEL_PIDFILE" ] && kill -0 "$(cat "$TUNNEL_PIDFILE")" 2>/dev/null; then
            echo "✅ Tunnel 正在运行 (PID: $(cat "$TUNNEL_PIDFILE"))"
            source config/.env 2>/dev/null || true
            if [ -n "$PUBLIC_DOMAIN" ] && [ "$PUBLIC_DOMAIN" != "wait to set" ]; then
                echo "🌍 公网地址: $PUBLIC_DOMAIN"
                print_magic_link
            else
                echo "⏳ 公网地址尚未就绪"
            fi
        else
            echo "❌ Tunnel 未运行"
            rm -f "$TUNNEL_PIDFILE" 2>/dev/null
        fi
        exit 0
        ;;

    help|--help|-h)
        echo "TeamBot Skill 入口"
        echo ""
        echo "用法: bash selfskill/scripts/run.sh <command> [args]"
        echo ""
        echo "命令:"
        echo "  start                          后台启动服务（自动预热已安装的 OpenClaw gateway）"
        echo "  start-foreground               前台启动服务（适合受管终端 / CI / agent runner；同样自动预热 OpenClaw）"
        echo "  stop                           停止服务"
        echo "  status                         检查服务状态"
        echo "  start-tunnel                   启动公网隧道（自动下载 cloudflared）"
        echo "  stop-tunnel                    停止公网隧道"
        echo "  tunnel-status                  查看隧道状态和公网地址"
        echo "  setup                          安装环境依赖（首次）"
        echo "  add-user <name> <password>     创建/更新用户"
        echo "  configure <KEY> <VALUE>        设置 .env 配置项"
        echo "  configure --batch K1=V1 K2=V2  批量设置配置"
        echo "  configure --show               查看当前配置"
        echo "  configure --init               从模板初始化 .env"
        echo "  auto-model                     查询 API 可用模型列表（供 agent 选择）"
        echo "  sync-openclaw-llm              将 TeamClaw 当前 LLM 配置回写到 OpenClaw"
        echo "  check-openclaw                 检测/安装 OpenClaw 并自动配置集成"
        echo "  check-openclaw-weixin          检测/安装 OpenClaw 微信插件并提示扫码/绑定"
        echo "  bind-openclaw-channel <agent> <bind_key>  绑定 OpenClaw channel 到指定 agent"
        echo "  cli <command> [args]           命令行控制工具（chat/sessions/settings 等）"
        echo "  help                           显示此帮助"
        echo ""
        print_teamclaw_docs_hint
        exit 0
        ;;

    *)
        echo "未知命令: $1" >&2
        echo "运行 '$0 help' 查看可用命令" >&2
        exit 1
        ;;
esac

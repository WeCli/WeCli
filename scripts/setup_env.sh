#!/bin/bash
# TeamBot 自动环境配置脚本 (Linux / macOS)

set -e
cd "$(dirname "$0")/.."

echo "=========================================="
echo "  TeamBot 环境自动配置"
echo "=========================================="
echo ""

# --- 1. 检查并安装 uv ---
if command -v uv &>/dev/null; then
    echo "✅ uv 已安装: $(uv --version)"
else
    echo "📦 未检测到 uv，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # 加载 uv 到当前 shell
    export PATH="$HOME/.local/bin:$PATH"
    if command -v uv &>/dev/null; then
        echo "✅ uv 安装成功: $(uv --version)"
    else
        echo "❌ uv 安装失败，请手动安装: https://docs.astral.sh/uv/"
        exit 1
    fi
fi

# --- 2. 检查并创建虚拟环境 ---
if [ -d ".venv" ]; then
    echo "✅ 虚拟环境已存在: .venv/"
else
    echo "🔧 创建虚拟环境 (.venv, Python 3.11+)..."
    uv venv .venv --python 3.11
    echo "✅ 虚拟环境创建完成"
fi

# --- 3. 激活虚拟环境 ---
source .venv/bin/activate
echo "✅ 虚拟环境已激活: $(python --version)"

# --- 4. 安装/更新依赖 ---
echo "📦 安装依赖 (config/requirements.txt)..."
uv pip install -r config/requirements.txt
echo "✅ 依赖安装完成"

# --- 4.5. 检查并安装 acpx (ACP 通信插件) ---
if command -v acpx &>/dev/null; then
    echo "✅ acpx 已安装: $(acpx --version 2>/dev/null || echo 'unknown')"
else
    echo "📦 未检测到 acpx，正在安装..."
    if command -v npm &>/dev/null; then
        npm install -g acpx@latest 2>/dev/null || true
        # npm 全局安装后可能需要手动链接
        if ! command -v acpx &>/dev/null; then
            ACPX_BIN=$(find "$(npm prefix -g 2>/dev/null)/lib/node_modules/acpx" -name "cli.js" 2>/dev/null | head -1)
            if [ -n "$ACPX_BIN" ] && [ -f "$ACPX_BIN" ]; then
                ln -sf "$ACPX_BIN" /usr/local/bin/acpx 2>/dev/null || true
                chmod +x "$ACPX_BIN" 2>/dev/null || true
            fi
        fi
        if command -v acpx &>/dev/null; then
            echo "✅ acpx 安装成功: $(acpx --version 2>/dev/null || echo 'unknown')"
        else
            echo "⚠️  acpx 安装后未在 PATH 中找到，群聊 ACP 广播功能可能不可用"
            echo "   手动安装: npm install -g acpx@latest"
        fi
    else
        echo "⚠️  npm 未安装，跳过 acpx 安装（群聊 ACP 广播功能不可用）"
        echo "   安装 Node.js 后执行: npm install -g acpx@latest"
    fi
fi

# --- 5. 检查配置文件 ---
echo ""
echo "--- 配置检查 ---"

if [ -f "config/.env" ]; then
    echo "✅ config/.env 已存在"
else
    echo "⚠️  config/.env 不存在，请创建并填入: LLM_API_KEY=your_key"
fi

if [ -f "config/users.json" ]; then
    echo "✅ config/users.json 已存在"
else
    echo "⚠️  config/users.json 不存在，请运行 scripts/adduser.sh 创建用户"
fi

echo ""
echo "=========================================="
echo "  ✅ 环境配置完成！"
echo "  启动服务: scripts/start.sh"
echo "=========================================="

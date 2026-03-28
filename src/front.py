from flask import Flask, render_template, request, jsonify, session, Response, redirect
from werkzeug.middleware.proxy_fix import ProxyFix
import hashlib
import requests
import os
import json
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from cron_utils import get_agent_cron_jobs, restore_cron_jobs
from front_group_routes import register_group_routes
from front_oasis_routes import register_oasis_routes
from front_session_routes import register_session_routes

# 加载 .env 配置
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
load_dotenv(dotenv_path=os.path.join(root_dir, "config", ".env"))

app = Flask(__name__,
            template_folder=os.path.join(current_dir, 'templates'),
            static_folder=os.path.join(current_dir, 'static'))

# 信任反向代理的 X-Forwarded-Proto / X-Forwarded-For 等头
# 这样 Cloudflare Tunnel 转发的 HTTPS 请求会被正确识别为 HTTPS，
# Flask 才会在 HTTP 内部连接上正确读取 Secure cookie
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# 基于 INTERNAL_TOKEN 生成稳定的 secret_key，避免每次重启时所有 session 失效
_token = os.getenv("INTERNAL_TOKEN", "")
app.secret_key = hashlib.sha256(f"teamclaw-session-{_token}".encode()).digest() if _token else os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB for image uploads

# --- 配置区 ---
from datetime import timedelta
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
app.config['SESSION_COOKIE_HTTPONLY'] = True      # 防止 XSS 读取 Session Cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'     # 防止 CSRF 跨站请求携带 Cookie
# 不硬编码 SESSION_COOKIE_SECURE：因为用户可能同时通过 HTTPS tunnel 和 HTTP localhost 访问。
# ProxyFix 已让 request.is_secure 能正确识别反向代理转发的 HTTPS。
# SameSite=Lax 对两种场景都已足够安全。

PORT_AGENT = int(os.getenv("PORT_AGENT", "51200"))
# [已弃用] 旧端点 URL，已被 /v1/chat/completions 替代
# LOCAL_AGENT_URL = f"http://127.0.0.1:{PORT_AGENT}/ask"
# LOCAL_AGENT_STREAM_URL = f"http://127.0.0.1:{PORT_AGENT}/ask_stream"
LOCAL_AGENT_CANCEL_URL = f"http://127.0.0.1:{PORT_AGENT}/cancel"
LOCAL_LOGIN_URL = f"http://127.0.0.1:{PORT_AGENT}/login"
LOCAL_TOOLS_URL = f"http://127.0.0.1:{PORT_AGENT}/tools"
LOCAL_SESSIONS_URL = f"http://127.0.0.1:{PORT_AGENT}/sessions"
LOCAL_SESSION_HISTORY_URL = f"http://127.0.0.1:{PORT_AGENT}/session_history"
LOCAL_DELETE_SESSION_URL = f"http://127.0.0.1:{PORT_AGENT}/delete_session"
LOCAL_TTS_URL = f"http://127.0.0.1:{PORT_AGENT}/tts"
LOCAL_SESSION_STATUS_URL = f"http://127.0.0.1:{PORT_AGENT}/session_status"
# OpenAI 兼容端点
LOCAL_OPENAI_COMPLETIONS_URL = f"http://127.0.0.1:{PORT_AGENT}/v1/chat/completions"
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "")

# OASIS Forum proxy
PORT_OASIS = int(os.getenv("PORT_OASIS", "51202"))
OASIS_BASE_URL = f"http://127.0.0.1:{PORT_OASIS}"


# ============================================================================
# Token Login Support - Magic Link Authentication
# Using INTERNAL_TOKEN + user_id + timestamp with HMAC signature
# ============================================================================
import time
import secrets
import hmac
import hashlib
import base64

def generate_login_token(user_id: str, valid_hours: int = 24) -> str:
    """Generate HMAC-signed login token.
    Token format: base64(user_id:expire_ts:random:signature)
    Signature = HMAC(INTERNAL_TOKEN, user_id:expire_ts:random)
    
    Args:
        user_id: The user ID to generate token for
        valid_hours: Token validity period in hours (default: 24)
    
    Returns:
        URL-safe token string with HMAC signature
    """
    expire_ts = int(time.time()) + valid_hours * 3600
    random_str = secrets.token_urlsafe(8)
    payload = f"{user_id}:{expire_ts}:{random_str}"
    # Generate HMAC signature using INTERNAL_TOKEN as key
    signature = hmac.new(
        INTERNAL_TOKEN.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()[:16]
    token = base64.urlsafe_b64encode(f"{payload}:{signature}".encode()).decode().rstrip('=')
    return token


def verify_login_token(token: str) -> str | None:
    """Verify HMAC-signed login token.
    
    Args:
        token: The signed token to verify
    
    Returns:
        user_id if signature is valid and not expired, None otherwise
    """
    try:
        # Add padding back for base64 decoding
        padded = token + '=' * (-len(token) % 4)
        decoded = base64.urlsafe_b64decode(padded).decode()
        parts = decoded.rsplit(':', 1)  # Split from right to separate signature
        if len(parts) != 2:
            return None
        payload, signature = parts
        user_id, expire_ts, random_str = payload.split(':')
        expire_ts = int(expire_ts)
        
        # Check expiration
        if time.time() > expire_ts:
            return None
        
        # Verify HMAC signature
        expected = hmac.new(
            INTERNAL_TOKEN.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        
        if not hmac.compare_digest(signature, expected):
            return None
        
        return user_id
    except Exception:
        return None


register_group_routes(app, port_agent=PORT_AGENT, internal_token=INTERNAL_TOKEN)
register_oasis_routes(app, oasis_base_url=OASIS_BASE_URL)
register_session_routes(
    app,
    port_agent=PORT_AGENT,
    internal_token=INTERNAL_TOKEN,
    local_sessions_url=LOCAL_SESSIONS_URL,
    local_session_history_url=LOCAL_SESSION_HISTORY_URL,
    local_session_status_url=LOCAL_SESSION_STATUS_URL,
    local_delete_session_url=LOCAL_DELETE_SESSION_URL,
)

# --- users.json 检查（密码登录时验证用户是否存在）---
USERS_PATH = os.path.join(root_dir, "config", "users.json")

def _user_exists_in_users_json(username: str) -> bool:
    """检查用户名是否在 users.json 中（有密码记录）"""
    if not os.path.exists(USERS_PATH):
        return False
    try:
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            users = json.load(f)
        return username in users
    except Exception:
        return False


# --- Unified auth: before_request hook ---
# Routes that do NOT require login
_PUBLIC_ROUTES = frozenset({
    'index', 'manifest', 'service_worker', 'static',
    'proxy_openai_completions', 'proxy_openai_models',
    'proxy_login', 'proxy_logout', 'proxy_check_session',
    'proxy_login_with_token', 'magic_login',
    'group_chat_mobile', 'group_chat_mobile_alias', 'studio',
    'llm_config_status', 'setup_status', 'import_openclaw_config',
})


def _is_direct_local_request():
    """判断是否为本机直连（非经过任何反向代理）。

    只有同时满足两个条件才算本地直连：
    1. remote_addr 是 127.0.0.1 / ::1
    2. 没有任何常见反向代理注入的头（说明不是被代理转发过来的）

    兼容：Cloudflare Tunnel、Nginx、Caddy、Traefik、HAProxy、Apache 等。
    """
    remote = request.remote_addr or ''
    if remote not in ('127.0.0.1', '::1'):
        return False
    # 任何反向代理都会注入至少一个这类头
    _PROXY_HEADERS = (
        'X-Forwarded-For',      # Nginx / Caddy / Traefik / HAProxy / 通用
        'X-Forwarded-Proto',    # Nginx / Caddy / 通用
        'X-Forwarded-Host',     # Nginx / Traefik
        'X-Real-Ip',            # Nginx
        'Cf-Connecting-Ip',     # Cloudflare Tunnel
        'Cf-Ray',               # Cloudflare Tunnel
        'True-Client-Ip',       # Cloudflare / Akamai
        'Forwarded',            # RFC 7239 标准头
        'Via',                  # HTTP 标准代理头
    )
    return not any(request.headers.get(h) for h in _PROXY_HEADERS)


@app.before_request
def _unified_auth_check():
    """鉴权入口，规则极简：

    1. 公开路由 → 放行
    2. 本机直连（127.0.0.1 且无代理头）→ 放行
       - 如果请求携带 X-User-Id header，自动注入 session（CLI 场景）
    3. 其余一律要登录（包括所有反向代理转发的请求）
    """
    if request.endpoint in _PUBLIC_ROUTES:
        return None
    if _is_direct_local_request():
        # CLI / 内部调用：如果带了 X-User-Id，注入到 Flask session
        header_uid = request.headers.get("X-User-Id", "").strip()
        if header_uid and not session.get("user_id"):
            session["user_id"] = header_uid
        return None
    if not session.get('user_id'):
        return jsonify({'error': '未登录'}), 401
    return None


def _internal_auth_headers():
    """Build headers for Flask → backend internal communication.
    Uses INTERNAL_TOKEN instead of forwarding user password.
    """
    return {"X-Internal-Token": INTERNAL_TOKEN}


def _internal_auth_params(extra: dict | None = None):
    """Build common params (user_id) + merge extra params."""
    params = {"user_id": session.get("user_id", "")}
    if extra:
        params.update(extra)
    return params


@app.route("/")
def index():
    """主页 - 默认跳转移动端群聊页面。支持通过 URL 参数携带 Token 自动登录。"""
    token = request.args.get('token', '')
    user_id = request.args.get('user', '')
    
    # 如果 URL 中包含有效的 Token，自动创建 session
    if token and user_id:
        verified_user = verify_login_token(token)
        if verified_user == user_id:
            session['user_id'] = user_id
            session.permanent = True
            # 重定向到移动端群聊页面（去除 URL 中的 token）
            return redirect('/mobile_group_chat')
    
    # 如果带有 redirect=group_chat 参数，转发到 studio 进行登录后再跳回
    redirect_param = request.args.get('redirect', '')
    if redirect_param:
        return redirect(f'/studio?redirect={redirect_param}')
    
    return redirect('/mobile_group_chat')


@app.route("/api/llm_config_status")
def llm_config_status():
    """检查 LLM API 是否已配置，供前端判断是否显示提示横幅。"""
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "").strip()
    model = os.getenv("LLM_MODEL", "").strip()
    configured = bool(api_key) and bool(base_url) and bool(model)
    return jsonify({"configured": configured})


@app.route("/api/setup_status")
def setup_status():
    """首次登录向导状态检测：返回 LLM、OpenClaw、Antigravity、密码等配置状态。"""
    import shutil
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "").strip()
    model = os.getenv("LLM_MODEL", "").strip()
    llm_configured = bool(api_key) and api_key != "your_api_key_here" and bool(base_url) and bool(model)

    # Check OpenClaw
    openclaw_installed = shutil.which("openclaw") is not None

    # Check Antigravity (probe port 8045)
    antigravity_running = False
    try:
        import urllib.request
        req = urllib.request.Request("http://127.0.0.1:8045/v1/models")
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status == 200:
                antigravity_running = True
    except Exception:
        pass

    # Check if any password users exist
    users_json_path = os.path.join(root_dir, "config", "users.json")
    password_set = False
    if os.path.isfile(users_json_path):
        try:
            import json as _json
            with open(users_json_path, "r", encoding="utf-8") as f:
                users_data = _json.load(f)
            if isinstance(users_data, dict) and len(users_data) > 0:
                password_set = True
        except Exception:
            pass

    return jsonify({
        "llm_configured": llm_configured,
        "openclaw_installed": openclaw_installed,
        "antigravity_running": antigravity_running,
        "password_set": password_set,
        "current_provider": os.getenv("LLM_PROVIDER", "").strip(),
        "current_model": model,
        "current_base_url": base_url,
    })


@app.route("/api/import_openclaw_config")
def import_openclaw_config():
    """从本地 OpenClaw 读取 LLM 配置（API Key / Base URL / Model / Provider），
    返回给前端 wizard 用于一键导入。不直接写入 .env。"""
    import subprocess, shutil, sys

    oc_bin = shutil.which("openclaw")
    if not oc_bin:
        return jsonify({"error": "OpenClaw 未安装", "found": False}), 404

    # 复用 configure_openclaw.py 的探测逻辑
    script_dir = os.path.join(root_dir, "selfskill", "scripts")
    sys_path_backup = list(sys.path)
    try:
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        from configure_openclaw import detect_llm_config_from_openclaw
        detected = detect_llm_config_from_openclaw()
    except Exception as e:
        return jsonify({"error": f"读取 OpenClaw 配置失败: {e}", "found": True}), 500
    finally:
        sys.path[:] = sys_path_backup

    if not detected:
        return jsonify({
            "error": "OpenClaw 已安装但未检测到 LLM 配置",
            "found": True,
        }), 404

    return jsonify({
        "found": True,
        "api_key": detected.get("LLM_API_KEY", ""),
        "base_url": detected.get("LLM_BASE_URL", ""),
        "model": detected.get("LLM_MODEL", ""),
        "provider": detected.get("LLM_PROVIDER", ""),
    })


@app.route("/api/discover_models", methods=["POST"])
def discover_models():
    """代理调用 /v1/models 端点，返回可用模型列表。
    前端 setup wizard 用此端点检测模型。
    """
    data = request.get_json(force=True)
    api_key = data.get("api_key", "").strip()
    base_url = data.get("base_url", "").strip()

    if not api_key or not base_url:
        return jsonify({"error": "api_key and base_url required"}), 400

    # Build /v1/models URL
    models_url = base_url.rstrip("/")
    if not models_url.endswith("/v1"):
        models_url += "/v1"
    models_url += "/models"

    try:
        import urllib.request
        import urllib.error
        import json as _json

        req = urllib.request.Request(
            models_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = _json.loads(resp.read().decode())

        models_data = body.get("data", [])
        model_ids = []
        for m in models_data:
            mid = m.get("id", "")
            if mid and not mid.startswith("ft:") and not mid.startswith("dall-e"):
                model_ids.append(mid)
        model_ids.sort()

        return jsonify({"models": model_ids})
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode()[:300]
        except Exception:
            pass
        return jsonify({"error": f"API error {e.code}", "detail": err_body}), e.code
    except urllib.error.URLError as e:
        return jsonify({"error": f"Cannot connect: {e.reason}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/studio")
def studio():
    """Team Studio 页面"""
    return render_template("index.html")


@app.route("/mobile/group_chat")
def group_chat_mobile():
    """移动端群组群聊页面 - 需要登录访问"""
    return render_template("group_chat_mobile.html")


@app.route("/mobile_group_chat")
def group_chat_mobile_alias():
    """移动端群组群聊页面(别名) - 需要登录访问"""
    return render_template("group_chat_mobile.html")


@app.route("/manifest.json")
def manifest():
    """Serve PWA manifest for iOS/Android Add-to-Home-Screen support."""
    manifest_data = {
        "name": "Teamclaw",
        "short_name": "Teamclaw",
        "description": "TeamBot AI Agent - Intelligent Control Assistant",
        "start_url": "/mobile_group_chat",
        "scope": "/",
        "display": "standalone",
        "orientation": "portrait",
        "background_color": "#111827",
        "theme_color": "#111827",
        "lang": "zh-CN",
        "categories": ["productivity", "utilities"],
        "icons": [
            {
                "src": "https://img.icons8.com/fluency/192/robot-2.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "https://img.icons8.com/fluency/512/robot-2.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ]
    }
    return app.response_class(
        response=__import__("json").dumps(manifest_data),
        mimetype="application/manifest+json"
    )


@app.route("/sw.js")
def service_worker():
    """Serve Service Worker for PWA offline support and caching."""
    sw_code = """
// Teamclaw Service Worker v4 — network-first for all resources
const CACHE_NAME = 'teamclaw-v4';
const PRECACHE_URLS = ['/'];

self.addEventListener('install', event => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE_URLS))
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
        ).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', event => {
    // CRITICAL: Only handle GET requests. Non-GET (POST, PUT, DELETE) must pass through directly.
    if (event.request.method !== 'GET') return;

    // API / dynamic GET requests must NEVER be cached by SW — pass through directly
    const url = event.request.url;
    if (url.includes('/proxy_') || url.includes('/ask') || url.includes('/v1/') || url.includes('/api/')
        || url.includes('/teams') || url.includes('/internal_agent') || url.includes('/login')
        || url.includes('/status') || url.includes('/sessions') || url.includes('/experts')) return;

    // Network-first for static assets (JS/CSS/images/HTML):
    // Always try network first to get the latest version;
    // fall back to cache only when offline.
    event.respondWith(
        fetch(event.request).then(response => {
            if (response.ok) {
                const clone = response.clone();
                caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
            }
            return response;
        }).catch(() => caches.match(event.request))
    );
});
"""
    return app.response_class(
        response=sw_code,
        mimetype="application/javascript",
        headers={"Service-Worker-Allowed": "/"}
    )


@app.route("/v1/chat/completions", methods=["POST", "OPTIONS"])
def proxy_openai_completions():
    """OpenAI 兼容端点透传：前端直接发 OpenAI 格式，原样转发到后端"""
    if request.method == "OPTIONS":
        # CORS preflight
        resp = Response("", status=204)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return resp

    # 认证策略：
    # 1. 有 Flask session（前端网页登录）→ 用 INTERNAL_TOKEN:user_id 构造认证头
    # 2. 无 session 但有 Authorization（远程 CLI / 第三方客户端经 Tunnel）→ 原样透传
    auth_header = request.headers.get("Authorization", "")
    user_id = session.get("user_id")
    if user_id:
        # 前端网页走 session，用 INTERNAL_TOKEN 补全认证，不暴露密码
        auth_header = f"Bearer {INTERNAL_TOKEN}:{user_id}"
    # else: 外部调用自带 Bearer user:password，原样透传

    try:
        r = requests.post(
            LOCAL_OPENAI_COMPLETIONS_URL,
            json=request.get_json(silent=True),
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json",
            },
            stream=True,
            timeout=120,
        )
        if r.status_code != 200:
            return Response(r.content, status=r.status_code, content_type=r.headers.get("content-type", "application/json"))

        # 判断是否是流式响应
        content_type = r.headers.get("content-type", "")
        if "text/event-stream" in content_type:
            def generate():
                for chunk in r.iter_content(chunk_size=None):
                    if chunk:
                        yield chunk
            return Response(
                generate(),
                mimetype="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )
        else:
            return Response(r.content, status=r.status_code, content_type=content_type)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/v1/models", methods=["GET"])
def proxy_openai_models():
    """透传 /v1/models"""
    try:
        r = requests.get(f"http://127.0.0.1:{PORT_AGENT}/v1/models", timeout=10)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("content-type", "application/json"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_check_session")
def proxy_check_session():
    """轻量 session 校验：前端页面加载时调用，确认后端 session 仍然有效"""
    user_id = session.get("user_id")
    if user_id:
        return jsonify({"valid": True, "user_id": user_id})
    return jsonify({"valid": False}), 401


@app.route("/proxy_login", methods=["POST"])
def proxy_login():
    """代理登录请求到后端 Agent
    
    支持两种登录方式：
    1. 密码登录：user_id + password
    2. 本机免密登录：本地 127.0.0.1 直连时，只需要 user_id，不需要密码
    """
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    is_local = _is_direct_local_request()

    # 本机免密登录：127.0.0.1 直连且未提供密码时
    if is_local and not password:
        # 直接创建 session，不需要验证密码
        if user_id:
            session["user_id"] = user_id
            session.permanent = True
            return jsonify({"ok": True, "user_id": user_id, "mode": "local_no_password"})
        else:
            return jsonify({"error": "user_id required"}), 400

    # 密码登录
    if not password:
        return jsonify({"error": "password required"}), 400

    # 检查用户是否在 users.json 中（有密码记录）
    # 仅免密用户（不在 users.json 中）不允许密码登录
    if not _user_exists_in_users_json(user_id):
        return jsonify({
            "error": f"用户 '{user_id}' 未设置密码，无法使用密码登录。"
                     f"请使用「本机免密登录」，或通过 add-user 命令创建密码。"
        }), 403

    try:
        r = requests.post(LOCAL_LOGIN_URL, json={"user_id": user_id, "password": password}, timeout=10)
        if r.status_code == 200:
            # Login succeeded — only store user_id, NOT password.
            # Subsequent requests use INTERNAL_TOKEN for backend auth.
            session["user_id"] = user_id
            session.permanent = True
            return jsonify(r.json())
        else:
            return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ──────────────────────────────────────────────────────────────
# [已弃用] proxy_ask 和 proxy_ask_stream — 已被前端直接调用
# /v1/chat/completions 替代，以下端点注释保留备查。
# ──────────────────────────────────────────────────────────────
# @app.route("/proxy_ask", methods=["POST"])
# def proxy_ask():
#     ...
#
# @app.route("/proxy_ask_stream", methods=["POST"])
# def proxy_ask_stream():
#     ...

@app.route("/proxy_cancel", methods=["POST"])
def proxy_cancel():
    """代理取消请求到后端 Agent"""
    user_id = session.get("user_id", "")
    session_id = request.json.get("session_id", "default") if request.is_json else "default"
    try:
        r = requests.post(LOCAL_AGENT_CANCEL_URL, json={"user_id": user_id, "session_id": session_id}, headers=_internal_auth_headers(), timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/proxy_tts", methods=["POST"])
def proxy_tts():
    """代理 TTS 请求到后端 Agent，返回 mp3 音频流"""
    user_id = session.get("user_id", "")

    text = request.json.get("text", "")
    voice = request.json.get("voice")
    if not text.strip():
        return jsonify({"error": "文本不能为空"}), 400

    try:
        payload = {"user_id": user_id, "text": text}
        if voice:
            payload["voice"] = voice
        r = requests.post(LOCAL_TTS_URL, json=payload, headers=_internal_auth_headers(), timeout=60)
        if r.status_code != 200:
            return jsonify({"error": f"TTS 服务错误: {r.status_code}"}), r.status_code

        return Response(
            r.content,
            mimetype="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=tts_output.mp3"},
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/proxy_tools")
def proxy_tools():
    """代理获取工具列表请求到后端 Agent"""
    try:
        r = requests.get(LOCAL_TOOLS_URL, headers={"X-Internal-Token": INTERNAL_TOKEN}, timeout=10)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e), "tools": []}), 500

@app.route("/proxy_logout", methods=["POST"])
def proxy_logout():
    session.clear()
    return jsonify({"status": "success"})


@app.route("/login-link/<token>")
def magic_login(token):
    """Magic link login endpoint - login with a token in URL.
    
    Usage: /login-link/<token>?user=<user_id>
    """
    user_id = request.args.get('user', '')
    if not user_id:
        return jsonify({"error": "Missing user parameter"}), 400
    
    verified_user = verify_login_token(token)
    if verified_user == user_id:
        session['user_id'] = user_id
        session.permanent = True
        # Redirect to mobile group chat after successful login
        return redirect('/mobile_group_chat')
    else:
        return jsonify({"error": "Invalid or expired token"}), 401


@app.route("/generate_login_link", methods=["POST"])
def generate_login_link():
    """Generate a login token link for a user.
    
    Body: { "user_id": "username" }
    Returns: { "ok": true, "token": "...", "link": "https://.../login-link/xxx" }
    
    Note: This endpoint can ONLY be called from localhost (127.0.0.1) for security.
    """
    # Security: Only allow direct localhost requests
    if not _is_direct_local_request():
        return jsonify({"error": "Forbidden - localhost only"}), 403
    
    body = request.get_json(force=True)
    user_id = body.get("user_id", "")
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    # Generate token
    token = generate_login_token(user_id)
    
    # Build magic link
    # Try to get public domain from env
    public_domain = os.getenv('PUBLIC_DOMAIN', '')
    if public_domain == 'wait to set':
        public_domain = ''
    
    if public_domain:
        base_url = f"https://{public_domain}"
    else:
        # Fallback to request host
        base_url = request.host_url.rstrip('/')
    
    magic_link = f"{base_url}/login-link/{token}?user={user_id}"
    
    return jsonify({
        "ok": True,
        "token": token,
        "link": magic_link,
        "user_id": user_id
    })


@app.route("/proxy_login_with_token", methods=["POST"])
def proxy_login_with_token():
    """Login with a magic token.
    
    Body: { "user_id": "username", "token": "xxx" }
    Returns: { "ok": true, "user_id": "..." } or { "error": "..." }
    """
    body = request.get_json(force=True)
    user_id = body.get("user_id", "")
    token = body.get("token", "")
    
    if not user_id or not token:
        return jsonify({"error": "user_id and token are required"}), 400
    
    # Verify token
    verified_user = verify_login_token(token)
    if verified_user != user_id:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    # Create session
    session['user_id'] = user_id
    session.permanent = True
    
    return jsonify({
        "ok": True,
        "user_id": user_id,
        "mode": "token_login"
    })


LOCAL_SETTINGS_URL = f"http://127.0.0.1:{PORT_AGENT}/settings"


@app.route("/proxy_settings", methods=["GET"])
def proxy_get_settings():
    """代理获取系统配置"""
    user_id = session.get("user_id", "")
    try:
        r = requests.get(LOCAL_SETTINGS_URL, params={"user_id": user_id}, headers=_internal_auth_headers(), timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_settings", methods=["POST"])
def proxy_update_settings():
    """代理更新系统配置"""
    user_id = session.get("user_id", "")
    try:
        data = request.get_json(force=True)
        data["user_id"] = user_id
        r = requests.post(LOCAL_SETTINGS_URL, json=data, headers=_internal_auth_headers(), timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


LOCAL_SETTINGS_FULL_URL = f"http://127.0.0.1:{PORT_AGENT}/settings/full"
LOCAL_RESTART_URL = f"http://127.0.0.1:{PORT_AGENT}/restart"


@app.route("/proxy_settings_full", methods=["GET"])
def proxy_get_settings_full():
    """代理获取全量系统配置（不受白名单限制）"""
    user_id = session.get("user_id", "")
    try:
        r = requests.get(LOCAL_SETTINGS_FULL_URL, params={"user_id": user_id}, headers=_internal_auth_headers(), timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_settings_full", methods=["POST"])
def proxy_update_settings_full():
    """代理更新全量系统配置（不受白名单限制）"""
    user_id = session.get("user_id", "")
    try:
        data = request.get_json(force=True)
        data["user_id"] = user_id
        r = requests.post(LOCAL_SETTINGS_FULL_URL, json=data, headers=_internal_auth_headers(), timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_restart", methods=["POST"])
def proxy_restart_services():
    """直接写重启信号文件，不经过 mainagent（避免响应返回前进程被杀）"""
    user_id = session.get("user_id", "")
    try:
        restart_flag = os.path.join(root_dir, ".restart_flag")
        with open(restart_flag, "w") as f:
            f.write("restart")
        return jsonify({"status": "success", "message": "重启信号已发送"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_user_profile", methods=["GET"])
def proxy_user_profile():
    """读取当前用户的用户画像文本（user_profile.txt）"""
    user_id = session.get("user_id", "")
    if not user_id:
        return jsonify({"error": "not logged in"}), 401
    profile_path = os.path.join(root_dir, "data", "user_files", user_id, "user_profile.txt")
    profile_text = ""
    try:
        if os.path.isfile(profile_path):
            with open(profile_path, "r", encoding="utf-8") as f:
                profile_text = f.read().strip()
    except Exception:
        pass
    return jsonify({"user_id": user_id, "profile": profile_text})


@app.route("/proxy_user_profile", methods=["PUT"])
def proxy_save_user_profile():
    """保存当前用户的用户画像文本到 user_profile.txt"""
    user_id = session.get("user_id", "")
    if not user_id:
        return jsonify({"error": "not logged in"}), 401
    data = request.get_json() or {}
    profile_text = data.get("profile", "")
    profile_dir = os.path.join(root_dir, "data", "user_files", user_id)
    profile_path = os.path.join(profile_dir, "user_profile.txt")
    try:
        os.makedirs(profile_dir, exist_ok=True)
        with open(profile_path, "w", encoding="utf-8") as f:
            f.write(profile_text)
        return jsonify({"ok": True, "profile": profile_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_openclaw_sessions")
def proxy_openclaw_sessions():
    """Proxy to fetch OpenClaw session list from OASIS server."""

    filter_kw = request.args.get("filter", "")
    try:
        r = requests.get(
            f"{OASIS_BASE_URL}/sessions/openclaw",
            params={"filter": filter_kw},
            timeout=10,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e), "sessions": [], "available": False}), 500


@app.route("/proxy_openclaw_add", methods=["POST"])
def proxy_openclaw_add():
    """Proxy to create a new OpenClaw agent via OASIS server."""

    try:
        r = requests.post(
            f"{OASIS_BASE_URL}/sessions/openclaw/add",
            json=request.get_json(force=True),
            timeout=35,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/proxy_openclaw_default_workspace", methods=["GET"])
def proxy_openclaw_default_workspace():
    """Proxy to get the default OpenClaw workspace parent directory."""

    try:
        r = requests.get(f"{OASIS_BASE_URL}/sessions/openclaw/default-workspace", timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/proxy_openclaw_workspace_files", methods=["GET"])
def proxy_openclaw_workspace_files():
    """Proxy to list core files in an OpenClaw agent's workspace."""

    try:
        r = requests.get(
            f"{OASIS_BASE_URL}/sessions/openclaw/workspace-files",
            params={"workspace": request.args.get("workspace", "")},
            timeout=10,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/proxy_openclaw_workspace_file", methods=["GET"])
def proxy_openclaw_workspace_file_read():
    """Proxy to read a single workspace file."""

    try:
        r = requests.get(
            f"{OASIS_BASE_URL}/sessions/openclaw/workspace-file",
            params={"workspace": request.args.get("workspace", ""),
                    "filename": request.args.get("filename", "")},
            timeout=10,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/proxy_openclaw_workspace_file", methods=["POST"])
def proxy_openclaw_workspace_file_save():
    """Proxy to save a workspace file."""

    try:
        r = requests.post(
            f"{OASIS_BASE_URL}/sessions/openclaw/workspace-file",
            json=request.get_json(force=True),
            timeout=15,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/proxy_openclaw_agent_detail", methods=["GET"])
def proxy_openclaw_agent_detail():
    """Proxy to get detailed agent config (skills, tools, profile)."""

    try:
        r = requests.get(
            f"{OASIS_BASE_URL}/sessions/openclaw/agent-detail",
            params={"name": request.args.get("name", "")},
            timeout=15,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 502

@app.route("/proxy_openclaw_skills", methods=["GET"])
def proxy_openclaw_skills():
    """Proxy to OASIS /sessions/openclaw/skills, passing optional agent name for filtering."""

    try:
        agent_name = request.args.get("agent", "")
        params = {}
        if agent_name:
            params["name"] = agent_name
        r = requests.get(
            f"{OASIS_BASE_URL}/sessions/openclaw/skills",
            params=params,
            timeout=20,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/proxy_openclaw_tool_groups", methods=["GET"])
def proxy_openclaw_tool_groups():
    """Proxy to get available tool groups and profiles."""

    try:
        r = requests.get(f"{OASIS_BASE_URL}/sessions/openclaw/tool-groups", timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/proxy_openclaw_update_config", methods=["POST"])
def proxy_openclaw_update_config():
    """Proxy to update an agent's skills/tools config."""

    try:
        r = requests.post(
            f"{OASIS_BASE_URL}/sessions/openclaw/update-config",
            json=request.get_json(force=True),
            timeout=15,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/proxy_openclaw_channels", methods=["GET"])
def proxy_openclaw_channels():
    """Proxy to list all available channels."""

    try:
        r = requests.get(f"{OASIS_BASE_URL}/sessions/openclaw/channels", timeout=15)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/proxy_openclaw_agent_bindings", methods=["GET"])
def proxy_openclaw_agent_bindings():
    """Proxy to get an agent's current channel bindings."""

    try:
        r = requests.get(
            f"{OASIS_BASE_URL}/sessions/openclaw/agent-bindings",
            params={"agent": request.args.get("agent", "")},
            timeout=15,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/proxy_openclaw_agent_bind", methods=["POST"])
def proxy_openclaw_agent_bind():
    """Proxy to bind/unbind a channel to an agent."""

    try:
        r = requests.post(
            f"{OASIS_BASE_URL}/sessions/openclaw/agent-bind",
            json=request.get_json(force=True),
            timeout=15,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/proxy_openclaw_remove", methods=["DELETE"])
def proxy_openclaw_remove():
    """Proxy to delete an OpenClaw agent via OASIS server."""

    try:
        body = request.get_json(force=True)
        agent_name = body.get("name", "")
        if not agent_name:
            return jsonify({"ok": False, "error": "Agent name is required"}), 400
        
        r = requests.get(
            f"{OASIS_BASE_URL}/sessions/openclaw/remove",
            params={"name": agent_name},
            timeout=15,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/proxy_openclaw_chat", methods=["POST", "OPTIONS"])
def proxy_openclaw_chat():
    """Proxy chat completions to OpenClaw gateway.
    
    Forwards OpenAI-compatible chat requests to the OpenClaw gateway,
    allowing the frontend to chat directly with OpenClaw agents.
    The model field should be 'agent:<agent_name>'.
    """
    if request.method == "OPTIONS":
        resp = Response("", status=204)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return resp

    openclaw_api_url = os.getenv("OPENCLAW_API_URL", "")
    openclaw_api_key = os.getenv("OPENCLAW_GATEWAY_TOKEN", "") or os.getenv("OPENCLAW_API_KEY", "")

    if not openclaw_api_url:
        return jsonify({"error": "OPENCLAW_API_URL not configured"}), 503

    try:
        headers = {"Content-Type": "application/json"}
        if openclaw_api_key:
            headers["Authorization"] = f"Bearer {openclaw_api_key}"

        r = requests.post(
            openclaw_api_url,
            json=request.get_json(silent=True),
            headers=headers,
            stream=True,
            timeout=120,
        )
        if r.status_code != 200:
            return Response(r.content, status=r.status_code,
                            content_type=r.headers.get("content-type", "application/json"))

        content_type = r.headers.get("content-type", "")
        if "text/event-stream" in content_type:
            def generate():
                for chunk in r.iter_content(chunk_size=None):
                    if chunk:
                        yield chunk
            return Response(
                generate(),
                mimetype="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )
        else:
            return Response(r.content, status=r.status_code, content_type=content_type)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------------------
# Team OpenClaw Snapshot — export/restore agent configs in team folder
# ------------------------------------------------------------------

def _team_openclaw_agents_path(user_id: str, team: str) -> str:
    """Return the path to the team's external_agents.json file."""
    return os.path.join(root_dir, "data", "user_files", user_id, "teams", team, "external_agents.json")


def _team_openclaw_agents_load(user_id: str, team: str) -> list:
    """Load the team's external agents list; return [] if missing."""
    p = _team_openclaw_agents_path(user_id, team)
    if not os.path.isfile(p):
        return []
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def _team_openclaw_agents_save(user_id: str, team: str, data: list):
    """Save the team's external agents list to disk."""
    p = _team_openclaw_agents_path(user_id, team)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route("/team_openclaw_snapshot", methods=["GET"])
def team_openclaw_snapshot_get():
    """Get the team's saved external agent list.
    Query: ?team=<name>
    Returns: { ok, agents: [ { name, tag, global_name, config?, workspace_files?, meta? }, ... ] }
    """
    user_id = session.get("user_id", "")
    team = request.args.get("team", "")
    if not team:
        return jsonify({"ok": False, "error": "team is required"}), 400
    data = _team_openclaw_agents_load(user_id, team)
    return jsonify({"ok": True, "agents": data})


@app.route("/team_openclaw_snapshot/export", methods=["POST"])
def team_openclaw_snapshot_export():
    """Export (save) an OpenClaw agent's full config into the team's external_agents.json.
    Body: { "team": "...", "agent_name": "real_agent_name (global_name)", "short_name": "display_name" }
    Fetches agent snapshot from oasis server and upserts into external_agents.json.
    Also fetches and saves cron jobs for this agent.
    """
    user_id = session.get("user_id", "")

    body = request.get_json(force=True)
    team = body.get("team", "")
    agent_name = body.get("agent_name", "")
    short_name = body.get("short_name", "") or agent_name

    if not team or not agent_name:
        return jsonify({"ok": False, "error": "team and agent_name are required"}), 400

    # Fetch snapshot from oasis server
    try:
        r = requests.get(
            f"{OASIS_BASE_URL}/sessions/openclaw/agent-snapshot",
            params={"name": agent_name},
            timeout=30,
        )
        snapshot = r.json()
        if not snapshot.get("ok"):
            return jsonify({"ok": False, "error": snapshot.get("error", "Export failed")}), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

    # Fetch cron jobs for this agent using cron_utils
    cron_jobs, cron_error = get_agent_cron_jobs(agent_name)
    if cron_error:
        print(f"[Warning] Failed to fetch cron jobs for {agent_name}: {cron_error}")
        cron_jobs = []

    # Save to team snapshot list
    data = _team_openclaw_agents_load(user_id, team)
    # Remove existing entry with same name if present, then append
    data = [a for a in data if a.get("name") != short_name]
    data.append({
        "name": short_name,
        "tag": "openclaw",
        "global_name": agent_name,
        "config": snapshot.get("config", {}),
        "workspace_files": snapshot.get("workspace_files", {}),
        "cron_jobs": cron_jobs,
    })
    _team_openclaw_agents_save(user_id, team, data)

    file_count = len(snapshot.get("workspace_files", {}))
    return jsonify({
        "ok": True,
        "short_name": short_name,
        "agent_name": agent_name,
        "file_count": file_count,
        "cron_count": len(cron_jobs),
        "message": f"Exported '{agent_name}' → team snapshot as '{short_name}' ({file_count} files, {len(cron_jobs)} cron jobs)",
    })


@app.route("/team_openclaw_snapshot/sync_all", methods=["POST"])
def team_openclaw_snapshot_sync_all():
    """Sync ALL OpenClaw agents in the team's external_agents.json.

    Reads the existing openclaw entries from external_agents.json (the JSON is
    the source of truth for which agents belong to this team), fetches each
    agent's latest snapshot from the OASIS server using the 'global_name' field,
    and updates the JSON in-place.
    Also fetches and updates cron jobs for each agent.

    Body: { "team": "team_name" }
    Returns: { ok, synced: int, agents: [...] }
    """
    user_id = session.get("user_id", "")

    body = request.get_json(force=True)
    team = body.get("team", "")
    if not team:
        return jsonify({"ok": False, "error": "team is required"}), 400

    team_dir = os.path.join(root_dir, "data", "user_files", user_id, "teams", team)
    if not os.path.exists(team_dir):
        return jsonify({"ok": False, "error": "Team not found"}), 404

    # Source of truth: existing external_agents.json
    existing = _team_openclaw_agents_load(user_id, team)
    openclaw_entries = [a for a in existing if a.get("tag") == "openclaw"]
    non_openclaw = [a for a in existing if a.get("tag") != "openclaw"]

    if not openclaw_entries:
        return jsonify({"ok": True, "synced": 0, "agents": existing})

    # Fetch latest snapshot for each openclaw agent using its session (real agent name)
    new_openclaw = []
    errors = []
    for entry in openclaw_entries:
        short_name = entry.get("name", "")
        agent_name = entry.get("global_name", "")
        if not agent_name:
            errors.append(f"{short_name}: missing global_name field")
            new_openclaw.append(entry)  # keep as-is
            continue
        try:
            sr = requests.get(
                f"{OASIS_BASE_URL}/sessions/openclaw/agent-snapshot",
                params={"name": agent_name},
                timeout=30,
            )
            snap = sr.json()
            if snap.get("ok"):
                config = snap.get("config", {})
                # Remove channel-related keys if present
                config.pop("channels", None)
                config.pop("bindings", None)
                
                # Fetch cron jobs for this agent using cron_utils
                cron_jobs, cron_error = get_agent_cron_jobs(agent_name)
                if cron_error:
                    print(f"[Warning] Failed to fetch cron jobs for {agent_name}: {cron_error}")
                    cron_jobs = []
                
                new_openclaw.append({
                    "name": short_name,
                    "tag": "openclaw",
                    "global_name": agent_name,
                    "config": config,
                    "workspace_files": snap.get("workspace_files", {}),
                    "cron_jobs": cron_jobs,
                })
            else:
                errors.append(f"{agent_name}: {snap.get('error', 'unknown')}")
                new_openclaw.append(entry)  # keep old snapshot on failure
        except Exception as e:
            errors.append(f"{agent_name}: {e}")
            new_openclaw.append(entry)  # keep old snapshot on failure

    merged = new_openclaw + non_openclaw
    _team_openclaw_agents_save(user_id, team, merged)

    resp = {"ok": True, "synced": len(new_openclaw), "agents": merged}
    if errors:
        resp["warnings"] = errors
    return jsonify(resp)


@app.route("/team_openclaw_snapshot/restore", methods=["POST"])
def team_openclaw_snapshot_restore():
    """Restore an OpenClaw agent from the team snapshot.
    Body: { "team": "...", "short_name": "...", "target_agent_name": "optional, defaults to team_name" }
    Reads from external_agents.json and sends to oasis server's restore endpoint.
    If target_agent_name is not provided, generates one as team + "_" + short_name
    to avoid agent name collisions on a new device.
    On success, updates the global_name field in external_agents.json.
    Also restores cron jobs for this agent.
    """
    user_id = session.get("user_id", "")

    body = request.get_json(force=True)
    team = body.get("team", "")
    short_name = body.get("short_name", "")
    target_name = body.get("target_agent_name", "")

    if not team or not short_name:
        return jsonify({"ok": False, "error": "team and short_name are required"}), 400
    # Load snapshot — find the openclaw entry by name
    data = _team_openclaw_agents_load(user_id, team)
    agent_snapshot = None
    for entry in data:
        if entry.get("name") == short_name and entry.get("tag") == "openclaw":
            agent_snapshot = entry
            break
    if not agent_snapshot:
        return jsonify({"ok": False, "error": f"No snapshot found for '{short_name}' in team '{team}'"}), 404

    # Use target_agent_name from request, or generate from team + "_" + name
    # to avoid agent name collisions on a new device.
    if not target_name:
        target_name = team + "_" + short_name

    # Send to oasis server restore endpoint
    try:
        r = requests.post(
            f"{OASIS_BASE_URL}/sessions/openclaw/agent-restore",
            json={
                "agent_name": target_name,
                "config": agent_snapshot.get("config", {}),
                "workspace_files": agent_snapshot.get("workspace_files", {}),
            },
            timeout=60,
        )
        result = r.json()
        # On success, persist the new session name back to external_agents.json
        if result.get("ok"):
            agent_snapshot["global_name"] = target_name
            _team_openclaw_agents_save(user_id, team, data)
            
            # Restore cron jobs for this agent using cron_utils
            cron_jobs = agent_snapshot.get("cron_jobs", [])
            if cron_jobs:
                cron_restored, cron_errors = restore_cron_jobs(cron_jobs, target_name)
                result["cron_restored"] = cron_restored
                result["cron_total"] = len(cron_jobs)
                if cron_errors:
                    result["cron_errors"] = cron_errors
        
        return jsonify(result), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/team_openclaw_snapshot/export_all", methods=["POST"])
def team_openclaw_snapshot_export_all():
    """Export (re-fetch snapshots for) ALL OpenClaw agents in the team's JSON.
    Body: { "team": "..." }
    Uses external_agents.json as the source of truth for which agents belong
    to this team, fetches each one's latest snapshot, and updates in-place.
    Also fetches and saves cron jobs for each agent.
    """
    user_id = session.get("user_id", "")

    body = request.get_json(force=True)
    team = body.get("team", "")
    if not team:
        return jsonify({"ok": False, "error": "team is required"}), 400

    # Source of truth: existing external_agents.json
    existing = _team_openclaw_agents_load(user_id, team)
    openclaw_entries = [a for a in existing if a.get("tag") == "openclaw"]
    non_openclaw = [a for a in existing if a.get("tag") != "openclaw"]

    if not openclaw_entries:
        return jsonify({"ok": True, "exported": 0, "message": "No openclaw agents in JSON"}), 200

    new_openclaw = []
    exported = 0
    errors = []

    for entry in openclaw_entries:
        short_name = entry.get("name", "")
        agent_name = entry.get("global_name", "")
        if not agent_name:
            errors.append(f"{short_name}: missing global_name field")
            new_openclaw.append(entry)  # keep as-is
            continue
        try:
            r = requests.get(
                f"{OASIS_BASE_URL}/sessions/openclaw/agent-snapshot",
                params={"name": agent_name},
                timeout=30,
            )
            snapshot = r.json()
            if snapshot.get("ok"):
                # Fetch cron jobs for this agent using cron_utils
                cron_jobs, cron_error = get_agent_cron_jobs(agent_name)
                if cron_error:
                    print(f"[Warning] Failed to fetch cron jobs for {agent_name}: {cron_error}")
                    cron_jobs = []
                
                new_openclaw.append({
                    "name": short_name,
                    "tag": "openclaw",
                    "global_name": agent_name,
                    "config": snapshot.get("config", {}),
                    "workspace_files": snapshot.get("workspace_files", {}),
                    "cron_jobs": cron_jobs,
                })
                exported += 1
            else:
                errors.append(f"{agent_name}: {snapshot.get('error', 'failed')}")
                new_openclaw.append(entry)  # keep old snapshot on failure
        except Exception as e:
            errors.append(f"{agent_name}: {e}")
            new_openclaw.append(entry)  # keep old snapshot on failure

    merged = new_openclaw + non_openclaw
    _team_openclaw_agents_save(user_id, team, merged)

    return jsonify({
        "ok": True,
        "exported": exported,
        "total": len(openclaw_entries),
        "errors": errors,
        "message": f"Exported {exported}/{len(openclaw_entries)} agents to team snapshot",
    })


@app.route("/team_openclaw_snapshot/restore_all", methods=["POST"])
def team_openclaw_snapshot_restore_all():
    """Restore ALL openclaw agents from the team's external_agents.json.
    Body: { "team": "..." }
    For each openclaw agent in the JSON, generates a new global name as
    team + "_" + agent_name to avoid collisions, then restores it.
    On success, updates global_name fields in external_agents.json.
    """
    user_id = session.get("user_id", "")

    body = request.get_json(force=True)
    team = body.get("team", "")
    if not team:
        return jsonify({"ok": False, "error": "team is required"}), 400

    data = _team_openclaw_agents_load(user_id, team)
    openclaw_entries = [a for a in data if a.get("tag") == "openclaw"]
    if not openclaw_entries:
        return jsonify({"ok": True, "restored": 0, "message": "No openclaw snapshots found"}), 200

    restored = 0
    errors = []

    for entry in openclaw_entries:
        short_name = entry.get("name", "")
        # Generate new session from team + "_" + name to avoid collisions
        target_name = team + "_" + short_name
        try:
            r = requests.post(
                f"{OASIS_BASE_URL}/sessions/openclaw/agent-restore",
                json={
                    "agent_name": target_name,
                    "config": entry.get("config", {}),
                    "workspace_files": entry.get("workspace_files", {}),
                },
                timeout=60,
            )
            result = r.json()
            if result.get("ok"):
                restored += 1
                # Update global_name in JSON to reflect the new agent name
                entry["global_name"] = target_name
                
                # Restore cron jobs for this agent using cron_utils
                cron_jobs = entry.get("cron_jobs", [])
                if cron_jobs:
                    cron_restored, cron_errors = restore_cron_jobs(cron_jobs, target_name)
                    result["cron_restored"] = cron_restored
                    result["cron_total"] = len(cron_jobs)
                    if cron_errors:
                        result["cron_errors"] = cron_errors
            else:
                errors.append(f"{target_name}: {result.get('errors', result.get('error', 'failed'))}")
        except Exception as e:
            errors.append(f"{target_name}: {e}")

    # Persist updated global_names back to external_agents.json
    _team_openclaw_agents_save(user_id, team, data)

    return jsonify({
        "ok": True,
        "restored": restored,
        "total": len(openclaw_entries),
        "errors": errors,
        "message": f"Restored {restored}/{len(openclaw_entries)} agents from team snapshot",
    })


# ──────────────────────────────────────────────────────────────
# Visual Orchestration – proxy endpoints
# ──────────────────────────────────────────────────────────────
import sys as _sys, math as _math, re as _re, yaml as _yaml

# Import expert pool & conversion helpers from visual/main.py
_VISUAL_DIR = os.path.join(root_dir, "visual")
if _VISUAL_DIR not in _sys.path:
    _sys.path.insert(0, _VISUAL_DIR)

try:
    from main import (
        DEFAULT_EXPERTS as _VIS_EXPERTS,
        TAG_EMOJI as _VIS_TAG_EMOJI,
        layout_to_yaml as _vis_layout_to_yaml,
        _build_llm_prompt as _vis_build_llm_prompt,
        _extract_yaml_from_response as _vis_extract_yaml,
        _validate_generated_yaml as _vis_validate_yaml,
    )
except Exception:
    # Fallback: define minimal versions if visual module unavailable
    _VIS_EXPERTS = []
    _VIS_TAG_EMOJI = {}
    _vis_layout_to_yaml = None
    _vis_build_llm_prompt = None
    _vis_extract_yaml = None
    _vis_validate_yaml = None

# Import YAML→Layout converter (used for on-the-fly layout generation from saved YAML)
try:
    from mcp_oasis import _yaml_to_layout_data as _vis_yaml_to_layout
except Exception:
    _vis_yaml_to_layout = None


def _yaml_dir(user_id: str, team: str = "") -> str:
    """Return the YAML workflow directory path for a user (team-scoped when team is provided)."""
    if team:
        return os.path.join(root_dir, "data", "user_files", user_id, "teams", team, "oasis", "yaml")
    return os.path.join(root_dir, "data", "user_files", user_id, "oasis", "yaml")


@app.route("/proxy_visual/experts", methods=["GET"])
def proxy_visual_experts():
    """Return available expert pool for orchestration canvas (public + user custom + team)."""
    user_id = session.get("user_id", "")
    team = request.args.get("team", "")
    # Fetch full expert list from OASIS server (public + user custom + team)
    all_experts = []
    try:
        params = {"user_id": user_id}
        if team:
            params["team"] = team
        r = requests.get(f"{OASIS_BASE_URL}/experts", params=params, timeout=5)
        if r.ok:
            all_experts = r.json().get("experts", [])
    except Exception:
        pass

    # Fallback to static list if OASIS unavailable
    if not all_experts:
        all_experts = [{**e, "source": "public"} for e in _VIS_EXPERTS]

    # Agency 专家按 category 分配不同的 emoji
    _AGENCY_CAT_EMOJI = {
        "design": "🎨", "engineering": "⚙️", "marketing": "📢",
        "product": "📦", "project-management": "📋",
        "spatial-computing": "🥽", "specialized": "🔬",
        "support": "🛡️", "testing": "🧪",
    }

    result = []
    for e in all_experts:
        emoji = _VIS_TAG_EMOJI.get(e.get("tag", ""), "")
        if not emoji:
            # Agency 专家: 根据 category 分配 emoji
            emoji = _AGENCY_CAT_EMOJI.get(e.get("category", ""), "⭐")
        if e.get("source") == "custom":
            emoji = "🛠️"
        if e.get("source") == "team":
            emoji = "👥"
        result.append({
            **e,
            "emoji": emoji,
            "deletable": e.get("deletable", e.get("source") not in {"public", "agency"}),
        })
    return jsonify(result)


@app.route("/proxy_visual/experts/custom", methods=["POST"])
def proxy_visual_add_custom_expert():
    """Add a custom expert via OASIS server (team-scoped when team param provided)."""
    user_id = session.get("user_id", "")
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    team = request.args.get("team", "") or data.get("team", "")
    try:
        r = requests.post(
            f"{OASIS_BASE_URL}/experts/user",
            json={"user_id": user_id, "team": team, **data},
            timeout=10,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_visual/experts/custom/<tag>", methods=["DELETE"])
def proxy_visual_delete_custom_expert(tag):
    """Delete a custom expert via OASIS server (team-scoped when team param provided)."""
    user_id = session.get("user_id", "")
    team = request.args.get("team", "")
    try:
        params = {"user_id": user_id}
        if team:
            params["team"] = team
        r = requests.delete(
            f"{OASIS_BASE_URL}/experts/user/{tag}",
            params=params,
            timeout=10,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_visual/generate-yaml", methods=["POST"])
def proxy_visual_generate_yaml():
    """Convert canvas layout to OASIS YAML (rule-based)."""
    data = request.get_json()
    if not data or not _vis_layout_to_yaml:
        return jsonify({"error": "No data or visual module unavailable"}), 400
    try:
        yaml_out = _vis_layout_to_yaml(data)
        return jsonify({"yaml": yaml_out})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_visual/agent-generate-yaml", methods=["POST"])
def proxy_visual_agent_generate_yaml():
    """Build prompt + send to main agent using session credentials → get YAML."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    user_id = session.get("user_id", "")

    try:
        prompt = _vis_build_llm_prompt(data) if _vis_build_llm_prompt else "Error: visual module unavailable"

        # Call main agent with INTERNAL_TOKEN credentials
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {INTERNAL_TOKEN}:{user_id}",
        }
        payload = {
            "model": "teambot",
            "messages": [
                {"role": "system", "content": (
                    "You are a YAML schedule generator for the OASIS expert orchestration engine. "
                    "Output ONLY valid YAML, no markdown fences, no explanations, no commentary. "
                    "The YAML must start with 'version: 1' and contain a 'plan:' section."
                )},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "session_id": data.get("target_session_id") or "visual_orchestrator",
            "temperature": 0.3,
        }
        resp = requests.post(LOCAL_OPENAI_COMPLETIONS_URL, json=payload, headers=headers, timeout=60)
        if resp.status_code != 200:
            return jsonify({"prompt": prompt, "error": f"Agent returned HTTP {resp.status_code}: {resp.text[:500]}", "agent_yaml": None})

        result = resp.json()
        agent_reply = ""
        try:
            agent_reply = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            agent_reply = str(result)

        agent_yaml = _vis_extract_yaml(agent_reply) if _vis_extract_yaml else agent_reply
        validation = _vis_validate_yaml(agent_yaml) if _vis_validate_yaml else {"valid": False, "error": "validator unavailable"}

        # Auto-save valid YAML to user's oasis/yaml directory (team-scoped)
        saved_path = None
        if validation.get("valid"):
            try:
                import time as _time
                team = data.get("team", "")
                yd = _yaml_dir(user_id, team)
                os.makedirs(yd, exist_ok=True)
                fname = data.get("save_name") or f"orch_{_time.strftime('%Y%m%d_%H%M%S')}"
                if not fname.endswith((".yaml", ".yml")):
                    fname += ".yaml"
                fpath = os.path.join(yd, fname)
                with open(fpath, "w", encoding="utf-8") as _yf:
                    _yf.write(f"# Auto-generated from visual orchestrator\n{agent_yaml}")
                saved_path = fname
            except Exception as save_err:
                saved_path = f"save_error: {save_err}"

        return jsonify({"prompt": prompt, "agent_yaml": agent_yaml, "agent_reply_raw": agent_reply, "validation": validation, "saved_file": saved_path})

    except requests.exceptions.ConnectionError:
        prompt = _vis_build_llm_prompt(data) if _vis_build_llm_prompt else ""
        return jsonify({"prompt": prompt, "error": "Cannot connect to main agent. Is mainagent.py running?", "agent_yaml": None})
    except requests.exceptions.Timeout:
        prompt = _vis_build_llm_prompt(data) if _vis_build_llm_prompt else ""
        return jsonify({"prompt": prompt, "error": "Agent request timed out (60s).", "agent_yaml": None})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_visual/save-layout", methods=["POST"])
def proxy_visual_save_layout():
    """Save canvas layout as YAML (no separate layout JSON stored)."""
    user_id = session.get("user_id", "")
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    if not _vis_layout_to_yaml:
        return jsonify({"error": "Layout-to-YAML converter unavailable"}), 500
    name = data.get("name", "untitled")
    safe = "".join(c for c in name if c.isalnum() or c in "-_ ").strip() or "untitled"
    try:
        yaml_out = _vis_layout_to_yaml(data)
    except Exception as e:
        return jsonify({"error": f"YAML conversion failed: {e}"}), 500
    team = data.get("team", "")
    yd = _yaml_dir(user_id, team)
    os.makedirs(yd, exist_ok=True)
    fpath = os.path.join(yd, f"{safe}.yaml")
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(f"# Saved from visual orchestrator\n{yaml_out}")
    return jsonify({"saved": True})


@app.route("/proxy_visual/load-layouts", methods=["GET"])
def proxy_visual_load_layouts():
    """List saved YAML workflows as available layouts (team-scoped)."""
    user_id = session.get("user_id", "")
    team = request.args.get("team", "")
    yd = _yaml_dir(user_id, team)
    if not os.path.isdir(yd):
        return jsonify([])
    return jsonify([f.replace('.yaml', '').replace('.yml', '') for f in sorted(os.listdir(yd)) if f.endswith((".yaml", ".yml"))])


@app.route("/proxy_visual/load-layout/<name>", methods=["GET"])
def proxy_visual_load_layout(name):
    """Load a layout by reading the YAML file and converting to layout on-the-fly."""
    user_id = session.get("user_id", "")
    if not _vis_yaml_to_layout:
        return jsonify({"error": "YAML-to-layout converter unavailable"}), 500
    safe = "".join(c for c in name if c.isalnum() or c in "-_ ").strip()
    team = request.args.get("team", "")
    yd = _yaml_dir(user_id, team)
    # Try .yaml then .yml
    fpath = os.path.join(yd, f"{safe}.yaml")
    if not os.path.isfile(fpath):
        fpath = os.path.join(yd, f"{safe}.yml")
    if not os.path.isfile(fpath):
        return jsonify({"error": "Not found"}), 404
    with open(fpath, "r", encoding="utf-8") as f:
        yaml_content = f.read()
    try:
        layout = _vis_yaml_to_layout(yaml_content)
        layout["name"] = safe
        return jsonify(layout)
    except Exception as e:
        return jsonify({"error": f"YAML-to-layout conversion failed: {e}"}), 500


@app.route("/proxy_visual/load-yaml-raw/<name>", methods=["GET"])
def proxy_visual_load_yaml_raw(name):
    """Return raw YAML text for a saved workflow."""
    user_id = session.get("user_id", "")
    safe = "".join(c for c in name if c.isalnum() or c in "-_ ").strip()
    team = request.args.get("team", "")
    yd = _yaml_dir(user_id, team)
    fpath = os.path.join(yd, f"{safe}.yaml")
    if not os.path.isfile(fpath):
        fpath = os.path.join(yd, f"{safe}.yml")
    if not os.path.isfile(fpath):
        return jsonify({"error": "Not found"}), 404
    with open(fpath, "r", encoding="utf-8") as f:
        return jsonify({"yaml": f.read()})


@app.route("/proxy_visual/delete-layout/<name>", methods=["DELETE"])
def proxy_visual_delete_layout(name):
    """Delete a saved YAML workflow."""
    user_id = session.get("user_id", "")
    safe = "".join(c for c in name if c.isalnum() or c in "-_ ").strip()
    team = request.args.get("team", "")
    yd = _yaml_dir(user_id, team)
    fpath = os.path.join(yd, f"{safe}.yaml")
    if not os.path.isfile(fpath):
        fpath = os.path.join(yd, f"{safe}.yml")
    if os.path.isfile(fpath):
        os.remove(fpath)
        return jsonify({"deleted": True})
    return jsonify({"error": "Not found"}), 404


@app.route("/proxy_visual/upload-yaml", methods=["POST"])
def proxy_visual_upload_yaml():
    """Upload a YAML file: save it and convert to layout data for canvas import."""
    user_id = session.get("user_id", "")
    data = request.get_json()
    if not data or not data.get("content"):
        return jsonify({"error": "No content"}), 400

    filename = data.get("filename", "upload.yaml")
    content = data["content"]

    # Validate YAML syntax
    try:
        _yaml.safe_load(content)
    except Exception as e:
        return jsonify({"error": f"Invalid YAML: {e}"}), 400

    # Save the file (team-scoped)
    safe = "".join(c for c in os.path.splitext(filename)[0] if c.isalnum() or c in "-_ ").strip() or "upload"
    team = data.get("team", "")
    yd = _yaml_dir(user_id, team)
    os.makedirs(yd, exist_ok=True)
    fpath = os.path.join(yd, f"{safe}.yaml")
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)

    # Convert to layout data if converter available
    layout = None
    if _vis_yaml_to_layout:
        try:
            layout = _vis_yaml_to_layout(content)
            layout["name"] = safe
        except Exception:
            layout = None

    return jsonify({"saved": True, "name": safe, "layout": layout})


@app.route("/proxy_visual/sessions-status", methods=["GET"])
def proxy_visual_sessions_status():
    """Return all sessions with their running status for the canvas display."""
    user_id = session.get("user_id", "")
    try:
        r = requests.post(LOCAL_SESSIONS_URL, json={"user_id": user_id}, headers=_internal_auth_headers(), timeout=10)
        if r.status_code != 200:
            return jsonify([])
        sessions_data = r.json()
        return jsonify(sessions_data if isinstance(sessions_data, list) else [])
    except Exception:
        return jsonify([])


# ===== Tunnel Control API =====

import subprocess as _subprocess
import signal as _signal
import platform as _platform

_IS_WINDOWS = _platform.system().lower() == "windows"
_TUNNEL_PIDFILE = os.path.join(root_dir, ".tunnel.pid")
_TUNNEL_SCRIPT = os.path.join(root_dir, "scripts", "tunnel.py")


def _tunnel_running() -> tuple[bool, int | None]:
    """Check if tunnel is running, return (running, pid).
    Cleans up stale PID file if the process is dead."""
    if not os.path.isfile(_TUNNEL_PIDFILE):
        return False, None
    try:
        with open(_TUNNEL_PIDFILE) as f:
            pid = int(f.read().strip())
        if _IS_WINDOWS:
            # Windows: use tasklist to check if PID exists
            result = _subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                capture_output=True, text=True, timeout=5,
            )
            if str(pid) not in result.stdout:
                raise OSError("Process not found")
        else:
            os.kill(pid, 0)  # check if alive (Unix)
        return True, pid
    except (ValueError, OSError):
        # PID file exists but process is dead — clean up stale PID file
        try:
            os.remove(_TUNNEL_PIDFILE)
        except OSError:
            pass
        return False, None


def _get_public_domain() -> str:
    """Read PUBLIC_DOMAIN from .env."""
    from dotenv import dotenv_values
    vals = dotenv_values(os.path.join(root_dir, "config", ".env"))
    domain = vals.get("PUBLIC_DOMAIN", "")
    if domain == "wait to set":
        return ""
    return domain


@app.route("/proxy_tunnel/status", methods=["GET"])
def proxy_tunnel_status():
    """Return tunnel running status and public URL."""
    running, pid = _tunnel_running()
    domain = _get_public_domain() if running else ""
    return jsonify({"running": running, "pid": pid, "public_domain": domain})


@app.route("/proxy_tunnel/start", methods=["POST"])
def proxy_tunnel_start():
    """Start cloudflare tunnel in background."""
    user_id = session.get("user_id", "")

    running, pid = _tunnel_running()
    if running:
        domain = _get_public_domain()
        return jsonify({"status": "already_running", "pid": pid, "public_domain": domain})

    # Start tunnel.py in background
    log_dir = os.path.join(root_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "tunnel.log")

    try:
        import sys as _sys
        log_fh = open(log_file, "w")
        popen_kwargs = dict(
            stdout=log_fh,
            stderr=_subprocess.STDOUT,
            cwd=root_dir,
        )
        if _IS_WINDOWS:
            popen_kwargs["creationflags"] = (
                _subprocess.CREATE_NO_WINDOW | _subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            popen_kwargs["start_new_session"] = True

        proc = _subprocess.Popen(
            [_sys.executable, _TUNNEL_SCRIPT],
            **popen_kwargs,
        )
        with open(_TUNNEL_PIDFILE, "w") as f:
            f.write(str(proc.pid))
        return jsonify({"status": "started", "pid": proc.pid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_tunnel/stop", methods=["POST"])
def proxy_tunnel_stop():
    """Stop the running tunnel."""
    user_id = session.get("user_id", "")

    running, pid = _tunnel_running()
    if not running:
        # Clean up stale pidfile
        if os.path.isfile(_TUNNEL_PIDFILE):
            os.remove(_TUNNEL_PIDFILE)
        return jsonify({"status": "not_running"})

    try:
        if _IS_WINDOWS:
            # Windows: use taskkill to terminate process tree
            _subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                capture_output=True, timeout=10,
            )
        else:
            os.kill(pid, _signal.SIGTERM)
            # Wait briefly for exit
            import time as _time
            for _ in range(10):
                try:
                    os.kill(pid, 0)
                    _time.sleep(0.5)
                except OSError:
                    break
            else:
                # Force kill
                try:
                    os.kill(pid, _signal.SIGKILL)
                except OSError:
                    pass
    except OSError:
        pass

    if os.path.isfile(_TUNNEL_PIDFILE):
        os.remove(_TUNNEL_PIDFILE)

    # Clear PUBLIC_DOMAIN from .env so stale URLs are not used
    _clear_public_domain()

    return jsonify({"status": "stopped"})


def _clear_public_domain():
    """Clear PUBLIC_DOMAIN in config/.env after tunnel stops."""
    env_file = os.path.join(root_dir, "config", ".env")
    if not os.path.exists(env_file):
        return
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            if line.strip().startswith("PUBLIC_DOMAIN="):
                new_lines.append("PUBLIC_DOMAIN=\n")
            else:
                new_lines.append(line)
        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        # Also clear from current process env
        os.environ.pop("PUBLIC_DOMAIN", None)
    except Exception:
        pass


# ------------------------------------------------------------------
# Internal Agent CRUD  — per-user agent list stored as JSON
# Single file:
#   internal_agents.json: [{"name": "...", "tag": "...", "session": "sid"}, ...]
#   (session is a per-entry field, analogous to global_name in external_agents.json)
# Paths:
#   - Team mode: data/user_files/{user_id}/teams/{team}/internal_agents.json
#   - Non-team mode: data/user_files/{user_id}/internal_agents.json
# Frontend expects: {"agents": [{"session": "sid", "meta": {...}}, ...]}
# ------------------------------------------------------------------

def _ia_dir(user_id: str, team: str = "") -> str:
    """Return the directory path for internal agent files."""
    if team:
        return os.path.join(root_dir, "data", "user_files", user_id, "teams", team)
    return os.path.join(root_dir, "data", "user_files", user_id)


def _ia_path(user_id: str, team: str = "") -> str:
    """Return the internal_agents.json file path."""
    return os.path.join(_ia_dir(user_id, team), "internal_agents.json")


def _ia_load(user_id: str, team: str = "") -> list:
    """Load internal agents from internal_agents.json.

    The file stores a flat list:
      [{"name": "...", "tag": "...", "session": "sid"}, ...]

    Returns: [{"session": "sid", "meta": {"name": "...", "tag": "..."}}, ...]
    """
    ia_file = _ia_path(user_id, team)

    if not os.path.isfile(ia_file):
        return []

    with open(ia_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    agents_list = data if isinstance(data, list) else []
    result = []
    for a in agents_list:
        if not isinstance(a, dict) or "name" not in a:
            continue
        sid = a.get("session", "")
        meta = {k: v for k, v in a.items() if k != "session"}
        result.append({"session": sid, "meta": meta})
    return result


def _ia_save(user_id: str, data: list, team: str = ""):
    """Save internal agents to internal_agents.json.

    data: [{"session": "sid", "meta": {"name": "...", "tag": "...", ...}}, ...]
    Stored as: [{"name": "...", "tag": "...", "session": "sid"}, ...]
    """
    ia_file = _ia_path(user_id, team)
    directory = _ia_dir(user_id, team)
    os.makedirs(directory, exist_ok=True)

    agents_list = []
    for item in data:
        meta = item.get("meta", {})
        if not isinstance(meta, dict):
            continue
        entry = dict(meta)  # copy all meta fields (name, tag, ...)
        sid = item.get("session", "")
        if sid:
            entry["session"] = sid
        agents_list.append(entry)

    with open(ia_file, "w", encoding="utf-8") as f:
        json.dump(agents_list, f, ensure_ascii=False, indent=2)


@app.route("/internal_agents", methods=["GET"])
def ia_list():
    """Return the internal-agent list for the logged-in user.

    ``agents`` contains only the primary source (current team or public).
    ``all_known_sessions`` is a list of ALL session IDs found across every
    ``internal_agents.json`` (public + every team).  The frontend uses
    ``agents`` for display and ``all_known_sessions`` to determine which
    sessions are truly unnamed (not in any json).
    """
    user_id = session.get("user_id", "")
    team = request.args.get("team", "")

    # Primary source: current team agents (or public agents when no team)
    primary_agents = _ia_load(user_id, team)
    seen_sids = {a["session"] for a in primary_agents if a.get("session")}

    # Collect ALL session IDs from other sources (public + all teams,
    # excluding whichever was already loaded as the primary source).
    other_sources = []

    # Include public (non-team) agents if team mode is active
    if team:
        other_sources.append("")

    # Include all teams (skipping the current team if one is selected)
    teams_dir = os.path.join(root_dir, "data", "user_files", user_id, "teams")
    if os.path.isdir(teams_dir):
        try:
            other_sources.extend(
                d for d in os.listdir(teams_dir)
                if d != team and os.path.isdir(os.path.join(teams_dir, d))
            )
        except OSError:
            pass

    # Read raw JSON from other sources to capture every session ID
    # (including entries without "name" that _ia_load would skip).
    for src in other_sources:
        try:
            ia_file = _ia_path(user_id, src)
            if not os.path.isfile(ia_file):
                continue
            with open(ia_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, list):
                for entry in raw:
                    if isinstance(entry, dict):
                        sid = entry.get("session", "")
                        if sid:
                            seen_sids.add(sid)
        except (OSError, json.JSONDecodeError):
            pass

    return jsonify({
        "status": "success",
        "agents": primary_agents,
        "all_known_sessions": list(seen_sids),
    })


@app.route("/internal_agents", methods=["POST"])
def ia_add():
    """Add a new internal agent entry.
    Body: { "session": "<id>", "meta": { ... optional ... } }
    Query: ?team=<name>  (optional, for team-scoped storage)
    """
    user_id = session.get("user_id", "")
    team = request.args.get("team", "")
    body = request.get_json(force=True)
    sid = body.get("session")
    if not sid:
        return jsonify({"error": "missing required field: session"}), 400
    agents = _ia_load(user_id, team)
    # Prevent duplicate session
    if any(a["session"] == sid for a in agents):
        return jsonify({"error": f"session '{sid}' already exists"}), 409
    entry = {"session": sid, "meta": body.get("meta", {})}
    agents.append(entry)
    _ia_save(user_id, agents, team)
    return jsonify({"status": "success", "agent": entry})


@app.route("/internal_agents/<sid>", methods=["PUT", "PATCH"])
def ia_update(sid):
    """Update the meta of an existing internal agent.
    Body: { "meta": { ...fields to merge... } }
    """
    user_id = session.get("user_id", "")
    team = request.args.get("team", "")
    body = request.get_json(force=True)
    agents = _ia_load(user_id, team)
    for a in agents:
        if a["session"] == sid:
            new_meta = body.get("meta", {})
            if not isinstance(a.get("meta"), dict):
                a["meta"] = {}
            a["meta"].update(new_meta)
            _ia_save(user_id, agents, team)
            return jsonify({"status": "success", "agent": a})
    return jsonify({"error": "not found"}), 404


@app.route("/internal_agents/<sid>", methods=["DELETE"])
def ia_delete(sid):
    """Remove an internal agent entry by session id."""
    user_id = session.get("user_id", "")
    team = request.args.get("team", "")
    
    # Load current data
    agents = _ia_load(user_id, team)
    
    # Find the agent to get its name
    target_agent = None
    for a in agents:
        if a["session"] == sid:
            target_agent = a
            break
    
    if not target_agent:
        return jsonify({"error": "not found"}), 404
    
    # Remove from agents list
    agents = [a for a in agents if a["session"] != sid]
    
    # Save back (will update both files)
    _ia_save(user_id, agents, team)
    
    return jsonify({"status": "success", "deleted": sid})


@app.route("/teams", methods=["GET"])
def list_teams():
    """List all team names for the current user."""
    user_id = session.get("user_id", "")
    teams_dir = os.path.join(root_dir, "data", "user_files", user_id, "teams")
    teams = []
    if os.path.isdir(teams_dir):
        try:
            teams = [d for d in os.listdir(teams_dir) 
                    if os.path.isdir(os.path.join(teams_dir, d))]
        except OSError:
            pass
    return jsonify({"status": "success", "teams": sorted(teams)})


@app.route("/teams", methods=["POST"])
def create_team():
    """Create a new team folder."""
    user_id = session.get("user_id", "")
    
    body = request.get_json(force=True)
    team = body.get("team", "")
    
    if not team:
        return jsonify({"error": "team name is required"}), 400
    
    # Validate team name (prevent path traversal)
    if "/" in team or "\\" in team or team.startswith("."):
        return jsonify({"error": "Invalid team name"}), 400
    
    team_dir = os.path.join(root_dir, "data", "user_files", user_id, "teams", team)
    
    if os.path.exists(team_dir):
        return jsonify({"error": "Team already exists"}), 400
    
    try:
        os.makedirs(team_dir, exist_ok=True)
        return jsonify({
            "success": True,
            "message": f"Team '{team}' created",
            "hint": "Before adding OpenClaw agents to this team, run 'openclaw sessions' to verify the agent exists."
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/teams/<team_name>", methods=["DELETE"])
def delete_team(team_name):
    """Delete a team and all its internal agents, then remove the folder."""
    user_id = session.get("user_id", "")
    
    # Validate team name
    if not team_name or "/" in team_name or "\\" in team_name:
        return jsonify({"error": "Invalid team name"}), 400
    
    team_dir = os.path.join(root_dir, "data", "user_files", user_id, "teams", team_name)
    
    if not os.path.exists(team_dir):
        return jsonify({"error": "Team not found"}), 404
    
    try:
        # Step 1: Delete all internal agents from oasis server
        agents = _ia_load(user_id, team_name)
        deleted_count = 0
        errors = []
        
        for agent in agents:
            sid = agent.get("session")
            if sid:
                try:
                    r = requests.post(
                        LOCAL_DELETE_SESSION_URL,
                        json={"user_id": user_id, "session_id": sid},
                        headers={"X-Internal-Token": INTERNAL_TOKEN},
                        timeout=10
                    )
                    if r.status_code == 200:
                        deleted_count += 1
                    else:
                        errors.append(f"Failed to delete session {sid}")
                except Exception as e:
                    errors.append(f"Error deleting session {sid}: {str(e)}")
        
        # Step 2: Delete the team folder
        import shutil
        shutil.rmtree(team_dir)
        
        return jsonify({
            "success": True,
            "message": f"Team '{team_name}' deleted",
            "deleted_agents": deleted_count,
            "errors": errors
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/teams/<team_name>/members", methods=["GET"])
def get_team_members(team_name):
    """Get all members (agents) in a team.
    Returns list of agents with name, type (oasis/openclaw/ext), tag, and global_name.
    """
    user_id = session.get("user_id", "")
    
    # Validate team name
    if "/" in team_name or "\\" in team_name or team_name.startswith("."):
        return jsonify({"error": "Invalid team name"}), 400
    
    team_dir = os.path.join(root_dir, "data", "user_files", user_id, "teams", team_name)
    
    if not os.path.exists(team_dir):
        return jsonify({"error": "Team not found"}), 404
    
    try:
        members = []
        
        # Load internal agents (oasis type)
        internal_agents = _ia_load(user_id, team_name)
        for agent in internal_agents:
            meta = agent.get("meta", {})
            members.append({
                "name": meta.get("name", ""),
                "type": "oasis",
                "tag": meta.get("tag", ""),
                "global_name": agent.get("session", "")
            })
        
        # Load external agents from external_agents.json (all types including openclaw)
        ext_path = os.path.join(team_dir, "external_agents.json")
        if os.path.isfile(ext_path):
            with open(ext_path, "r", encoding="utf-8") as f:
                all_ext = json.load(f)
                if isinstance(all_ext, list):
                    for agent in all_ext:
                        members.append({
                            "name": agent.get("name", ""),
                            "type": "ext",
                            "tag": agent.get("tag", ""),
                            "global_name": agent.get("global_name", ""),
                            "meta": agent.get("meta", {})
                        })
        
        return jsonify({
            "status": "success",
            "team": team_name,
            "members": members
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/teams/<team_name>/members/external", methods=["POST"])
def add_external_member(team_name):
    """Add an external agent to the team's external_agents.json."""
    user_id = session.get("user_id", "")
    
    # Validate team name
    if "/" in team_name or "\\" in team_name or team_name.startswith("."):
        return jsonify({"error": "Invalid team name"}), 400
    
    team_dir = os.path.join(root_dir, "data", "user_files", user_id, "teams", team_name)
    
    if not os.path.exists(team_dir):
        return jsonify({"error": "Team not found"}), 404
    
    body = request.get_json(force=True)
    name = body.get("name", "")
    tag = body.get("tag", "")
    global_name = body.get("global_name", "")
    api_url = body.get("api_url", "")
    api_key = body.get("api_key", "")
    model = body.get("model", "")
    headers = body.get("headers", {})
    
    if not name or not global_name:
        return jsonify({"error": "name and global_name are required"}), 400
    
    try:
        ext_path = os.path.join(team_dir, "external_agents.json")
        
        # Load existing agents list
        agents = []
        if os.path.isfile(ext_path):
            with open(ext_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
                if isinstance(raw, list):
                    agents = raw
        
        # Check for duplicate global_name
        if any(a.get("global_name") == global_name for a in agents):
            return jsonify({"error": "Global name already exists"}), 409
        
        # Add new agent with all metadata
        new_agent = {
            "name": name,
            "tag": tag,
            "global_name": global_name,
            "meta": {
                "api_url": api_url,
                "api_key": api_key,
                "model": model,
                "headers": headers
            }
        }
        agents.append(new_agent)
        
        # Save back
        with open(ext_path, "w", encoding="utf-8") as f:
            json.dump(agents, f, ensure_ascii=False, indent=2)
        
        return jsonify({"status": "success", "agent": new_agent})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/teams/<team_name>/members/external", methods=["DELETE"])
def delete_external_member(team_name):
    """Delete an external agent from the team's external_agents.json."""
    user_id = session.get("user_id", "")
    
    # Validate team name
    if "/" in team_name or "\\" in team_name or team_name.startswith("."):
        return jsonify({"error": "Invalid team name"}), 400
    
    team_dir = os.path.join(root_dir, "data", "user_files", user_id, "teams", team_name)
    
    if not os.path.exists(team_dir):
        return jsonify({"error": "Team not found"}), 404
    
    body = request.get_json(force=True)
    global_name = body.get("global_name", "")
    
    if not global_name:
        return jsonify({"error": "global_name is required"}), 400
    
    try:
        ext_path = os.path.join(team_dir, "external_agents.json")
        
        # Load existing agents list
        agents = []
        if os.path.isfile(ext_path):
            with open(ext_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
                if isinstance(raw, list):
                    agents = raw
        
        # Find and remove the agent
        deleted = None
        new_agents = []
        for a in agents:
            if a.get("global_name") == global_name:
                deleted = a
            else:
                new_agents.append(a)
        
        if not deleted:
            return jsonify({"error": "Global name not found"}), 404
        
        # Save back
        with open(ext_path, "w", encoding="utf-8") as f:
            json.dump(new_agents, f, ensure_ascii=False, indent=2)
        
        return jsonify({"status": "success", "deleted": deleted})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/teams/<team_name>/members/external", methods=["PUT"])
def update_external_member(team_name):
    """Update an external agent in the team's external_agents.json.

    Identify the agent by its current global_name value, then apply any provided
    fields (name, tag, global_name, api_url, api_key, model, headers).
    Only the fields present in the request body are updated.
    """
    user_id = session.get("user_id", "")

    # Validate team name
    if "/" in team_name or "\\" in team_name or team_name.startswith("."):
        return jsonify({"error": "Invalid team name"}), 400

    team_dir = os.path.join(root_dir, "data", "user_files", user_id, "teams", team_name)

    if not os.path.exists(team_dir):
        return jsonify({"error": "Team not found"}), 404

    body = request.get_json(force=True)
    target_global_name = body.get("global_name", "")

    if not target_global_name:
        return jsonify({"error": "global_name is required to identify the agent"}), 400

    try:
        ext_path = os.path.join(team_dir, "external_agents.json")

        # Load existing agents list
        agents = []
        if os.path.isfile(ext_path):
            with open(ext_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
                if isinstance(raw, list):
                    agents = raw

        # Find the agent to update
        found = None
        for a in agents:
            if a.get("global_name") == target_global_name:
                found = a
                break

        if not found:
            return jsonify({"error": "Agent not found by global_name"}), 404

        # Apply partial updates from body
        if "new_name" in body:
            found["name"] = body["new_name"]
        if "new_tag" in body:
            found["tag"] = body["new_tag"]
        if "new_global_name" in body:
            # Check no duplicate
            new_gn = body["new_global_name"]
            if new_gn != target_global_name and any(a.get("global_name") == new_gn for a in agents):
                return jsonify({"error": "New global_name already exists"}), 409
            found["global_name"] = new_gn

        # Update meta fields (only if provided)
        meta = found.get("meta", {})
        if "api_url" in body:
            meta["api_url"] = body["api_url"]
        if "api_key" in body:
            meta["api_key"] = body["api_key"]
        if "model" in body:
            meta["model"] = body["model"]
        if "headers" in body:
            meta["headers"] = body["headers"]
        if meta:
            found["meta"] = meta

        # Save back
        with open(ext_path, "w", encoding="utf-8") as f:
            json.dump(agents, f, ensure_ascii=False, indent=2)

        return jsonify({"status": "success", "agent": found})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------------------
# Team-specific expert CRUD  (stored in {team_dir}/oasis_experts.json)
# ------------------------------------------------------------------

def _team_experts_path(user_id: str, team_name: str) -> str:
    """Return the oasis_experts.json path for a team."""
    return os.path.join(root_dir, "data", "user_files", user_id, "teams", team_name, "oasis_experts.json")


def _team_experts_load(user_id: str, team_name: str) -> list:
    """Load team-specific experts list."""
    path = _team_experts_path(user_id, team_name)
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _team_experts_save(user_id: str, team_name: str, experts: list) -> None:
    """Save team-specific experts list."""
    path = _team_experts_path(user_id, team_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(experts, f, ensure_ascii=False, indent=2)


@app.route("/teams/<team_name>/experts", methods=["GET"])
def get_team_experts(team_name):
    """List all custom experts defined for this team."""
    user_id = session.get("user_id", "")
    if "/" in team_name or "\\" in team_name or team_name.startswith("."):
        return jsonify({"error": "Invalid team name"}), 400
    team_dir = os.path.join(root_dir, "data", "user_files", user_id, "teams", team_name)
    if not os.path.exists(team_dir):
        return jsonify({"error": "Team not found"}), 404
    experts = _team_experts_load(user_id, team_name)
    return jsonify({"status": "success", "team": team_name, "experts": experts})


@app.route("/teams/<team_name>/experts", methods=["POST"])
def add_team_expert(team_name):
    """Add a custom expert to this team's expert pool."""
    user_id = session.get("user_id", "")
    if "/" in team_name or "\\" in team_name or team_name.startswith("."):
        return jsonify({"error": "Invalid team name"}), 400
    team_dir = os.path.join(root_dir, "data", "user_files", user_id, "teams", team_name)
    if not os.path.exists(team_dir):
        return jsonify({"error": "Team not found"}), 404

    body = request.get_json(force=True)
    name = (body.get("name") or "").strip()
    tag = (body.get("tag") or "").strip()
    persona = (body.get("persona") or "").strip()
    if not name or not tag or not persona:
        return jsonify({"error": "name, tag, and persona are required"}), 400

    expert = {
        "name": name,
        "tag": tag,
        "persona": persona,
        "temperature": float(body.get("temperature", 0.7)),
    }
    # Preserve optional fields
    for key in ("name_en", "category", "description"):
        if body.get(key):
            expert[key] = body[key]

    experts = _team_experts_load(user_id, team_name)
    if any(e["tag"] == tag for e in experts):
        return jsonify({"error": f"Tag \"{tag}\" already exists in this team"}), 409
    experts.append(expert)
    _team_experts_save(user_id, team_name, experts)
    return jsonify({"status": "success", "expert": expert})


@app.route("/teams/<team_name>/experts/<tag>", methods=["PUT"])
def update_team_expert(team_name, tag):
    """Update an existing team expert by tag."""
    user_id = session.get("user_id", "")
    if "/" in team_name or "\\" in team_name or team_name.startswith("."):
        return jsonify({"error": "Invalid team name"}), 400
    team_dir = os.path.join(root_dir, "data", "user_files", user_id, "teams", team_name)
    if not os.path.exists(team_dir):
        return jsonify({"error": "Team not found"}), 404

    body = request.get_json(force=True)
    experts = _team_experts_load(user_id, team_name)
    for i, e in enumerate(experts):
        if e["tag"] == tag:
            name = (body.get("name") or e["name"]).strip()
            persona = (body.get("persona") or e["persona"]).strip()
            if not name or not persona:
                return jsonify({"error": "name and persona cannot be empty"}), 400
            updated = {
                "name": name,
                "tag": tag,
                "persona": persona,
                "temperature": float(body.get("temperature", e.get("temperature", 0.7))),
            }
            for key in ("name_en", "category", "description"):
                val = body.get(key, e.get(key))
                if val:
                    updated[key] = val
            experts[i] = updated
            _team_experts_save(user_id, team_name, experts)
            return jsonify({"status": "success", "expert": updated})
    return jsonify({"error": f"Expert tag \"{tag}\" not found"}), 404


@app.route("/teams/<team_name>/experts/<tag>", methods=["DELETE"])
def delete_team_expert(team_name, tag):
    """Delete a team expert by tag."""
    user_id = session.get("user_id", "")
    if "/" in team_name or "\\" in team_name or team_name.startswith("."):
        return jsonify({"error": "Invalid team name"}), 400
    team_dir = os.path.join(root_dir, "data", "user_files", user_id, "teams", team_name)
    if not os.path.exists(team_dir):
        return jsonify({"error": "Team not found"}), 404

    experts = _team_experts_load(user_id, team_name)
    for i, e in enumerate(experts):
        if e["tag"] == tag:
            deleted = experts.pop(i)
            _team_experts_save(user_id, team_name, experts)
            return jsonify({"status": "success", "deleted": deleted})
    return jsonify({"error": f"Expert tag \"{tag}\" not found"}), 404


@app.route("/teams/snapshot/preview", methods=["POST"])
def preview_team_snapshot():
    """Preview what would be exported in a team snapshot.
    Returns a JSON summary of all exportable sections:
    agents (internal_agents), personas (oasis_experts),
    skills (openclaw workspace/managed skills), cron jobs, workflows (yaml files).
    """
    user_id = session.get("user_id", "")

    body = request.get_json(force=True)
    team = body.get("team", "")

    if not team:
        return jsonify({"error": "team is required"}), 400

    team_dir = os.path.join(root_dir, "data", "user_files", user_id, "teams", team)

    if not os.path.exists(team_dir):
        return jsonify({"error": "Team not found"}), 404

    result = {"team": team, "sections": {}}

    # --- 1. agents (internal_agents.json) ---
    ia_path = os.path.join(team_dir, "internal_agents.json")
    agents_info = []
    if os.path.exists(ia_path):
        try:
            with open(ia_path, "r", encoding="utf-8") as f:
                ia_list = json.load(f)
            if isinstance(ia_list, list):
                for item in ia_list:
                    agents_info.append({
                        "name": item.get("name", "?"),
                        "tag": item.get("tag", ""),
                    })
        except Exception:
            pass
    result["sections"]["agents"] = {"count": len(agents_info), "items": agents_info}

    # --- 2. personas (oasis_experts.json) ---
    experts_path = os.path.join(team_dir, "oasis_experts.json")
    personas_info = []
    if os.path.exists(experts_path):
        try:
            with open(experts_path, "r", encoding="utf-8") as f:
                experts_list = json.load(f)
            if isinstance(experts_list, list):
                for item in experts_list:
                    personas_info.append({
                        "tag": item.get("tag", "?"),
                        "name": item.get("name", item.get("tag", "?")),
                    })
        except Exception:
            pass
    result["sections"]["personas"] = {"count": len(personas_info), "items": personas_info}

    # --- 3. external agents (external_agents.json — openclaw agents) ---
    ext_path = os.path.join(team_dir, "external_agents.json")
    openclaw_info = []
    ext_data = []
    if os.path.exists(ext_path):
        try:
            with open(ext_path, "r", encoding="utf-8") as f:
                ext_data = json.load(f)
            if isinstance(ext_data, list):
                for entry in ext_data:
                    if entry.get("tag") == "openclaw":
                        openclaw_info.append({
                            "name": entry.get("name", "?"),
                            "global_name": entry.get("global_name", ""),
                        })
        except Exception:
            pass

    # --- 4. skills (workspace + managed) for openclaw agents ---
    skills_info = []
    managed_skills_info = []  # [{"name": ..., "source": "managed"}]
    if isinstance(ext_data, list):
        managed_collected = False
        for entry in ext_data:
            if entry.get("tag") != "openclaw":
                continue
            short_name = entry.get("name", "")
            agent_name = entry.get("global_name", "") or short_name
            try:
                r = requests.get(
                    f"{OASIS_BASE_URL}/sessions/openclaw/agent-detail",
                    params={"name": agent_name},
                    timeout=15,
                )
                resp = r.json()
                if not resp.get("ok"):
                    continue
                agent_detail = resp.get("agent", {})
                workspace = agent_detail.get("workspace", "")

                # List workspace skill directory names only (no file contents)
                ws_skill_names = []
                if workspace:
                    ws_skills_dir = os.path.join(os.path.expanduser(workspace), "skills")
                    if os.path.isdir(ws_skills_dir):
                        for item in sorted(os.listdir(ws_skills_dir)):
                            if os.path.isdir(os.path.join(ws_skills_dir, item)):
                                ws_skill_names.append(item)

                skills_info.append({
                    "agent": short_name,
                    "skills": ws_skill_names,
                })

                # Collect managed skills (once)
                if not managed_collected:
                    user_skills = resp.get("user_skills", [])
                    for sk in user_skills:
                        if sk.get("source") == "managed" and sk.get("name"):
                            managed_skills_info.append({"name": sk["name"]})
                    managed_collected = True
            except Exception:
                skills_info.append({"agent": short_name, "skills": []})
    result["sections"]["skills"] = {
        "agents": openclaw_info,
        "details": skills_info,
        "managed": managed_skills_info,
    }

    # --- 5. cron jobs ---
    cron_info = {}
    if isinstance(ext_data, list):
        for entry in ext_data:
            if entry.get("tag") != "openclaw":
                continue
            short_name = entry.get("name", "")
            agent_name = entry.get("global_name", "") or short_name
            cron_jobs, cron_error = get_agent_cron_jobs(agent_name)
            if cron_error:
                cron_info[short_name] = {"count": 0, "error": cron_error}
            elif cron_jobs:
                cron_info[short_name] = {
                    "count": len(cron_jobs),
                    "items": [{"name": j.get("name", "?"), "schedule": j.get("schedule", "")} for j in cron_jobs],
                }
            else:
                cron_info[short_name] = {"count": 0}
    result["sections"]["cron"] = cron_info

    # --- 6. workflows (yaml files) ---
    yaml_files = []
    for root_path, dirs, files in os.walk(team_dir):
        for file in files:
            if file.endswith(('.yaml', '.yml')):
                file_path = os.path.join(root_path, file)
                rel_path = os.path.relpath(file_path, team_dir)
                yaml_files.append(rel_path)
    result["sections"]["workflows"] = {"count": len(yaml_files), "items": yaml_files}

    return jsonify(result)


@app.route("/teams/snapshot/download", methods=["POST"])
def download_team_snapshot():
    """Download a compressed snapshot of the team's data.
    Includes: internal_agents.json, oasis_experts.json, 
             external_agents.json, all .yaml files,
             and skill folders (workspace + managed) for each openclaw agent.
    Note: session fields inside internal_agents.json are excluded (private).
    Supports selective export via 'include' field in request body.
    Simple mode: {"team": "...", "include": {"agents": true, "personas": true, "skills": true, "cron": true, "workflows": true}}
    Granular mode for skills — select per-agent and per-skill:
      {"include": {"skills": {"AgentName": ["Skill1", "Skill2"], "Agent2": true}}}
    If 'include' is omitted, all sections are exported.
    """
    user_id = session.get("user_id", "")
    
    body = request.get_json(force=True)
    team = body.get("team", "")
    include = body.get("include", None)  # Selective export filter
    
    if not team:
        return jsonify({"error": "team is required"}), 400
    
    # Build include flags — default all True if 'include' not provided
    def _inc(section):
        if include is None:
            return True
        val = include.get(section, False)
        # For skills: value can be True/False or a dict for granular selection
        if isinstance(val, dict):
            return True  # dict means granular selection — section is included
        return bool(val)

    def _inc_agent_skill(agent_short_name, skill_name=None):
        """Check if a specific agent's skill should be included.
        include.skills can be: True, False, or {"AgentName": true/[skill_list], ...}
        """
        if include is None:
            return True
        skills_val = include.get("skills", False)
        if skills_val is True:
            return True
        if skills_val is False or not skills_val:
            return False
        if isinstance(skills_val, dict):
            agent_val = skills_val.get(agent_short_name, False)
            if agent_val is True:
                return True
            if agent_val is False or not agent_val:
                return False
            if isinstance(agent_val, list):
                if skill_name is None:
                    return True  # agent is selected, check skills individually
                return skill_name in agent_val
        return True

    team_dir = os.path.join(root_dir, "data", "user_files", user_id, "teams", team)
    
    if not os.path.exists(team_dir):
        return jsonify({"error": "Team not found"}), 404
    
    import zipfile
    import io
    import shutil
    from datetime import datetime
    
    try:
        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add internal agent JSON files (session fields stripped for privacy)
            # Map file → section name for selective export
            json_file_section = {
                "internal_agents.json": "agents",
                "oasis_experts.json": "personas",
                "external_agents.json": "skills",  # external_agents always included when skills or cron are selected
            }
            json_files = list(json_file_section.keys())
            
            for json_file in json_files:
                section = json_file_section[json_file]
                # external_agents.json is needed when skills OR cron are exported
                if json_file == "external_agents.json":
                    if not (_inc("skills") or _inc("cron")):
                        continue
                elif not _inc(section):
                    continue
                file_path = os.path.join(team_dir, json_file)
                if os.path.exists(file_path):
                    if json_file == "internal_agents.json":
                        # Strip session field before packing — it will be
                        # regenerated on restore (like global_name in external_agents).
                        try:
                            with open(file_path, "r", encoding="utf-8") as _iaf:
                                ia_list = json.load(_iaf)
                            if isinstance(ia_list, list):
                                cleaned = []
                                for item in ia_list:
                                    c = dict(item)
                                    c.pop("session", None)
                                    cleaned.append(c)
                                ia_list = cleaned
                            zipf.writestr(json_file, json.dumps(ia_list, ensure_ascii=False, indent=2))
                        except Exception:
                            zipf.write(file_path, json_file)
                    elif json_file == "external_agents.json":
                        # Strip global_name field before packing — it will be
                        # regenerated from team+name on restore.
                        try:
                            with open(file_path, "r", encoding="utf-8") as _ef:
                                ext_list = json.load(_ef)
                            if isinstance(ext_list, list):
                                cleaned = []
                                for item in ext_list:
                                    c = dict(item)
                                    c.pop("global_name", None)
                                    cleaned.append(c)
                                ext_list = cleaned
                            zipf.writestr(json_file, json.dumps(ext_list, ensure_ascii=False, indent=2))
                        except Exception:
                            zipf.write(file_path, json_file)
                    else:
                        zipf.write(file_path, json_file)
            
            # Add all .yaml files (workflows)
            if _inc("workflows"):
                for root_path, dirs, files in os.walk(team_dir):
                    for file in files:
                        if file.endswith(('.yaml', '.yml')):
                            file_path = os.path.join(root_path, file)
                            # Use relative path inside zip
                            rel_path = os.path.relpath(file_path, team_dir)
                            zipf.write(file_path, rel_path)

            # --- Add skill folders and cron jobs for each openclaw agent ---
            ext_path = os.path.join(team_dir, "external_agents.json")
            managed_skills_added = False
            cron_jobs_data = {}  # {short_name: [cron_jobs]}

            if (_inc("skills") or _inc("cron")) and os.path.exists(ext_path):
                try:
                    with open(ext_path, "r", encoding="utf-8") as f:
                        ext_data = json.load(f)
                except Exception:
                    ext_data = []

                if isinstance(ext_data, list):
                    for entry in ext_data:
                        if entry.get("tag") != "openclaw":
                            continue
                        short_name = entry.get("name", "")
                        # Use global_name as agentId for cron jobs
                        agent_name = entry.get("global_name", "") or short_name
                        
                        # Fetch agent detail from oasis server to get workspace path and user_skills
                        if _inc("skills") and _inc_agent_skill(short_name):
                            try:
                                r = requests.get(
                                    f"{OASIS_BASE_URL}/sessions/openclaw/agent-detail",
                                    params={"name": agent_name},
                                    timeout=15,
                                )
                                resp = r.json()
                                if resp.get("ok"):
                                    agent_detail = resp.get("agent", {})
                                    workspace = agent_detail.get("workspace", "")

                                    # 1. Add workspace skills to zip: skills/{short_name}/
                                    if workspace:
                                        ws_skills_dir = os.path.join(os.path.expanduser(workspace), "skills")
                                        if os.path.isdir(ws_skills_dir):
                                            for item in os.listdir(ws_skills_dir):
                                                item_path = os.path.join(ws_skills_dir, item)
                                                if not os.path.isdir(item_path):
                                                    continue
                                                # Check if this specific skill is selected
                                                if not _inc_agent_skill(short_name, item):
                                                    continue
                                                for dirpath, dirnames, filenames in os.walk(item_path):
                                                    for fname in filenames:
                                                        abs_path = os.path.join(dirpath, fname)
                                                        rel_in_skills = os.path.relpath(abs_path, ws_skills_dir)
                                                        zip_path = os.path.join("skills", short_name, rel_in_skills)
                                                        zipf.write(abs_path, zip_path)

                                    # 2. Add managed skills to zip: skills/_managed/ (once)
                                    if not managed_skills_added:
                                        user_skills = resp.get("user_skills", [])
                                        for sk in user_skills:
                                            if sk.get("source") == "managed" and sk.get("path"):
                                                sk_path = sk["path"]
                                                if os.path.isdir(sk_path):
                                                    for dirpath, dirnames, filenames in os.walk(sk_path):
                                                        for fname in filenames:
                                                            abs_path = os.path.join(dirpath, fname)
                                                            rel_in_sk = os.path.relpath(abs_path, sk_path)
                                                            zip_path = os.path.join("skills", "_managed", sk["name"], rel_in_sk)
                                                            zipf.write(abs_path, zip_path)
                                    managed_skills_added = True

                            except Exception:
                                pass
                        
                        # 3. Fetch cron jobs for this agent using global_name as agentId
                        if _inc("cron"):
                            cron_jobs, cron_error = get_agent_cron_jobs(agent_name)
                            if cron_error:
                                print(f"[Warning] Failed to fetch cron jobs for {agent_name}: {cron_error}")
                                cron_jobs = []
                            if cron_jobs:
                                cron_jobs_data[short_name] = cron_jobs
            
            # Save cron jobs to zip: cron_jobs.json
            if cron_jobs_data:
                zipf.writestr("cron_jobs.json", json.dumps(cron_jobs_data, ensure_ascii=False, indent=2))
        
        zip_buffer.seek(0)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"team_{team}_snapshot_{timestamp}.zip"
        
        return Response(
            zip_buffer.read(),
            mimetype='application/zip',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/teams/snapshot/upload", methods=["POST"])
def upload_team_snapshot():
    """Upload and restore a team snapshot from a zip file.
    Extracts to the team folder and recreates internal agents.
    """
    user_id = session.get("user_id", "")
    
    # Get team name from form data
    team = request.form.get("team", "")
    if not team:
        return jsonify({"error": "team is required"}), 400
    
    # Validate team name
    if "/" in team or "\\" in team or team.startswith("."):
        return jsonify({"error": "Invalid team name"}), 400
    
    # Check for uploaded file
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not file.filename.endswith('.zip'):
        return jsonify({"error": "File must be a .zip file"}), 400
    
    team_dir = os.path.join(root_dir, "data", "user_files", user_id, "teams", team)
    
    # Create team directory if it doesn't exist
    os.makedirs(team_dir, exist_ok=True)
    
    import zipfile
    import tempfile
    import shutil
    
    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
            # Extract zip file
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            # Validate zip contents (only allow safe file types)
            for file_info in zip_ref.infolist():
                filename = file_info.filename
                # Skip directories and absolute paths
                if filename.endswith('/') or filename.startswith('/'):
                    continue
                # Allow files inside skills/ directory (any file type)
                # For other files, only allow json and yaml
                if not filename.startswith('skills/'):
                    if not (filename.endswith(('.json', '.yaml', '.yml'))):
                        return jsonify({"error": f"Invalid file type in zip: {filename}"}), 400
                # Preserve relative directory structure from zip
                target_path = os.path.join(team_dir, filename)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with zip_ref.open(file_info) as source, open(target_path, 'wb') as target:
                    target.write(source.read())
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # After extraction, recreate agents from internal_agents.json
        # The file is a flat list: [{"name": ..., "tag": ...}, ...]
        # Session field was stripped during download; generate new ones.
        internal_agents_path = os.path.join(team_dir, "internal_agents.json")

        agents_data = []  # Format: [{"session": "sid", "meta": {...}}, ...]

        if os.path.exists(internal_agents_path):
            with open(internal_agents_path, "r", encoding="utf-8") as f:
                agents_list = json.load(f)
            if not isinstance(agents_list, list):
                agents_list = []

            # Generate new session_id for each agent and build agents_data
            import time, random
            for agent_meta in agents_list:
                if not isinstance(agent_meta, dict) or "name" not in agent_meta:
                    continue

                # Generate session_id (same format as frontend: base36 timestamp + random)
                def to_base36(n):
                    """Convert number to base36 string (same as JavaScript's toString(36))"""
                    if n == 0:
                        return '0'
                    digits = '0123456789abcdefghijklmnopqrstuvwxyz'
                    result = ''
                    while n > 0:
                        result = digits[n % 36] + result
                        n //= 36
                    return result

                timestamp_ms = int(time.time() * 1000)
                random_part = random.randint(0, 36**4 - 1)  # 4-digit base36 random
                new_sid = to_base36(timestamp_ms) + to_base36(random_part).zfill(4)

                # Strip any leftover session from meta (shouldn't be there, but safe)
                meta_clean = {k: v for k, v in agent_meta.items() if k != "session"}
                agents_data.append({
                    "session": new_sid,
                    "meta": meta_clean
                })

        # Save agents using _ia_save (writes unified internal_agents.json)
        if agents_data:
            _ia_save(user_id, agents_data, team)
        
        # After internal agents, also restore OpenClaw agents from external_agents.json
        openclaw_agents_path = os.path.join(team_dir, "external_agents.json")
        openclaw_restored = 0
        openclaw_errors = []
        
        # Paths for extracted skill folders
        extracted_skills_dir = os.path.join(team_dir, "skills")
        managed_skills_src = os.path.join(extracted_skills_dir, "_managed")

        if os.path.exists(openclaw_agents_path):
            try:
                with open(openclaw_agents_path, "r", encoding="utf-8") as f:
                    openclaw_data = json.load(f)
                
                if isinstance(openclaw_data, list) and openclaw_data:
                    for agent_entry in openclaw_data:
                        if agent_entry.get("tag") != "openclaw":
                            continue
                        short_name = agent_entry.get("name", "")
                        agent_snapshot = agent_entry
                        # Generate new global_name from team + "_" + name
                        target_name = team + "_" + short_name
                        try:
                            r = requests.post(
                                f"{OASIS_BASE_URL}/sessions/openclaw/agent-restore",
                                json={
                                    "agent_name": target_name,
                                    "config": agent_snapshot.get("config", {}),
                                    "workspace_files": agent_snapshot.get("workspace_files", {}),
                                },
                                timeout=60,
                            )
                            result = r.json()
                            if result.get("ok"):
                                openclaw_restored += 1
                                # Update global_name in JSON to reflect the new agent name
                                agent_entry["global_name"] = target_name
                                # --- Restore skill folders into agent workspace ---
                                workspace = result.get("workspace", "")
                                if workspace:
                                    ws_skills_target = os.path.join(os.path.expanduser(workspace), "skills")
                                    agent_skills_src = os.path.join(extracted_skills_dir, short_name)

                                    # Clear existing skills folder and rebuild
                                    if os.path.isdir(ws_skills_target):
                                        shutil.rmtree(ws_skills_target)
                                    os.makedirs(ws_skills_target, exist_ok=True)

                                    # Copy workspace skills from snapshot
                                    if os.path.isdir(agent_skills_src):
                                        for item in os.listdir(agent_skills_src):
                                            src_item = os.path.join(agent_skills_src, item)
                                            dst_item = os.path.join(ws_skills_target, item)
                                            if os.path.isdir(src_item):
                                                shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
                                            else:
                                                shutil.copy2(src_item, dst_item)

                                    # Merge managed skills into the same workspace skills folder
                                    if os.path.isdir(managed_skills_src):
                                        for item in os.listdir(managed_skills_src):
                                            src_item = os.path.join(managed_skills_src, item)
                                            dst_item = os.path.join(ws_skills_target, item)
                                            if os.path.isdir(src_item) and not os.path.exists(dst_item):
                                                shutil.copytree(src_item, dst_item)
                                            elif os.path.isdir(src_item):
                                                shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
                            else:
                                openclaw_errors.append(
                                    f"{target_name}: {result.get('errors', result.get('error', 'failed'))}"
                                )
                        except Exception as e:
                            openclaw_errors.append(f"{target_name}: {e}")
                    # Persist updated global_names back to external_agents.json
                    try:
                        with open(openclaw_agents_path, "w", encoding="utf-8") as f:
                            json.dump(openclaw_data, f, ensure_ascii=False, indent=2)
                    except Exception:
                        pass

            except Exception as e:
                openclaw_errors.append(f"Failed to read external_agents.json: {e}")

        # Clean up extracted skills directory from team folder (it was only temporary)
        if os.path.isdir(extracted_skills_dir):
            shutil.rmtree(extracted_skills_dir, ignore_errors=True)
        
        # --- Restore cron jobs from cron_jobs.json ---
        cron_jobs_path = os.path.join(team_dir, "cron_jobs.json")
        cron_restored_total = 0
        cron_errors = []
        
        if os.path.exists(cron_jobs_path):
            try:
                with open(cron_jobs_path, "r", encoding="utf-8") as f:
                    cron_jobs_data = json.load(f)
                
                if isinstance(cron_jobs_data, dict):
                    # cron_jobs_data format: {short_name: [cron_jobs]}
                    for short_name, cron_jobs in cron_jobs_data.items():
                        if not isinstance(cron_jobs, list) or not cron_jobs:
                            continue
                        # Use new global_name as target_agent
                        target_name = team + "_" + short_name
                        restored, errors = restore_cron_jobs(cron_jobs, target_name)
                        cron_restored_total += restored
                        if errors:
                            cron_errors.extend([f"{short_name}: {e}" for e in errors])
                
                # Clean up cron_jobs.json from team folder (it was only temporary)
                os.unlink(cron_jobs_path)
            except Exception as e:
                cron_errors.append(f"Failed to restore cron jobs: {e}")
        
        msg_parts = [f"Team '{team}' snapshot uploaded"]
        msg_parts.append(f"{len(agents_data)} internal agents restored")
        if openclaw_restored > 0 or openclaw_errors:
            msg_parts.append(f"{openclaw_restored} OpenClaw agents restored")
        if cron_restored_total > 0 or cron_errors:
            msg_parts.append(f"{cron_restored_total} cron jobs restored")
        
        return jsonify({
            "success": True,
            "message": ", ".join(msg_parts),
            "openclaw_errors": openclaw_errors if openclaw_errors else None,
            "cron_errors": cron_errors if cron_errors else None,
        })
    except zipfile.BadZipFile:
        return jsonify({"error": "Invalid zip file"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/teams/snapshot/import_from_url", methods=["POST"])
def import_team_from_url():
    """Download a zip from a remote URL, then delegate to /teams/snapshot/upload."""
    import io
    data = request.get_json(force=True, silent=True) or {}
    url = (data.get("url") or "").strip()
    team = (data.get("team") or "").strip()

    if not url:
        return jsonify({"error": "url is required"}), 400
    if not team:
        return jsonify({"error": "team is required"}), 400

    # Download the zip
    try:
        dl = requests.get(url, timeout=120, stream=True, allow_redirects=True)
        dl.raise_for_status()
    except Exception as e:
        return jsonify({"error": f"下载失败: {e}"}), 502

    zip_bytes = dl.content

    # Internally call the existing upload endpoint
    with app.test_client() as c:
        # Copy session cookie so upload_team_snapshot sees the same user
        with c.session_transaction() as sess:
            sess.update(dict(session))
        resp = c.post("/teams/snapshot/upload", data={
            "team": team,
            "file": (io.BytesIO(zip_bytes), "team_import.zip"),
        }, content_type="multipart/form-data")

    return resp.data, resp.status_code, dict(resp.headers)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT_FRONTEND", "51209")), debug=False, threaded=True)

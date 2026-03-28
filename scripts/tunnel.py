#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare Tunnel 公网部署脚本
- 自动检测平台（Linux/macOS/Windows + amd64/arm64）
- 提示用户手动安装 cloudflared
- 启动隧道：前端 Web UI
- 打印公网地址
"""

import os
import sys
import re
import signal
import platform
import subprocess
import shutil
import threading
import atexit
from dotenv import load_dotenv

IS_WINDOWS = platform.system().lower() == "windows"

# ── 项目路径 ──────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

BIN_DIR = os.path.join(PROJECT_ROOT, "bin")
os.makedirs(BIN_DIR, exist_ok=True)

CLOUDFLARED_PATH = os.path.join(BIN_DIR, "cloudflared.exe" if IS_WINDOWS else "cloudflared")
ENV_PATH = os.path.join(PROJECT_ROOT, "config", ".env")
PIDFILE_PATH = os.path.join(PROJECT_ROOT, ".tunnel.pid")

# ── 加载配置 ──────────────────────────────────────────────
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, "config", ".env"))
PORT_FRONTEND = os.getenv("PORT_FRONTEND", "51209")

# ── 全局进程引用 ──────────────────────────────────────────
tunnel_procs = []
tunnel_urls = {}  # {"frontend": "https://..."}
urls_lock = threading.Lock()
all_tunnels_ready = threading.Event()
expected_tunnels = 1
_cleanup_done = False


def detect_platform():
    """检测当前平台，返回 (os_name, arch)"""
    os_name = platform.system().lower()   # linux / darwin / windows
    machine = platform.machine().lower()  # x86_64 / aarch64 / arm64 / amd64

    if os_name not in ("linux", "darwin", "windows"):
        print(f"❌ 不支持的操作系统: {os_name}")
        sys.exit(1)

    if machine in ("x86_64", "amd64"):
        arch = "amd64"
    elif machine in ("aarch64", "arm64"):
        arch = "arm64"
    else:
        print(f"❌ 不支持的架构: {machine}")
        sys.exit(1)

    return os_name, arch


def download_url(os_name, arch):
    """根据平台返回 cloudflared 下载 URL"""
    base = "https://github.com/cloudflare/cloudflared/releases/latest/download"
    if os_name == "linux":
        return f"{base}/cloudflared-linux-{arch}"
    elif os_name == "darwin":
        return f"{base}/cloudflared-darwin-{arch}.tgz"
    elif os_name == "windows":
        return f"{base}/cloudflared-windows-{arch}.exe"
    return None


def _download_cloudflared():
    """自动下载 cloudflared 到 bin/ 目录，返回路径或 None"""
    os_name, arch = detect_platform()
    url = download_url(os_name, arch)
    if not url:
        return None

    print(f"📥 正在自动下载 cloudflared ({os_name}/{arch})...")
    print(f"   URL: {url}")

    try:
        import urllib.request
        if os_name == "darwin":
            # macOS: 下载 tgz 并解压
            tgz_path = os.path.join(BIN_DIR, "cloudflared.tgz")
            urllib.request.urlretrieve(url, tgz_path)
            import tarfile
            with tarfile.open(tgz_path, "r:gz") as tar:
                tar.extract("cloudflared", BIN_DIR)
            os.remove(tgz_path)
        else:
            # Linux/Windows: 直接下载二进制
            urllib.request.urlretrieve(url, CLOUDFLARED_PATH)

        if not IS_WINDOWS:
            os.chmod(CLOUDFLARED_PATH, 0o755)
        print(f"✅ cloudflared 已下载到: {CLOUDFLARED_PATH}")
        return CLOUDFLARED_PATH
    except Exception as e:
        print(f"❌ 自动下载失败: {e}")
        return None


def get_cloudflared_install_guide(os_name, arch):
    """返回 cloudflared 手动安装指南"""
    url = download_url(os_name, arch)

    if os_name == "linux":
        return f"""
📥 手动安装 cloudflared (Linux {arch}):

1. 下载二进制文件:
   wget {url} -O cloudflared

2. 添加执行权限:
   chmod +x cloudflared

3. 移动到系统路径或项目 bin/ 目录:
   sudo mv cloudflared /usr/local/bin/  # 系统路径
   或
   mv cloudflared {BIN_DIR}/           # 项目路径
"""
    elif os_name == "darwin":
        return f"""
📥 手动安装 cloudflared (macOS {arch}):

1. 下载压缩包:
   curl -L {url} -o cloudflared.tgz

2. 解压:
   tar -xzf cloudflared.tgz

3. 移动到系统路径或项目 bin/ 目录:
   sudo mv cloudflared /usr/local/bin/  # 系统路径
   或
   mv cloudflared {BIN_DIR}/           # 项目路径

4. 清理压缩包:
   rm cloudflared.tgz
"""
    elif os_name == "windows":
        return f"""
📥 手动安装 cloudflared (Windows {arch}):

1. 下载可执行文件:
   {url}

2. 将下载的 .exe 文件移动到项目 bin\\ 目录:
   move cloudflared-windows-{arch}.exe {BIN_DIR}\\cloudflared.exe

3. 或添加到系统 PATH 中
"""
    return ""


def ensure_cloudflared():
    """确保 cloudflared 可用：优先查找已有 → 自动下载 → 失败则打印手动指南"""
    # 优先检查 bin/ 目录
    if os.path.isfile(CLOUDFLARED_PATH) and (IS_WINDOWS or os.access(CLOUDFLARED_PATH, os.X_OK)):
        print(f"✅ 已找到 cloudflared: {CLOUDFLARED_PATH}")
        return CLOUDFLARED_PATH

    # 检查系统 PATH
    system_cf = shutil.which("cloudflared")
    if system_cf:
        print(f"✅ 已找到系统 cloudflared: {system_cf}")
        return system_cf

    # 尝试自动下载
    path = _download_cloudflared()
    if path:
        return path

    # 下载失败，打印手动安装指南
    os_name, arch = detect_platform()
    print("❌ 未找到且自动下载失败")
    print("=" * 60)
    print(get_cloudflared_install_guide(os_name, arch))
    print("=" * 60)
    print("\n💡 安装完成后，请重新运行此脚本")
    sys.exit(1)


def _remove_pidfile():
    """安全删除 PID 文件"""
    try:
        if os.path.isfile(PIDFILE_PATH):
            os.remove(PIDFILE_PATH)
    except OSError:
        pass


def cleanup(signum=None, frame=None):
    """清理所有隧道进程、PID 文件和 PUBLIC_DOMAIN"""
    global _cleanup_done
    if _cleanup_done:
        return
    _cleanup_done = True

    for proc in tunnel_procs:
        if proc and proc.poll() is None:
            print(f"🛑 正在关闭隧道进程 (PID: {proc.pid})...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
    if tunnel_procs:
        print("✅ 所有隧道已关闭")

    # 清理 PID 文件
    _remove_pidfile()

    # 清理 PUBLIC_DOMAIN
    try:
        write_env_key("PUBLIC_DOMAIN", "")
        print("🧹 已清理 PUBLIC_DOMAIN")
    except Exception:
        pass

    if signum is not None:
        sys.exit(0)


def write_env_key(key: str, value: str):
    """Write or update a single key in config/.env"""
    env_file = ENV_PATH

    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = []

    key_found = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{key}=") or stripped.startswith(f"# {key}="):
            new_lines.append(f"{key}={value}\n")
            key_found = True
        else:
            new_lines.append(line)

    if not key_found:
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines.append("\n")
        new_lines.append(f"{key}={value}\n")

    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def write_domains_to_env():
    """Write all captured tunnel URLs to config/.env"""
    with urls_lock:
        if "frontend" in tunnel_urls:
            write_env_key("PUBLIC_DOMAIN", tunnel_urls["frontend"])
    print(f"📝 已将公网域名写入 {ENV_PATH}")


def run_tunnel(cf_bin: str, name: str, local_port: str, env_key: str):
    """
    Start a single cloudflared tunnel in a thread.
    Captures the public URL and stores it in tunnel_urls.
    """
    print(f"🌐 [{name}] 正在启动隧道 (转发 → 127.0.0.1:{local_port})...")

    popen_kwargs = dict(
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    # Windows: use CREATE_NO_WINDOW to avoid flashing a console
    if IS_WINDOWS:
        popen_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    proc = subprocess.Popen(
        [cf_bin, "tunnel", "--url", f"http://127.0.0.1:{local_port}"],
        **popen_kwargs,
    )
    tunnel_procs.append(proc)

    url_pattern = re.compile(r"(https://[a-zA-Z0-9-]+\.trycloudflare\.com)")
    public_url = None

    try:
        for line in proc.stdout:
            line = line.strip()
            if not public_url:
                match = url_pattern.search(line)
                if match:
                    public_url = match.group(1)
                    with urls_lock:
                        tunnel_urls[name] = public_url

                    print(f"  ✅ [{name}] 公网地址: {public_url}")

                    # Check if all tunnels are ready
                    with urls_lock:
                        if len(tunnel_urls) >= expected_tunnels:
                            all_tunnels_ready.set()

        # stdout closed => process exited
        proc.wait()
    except Exception as e:
        print(f"  ❌ [{name}] 隧道异常: {e}")


def start_tunnels():
    """启动所有 Cloudflare Tunnel 并等待公网地址就绪"""
    cf_bin = ensure_cloudflared()

    # 注册信号处理（Windows 只支持 SIGINT/SIGTERM 有限制，用 atexit 兜底）
    signal.signal(signal.SIGINT, cleanup)
    if not IS_WINDOWS:
        signal.signal(signal.SIGTERM, cleanup)
    atexit.register(cleanup)

    # Define tunnels: (name, local_port, env_key)
    tunnel_configs = [
        ("frontend", PORT_FRONTEND, "PUBLIC_DOMAIN"),
    ]

    # Start each tunnel in a background thread
    threads = []
    for name, port, env_key in tunnel_configs:
        t = threading.Thread(target=run_tunnel, args=(cf_bin, name, port, env_key), daemon=True)
        t.start()
        threads.append(t)

    # Wait for all tunnels to report their URLs (timeout 60s)
    print("\n⏳ 等待所有隧道就绪...")
    ready = all_tunnels_ready.wait(timeout=60)

    if ready:
        # Write all URLs to .env
        write_domains_to_env()

        print()
        print("============================================")
        print("  🎉 公网部署成功！")
        with urls_lock:
            if "frontend" in tunnel_urls:
                print(f"  🌍 前端地址: {tunnel_urls['frontend']}")
        print("  按 Ctrl+C 关闭所有隧道")
        print("============================================")
        print()
    else:
        print("⚠️  部分隧道未能在 60 秒内就绪")
        with urls_lock:
            if tunnel_urls:
                write_domains_to_env()
                for name, url in tunnel_urls.items():
                    print(f"  ✅ [{name}] {url}")
            else:
                print("❌ 所有隧道均启动失败")
                cleanup()
                sys.exit(1)

    # Keep main thread alive, waiting for tunnel threads
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == "__main__":
    start_tunnels()

import hashlib
import json
import os

from logging_utils import get_logger

logger = get_logger("user_auth")


def load_users(users_path: str) -> dict:
    """Load username -> password-hash mapping from users.json."""
    if not os.path.exists(users_path):
        logger.warning("未找到用户配置文件 %s，请先运行 python tools/gen_password.py 创建用户", users_path)
        return {}
    with open(users_path, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_password(users_path: str, username: str, password: str) -> bool:
    """Verify plaintext password by comparing SHA-256 hash."""
    users = load_users(users_path)
    if username not in users:
        return False
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pw_hash == users[username]

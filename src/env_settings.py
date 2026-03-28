from typing import Iterable


SETTINGS_WHITELIST = [
    "LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL", "LLM_PROVIDER", "LLM_VISION_SUPPORT",
    "TTS_MODEL", "TTS_VOICE",
    "PORT_AGENT", "PORT_SCHEDULER", "PORT_OASIS", "PORT_FRONTEND",
    "OASIS_BASE_URL",
    "TELEGRAM_BOT_TOKEN", "TELEGRAM_ALLOWED_USERS",
    "QQ_APP_ID", "QQ_BOT_SECRET", "QQ_BOT_USERNAME",
    "PUBLIC_DOMAIN",
    "OPENAI_STANDARD_MODE",
    "ALLOWED_COMMANDS", "EXEC_TIMEOUT", "MAX_OUTPUT_LENGTH",
]

MASK_FIELDS = {"LLM_API_KEY", "TELEGRAM_BOT_TOKEN", "QQ_BOT_SECRET"}
FULL_MASK_PATTERNS = ("KEY", "TOKEN", "SECRET", "PASSWORD")


def _iter_env_items(env_path: str):
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                if key:
                    yield key, val.strip()
    except FileNotFoundError:
        return


def read_env_settings(env_path: str, allowed_keys: Iterable[str] | None = None) -> dict:
    """Read whitelisted keys from .env."""
    allowed = set(allowed_keys if allowed_keys is not None else SETTINGS_WHITELIST)
    settings = {}
    for key, val in _iter_env_items(env_path):
        if key in allowed:
            settings[key] = val
    return settings


def read_env_all(env_path: str) -> dict:
    """Read all non-comment key-value pairs from .env."""
    settings = {}
    for key, val in _iter_env_items(env_path):
        settings[key] = val
    return settings


def mask_sensitive(settings: dict, masked_fields: set[str] | None = None) -> dict:
    """Mask selected sensitive fields."""
    fields = masked_fields if masked_fields is not None else MASK_FIELDS
    masked = {}
    for key, val in settings.items():
        if key in fields and val and len(val) > 8:
            masked[key] = val[:4] + "****" + val[-4:]
        else:
            masked[key] = val
    return masked


def mask_all_sensitive(settings: dict, patterns: tuple[str, ...] | None = None) -> dict:
    """Mask any key whose name contains sensitive patterns."""
    mask_patterns = patterns if patterns is not None else FULL_MASK_PATTERNS
    masked = {}
    for key, val in settings.items():
        if any(p in key.upper() for p in mask_patterns) and val and len(val) > 8:
            masked[key] = val[:4] + "****" + val[-4:]
        else:
            masked[key] = val
    return masked


def write_env_settings(env_path: str, updates: dict):
    """Merge updates into .env; update existing keys and append missing ones."""
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    updated_keys = set()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.partition("=")[0].strip()
            if key in updates:
                new_lines.append(f"{key}={updates[key]}\n")
                updated_keys.add(key)
                continue
        new_lines.append(line)

    for key, val in updates.items():
        if key not in updated_keys:
            new_lines.append(f"{key}={val}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def filter_whitelisted_updates(
    incoming: dict,
    allowed_keys: Iterable[str] | None = None,
) -> dict:
    """Keep only whitelisted keys and skip masked placeholder values."""
    allowed = set(allowed_keys if allowed_keys is not None else SETTINGS_WHITELIST)
    filtered = {}
    for key, value in incoming.items():
        if key not in allowed:
            continue
        if "****" in str(value):
            continue
        filtered[key] = str(value)
    return filtered


def filter_updates_skip_mask(incoming: dict) -> dict:
    """Keep all keys except masked placeholder values."""
    updates = {}
    for key, value in incoming.items():
        if "****" in str(value):
            continue
        updates[key] = str(value)
    return updates

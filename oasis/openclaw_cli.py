import json
import os
import subprocess
from typing import Optional

from src.logging_utils import get_logger

logger = get_logger("oasis.openclaw_cli")


def _parse_first_json_document(raw: str):
    if not raw:
        return None
    idx = raw.find("{")
    arr_idx = raw.find("[")
    if idx < 0 or (arr_idx >= 0 and arr_idx < idx):
        idx = arr_idx
    if idx < 0:
        return None
    try:
        decoder = json.JSONDecoder()
        data, _ = decoder.raw_decode(raw[idx:])
        return data
    except json.JSONDecodeError:
        return None


def fetch_openclaw_full_config(openclaw_bin: Optional[str]) -> Optional[dict]:
    if not openclaw_bin:
        return None
    try:
        result = subprocess.run(
            [openclaw_bin, "config", "get", "agents"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            logger.warning("openclaw config get agents failed: %s", result.stderr.strip()[:200])
            return None
        return _parse_first_json_document(result.stdout)
    except (json.JSONDecodeError, subprocess.TimeoutExpired, Exception) as e:
        logger.warning("openclaw config get agents parse error: %s", e)
        return None


def build_agent_detail(agent_cfg: dict, defaults: dict) -> dict:
    agent_id = agent_cfg.get("id", "")
    tools_cfg = agent_cfg.get("tools", {})
    profile = tools_cfg.get("profile", "")
    also_allow = tools_cfg.get("alsoAllow", tools_cfg.get("allow", []))
    deny = tools_cfg.get("deny", [])

    skills_cfg = agent_cfg.get("skills", None)
    if skills_cfg == "null" or skills_cfg == "":
        skills_cfg = None
    skills_all = not isinstance(skills_cfg, list)

    return {
        "id": agent_id,
        "name": agent_cfg.get("name", agent_id),
        "workspace": agent_cfg.get("workspace", defaults.get("workspace", "")),
        "agentDir": agent_cfg.get("agentDir", ""),
        "is_default": agent_cfg.get("isDefault", False),
        "model": (
            agent_cfg.get("model", {})
            if isinstance(agent_cfg.get("model"), dict)
            else {"primary": agent_cfg.get("model", "")}
        ),
        "tools": {
            "profile": profile,
            "alsoAllow": also_allow if isinstance(also_allow, list) else [],
            "deny": deny if isinstance(deny, list) else [],
        },
        "skills": skills_cfg if isinstance(skills_cfg, list) else [],
        "skills_all": skills_all,
    }


def get_openclaw_default_workspace(openclaw_bin: Optional[str]) -> Optional[str]:
    if not openclaw_bin:
        return None
    try:
        result = subprocess.run(
            [openclaw_bin, "config", "get", "agents.defaults.workspace"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return None
        ws = result.stdout.strip()
        return os.path.expanduser(ws) if ws else None
    except Exception:
        return None


def get_openclaw_workspace_path(openclaw_bin: Optional[str]) -> Optional[str]:
    if openclaw_bin:
        try:
            result = subprocess.run(
                [openclaw_bin, "config", "get", "agents.defaults.workspace"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.splitlines():
                    line = line.strip()
                    if line and os.path.sep in line:
                        return line
        except Exception:
            pass

    default_paths = [
        os.path.expanduser("~/.openclaw/workspace"),
        os.path.expanduser("~/.moltbot/workspace"),
        "/projects/.openclaw/workspace",
        "/projects/.moltbot/workspace",
    ]
    for path in default_paths:
        if os.path.isdir(path):
            return path
    return None


def fetch_openclaw_channels(openclaw_bin: Optional[str]) -> Optional[dict]:
    if not openclaw_bin:
        return None
    try:
        result = subprocess.run(
            [openclaw_bin, "channels", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=45,
        )
        if result.returncode != 0:
            logger.warning("openclaw channels list failed: %s", result.stderr.strip()[:200])
            return None
        return _parse_first_json_document(result.stdout)
    except (json.JSONDecodeError, subprocess.TimeoutExpired, Exception) as e:
        logger.warning("openclaw channels parse error: %s", e)
        return None

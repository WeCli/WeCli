#!/usr/bin/env python3
"""Bulk rename TeamBot→WeBot and remaining TeamClaw→WeCli across the repo.

Steps:
  1. git mv all teambot-named files to webot equivalents
  2. Replace content in all text files
  3. Fix SVG IDs (teamclaw* → wecli*)
  4. Fix packaging references (TeamBot.exe → WeBot.exe, com.teambot → com.webot)
"""

import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Directories to skip
SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", ".mypy_cache", ".pytest_cache"}

# File extensions to treat as text
TEXT_EXTS = {
    ".py", ".sh", ".ps1", ".md", ".json", ".yaml", ".yml", ".html", ".js",
    ".css", ".txt", ".env", ".example", ".mjs", ".svg", ".toml", ".cfg",
    ".ini", ".gitignore", ".spec",
}

# ── Step 1: File renames ──────────────────────────────────────

def find_files_to_rename() -> list[tuple[Path, Path]]:
    """Find all files/dirs containing 'teambot' in their name."""
    renames: list[tuple[Path, Path]] = []

    self_path = Path(__file__).resolve()
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Prune skip dirs
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        root_path = Path(root)
        for name in files:
            if "teambot" in name.lower():
                old = root_path / name
                # Don't rename this script itself
                if old.resolve() == self_path:
                    continue
                new_name = name.replace("teambot", "webot").replace("TeamBot", "WeBot")
                new = root_path / new_name
                renames.append((old, new))

    # Also check for teambot in directory names (docs/teambot-*)
    for root, dirs, _files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        root_path = Path(root)
        for d in list(dirs):
            if "teambot" in d.lower():
                old = root_path / d
                new_name = d.replace("teambot", "webot").replace("TeamBot", "WeBot")
                new = root_path / new_name
                renames.append((old, new))

    return renames


def git_mv(old: Path, new: Path) -> bool:
    """Rename file using git mv."""
    if not old.exists():
        return False
    try:
        subprocess.run(
            ["git", "mv", str(old), str(new)],
            cwd=PROJECT_ROOT, check=True, capture_output=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  git mv failed: {old.name} → {new.name}: {e.stderr.decode()}", file=sys.stderr)
        return False


# ── Step 2: Content replacement ───────────────────────────────

# Ordered replacements (longer patterns first to avoid partial matches)
REPLACEMENTS = [
    # TeamBot variants
    ("TEAMBOT_RUNTIME_ARTIFACTS_ENABLED", "WEBOT_RUNTIME_ARTIFACTS_ENABLED"),
    ("TEAMBOT_HEADLESS", "WEBOT_HEADLESS"),
    ("TEAMBOT_SUBAGENT_TOOLS", "WEBOT_SUBAGENT_TOOLS"),
    ("TEAMBOT_RUNTIME_TOOLS", "WEBOT_RUNTIME_TOOLS"),
    ("front_teambot_routes", "front_webot_routes"),
    ("register_teambot_routes", "register_webot_routes"),
    ("proxy_teambot_subagents", "proxy_webot_subagents"),
    ("proxy_teambot_subagent_history", "proxy_webot_subagent_history"),
    ("proxy_teambot_subagent_cancel", "proxy_webot_subagent_cancel"),
    ("proxy_teambot_tool_policy", "proxy_webot_tool_policy"),
    ("proxy_teambot_session_runtime", "proxy_webot_session_runtime"),
    ("proxy_teambot_session_mode", "proxy_webot_session_mode"),
    ("create_teambot_router", "create_webot_router"),
    ("teambot_workflow_presets", "webot_workflow_presets"),
    ("teambot_runtime_store", "webot_runtime_store"),
    ("teambot_permission_context", "webot_permission_context"),
    ("teambot_workspace", "webot_workspace"),
    ("teambot_subagents", "webot_subagents"),
    ("teambot_orchestration", "webot_orchestration"),
    ("teambot_buddy_voice", "webot_buddy_voice"),
    ("teambot_profiles", "webot_profiles"),
    ("teambot_context", "webot_context"),
    ("teambot_runtime", "webot_runtime"),
    ("teambot_service", "webot_service"),
    ("teambot_routes", "webot_routes"),
    ("teambot_memory", "webot_memory"),
    ("teambot_bridge", "webot_bridge"),
    ("teambot_models", "webot_models"),
    ("teambot_policy", "webot_policy"),
    ("teambot_buddy", "webot_buddy"),
    ("teambot_voice", "webot_voice"),
    ("mcp_teambot", "mcp_webot"),
    ("teambot-agent-runtime", "webot-agent-runtime"),
    ("teambot-claude-gap-analysis", "webot-claude-gap-analysis"),
    # Generic teambot patterns (after specific ones)
    ("TeamBot_01", "WeBot_01"),
    ("TeamBot.exe", "WeBot.exe"),
    ("TeamBot.app", "WeBot.app"),
    ("com.teambot.app", "com.webot.app"),
    ("TeamBot", "WeBot"),
    ("teambot", "webot"),
    ("TEAMBOT", "WEBOT"),
    # Remaining TeamClaw
    ("teamclawShadow", "wecliShadow"),
    ("teamclawBlade", "wecliBlade"),
    ("teamclawNode", "wecliNode"),
    ("teamclawOrbit", "wecliOrbit"),
    ("teamclaw-oasis", "wecli-oasis"),
    ("TeamClaw", "WeCli"),
    ("teamclaw", "wecli"),
]


def is_text_file(path: Path) -> bool:
    """Check if a file should be treated as text."""
    if path.suffix in TEXT_EXTS:
        return True
    if path.name in {".gitignore", ".env", ".env.example", "Makefile", "Dockerfile"}:
        return True
    return False


def replace_in_file(path: Path, dry_run: bool = False) -> int:
    """Replace all old names in a single file. Returns number of replacements."""
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return 0

    original = content
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)

    if content == original:
        return 0

    count = sum(
        original.count(old) for old, _new in REPLACEMENTS if old in original
    )

    if not dry_run:
        path.write_text(content, encoding="utf-8")

    return count


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("🔍 DRY RUN — no changes will be made\n")

    # Step 1: File renames
    print("📁 Step 1: Renaming files...")
    renames = find_files_to_rename()
    # Sort by path depth (deeper first) so we rename files before dirs
    renames.sort(key=lambda x: -len(x[0].parts))

    renamed = 0
    for old, new in renames:
        rel_old = old.relative_to(PROJECT_ROOT)
        rel_new = new.relative_to(PROJECT_ROOT)
        if dry_run:
            print(f"  {rel_old} → {rel_new}")
            renamed += 1
        else:
            if git_mv(old, new):
                print(f"  ✅ {rel_old} → {rel_new}")
                renamed += 1
    print(f"  📊 {renamed} files renamed\n")

    # Step 2: Content replacement
    print("📝 Step 2: Replacing content...")
    files_changed = 0
    total_replacements = 0

    self_path = Path(__file__).resolve()
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        root_path = Path(root)

        for name in files:
            fpath = root_path / name
            # Don't modify this script itself
            if fpath.resolve() == self_path:
                continue
            if not is_text_file(fpath):
                continue

            count = replace_in_file(fpath, dry_run=dry_run)
            if count > 0:
                rel = fpath.relative_to(PROJECT_ROOT)
                print(f"  {'🔍' if dry_run else '✅'} {rel} ({count} replacements)")
                files_changed += 1
                total_replacements += count

    print(f"\n  📊 {total_replacements} replacements in {files_changed} files")

    print(f"\n{'🔍 DRY RUN complete' if dry_run else '✅ All done!'}")


if __name__ == "__main__":
    main()

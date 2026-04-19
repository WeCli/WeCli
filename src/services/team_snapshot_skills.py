from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

from webot.skills import USER_FILES_DIR, _rebuild_index, list_skills


SNAPSHOT_SKILLS_DIR = "clawcross_user_skills"
SNAPSHOT_MANIFEST = "clawcross_skills_manifest.json"


def _user_root(user_id: str) -> Path:
    return Path(USER_FILES_DIR) / (user_id or "anonymous")


def _user_skills_dir(user_id: str) -> Path:
    return _user_root(user_id) / "skills"


def _build_manifest_payload(user_id: str) -> list[dict[str, Any]]:
    base = _user_skills_dir(user_id)
    payload: list[dict[str, Any]] = []
    for item in list_skills(user_id):
        skill_path = Path(item.get("path") or "")
        rel_file = ""
        if skill_path.is_file():
            try:
                rel_file = str(skill_path.relative_to(base))
            except ValueError:
                rel_file = skill_path.name
        payload.append(
            {
                "name": item.get("name", ""),
                "description": item.get("description", ""),
                "file": rel_file,
                "category": item.get("category", ""),
            }
        )
    return payload


def add_user_skills_to_zip(zipf: Any, user_id: str) -> int:
    base = _user_skills_dir(user_id)
    if not base.is_dir():
        return 0

    file_count = 0
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(base)
        zipf.write(path, os.path.join(SNAPSHOT_SKILLS_DIR, str(rel)))
        file_count += 1

    manifest = _build_manifest_payload(user_id)
    zipf.writestr(
        SNAPSHOT_MANIFEST,
        json.dumps({"skills": manifest}, ensure_ascii=False, indent=2),
    )
    return file_count


def restore_user_skills_from_team_dir(team_dir: str | Path, user_id: str) -> dict[str, Any]:
    team_path = Path(team_dir)
    extracted = team_path / SNAPSHOT_SKILLS_DIR
    target = _user_skills_dir(user_id)
    restored_files = 0
    restored_skill_dirs = 0

    if extracted.is_dir():
        target.mkdir(parents=True, exist_ok=True)
        for item in sorted(extracted.iterdir()):
            dst = target / item.name
            if item.is_dir():
                if dst.exists():
                    shutil.rmtree(dst, ignore_errors=True)
                shutil.copytree(item, dst)
                restored_skill_dirs += 1
                restored_files += sum(1 for p in dst.rglob("*") if p.is_file())
            elif item.is_file():
                shutil.copy2(item, dst)
                restored_files += 1
        shutil.rmtree(extracted, ignore_errors=True)

    manifest_src = team_path / SNAPSHOT_MANIFEST
    manifest_dst = _user_root(user_id) / "skills_manifest.json"
    manifest_written = False
    if manifest_src.is_file():
        manifest_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(manifest_src, manifest_dst)
        manifest_src.unlink(missing_ok=True)
        manifest_written = True
    elif restored_skill_dirs or restored_files:
        manifest_dst.parent.mkdir(parents=True, exist_ok=True)
        manifest_dst.write_text(
            json.dumps({"skills": _build_manifest_payload(user_id)}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        manifest_written = True

    if restored_skill_dirs or restored_files:
        _rebuild_index(user_id)

    return {
        "restored_skill_dirs": restored_skill_dirs,
        "restored_files": restored_files,
        "manifest_written": manifest_written,
    }

"""
WeBot memory/Kairos/auto-dream helpers.

This remains file-first for portability, but now adds:
- optional Chroma-backed local vector indexing
- mempalace-style halls/rooms/type metadata
- layered recall (identity / essential / focus / deep search)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
from typing import Any

from utils.chroma_memory import (
    chroma_status,
    list_unique_metadata_values,
    query_text,
    upsert_text,
)
from webot.profiles import slugify
from webot.runtime_store import save_memory_state
from webot.workspace import resolve_session_workspace


PROJECT_ROOT = Path(__file__).resolve().parents[2]
USER_FILES_DIR = PROJECT_ROOT / "data" / "user_files"
_MAX_INDEX_LINES = 200
_MAX_INDEX_BYTES = 25_000
_MEMORY_COLLECTION = "webot_memory"

_HALL_BY_TYPE = {
    "decision": "facts",
    "fact": "facts",
    "project": "facts",
    "reference": "advice",
    "feedback": "advice",
    "preference": "preferences",
    "milestone": "discoveries",
    "dream": "discoveries",
    "problem": "events",
    "log": "events",
    "note": "events",
}
_TYPE_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "decision": (
        re.compile(r"\b(decided|decision|went with|pick(ed)?|choose|switch(ed)? to|trade-?off|because)\b", re.I),
    ),
    "preference": (
        re.compile(r"\b(prefer|always use|never use|style|convention|habit)\b", re.I),
    ),
    "milestone": (
        re.compile(r"\b(finally|worked|works|breakthrough|shipped|launched|solved|fixed)\b", re.I),
    ),
    "problem": (
        re.compile(r"\b(error|bug|issue|problem|failed|crash|broken|regression|root cause)\b", re.I),
    ),
    "fact": (
        re.compile(r"\b(require(s|d)?|uses?|is configured|status|fact|constraint|workspace)\b", re.I),
    ),
}
_TYPE_PRIORITY = {
    "decision": 5,
    "preference": 4,
    "milestone": 4,
    "problem": 4,
    "fact": 3,
    "reference": 3,
    "feedback": 3,
    "project": 2,
    "dream": 2,
    "note": 2,
    "log": 1,
}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _user_root(user_id: str) -> Path:
    root = USER_FILES_DIR / (user_id or "anonymous")
    root.mkdir(parents=True, exist_ok=True)
    return root


def _project_slug(user_id: str, session_id: str) -> str:
    workspace = resolve_session_workspace(user_id, session_id)
    source = str(workspace.cwd or workspace.root or session_id or "default")
    return slugify(source.replace("/", "-"), "default-project") or "default-project"


def _semantic_store_path(user_id: str, session_id: str) -> Path:
    return get_memory_dir(user_id, session_id) / "semantic"


def _sync_runtime_store(
    user_id: str,
    session_id: str,
    *,
    dream_status: str = "idle",
    active_run_id: str = "",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    local_state = _load_state(user_id, session_id)
    chroma = chroma_status()
    payload = {
        "enabled": True,
        "project_slug": _project_slug(user_id, session_id),
        "memory_dir": str(get_memory_dir(user_id, session_id)),
        "index_path": str(_index_path(user_id, session_id)),
        "daily_log_path": str(_daily_log_path(user_id, session_id)),
        "vector_store_path": str(_semantic_store_path(user_id, session_id)),
        "search_provider": chroma["provider"],
        "semantic_enabled": bool(chroma["available"]),
        "kairos_enabled": bool(local_state.get("kairos_enabled", False)),
        "last_dream_at": str(local_state.get("last_dream_at") or ""),
        "log_entries_since_dream": int(local_state.get("log_entries_since_dream") or 0),
    }
    merged_metadata = {
        "search_provider": chroma["provider"],
        "semantic_enabled": bool(chroma["available"]),
        **(metadata or {}),
    }
    save_memory_state(
        user_id,
        session_id,
        project_slug=payload["project_slug"],
        memory_dir=payload["memory_dir"],
        index_path=payload["index_path"],
        kairos_enabled=payload["kairos_enabled"],
        dream_status=dream_status,
        active_run_id=active_run_id,
        last_dream_at=payload["last_dream_at"],
        daily_log_path=payload["daily_log_path"],
        metadata=merged_metadata,
    )
    return payload


def get_memory_dir(user_id: str, session_id: str) -> Path:
    root = _user_root(user_id) / "projects" / _project_slug(user_id, session_id) / "memory"
    (root / "entries").mkdir(parents=True, exist_ok=True)
    (root / "logs").mkdir(parents=True, exist_ok=True)
    return root


def _state_path(user_id: str, session_id: str) -> Path:
    return get_memory_dir(user_id, session_id) / "state.json"


def _index_path(user_id: str, session_id: str) -> Path:
    return get_memory_dir(user_id, session_id) / "MEMORY.md"


def _daily_log_path(user_id: str, session_id: str, at: datetime | None = None) -> Path:
    current = at or _utc_now()
    log_root = get_memory_dir(user_id, session_id) / "logs" / current.strftime("%Y") / current.strftime("%m")
    log_root.mkdir(parents=True, exist_ok=True)
    return log_root / f"{current.strftime('%Y-%m-%d')}.md"


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9_]{3,}", (text or "").lower())}


def _load_state(user_id: str, session_id: str) -> dict[str, Any]:
    path = _state_path(user_id, session_id)
    if not path.is_file():
        return {"kairos_enabled": False, "last_dream_at": "", "log_entries_since_dream": 0, "updated_at": ""}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        raw = {}
    if not isinstance(raw, dict):
        raw = {}
    return {
        "kairos_enabled": bool(raw.get("kairos_enabled", False)),
        "last_dream_at": str(raw.get("last_dream_at") or ""),
        "log_entries_since_dream": int(raw.get("log_entries_since_dream") or 0),
        "updated_at": str(raw.get("updated_at") or ""),
    }


def _save_state(user_id: str, session_id: str, state: dict[str, Any]) -> dict[str, Any]:
    payload = dict(state)
    payload["updated_at"] = _utc_now().isoformat()
    _state_path(user_id, session_id).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def _normalize_memory_type(
    *,
    name: str,
    description: str,
    content: str,
    mem_type: str,
) -> str:
    explicit = slugify(mem_type, "project").replace("-", "_")
    if explicit and explicit not in {"project", "note", "memory"}:
        return explicit
    haystack = f"{name}\n{description}\n{content}"
    for memory_type, patterns in _TYPE_PATTERNS.items():
        if any(pattern.search(haystack) for pattern in patterns):
            return memory_type
    if explicit and explicit not in {"", "project", "memory"}:
        return explicit
    return "project" if explicit in {"", "project", "memory"} else explicit


def _normalize_room(name: str, description: str, room: str, memory_type: str) -> str:
    if room:
        return slugify(room, "general") or "general"
    source = description or name or memory_type or "general"
    return slugify(source, "general") or "general"


def _normalize_hall(memory_type: str, hall: str) -> str:
    if hall:
        return slugify(hall, "events") or "events"
    return _HALL_BY_TYPE.get(memory_type, "events")


def _build_taxonomy(
    *,
    name: str,
    description: str,
    content: str,
    mem_type: str = "project",
    room: str = "",
    hall: str = "",
) -> dict[str, str]:
    memory_type = _normalize_memory_type(name=name, description=description, content=content, mem_type=mem_type)
    return {
        "type": memory_type,
        "hall": _normalize_hall(memory_type, hall),
        "room": _normalize_room(name, description, room, memory_type),
    }


def _semantic_where(*, hall: str = "", room: str = "", source_kind: str = "") -> dict[str, Any] | None:
    filters = []
    if hall:
        filters.append({"hall": hall})
    if room:
        filters.append({"room": room})
    if source_kind:
        filters.append({"source_kind": source_kind})
    if not filters:
        return None
    if len(filters) == 1:
        return filters[0]
    return {"$and": filters}


def _index_memory_document(
    user_id: str,
    session_id: str,
    *,
    record_id: str,
    title: str,
    content: str,
    taxonomy: dict[str, str],
    description: str = "",
    source_kind: str = "entry",
    file_path: str = "",
    created_at: str = "",
    metadata: dict[str, Any] | None = None,
) -> bool:
    document = "\n".join(
        [
            f"Title: {title}",
            f"Description: {description}",
            f"Type: {taxonomy['type']}",
            f"Hall: {taxonomy['hall']}",
            f"Room: {taxonomy['room']}",
            "",
            content.strip(),
        ]
    ).strip()
    payload = {
        "user_id": user_id,
        "session_id": session_id,
        "project_slug": _project_slug(user_id, session_id),
        "title": title[:200],
        "description": description[:300],
        "memory_type": taxonomy["type"],
        "hall": taxonomy["hall"],
        "room": taxonomy["room"],
        "source_kind": source_kind,
        "file_path": file_path,
        "created_at": created_at or _utc_now().isoformat(),
        **(metadata or {}),
    }
    return upsert_text(
        path=_semantic_store_path(user_id, session_id),
        collection_name=_MEMORY_COLLECTION,
        record_id=record_id,
        document=document,
        metadata=payload,
    )


def _parse_frontmatter(text: str, path: Path) -> dict[str, Any]:
    lines = text.splitlines()
    meta: dict[str, str] = {"name": path.stem, "description": "", "type": "project", "hall": "events", "room": "general"}
    if lines[:1] != ["---"]:
        return meta
    for line in lines[1:20]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta


def _memory_priority(item: dict[str, Any]) -> int:
    memory_type = str(item.get("type") or "")
    return _TYPE_PRIORITY.get(memory_type, 1)


def set_kairos_mode(user_id: str, session_id: str, enabled: bool, reason: str = "") -> dict[str, Any]:
    state = _load_state(user_id, session_id)
    state["kairos_enabled"] = bool(enabled)
    if reason:
        state["reason"] = reason[:240]
    _save_state(user_id, session_id, state)
    return ensure_memory_state(user_id, session_id, kairos_enabled=enabled)


def _allocate_entry_path(entry_dir: Path, name: str) -> Path:
    base_slug = slugify(name, "memory")
    candidate = entry_dir / f"{base_slug}.md"
    if not candidate.exists():
        return candidate
    stamp = _utc_now().strftime("%Y%m%d-%H%M%S")
    counter = 1
    while True:
        suffix = f"{stamp}-{counter}" if counter > 1 else stamp
        candidate = entry_dir / f"{base_slug}-{suffix}.md"
        if not candidate.exists():
            return candidate
        counter += 1


def append_memory_entry(
    user_id: str,
    session_id: str,
    *,
    name: str,
    content: str,
    mem_type: str = "project",
    description: str = "",
    room: str = "",
    hall: str = "",
    source_kind: str = "entry",
) -> Path:
    from webot.memory_guard import scan_memory_content

    scan = scan_memory_content(content)
    if not scan.safe:
        import logging

        logging.getLogger("memory").warning(
            "Memory injection blocked for user=%s: %s", user_id, "; ".join(scan.violations)
        )
        raise ValueError(f"Memory content blocked by security scan: {'; '.join(scan.violations)}")

    taxonomy = _build_taxonomy(
        name=name,
        description=description,
        content=content,
        mem_type=mem_type,
        room=room,
        hall=hall,
    )
    memory_dir = get_memory_dir(user_id, session_id)
    path = _allocate_entry_path(memory_dir / "entries", name)
    created_at = _utc_now().isoformat()
    frontmatter = [
        "---",
        f"name: {name.strip() or 'memory'}",
        f"description: {(description or name).strip()[:180]}",
        f"type: {taxonomy['type']}",
        f"hall: {taxonomy['hall']}",
        f"room: {taxonomy['room']}",
        f"source_kind: {source_kind}",
        "---",
        "",
        content.strip(),
        "",
    ]
    path.write_text("\n".join(frontmatter), encoding="utf-8")
    refresh_memory_index(user_id, session_id)
    _index_memory_document(
        user_id,
        session_id,
        record_id=f"entry:{path.stem}",
        title=name.strip() or "memory",
        content=content,
        taxonomy=taxonomy,
        description=(description or name).strip()[:180],
        source_kind=source_kind,
        file_path=str(path),
        created_at=created_at,
    )
    return path


def list_memory_entries(user_id: str, session_id: str) -> list[dict[str, Any]]:
    entry_dir = get_memory_dir(user_id, session_id) / "entries"
    rows: list[dict[str, Any]] = []
    for path in sorted(entry_dir.glob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True):
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = _parse_frontmatter(text, path)
        taxonomy = _build_taxonomy(
            name=meta.get("name", path.stem),
            description=meta.get("description", ""),
            content=text,
            mem_type=meta.get("type", "project"),
            room=meta.get("room", ""),
            hall=meta.get("hall", ""),
        )
        rows.append(
            {
                "id": f"entry:{path.stem}",
                "name": meta.get("name", path.stem),
                "description": meta.get("description", ""),
                "type": taxonomy["type"],
                "hall": taxonomy["hall"],
                "room": taxonomy["room"],
                "source_kind": meta.get("source_kind", "entry"),
                "path": str(path),
                "updated_at": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
                "snippet": text[:280].replace("\n", " "),
            }
        )
    return rows


def refresh_memory_index(user_id: str, session_id: str) -> Path:
    entries = list_memory_entries(user_id, session_id)
    lines = ["# MEMORY", "", "Known memory entries for this project:", ""]
    for item in entries[:80]:
        lines.append(
            f"- `{item['name']}` [{item['type']}/{item['hall']}/{item['room']}] - "
            f"{item['description'] or item['snippet'][:120]}"
        )
    text = "\n".join(lines[:_MAX_INDEX_LINES])
    encoded = text.encode("utf-8")
    if len(encoded) > _MAX_INDEX_BYTES:
        text = encoded[:_MAX_INDEX_BYTES].decode("utf-8", errors="ignore")
    path = _index_path(user_id, session_id)
    path.write_text(text, encoding="utf-8")
    return path


def append_daily_log(user_id: str, session_id: str, title: str, body: str) -> Path:
    path = _daily_log_path(user_id, session_id)
    timestamp = _utc_now().strftime("%H:%M:%S")
    block = f"\n## {timestamp} {title.strip()[:120]}\n\n{body.strip()[:2000]}\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(block)
    state = _load_state(user_id, session_id)
    state["log_entries_since_dream"] = int(state.get("log_entries_since_dream") or 0) + 1
    _save_state(user_id, session_id, state)
    taxonomy = _build_taxonomy(
        name=title.strip()[:120] or "log",
        description="Daily log entry",
        content=body,
        mem_type="log",
        room=title,
        hall="events",
    )
    _index_memory_document(
        user_id,
        session_id,
        record_id=f"log:{path.stem}:{slugify(timestamp + '-' + title, 'log')}",
        title=title.strip()[:120] or "log",
        content=body.strip()[:2000],
        taxonomy=taxonomy,
        description="Daily log entry",
        source_kind="log",
        file_path=str(path),
    )
    _sync_runtime_store(user_id, session_id, metadata={"last_log_title": title[:120]})
    return path


def _fallback_memory_search(
    user_id: str,
    session_id: str,
    query: str,
    *,
    hall: str = "",
    room: str = "",
    limit: int = 5,
) -> list[dict[str, Any]]:
    query_tokens = _tokenize(query)
    ranked: list[tuple[int, dict[str, Any]]] = []
    for item in list_memory_entries(user_id, session_id):
        if hall and item.get("hall") != hall:
            continue
        if room and item.get("room") != room:
            continue
        haystack = " ".join([item["name"], item["description"], item["snippet"]])
        score = len(query_tokens & _tokenize(haystack))
        if score > 0 or not query_tokens:
            enriched = dict(item)
            enriched["similarity"] = float(score)
            ranked.append((score, enriched))
    ranked.sort(key=lambda pair: (pair[0], _memory_priority(pair[1]), pair[1]["updated_at"]), reverse=True)
    return [item for _, item in ranked[: max(1, limit)]]


def search_memory_entries(
    user_id: str,
    session_id: str,
    query: str,
    *,
    hall: str = "",
    room: str = "",
    limit: int = 5,
) -> list[dict[str, Any]]:
    if not str(query or "").strip():
        entries = list_memory_entries(user_id, session_id)
        entries.sort(key=lambda item: (_memory_priority(item), item.get("updated_at", "")), reverse=True)
        return entries[: max(1, limit)]
    semantic_results = query_text(
        path=_semantic_store_path(user_id, session_id),
        collection_name=_MEMORY_COLLECTION,
        query=query,
        limit=limit,
        where=_semantic_where(hall=hall, room=room),
    )
    if semantic_results:
        normalized: list[dict[str, Any]] = []
        for item in semantic_results:
            metadata = item.get("metadata") or {}
            normalized.append(
                {
                    "id": item.get("id", ""),
                    "name": metadata.get("title") or metadata.get("room") or metadata.get("source_kind") or "memory",
                    "description": metadata.get("description", ""),
                    "type": metadata.get("memory_type", "project"),
                    "hall": metadata.get("hall", "events"),
                    "room": metadata.get("room", "general"),
                    "source_kind": metadata.get("source_kind", "entry"),
                    "path": metadata.get("file_path", ""),
                    "snippet": str(item.get("document") or "")[:320].replace("\n", " "),
                    "similarity": float(item.get("similarity", 0.0)),
                    "updated_at": metadata.get("created_at", ""),
                }
            )
        return normalized
    return _fallback_memory_search(user_id, session_id, query, hall=hall, room=room, limit=limit)


def recall_relevant_memories(user_id: str, session_id: str, query: str, limit: int = 5) -> list[dict[str, Any]]:
    return search_memory_entries(user_id, session_id, query, limit=limit)


def _memory_layers(user_id: str, session_id: str, query: str = "") -> dict[str, Any]:
    entries = list_memory_entries(user_id, session_id)
    essential = sorted(entries, key=lambda item: (_memory_priority(item), item.get("updated_at", "")), reverse=True)[:6]
    focus = search_memory_entries(user_id, session_id, query, limit=5) if query else essential[:3]
    chroma = chroma_status()
    halls = list_unique_metadata_values(
        path=_semantic_store_path(user_id, session_id),
        collection_name=_MEMORY_COLLECTION,
        field="hall",
    ) or sorted({str(item.get("hall") or "events") for item in entries})
    rooms = list_unique_metadata_values(
        path=_semantic_store_path(user_id, session_id),
        collection_name=_MEMORY_COLLECTION,
        field="room",
    ) or sorted({str(item.get("room") or "general") for item in entries})
    identity = {
        "project_slug": _project_slug(user_id, session_id),
        "summary": f"{len(entries)} entry files · {len(halls)} halls · {len(rooms)} rooms · provider={chroma['provider']}",
    }
    return {
        "identity": identity,
        "essential": essential,
        "focus": focus,
        "deep": search_memory_entries(user_id, session_id, query, limit=8) if query else [],
        "halls": halls[:24],
        "rooms": rooms[:32],
        "search_provider": chroma["provider"],
        "search_enabled": bool(chroma["available"]),
    }


def get_memory_state(user_id: str, session_id: str, query: str = "") -> dict[str, Any]:
    state = _load_state(user_id, session_id)
    entries = list_memory_entries(user_id, session_id)
    relevant = search_memory_entries(user_id, session_id, query, limit=5) if query else entries[:5]
    layers = _memory_layers(user_id, session_id, query=query)
    chroma = chroma_status()
    return {
        "enabled": True,
        "project_slug": _project_slug(user_id, session_id),
        "memory_dir": str(get_memory_dir(user_id, session_id)),
        "index_path": str(_index_path(user_id, session_id)),
        "entry_count": len(entries),
        "relevant_entries": relevant,
        "daily_log_path": str(_daily_log_path(user_id, session_id)),
        "kairos_enabled": bool(state.get("kairos_enabled", False)),
        "last_dream_at": state.get("last_dream_at", ""),
        "log_entries_since_dream": int(state.get("log_entries_since_dream") or 0),
        "can_dream": should_run_auto_dream(user_id, session_id),
        "search_provider": chroma["provider"],
        "semantic_enabled": bool(chroma["available"]),
        "vector_store_path": str(_semantic_store_path(user_id, session_id)),
        "layers": layers,
        "halls": layers["halls"],
        "rooms": layers["rooms"],
    }


def ensure_memory_state(
    user_id: str,
    session_id: str,
    *,
    project_slug: str = "",
    kairos_enabled: bool | None = None,
) -> dict[str, Any]:
    del project_slug
    memory_dir = get_memory_dir(user_id, session_id)
    memory_dir.mkdir(parents=True, exist_ok=True)
    state = _load_state(user_id, session_id)
    if kairos_enabled is not None:
        state["kairos_enabled"] = bool(kairos_enabled)
        _save_state(user_id, session_id, state)
    refresh_memory_index(user_id, session_id)
    payload = get_memory_state(user_id, session_id)
    _sync_runtime_store(
        user_id,
        session_id,
        dream_status="idle",
        metadata={"source": "ensure_memory_state", "search_provider": payload["search_provider"]},
    )
    return payload


def reindex_memory_store(user_id: str, session_id: str) -> dict[str, Any]:
    indexed_entries = 0
    indexed_logs = 0
    for item in list_memory_entries(user_id, session_id):
        file_path = Path(item["path"])
        if not file_path.is_file():
            continue
        text = file_path.read_text(encoding="utf-8", errors="replace")
        taxonomy = {
            "type": item.get("type", "project"),
            "hall": item.get("hall", "events"),
            "room": item.get("room", "general"),
        }
        if _index_memory_document(
            user_id,
            session_id,
            record_id=item["id"],
            title=item.get("name", file_path.stem),
            content=text,
            taxonomy=taxonomy,
            description=item.get("description", ""),
            source_kind=item.get("source_kind", "entry"),
            file_path=str(file_path),
            created_at=item.get("updated_at", ""),
        ):
            indexed_entries += 1

    for log_path in sorted((get_memory_dir(user_id, session_id) / "logs").rglob("*.md")):
        text = log_path.read_text(encoding="utf-8", errors="replace")
        if not text.strip():
            continue
        if _index_memory_document(
            user_id,
            session_id,
            record_id=f"logfile:{log_path.stem}",
            title=log_path.stem,
            content=text,
            taxonomy={"type": "log", "hall": "events", "room": slugify(log_path.stem, "daily-log")},
            description="Daily log archive",
            source_kind="log_archive",
            file_path=str(log_path),
        ):
            indexed_logs += 1

    memory = ensure_memory_state(user_id, session_id)
    return {"entries_indexed": indexed_entries, "logs_indexed": indexed_logs, "memory": memory}


def should_run_auto_dream(user_id: str, session_id: str, *, min_hours: int = 24, min_entries: int = 5) -> bool:
    state = _load_state(user_id, session_id)
    last_dream_text = str(state.get("last_dream_at") or "")
    last_dream_at = None
    if last_dream_text:
        try:
            last_dream_at = datetime.fromisoformat(last_dream_text)
        except ValueError:
            last_dream_at = None
    enough_time = last_dream_at is None or last_dream_at <= (_utc_now() - timedelta(hours=min_hours))
    enough_entries = int(state.get("log_entries_since_dream") or 0) >= min_entries
    return enough_time and enough_entries


def run_auto_dream(
    user_id: str,
    session_id: str,
    *,
    query: str = "",
    force: bool = False,
    plan: dict[str, Any] | None = None,
    todos: list[dict[str, Any]] | None = None,
    verifications: list[dict[str, Any]] | None = None,
    inbox: list[dict[str, Any]] | None = None,
    recent_runs: list[dict[str, Any]] | None = None,
    recent_artifacts: list[dict[str, Any]] | None = None,
    reason: str = "",
) -> dict[str, Any]:
    if not force and not should_run_auto_dream(user_id, session_id):
        return {
            "ran": False,
            "reason": "dream gates not satisfied",
            "state": ensure_memory_state(user_id, session_id),
        }
    memory_state = get_memory_state(user_id, session_id, query=query)
    log_path = Path(memory_state["daily_log_path"])
    recent_log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else ""
    relevant = memory_state["relevant_entries"]
    summary_lines = [
        "# Auto Dream",
        "",
        f"Generated at: {_utc_now().isoformat()}",
        "",
        "## Recent signal",
        recent_log[-2500:] if recent_log else "(no daily log yet)",
        "",
        "## Relevant memories",
    ]
    if relevant:
        for item in relevant:
            summary_lines.append(
                f"- {item['name']} [{item['type']}/{item.get('hall', 'events')}/{item.get('room', 'general')}] - "
                f"{item.get('description') or item.get('snippet', '')[:160]}"
            )
    else:
        summary_lines.append("- (none)")
    if plan:
        summary_lines.extend(["", "## Active plan", json.dumps(plan, ensure_ascii=False, indent=2)[:2400]])
    if todos:
        summary_lines.extend(["", "## Todos", json.dumps(todos[:20], ensure_ascii=False, indent=2)[:2400]])
    if verifications:
        summary_lines.extend(["", "## Verifications", json.dumps(verifications[:20], ensure_ascii=False, indent=2)[:2400]])
    if inbox:
        summary_lines.extend(["", "## Inbox", json.dumps(inbox[:20], ensure_ascii=False, indent=2)[:2400]])
    if recent_runs:
        summary_lines.extend(["", "## Recent runs", json.dumps(recent_runs[:10], ensure_ascii=False, indent=2)[:2400]])
    if recent_artifacts:
        summary_lines.extend(["", "## Recent artifacts", json.dumps(recent_artifacts[:10], ensure_ascii=False, indent=2)[:2400]])
    if reason:
        summary_lines.extend(["", f"## Trigger\n{reason[:400]}"])
    path = append_memory_entry(
        user_id,
        session_id,
        name="auto_dream_summary",
        content="\n".join(summary_lines),
        mem_type="dream",
        description="Auto-dream consolidated summary",
        room="auto-dream",
        hall="discoveries",
        source_kind="dream",
    )
    state = _load_state(user_id, session_id)
    state["last_dream_at"] = _utc_now().isoformat()
    state["log_entries_since_dream"] = 0
    _save_state(user_id, session_id, state)
    append_daily_log(
        user_id,
        session_id,
        "Auto Dream",
        f"Consolidated memory state into {path.name}. Trigger: {(reason or 'auto')[:240]}",
    )
    synced_state = ensure_memory_state(user_id, session_id)
    _sync_runtime_store(
        user_id,
        session_id,
        dream_status="idle",
        metadata={"last_dream_summary": str(path)},
    )
    return {
        "ran": True,
        "summary_path": str(path),
        "state": synced_state,
    }

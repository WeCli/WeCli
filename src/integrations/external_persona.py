from __future__ import annotations


def build_external_persona_prompt(tag: str, *, user_id: str = "", team: str = "") -> str:
    """Resolve an external-agent persona by tag and format it for first-prompt injection."""
    persona_tag = str(tag or "").strip()
    if not persona_tag:
        return ""
    try:
        from oasis.experts import get_all_experts
    except Exception:
        return ""

    try:
        experts = get_all_experts(user_id or None, team=team or "")
    except Exception:
        return ""

    matched = None
    for expert in experts:
        if not isinstance(expert, dict):
            continue
        if str(expert.get("tag", "")).strip() == persona_tag:
            matched = expert
            break
    if not matched:
        return ""

    persona = str(matched.get("persona", "") or "").strip()
    if not persona:
        return ""

    expert_name = str(matched.get("name", "") or persona_tag).strip()
    return (
        "【外部 Agent 人设】\n"
        f"当前 persona tag: {persona_tag}\n"
        f"当前角色名: {expert_name}\n"
        "以下是你需要遵循的人设与行为描述：\n\n"
        f"{persona}"
    ).strip()

from typing import Any, Iterable


def extract_human_content(raw: Any, list_fallback: str = "(图片消息)") -> str:
    """从 HumanMessage.content 中提取可展示文本。"""
    if isinstance(raw, str):
        return raw
    if isinstance(raw, list):
        text = " ".join(
            p.get("text", "") for p in raw if isinstance(p, dict) and p.get("type") == "text"
        )
        return text or list_fallback
    return str(raw)


def iter_human_texts(
    messages: Iterable[Any],
    *,
    skip_prefixes: tuple[str, ...] = (),
    list_fallback: str = "(图片消息)",
):
    """遍历消息列表，产出过滤后的 HumanMessage 文本。"""
    for msg in messages:
        if type(msg).__name__ != "HumanMessage" or not hasattr(msg, "content"):
            continue
        content = extract_human_content(msg.content, list_fallback=list_fallback)
        if content and any(content.startswith(prefix) for prefix in skip_prefixes):
            continue
        yield content


def build_session_summary(
    messages: Iterable[Any],
    *,
    skip_prefixes: tuple[str, ...] = (),
    title_len: int = 50,
    last_len: int = 50,
    list_fallback: str = "(图片消息)",
) -> dict:
    """构建会话摘要（首条、末条、计数）。"""
    first_human = ""
    last_human = ""
    msg_count = 0

    for content in iter_human_texts(
        messages,
        skip_prefixes=skip_prefixes,
        list_fallback=list_fallback,
    ):
        msg_count += 1
        if not first_human:
            first_human = content[:title_len]
        last_human = content[:last_len]

    return {
        "first_human": first_human,
        "last_human": last_human,
        "msg_count": msg_count,
    }


def first_human_title(
    messages: Iterable[Any],
    *,
    skip_prefixes: tuple[str, ...] = (),
    title_len: int = 80,
    list_fallback: str = "(图片消息)",
    default: str = "",
) -> str:
    """提取第一条可展示的 HumanMessage 文本作为标题。"""
    for content in iter_human_texts(
        messages,
        skip_prefixes=skip_prefixes,
        list_fallback=list_fallback,
    ):
        if content:
            return content[:title_len]
    return default

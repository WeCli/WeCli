"""
OASIS Forum - Expert Agent definitions

Three expert backends:
  1. ExpertAgent  — direct LLM call (stateless, single-shot)
     name = "display_name#temp#N" (display_name from preset by tag)
  2. SessionExpert — calls mini_timebot's /v1/chat/completions endpoint
     using an existing or auto-created session_id.
     - session_id format "tag#oasis#id" → oasis-managed session, first-round
       identity injection (tag → name/persona from preset configs)
     - other session_id (e.g. "助手#default") → regular agent,
       no identity injection, relies on session's own system prompt
  3. ExternalExpert — direct call to any external OpenAI-compatible API
     name = "display_name#ext#id"
     Connects to external endpoints (DeepSeek, GPT-4, Moonshot, Ollama, etc)
     with their own URL and API key. External service is assumed stateful
     (holds conversation history server-side); only incremental context is sent.
    **ACP agent support**: When model matches "agent:<name>[:<session>]" and
    the tag is an ACP-capable tool (openclaw, codex, etc), prefers ACP persistent
    connection; falls back to HTTP API if ACP is unavailable and api_url is set.
    The tag determines which CLI binary is used for the ACP subprocess.
    Session defaults to team name if not specified in the model string.

Expert pool is built from schedule_yaml or schedule_file (YAML-only mode).
schedule_file takes priority if both provided.
Session IDs can be freely chosen; new IDs auto-create sessions on first use.
Append "#new" to any session name in YAML to force a fresh session (ID
replaced with random UUID, guaranteeing no reuse).
No separate expert-session storage: oasis sessions are identified by the
"#oasis#" pattern in their session_id and live in the normal Agent
checkpoint DB.

Both participate() methods accept an optional `instruction` parameter,
which is injected into the expert's prompt to guide their focus.
"""

import asyncio
import json
import os
import re
import shlex
import shutil
import sys

import httpx
from langchain_core.messages import HumanMessage

# ACP long-lived connection support (from acptest4)
try:
    from acp import PROTOCOL_VERSION, Client, connect_to_agent, text_block
    from acp.schema import ClientCapabilities, Implementation, AgentMessageChunk
    _ACP_AVAILABLE = True
except ImportError:
    _ACP_AVAILABLE = False

# 确保 src/ 在 import 路径中，以便导入 llm_factory
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))
from llm_factory import create_chat_model, extract_text

from oasis.forum import DiscussionForum


# --- 加载 prompt 和专家配置（模块级别，导入时执行一次） ---
_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_prompts_dir = os.path.join(_data_dir, "prompts")
_agency_prompts_dir = os.path.join(_prompts_dir, "agency_agents")


def _load_prompt_file(prompt_file: str) -> str:
    """Load the full prompt content from an agency_agents .md file.

    Strips YAML frontmatter (--- ... ---) and returns the body text.
    Returns empty string if file not found.
    """
    import re as _re
    fpath = os.path.join(_agency_prompts_dir, prompt_file)
    if not os.path.isfile(fpath):
        return ""
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        # Strip YAML frontmatter
        fm_match = _re.match(r'^---\s*\n.*?\n---\s*\n', content, _re.DOTALL)
        body = content[fm_match.end():] if fm_match else content
        return body.strip()
    except Exception:
        return ""


# 加载公共专家配置（原始简版）
_experts_json_path = os.path.join(_prompts_dir, "oasis_experts.json")
try:
    with open(_experts_json_path, "r", encoding="utf-8") as f:
        EXPERT_CONFIGS: list[dict] = json.load(f)
    print(f"[prompts] ✅ oasis 已加载 oasis_experts.json ({len(EXPERT_CONFIGS)} 位公共专家)")
except FileNotFoundError:
    print(f"[prompts] ⚠️ 未找到 {_experts_json_path}，使用内置默认配置")
    EXPERT_CONFIGS = [
        {"name": "创意专家", "tag": "creative", "persona": "你是一个乐观的创新者，善于发现机遇和非常规解决方案。你喜欢挑战传统观念，提出大胆且具有前瞻性的想法。", "temperature": 0.9},
        {"name": "PUA专家", "tag": "critical", "persona": (
            "## 角色\n"
            "你是 PUA 专家，基于原版 pua 协议运行的高压审查官。你的任务不是为了否定而否定，而是像绩效改进计划一样识别失败模式、升级压力等级、逼团队拿出证据、切换方案并把事情真正闭环。\n\n"
            "## OASIS 适配规则\n"
            "- 你在 OASIS 论坛中发言时，要把原版 pua 协议压缩成短评；不要输出长面板、ASCII 方框或冗长仪式。\n"
            "- 如果你发言，优先用这一句开头：[自动选择：<味道>/<等级> | 因为：<失败模式>]。\n"
            "- 随后只讲 3 件事：当前根因、最大缺口、下一步强制动作与验证标准。\n"
            "- 没有日志、测试、curl、截图、实验结果或原始依据时，不接受任何人声称已完成。\n"
            "- 即使主题是策略、研究、文案或规划，也要沿用同一标准：是否穷尽、是否有原始依据、是否有验证闭环、是否存在本质不同的替代方案。\n\n"
            "## 三条铁律\n"
            "- 穷尽一切：在确认已试尽本质不同方案前，禁止接受做不到、建议人工处理、可能是环境问题这类说法。\n"
            "- 先做后问：先搜索、读源码或原始材料、跑验证，再提问；提问时必须附上已经查到的证据。\n"
            "- Owner 意识：修一个点不够，要顺手检查同类问题、上下游影响、回归风险与预防动作。\n\n"
            "## 失败模式选择器\n"
            "先识别最接近的一类，再决定语气和施压方式：\n"
            "- 卡住原地打转：反复微调同一路线，不换假设。\n"
            "- 直接放弃推锅：未验证就甩给环境、权限或用户手动处理。\n"
            "- 完成但质量烂：表面交付，实质空洞、颗粒度粗、没有抓手。\n"
            "- 没搜索就猜：靠记忆和拍脑袋，不查文档、源码或数据。\n"
            "- 被动等待：不主动验证、不主动延伸排查，只等别人指示。\n"
            "- 空口完成：说已完成，但没有任何可验证证据。\n\n"
            "## 味道映射\n"
            "- 卡住原地打转：默认阿里味，强调底层逻辑、抓手、闭环。\n"
            "- 直接放弃推锅：先 Netflix 味，再必要时切华为味。\n"
            "- 没搜索就猜：默认百度味，追问为什么不先搜。\n"
            "- 被动等待或空口完成：优先阿里验证型，必要时叠加美团味。\n"
            "- 完成但质量烂：优先 Jobs 味，再补阿里味做闭环审查。\n\n"
            "## 压力升级\n"
            "- L1：第 2 次失败或明显同路打转，要求立刻换本质不同方案。\n"
            "- L2：第 3 次失败，要求补齐错误原文、原始材料和 3 个不同假设。\n"
            "- L3：第 4 次失败，要求逐项完成 7 项检查清单，并给出 3 个新方向。\n"
            "- L4：第 5 次及以上，要求最小 PoC、隔离环境、完全不同技术路线；仍无解时只能输出结构化交接。\n\n"
            "## 7 项检查清单\n"
            "1. 逐字读失败信号。\n"
            "2. 搜索核心问题。\n"
            "3. 读原始材料。\n"
            "4. 验证前置假设。\n"
            "5. 反转关键假设。\n"
            "6. 做最小隔离或最小复现。\n"
            "7. 换到本质不同的方法。\n\n"
            "## 发言要求\n"
            "- 语气保留 pua 风格，直接、有压迫感，但必须给出根因、风险、抓手、闭环，不准只会骂。\n"
            "- 优先攻击空话、未验证结论、想当然归因、只做一半的交付。\n"
            "- 发现方案可行，也要指出还差哪一步验证才算真正过线。\n"
            "- 如果确认仍未解决，输出已验证事实、已排除项、缩小范围、下一步建议，而不是一句无能为力。\n"
            "- 可适度使用底层逻辑、抓手、闭环、owner、别自嗨、3.25、优化名单等原版 pua 术语，但避免无意义辱骂。"
        ), "temperature": 0.4},
        {"name": "数据分析师", "tag": "data", "persona": "你是一个数据驱动的分析师，只相信数据和事实。你用数字、案例和逻辑推导来支撑你的观点。", "temperature": 0.5},
        {"name": "综合顾问", "tag": "synthesis", "persona": "你善于综合不同观点，寻找平衡方案，关注实际可操作性。你会识别各方共识，提出兼顾多方利益的务实建议。", "temperature": 0.5},
    ]

# 加载 agency-agents 丰富版专家 prompt 库
_agency_json_path = os.path.join(_prompts_dir, "agency_experts.json")
AGENCY_EXPERT_CONFIGS: list[dict] = []
try:
    with open(_agency_json_path, "r", encoding="utf-8") as f:
        _raw_agency = json.load(f)
    # 为每个 agency 专家加载完整 prompt 并设置 persona
    _existing_tags = {c["tag"] for c in EXPERT_CONFIGS}
    for item in _raw_agency:
        if item["tag"] in _existing_tags:
            continue  # 跳过与原始专家 tag 冲突的（不应出现）
        prompt_body = _load_prompt_file(item["prompt_file"])
        if not prompt_body:
            continue  # 跳过加载失败的
        item["persona"] = prompt_body  # 用完整 md 正文作为 persona
        AGENCY_EXPERT_CONFIGS.append(item)
    print(f"[prompts] ✅ oasis 已加载 agency_experts.json ({len(AGENCY_EXPERT_CONFIGS)} 位 Agency 专家)")
except FileNotFoundError:
    print(f"[prompts] ⚠️ 未找到 {_agency_json_path}，Agency 专家库未启用")


# ======================================================================
# Per-user custom expert storage (persona definitions)
# ======================================================================
_USER_EXPERTS_DIR = os.path.join(_data_dir, "oasis_user_experts")
os.makedirs(_USER_EXPERTS_DIR, exist_ok=True)


def _user_experts_path(user_id: str) -> str:
    """Return the JSON file path for a user's custom experts."""
    safe = user_id.replace("/", "_").replace("\\", "_").replace("..", "_")
    return os.path.join(_USER_EXPERTS_DIR, f"{safe}.json")


def load_user_experts(user_id: str) -> list[dict]:
    """Load a user's custom expert list (returns [] if none)."""
    path = _user_experts_path(user_id)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_user_experts(user_id: str, experts: list[dict]) -> None:
    with open(_user_experts_path(user_id), "w", encoding="utf-8") as f:
        json.dump(experts, f, ensure_ascii=False, indent=2)


def _validate_expert(data: dict) -> dict:
    """Validate and normalize an expert config dict. Raises ValueError on bad input."""
    name = data.get("name", "").strip()
    tag = data.get("tag", "").strip()
    persona = data.get("persona", "").strip()
    if not name:
        raise ValueError("专家 name 不能为空")
    if not tag:
        raise ValueError("专家 tag 不能为空")
    if not persona:
        raise ValueError("专家 persona 不能为空")
    result = {
        "name": name,
        "tag": tag,
        "persona": persona,
        "temperature": float(data.get("temperature", 0.7)),
    }
    # 保留可选扩展字段
    for key in ("category", "description", "prompt_file"):
        if data.get(key):
            result[key] = data[key]
    return result


def add_user_expert(user_id: str, data: dict) -> dict:
    """Add a custom expert for a user. Returns the normalized expert dict."""
    expert = _validate_expert(data)
    experts = load_user_experts(user_id)
    if any(e["tag"] == expert["tag"] for e in experts):
        raise ValueError(f"用户已有 tag=\"{expert['tag']}\" 的专家，请换一个 tag 或使用更新功能")
    if any(e["tag"] == expert["tag"] for e in EXPERT_CONFIGS):
        raise ValueError(f"tag=\"{expert['tag']}\" 与公共专家冲突，请换一个 tag")
    if any(e["tag"] == expert["tag"] for e in AGENCY_EXPERT_CONFIGS):
        raise ValueError(f"tag=\"{expert['tag']}\" 与 Agency 专家库冲突，请换一个 tag")
    experts.append(expert)
    _save_user_experts(user_id, experts)
    return expert


def update_user_expert(user_id: str, tag: str, data: dict) -> dict:
    """Update an existing custom expert by tag. Returns the updated dict."""
    experts = load_user_experts(user_id)
    # 过滤掉空字符串值的可选字段，避免覆盖已有值
    _skip = {"user_id", "team", "tag"}
    patch = {k: v for k, v in data.items() if k not in _skip and v not in ("", None)}
    for i, e in enumerate(experts):
        if e["tag"] == tag:
            updated = _validate_expert({**e, **patch, "tag": tag})
            experts[i] = updated
            _save_user_experts(user_id, experts)
            return updated
    raise ValueError(f"未找到用户自定义专家 tag=\"{tag}\"")


def delete_user_expert(user_id: str, tag: str) -> dict:
    """Delete a custom expert by tag. Returns the deleted dict."""
    experts = load_user_experts(user_id)
    for i, e in enumerate(experts):
        if e["tag"] == tag:
            deleted = experts.pop(i)
            _save_user_experts(user_id, experts)
            return deleted
    raise ValueError(f"未找到用户自定义专家 tag=\"{tag}\"")


def load_team_experts(user_id: str, team: str) -> list[dict]:
    """Load team-specific custom experts from {user}/teams/{team}/oasis_experts.json.

    Returns [] if file missing or unreadable.
    """
    if not user_id or not team:
        return []
    path = os.path.join(_data_dir, "user_files", user_id, "teams", team, "oasis_experts.json")
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_team_experts(user_id: str, team: str, experts: list[dict]) -> None:
    """Save team-specific custom experts to {user}/teams/{team}/oasis_experts.json."""
    dir_path = os.path.join(_data_dir, "user_files", user_id, "teams", team)
    os.makedirs(dir_path, exist_ok=True)
    path = os.path.join(dir_path, "oasis_experts.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(experts, f, ensure_ascii=False, indent=2)


def add_team_expert(user_id: str, team: str, data: dict) -> dict:
    """Add a custom expert under a specific team. Returns the normalized expert dict."""
    expert = _validate_expert(data)
    experts = load_team_experts(user_id, team)
    if any(e["tag"] == expert["tag"] for e in experts):
        raise ValueError(f"Team '{team}' 已有 tag=\"{expert['tag']}\" 的专家，请换一个 tag 或使用更新功能")
    experts.append(expert)
    _save_team_experts(user_id, team, experts)
    return expert


def update_team_expert(user_id: str, team: str, tag: str, data: dict) -> dict:
    """Update an existing team expert by tag. Returns the updated dict."""
    experts = load_team_experts(user_id, team)
    # 过滤掉空字符串值的可选字段，避免覆盖已有值
    _skip = {"user_id", "team", "tag"}
    patch = {k: v for k, v in data.items() if k not in _skip and v not in ("", None)}
    for i, e in enumerate(experts):
        if e["tag"] == tag:
            updated = _validate_expert({**e, **patch, "tag": tag})
            experts[i] = updated
            _save_team_experts(user_id, team, experts)
            return updated
    raise ValueError(f"未找到 Team '{team}' 自定义专家 tag=\"{tag}\"")


def delete_team_expert(user_id: str, team: str, tag: str) -> dict:
    """Delete a team expert by tag. Returns the deleted dict."""
    experts = load_team_experts(user_id, team)
    for i, e in enumerate(experts):
        if e["tag"] == tag:
            deleted = experts.pop(i)
            _save_team_experts(user_id, team, experts)
            return deleted
    raise ValueError(f"未找到 Team '{team}' 自定义专家 tag=\"{tag}\"")


def get_all_experts(user_id: str | None = None, team: str = "") -> list[dict]:
    """Return public experts + agency experts + user's custom experts + team experts.

    When *team* is provided, team-specific experts are appended last with
    source="team".  Because _lookup_by_tag iterates in order and returns the
    first match, team experts effectively **override** public/agency/custom
    experts with the same tag — so we prepend them instead.
    """
    result: list[dict] = []
    # Team experts first (highest priority for tag lookup)
    if user_id and team:
        result.extend(
            {**c, "source": "team"} for c in load_team_experts(user_id, team)
        )
    result.extend(
        {**c, "source": "public"} for c in EXPERT_CONFIGS
    )
    result.extend(
        {**c, "source": "agency"} for c in AGENCY_EXPERT_CONFIGS
    )
    if user_id:
        result.extend(
            {**c, "source": "custom"} for c in load_user_experts(user_id)
        )
    return result


# ======================================================================
# Prompt helpers (shared by both backends)
# ======================================================================

# 加载讨论 prompt 模板
_discuss_tpl_path = os.path.join(_prompts_dir, "oasis_expert_discuss.txt")
try:
    with open(_discuss_tpl_path, "r", encoding="utf-8") as f:
        _DISCUSS_PROMPT_TPL = f.read().strip()
    print("[prompts] ✅ oasis 已加载 oasis_expert_discuss.txt")
except FileNotFoundError:
    print(f"[prompts] ⚠️ 未找到 {_discuss_tpl_path}，使用内置默认模板")
    _DISCUSS_PROMPT_TPL = ""


# Common behavior rules injected into all expert prompts (discussion & execute mode)
_BEHAVIOR_RULES = (
    '\n\n**重要行为规则：**\n'
    '0. **子 Agent 身份**：你是被上级调度系统（OASIS 工作流引擎）调用的子 Agent，你的职责是按照指令完成当前任务并返回结果，不要试图接管整个讨论流程或代替其他专家发言\n'
    '1. **禁止自动开启子工作流**：除非明确收到点名要求开启子工作流，否则不得自行开启任何子讨论或子工作流\n'
    '2. **单级讨论原则**：保持当前讨论层级，不创建多级嵌套讨论\n'
    '3. **任务专注**：专注于当前论坛主题，不偏离到其他无关话题\n'
)


def _get_llm(
    temperature: float = 0.7,
    *,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    provider: str | None = None,
):
    """Create an LLM instance.

    When *model*/*api_key*/*base_url*/*provider* are given they override the
    global ``LLM_*`` env vars, enabling per-expert model routing.
    """
    return create_chat_model(
        temperature=temperature,
        max_tokens=1024,
        model=model,
        api_key=api_key,
        base_url=base_url,
        provider=provider,
    )


def _build_discuss_prompt(
    expert_name: str,
    persona: str,
    question: str,
    posts_text: str,
    split: bool = False,
) -> str | tuple[str, str]:
    """Build the prompt that asks the expert to respond with JSON.

    Args:
        split: If True, return (system_prompt, user_prompt) tuple for session mode.
               If False, return a single combined string for direct LLM mode.
    """
    if _DISCUSS_PROMPT_TPL and not split:
        return _DISCUSS_PROMPT_TPL.format(
            expert_name=expert_name,
            persona=persona,
            question=question,
            posts_text=posts_text,
        )

    # --- Build system part (identity + behavior) ---
    # 判断是否是丰富的 agency 专家 prompt（含 markdown 标题）
    _is_rich_persona = persona and ("## " in persona or "# " in persona)
    if _is_rich_persona:
        # Agency 专家：完整 prompt 已包含身份/职责/规则等，直接使用
        identity = (
            f"你在 OASIS 论坛中的显示名称是「{expert_name}」。\n\n"
            f"以下是你的完整身份与行为指南：\n\n{persona}"
        )
    else:
        identity = f"你是论坛专家「{expert_name}」。{persona}" if persona else ""
    sys_parts = [p for p in [
        identity,
        "在接下来的讨论中，你将收到论坛的新增内容，需要以 JSON 格式回复你的观点和投票。",
        "你拥有工具调用能力，如需搜索资料、分析数据来支撑你的观点，可以使用可用的工具。",
        "注意：后续轮次只会发送新增帖子，之前的帖子请参考你的对话记忆。",
        "**重要行为规则：**\n"
        "0. **子 Agent 身份**：你是被上级调度系统（OASIS 工作流引擎）调用的子 Agent，你的职责是按照指令在当前讨论中发表你自己角色的观点并返回结果，不要试图接管整个讨论流程或代替其他专家发言\n"
        "1. **禁止自动开启子工作流**：除非明确收到点名要求开启子工作流，否则不得自行开启任何子讨论或子工作流\n"
        "2. **单级讨论原则**：保持当前讨论层级，不创建多级嵌套讨论\n"
        "3. **任务专注**：专注于当前论坛主题，不偏离到其他无关话题",
    ] if p]
    system_prompt = "\n".join(sys_parts)

    # --- Build user part (topic + forum content + JSON format) ---
    user_prompt = (
        f"讨论主题: {question}\n\n"
        f"当前论坛内容:\n{posts_text}\n\n"
        "请在回复中包含一个 JSON 对象（不要包含 markdown 代码块标记，不要包含注释）：\n"
        '{"teamclaw_type": "oasis reply", "reply_to": 2, "content": "你的观点（200字以内，观点鲜明）", '
        '"votes": [{"post_id": 1, "direction": "up"}]}\n\n'
        "说明:\n"
        "- teamclaw_type: 必须为 \"oasis reply\"\n"
        "- reply_to: 如果论坛中已有其他人的帖子，你**必须**选择一个帖子ID进行回复；只有在论坛为空时才填 null\n"
        "- content: 你的发言内容，要有独到见解，可以赞同、反驳或补充你所回复的帖子\n"
        '- votes: 对其他帖子的投票列表，direction 只能是 "up" 或 "down"。如果没有要投票的帖子，填空列表 []\n'
        "- JSON 前后可以有其他文字，系统会自动提取 JSON 部分\n"
        "- ⚠️ JSON 必须写在一行内，content 字段中不能有实际换行符（需要换行请用 \\n 转义）\n"
    )

    if split:
        return system_prompt, user_prompt
    else:
        return f"{system_prompt}\n\n{user_prompt}"


def _build_discuss_callback_prompt(
    expert_name: str,
    persona: str,
    question: str,
    posts_text: str,
    callback_hint: str,
    instruction: str = "",
) -> tuple[str, str]:
    """Build the prompt for ACP agents that must callback via CLI/API."""
    _is_rich_persona = persona and ("## " in persona or "# " in persona)
    if _is_rich_persona:
        identity = (
            f"你在 OASIS 论坛中的显示名称是「{expert_name}」。\n\n"
            f"以下是你的完整身份与行为指南：\n\n{persona}"
        )
    else:
        identity = f"你是论坛专家「{expert_name}」。{persona}" if persona else ""
    system_prompt = "\n".join(
        p for p in [
            identity,
            "你正在通过 ACP 长连接被 OASIS 调度。",
            "公开发言/投票/选择必须由你主动调用 CLI 回传到 OASIS，系统不会解析你的 ACP 文本并代发。",
            "如果你决定本轮不发言，可以只返回一句很短的确认，不要提交 callback。",
            "**重要行为规则：**\n"
            "0. **子 Agent 身份**：你是被上级调度系统（OASIS 工作流引擎）调用的子 Agent，只负责当前轮次的思考与回传\n"
            "1. **禁止自动开启子工作流**：除非明确点名，否则不得自行开启任何子讨论或子工作流\n"
            "2. **单级讨论原则**：保持当前讨论层级，不创建多级嵌套讨论\n"
            "3. **任务专注**：专注于当前论坛主题，不偏离到其他无关话题",
        ] if p
    )
    user_parts = [
        f"讨论主题: {question}",
        f"\n当前论坛内容:\n{posts_text}",
        "\n如果你要公开发言、投票或做分支选择，请主动执行以下命令回传：",
        callback_hint,
        "\n回传 JSON 格式示例：",
        '{"teamclaw_type": "oasis reply", "reply_to": 2, "content": "你的观点（200字以内，观点鲜明）", "votes": [{"post_id": 1, "direction": "up"}]}',
        '{"teamclaw_type": "oasis choose", "choose": {"option": "A", "reason": "理由"}, "content": "补充说明"}',
        "\n注意：不要把最终 JSON 直接放在 ACP 回复正文里，ACP 回复正文只用于简短确认。",
    ]
    if instruction:
        user_parts.append(f"\n📋 本轮你的专项指令：{instruction}\n请在 callback 的内容里体现这个指令。")
    return system_prompt, "\n".join(user_parts)


def _build_identity_prompt(expert_name: str, persona: str) -> str:
    """Build identity text for execute mode. Handles both short and rich personas."""
    if not persona:
        return ""
    _is_rich = "## " in persona or "# " in persona
    if _is_rich:
        return (
            f"你在 OASIS 论坛中的显示名称是「{expert_name}」。\n\n"
            f"以下是你的完整身份与行为指南：\n\n{persona}\n\n"
        )
    else:
        return f"你是「{expert_name}」。{persona}\n\n"


def _build_execute_callback_prompt(
    question: str,
    prior_posts_text: str,
    callback_hint: str,
    instruction: str = "",
    *,
    first_turn: bool,
) -> str:
    """Build execute-mode prompt for ACP agents that callback explicitly."""
    parts = [f"任务主题: {question}"]
    if instruction:
        parts.append(f"\n执行指令: {instruction}")
    if prior_posts_text:
        label = "前序 agent 的执行结果" if first_turn else "其他 agent 的新结果"
        parts.append(f"\n{label}:\n{prior_posts_text}")
    parts.append("\n如果你产出了执行结果，请不要把最终 JSON 直接写在 ACP 回复正文里。")
    parts.append("请主动执行以下命令，把结构化结果回传到 OASIS：")
    parts.append(callback_hint)
    parts.append("\n回传 JSON 示例：")
    parts.append('{"teamclaw_type": "oasis reply", "reply_to": null, "content": "你的执行结果", "votes": []}')
    parts.append("\n如果本轮没有新增结果，可以只返回一句很短的确认，不要提交 callback。")
    parts.append(_BEHAVIOR_RULES)
    return "\n".join(parts)


def _format_posts(posts) -> str:
    """Format posts for display in the prompt."""
    lines = []
    for p in posts:
        prefix = f"  ↳ 回复#{p.reply_to}" if p.reply_to else "📌"
        lines.append(
            f"{prefix} [#{p.id}] {p.author} "
            f"(👍{p.upvotes} 👎{p.downvotes}): {p.content}"
        )
    return "\n".join(lines)


def _fix_json_control_chars(text: str) -> str:
    """Fix raw control characters (\n, \r, \t, etc.) inside JSON string values.

    Walks through *text*; when inside a JSON string (between unescaped
    double-quotes), replaces literal control characters with their
    JSON-escaped equivalents so that ``json.loads`` can succeed.
    """
    _CTRL_MAP = {
        '\n': '\\n',
        '\r': '\\r',
        '\t': '\\t',
        '\x08': '\\b',
        '\x0c': '\\f',
    }
    in_str = False
    chars: list[str] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == '\\' and in_str and i + 1 < len(text):
            # Already-escaped char — keep as-is
            chars.append(ch)
            chars.append(text[i + 1])
            i += 2
            continue
        if ch == '"':
            in_str = not in_str
            chars.append(ch)
        elif in_str and ch in _CTRL_MAP:
            chars.append(_CTRL_MAP[ch])
        else:
            chars.append(ch)
        i += 1
    return ''.join(chars)


def _parse_expert_response(raw: str):
    """Strip markdown fences / oasis reply tags and parse JSON.

    Tries multiple strategies to extract valid JSON:
      1. Strip markdown code fences (```...```)
      2. Strip [oasis reply start/end] tags
      3. Direct json.loads
      4. Regex extraction of first {...} object from the text
    Raises json.JSONDecodeError if all strategies fail.
    """
    raw = raw.strip()
    # Strip markdown code fences
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    raw = raw.strip()

    # Strip [end padding] lines
    raw = re.sub(r"\[end\s*padding\]", "", raw, flags=re.IGNORECASE).strip()

    # Attempt 1: direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Attempt 1.5: try to fix raw control chars (\n, \r, \t …) inside JSON strings
    try:
        fixed = _fix_json_control_chars(raw)
        if fixed != raw:
            return json.loads(fixed)
    except (json.JSONDecodeError, Exception):
        pass

    # Attempt 2: tolerant extraction — find all top-level { ... } candidates
    candidates = []
    depth = 0
    start_idx = -1
    for i, ch in enumerate(raw):
        if ch == '{':
            if depth == 0:
                start_idx = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start_idx >= 0:
                candidates.append(raw[start_idx:i + 1])
                start_idx = -1
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    # Attempt 3: regex fallback for nested/malformed cases
    m = re.search(r"\{[\s\S]*\}", raw)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass

    # All strategies failed — raise for caller to handle
    raise json.JSONDecodeError("No valid JSON found in response", raw, 0)


async def _apply_response(
    result: dict,
    expert_name: str,
    forum: DiscussionForum,
    others: list,
):
    """Apply the parsed JSON response: publish post + cast votes.

    Supports two teamclaw_type values:
      - "oasis reply": publish post + cast votes
      - "oasis choose": publish choice as a post
    """
    resp_type = result.get("teamclaw_type", "oasis reply")

    if resp_type == "oasis choose":
        # Choice mode: publish the choice info as a post.
        # We embed the full JSON in the post content so that engine.py's
        # _extract_selector_choice() can parse it back for selector branching.
        choose = result.get("choose", {})
        content = result.get("content", "")

        # Build the published text: embed the original JSON for machine parsing,
        # followed by a human-readable summary.
        json_str = json.dumps(result, ensure_ascii=False)
        if content:
            choice_text = f"{json_str}\n{content}"
        else:
            choice_text = json_str

        reply_to = None
        if others:
            reply_to = others[-1].id
        await forum.publish(
            author=expert_name,
            content=choice_text,
            reply_to=reply_to,
        )
        print(f"  [OASIS] ✅ {expert_name} 选择完成 (choose={choose})")
        return

    # Default: "oasis reply"
    reply_to = result.get("reply_to")
    if reply_to is None and others:
        reply_to = others[-1].id
        print(f"  [OASIS] 🔧 {expert_name} reply_to 为 null，自动设为 #{reply_to}")

    await forum.publish(
        author=expert_name,
        content=result.get("content", "（发言内容为空）"),
        reply_to=reply_to,
    )

    for v in result.get("votes", []):
        pid = v.get("post_id")
        direction = v.get("direction", "up")
        if pid is not None and direction in ("up", "down"):
            await forum.vote(expert_name, int(pid), direction)

    print(f"  [OASIS] ✅ {expert_name} 发言完成")


# ======================================================================
# Backend 1: ExpertAgent — direct LLM call (stateless)
#   name = "title#temp#1", "title#temp#2", ...
# ======================================================================

class ExpertAgent:
    """
    A forum-resident expert agent (direct LLM backend).

    Each call is stateless: reads posts → single LLM call → publish + vote.
    name is "title#temp#N" to ensure uniqueness.
    """

    # Class-level counter for generating unique temp IDs (used when no explicit sid)
    _counter: int = 0

    def __init__(self, name: str, persona: str, temperature: float = 0.7, tag: str = "",
                 temp_id: int | None = None, *,
                 model: str | None = None, api_key: str | None = None,
                 base_url: str | None = None, provider: str | None = None):
        if temp_id is not None:
            # Explicit temp id from YAML (e.g. "创意专家#temp#1" → temp_id=1)
            self.session_id = f"temp#{temp_id}"
        else:
            ExpertAgent._counter += 1
            self.session_id = f"temp#{ExpertAgent._counter}"
        self.title = name
        self.name = f"{name}#{self.session_id}"
        self.persona = persona
        self.tag = tag
        self.llm = _get_llm(
            temperature,
            model=model,
            api_key=api_key,
            base_url=base_url,
            provider=provider,
        )

    async def participate(
        self,
        forum: DiscussionForum,
        instruction: str = "",
        discussion: bool = True,
        visible_authors: set[str] | None = None,
        from_round: int | None = None,
    ):
        others = await forum.browse(
            viewer=self.name,
            exclude_self=True,
            visible_authors=visible_authors if not discussion else None,
            from_round=from_round if not discussion else None,
        )

        if not discussion:
            # ── Execute mode (requires teamclaw_type JSON protocol, retry=1 for internal agent) ──
            _EXEC_JSON_HINT = (
                '\n\n请将你的执行结果用以下 JSON 格式返回'
                '（不要包含 markdown 代码块标记，不要包含注释）：\n'
                '{"teamclaw_type": "oasis reply", "reply_to": null, '
                '"content": "你的执行结果", "votes": []}\n'
                'JSON 前后可以有其他文字，系统会自动提取 JSON 部分。\n'
                '⚠️ JSON 必须写在一行内，content 字段中不能有实际换行符（需要换行请用 \\n 转义）。\n'
            )
            task_prompt = _build_identity_prompt(self.title, self.persona)
            task_prompt += f"任务主题: {forum.question}\n"
            if instruction:
                task_prompt += f"\n执行指令: {instruction}\n"
            if others:
                task_prompt += f"\n前序 agent 的执行结果:\n{_format_posts(others)}\n"
            task_prompt += "\n请直接执行任务并返回结果。"
            task_prompt += _EXEC_JSON_HINT
            task_prompt += _BEHAVIOR_RULES

            try:
                resp = await self.llm.ainvoke([HumanMessage(content=task_prompt)])
                text = extract_text(resp.content)
                result = _parse_expert_response(text)
                await _apply_response(result, self.name, forum, others)
            except json.JSONDecodeError as e:
                print(f"  [OASIS] ⚠️ {self.name} JSON parse error: {e}")
                try:
                    await forum.publish(author=self.name, content=extract_text(resp.content).strip()[:2000])
                except Exception:
                    pass
            except Exception as e:
                print(f"  [OASIS] ❌ {self.name} error: {e}")
            return

        # ── Discussion mode (original) ──
        posts_text = _format_posts(others) if others else "(还没有其他人发言，你来开启讨论吧)"
        prompt = _build_discuss_prompt(self.title, self.persona, forum.question, posts_text)
        if instruction:
            prompt += f"\n\n📋 本轮你的专项指令：{instruction}\n请在回复中重点关注和执行这个指令。"

        try:
            resp = await self.llm.ainvoke([HumanMessage(content=prompt)])
            text = extract_text(resp.content)
            result = _parse_expert_response(text)
            await _apply_response(result, self.name, forum, others)
        except json.JSONDecodeError as e:
            print(f"  [OASIS] ⚠️ {self.name} JSON parse error: {e}")
            try:
                await forum.publish(author=self.name, content=extract_text(resp.content).strip()[:300])
            except Exception:
                pass
        except Exception as e:
            print(f"  [OASIS] ❌ {self.name} error: {e}")


# ======================================================================
# Backend 2: SessionExpert — calls mini_timebot /v1/chat/completions
#   using an existing session_id.  name = "title#session_id"
# ======================================================================

class SessionExpert:
    """
    Expert backed by a mini_timebot session.

    Two sub-types determined by session_id format:
      - "#oasis#" in session_id → oasis-managed session.
        First round: inject persona as system prompt so the bot knows its
        discussion identity.  Persona is looked up from preset configs by
        title, or left empty if not found.
      - Other session_id → regular agent session.
        No identity injection; the session's own system prompt defines who
        it is.  Just send the discussion invitation.

    Sessions are lazily created: first call to the bot API auto-creates the
    thread in the checkpoint DB.  No separate record table needed.

    Incremental context: first call sends full discussion context; subsequent
    calls only send new posts since last participation.
    """

    def __init__(
        self,
        name: str,
        session_id: str,
        user_id: str,
        persona: str = "",
        bot_base_url: str | None = None,
        enabled_tools: list[str] | None = None,
        timeout: float | None = None,
        tag: str = "",
        extra_headers: dict[str, str] | None = None,
        *,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        provider: str | None = None,
    ):
        self.title = name
        self.session_id = session_id
        self.name = f"{name}#{session_id}"
        self.persona = persona
        self.is_oasis = "#oasis#" in session_id
        self.timeout = timeout or 500.0
        self.tag = tag
        self._extra_headers = extra_headers or {}

        port = os.getenv("PORT_AGENT", "51200")
        self._bot_url = (bot_base_url or f"http://127.0.0.1:{port}") + "/v1/chat/completions"

        self._user_id = user_id
        self._internal_token = os.getenv("INTERNAL_TOKEN", "")

        self.enabled_tools = enabled_tools
        self._initialized = False
        self._seen_post_ids: set[int] = set()

        # Per-expert LLM model override (threaded through Agent service)
        self._llm_override: dict | None = None
        _ov = {}
        if model:
            _ov["model"] = model
        if api_key:
            _ov["api_key"] = api_key
        if base_url:
            _ov["base_url"] = base_url
        if provider:
            _ov["provider"] = provider
        if _ov:
            self._llm_override = _ov

    def _auth_header(self) -> dict:
        h = {"Authorization": f"Bearer {self._internal_token}:{self._user_id}"}
        h.update(self._extra_headers)
        return h

    async def participate(
        self,
        forum: DiscussionForum,
        instruction: str = "",
        discussion: bool = True,
        visible_authors: set[str] | None = None,
        from_round: int | None = None,
    ):
        """
        Participate in one round.

        discussion=True: forum discussion mode (JSON reply/vote)
        discussion=False: execute mode — agent just runs the task, output logged to forum
        visible_authors: (execute mode only) if set, only see posts from these authors (DAG upstream)
        from_round: (execute mode only) if set, only see posts from this round onward (non-DAG prev round)
        """
        others = await forum.browse(
            viewer=self.name,
            exclude_self=True,
            visible_authors=visible_authors if not discussion else None,
            from_round=from_round if not discussion else None,
        )

        if not discussion:
            # ── Execute mode (requires teamclaw_type JSON protocol, retry=1 for internal agent) ──
            new_posts = [p for p in others if p.id not in self._seen_post_ids]
            self._seen_post_ids.update(p.id for p in others)

            _EXEC_JSON_HINT = (
                '\n\n请将你的执行结果用以下 JSON 格式返回'
                '（不要包含 markdown 代码块标记，不要包含注释）：\n'
                '{"teamclaw_type": "oasis reply", "reply_to": null, '
                '"content": "你的执行结果", "votes": []}\n'
                'JSON 前后可以有其他文字，系统会自动提取 JSON 部分。\n'
                '⚠️ JSON 必须写在一行内，content 字段中不能有实际换行符（需要换行请用 \\n 转义）。\n'
            )

            messages = []
            if not self._initialized:
                # First call
                task_parts = []
                if self.is_oasis and self.persona:
                    messages.append({"role": "system", "content": _build_identity_prompt(self.title, self.persona).strip()})
                task_parts.append(f"任务主题: {forum.question}")
                if instruction:
                    task_parts.append(f"\n执行指令: {instruction}")
                if others:
                    task_parts.append(f"\n前序 agent 的执行结果:\n{_format_posts(others)}")
                task_parts.append("\n请直接执行任务并返回结果。")
                task_parts.append(_EXEC_JSON_HINT)
                task_parts.append(_BEHAVIOR_RULES)
                messages.append({"role": "user", "content": "\n".join(task_parts)})
                self._initialized = True
            else:
                # Subsequent calls
                ctx_parts = [f"【第 {forum.current_round} 轮】"]
                if instruction:
                    ctx_parts.append(f"执行指令: {instruction}")
                if new_posts:
                    ctx_parts.append(f"其他 agent 的新结果:\n{_format_posts(new_posts)}")
                ctx_parts.append("请继续执行任务并返回结果。")
                ctx_parts.append(_EXEC_JSON_HINT)
                ctx_parts.append(_BEHAVIOR_RULES)
                messages.append({"role": "user", "content": "\n".join(ctx_parts)})

            body: dict = {
                "model": "teambot",
                "messages": messages,
                "stream": False,
                "session_id": self.session_id,
            }
            if self.enabled_tools is not None:
                body["enabled_tools"] = self.enabled_tools
            if self._llm_override:
                body["llm_override"] = self._llm_override

            try:
                async with httpx.AsyncClient(timeout=httpx.Timeout(timeout=None)) as client:
                    resp = await client.post(
                        self._bot_url, json=body, headers=self._auth_header(),
                    )
                if resp.status_code != 200:
                    print(f"  [OASIS] ❌ {self.name} bot API error {resp.status_code}: {resp.text[:200]}")
                    return
                data = resp.json()
                raw_content = data["choices"][0]["message"]["content"]
                result = _parse_expert_response(raw_content)
                await _apply_response(result, self.name, forum, others)
            except json.JSONDecodeError as e:
                print(f"  [OASIS] ⚠️ {self.name} JSON parse error: {e}")
                try:
                    await forum.publish(author=self.name, content=raw_content.strip()[:2000])
                except Exception:
                    pass
            except Exception as e:
                print(f"  [OASIS] ❌ {self.name} error: {e}")
            return

        # ── Discussion mode (original) ──
        others = await forum.browse(viewer=self.name, exclude_self=True)

        new_posts = [p for p in others if p.id not in self._seen_post_ids]
        self._seen_post_ids.update(p.id for p in others)

        instr_suffix = f"\n\n📋 本轮你的专项指令：{instruction}\n请在回复中重点关注和执行这个指令。" if instruction else ""

        messages = []
        if not self._initialized:
            posts_text = _format_posts(others) if others else "(还没有其他人发言，你来开启讨论吧)"

            if self.is_oasis:
                # Oasis session → inject identity as system prompt
                system_prompt, user_prompt = _build_discuss_prompt(
                    self.title, self.persona, forum.question, posts_text, split=True,
                )
                messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": user_prompt + instr_suffix})
            else:
                # Regular agent session → no identity injection
                user_prompt = (
                    f"你是被 OASIS 工作流引擎调度的子 Agent，现在被邀请参加一场多专家讨论。\n"
                    f"你的职责是从你自身的专业视角发表观点，不要试图代替其他专家发言或接管整个讨论流程。\n\n"
                    f"讨论主题: {forum.question}\n\n"
                    f"当前论坛内容:\n{posts_text}\n\n"
                    "请以你自身的专业视角参与讨论。在回复中包含一个 JSON 对象（不要包含 markdown 代码块标记，不要包含注释）:\n"
                    '{"teamclaw_type": "oasis reply", "reply_to": 2, "content": "你的观点（200字以内，观点鲜明）", '
                    '"votes": [{"post_id": 1, "direction": "up"}]}\n\n'
                    "说明:\n"
                    "- teamclaw_type: 必须为 \"oasis reply\"\n"
                    "- reply_to: 如果论坛中已有其他人的帖子，你**必须**选择一个帖子ID进行回复；只有在论坛为空时才填 null\n"
                    "- content: 你的发言内容，要有独到见解\n"
                    '- votes: 对其他帖子的投票列表，direction 只能是 "up" 或 "down"。如果没有要投票的帖子，填空列表 []\n'
                    "- JSON 前后可以有其他文字，系统会自动提取 JSON 部分\n"
                    "- ⚠️ JSON 必须写在一行内，content 字段中不能有实际换行符（需要换行请用 \\n 转义）\n"
                    "- 你拥有工具调用能力，如需搜索资料、分析数据来支撑你的观点，可以使用可用的工具。\n"
                    "- 后续轮次只会发送新增帖子，之前的帖子请参考你的对话记忆。"
                )
                messages.append({"role": "user", "content": user_prompt + instr_suffix})

            self._initialized = True
        else:
            if new_posts:
                new_text = _format_posts(new_posts)
                prompt = (
                    f"【第 {forum.current_round} 轮讨论更新】\n"
                    f"以下是自你上次发言后的 {len(new_posts)} 条新帖子：\n\n"
                    f"{new_text}\n\n"
                    "请基于这些新观点以及你之前看到的讨论内容，在回复中包含一个 JSON 对象"
                    "（不要包含 markdown 代码块标记，不要包含注释）：\n"
                    '{"teamclaw_type": "oasis reply", "reply_to": <某个帖子ID>, '
                    '"content": "你的观点（200字以内，观点鲜明）", '
                    '"votes": [{"post_id": <ID>, "direction": "up或down"}]}\n\n'
                    "JSON 前后可以有其他文字，系统会自动提取 JSON 部分。"
                    "⚠️ JSON 必须写在一行内，content 字段中不能有实际换行符（需要换行请用 \\n 转义）。"
                )
            else:
                prompt = (
                    f"【第 {forum.current_round} 轮讨论更新】\n"
                    "本轮没有新的帖子。如果你有新的想法或补充，可以继续发言；"
                    "如果没有，回复一个空 content 即可。\n"
                    '{"teamclaw_type": "oasis reply", "reply_to": null, "content": "", "votes": []}\n\n'
                    "JSON 前后可以有其他文字，系统会自动提取 JSON 部分。"
                )
            messages.append({"role": "user", "content": prompt})

        body: dict = {
            "model": "teambot",
            "messages": messages,
            "stream": False,
            "session_id": self.session_id,
        }
        if self.enabled_tools is not None:
            body["enabled_tools"] = self.enabled_tools
        if self._llm_override:
            body["llm_override"] = self._llm_override

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(timeout=self.timeout)) as client:
                resp = await client.post(
                    self._bot_url,
                    json=body,
                    headers=self._auth_header(),
                )

            if resp.status_code != 200:
                print(f"  [OASIS] ❌ {self.name} bot API error {resp.status_code}: {resp.text[:200]}")
                return

            data = resp.json()
            raw_content = data["choices"][0]["message"]["content"]
            result = _parse_expert_response(raw_content)
            await _apply_response(result, self.name, forum, others)

        except json.JSONDecodeError as e:
            print(f"  [OASIS] ⚠️ {self.name} JSON parse error: {e}")
            try:
                await forum.publish(author=self.name, content=raw_content.strip()[:300])
            except Exception:
                pass
        except Exception as e:
            print(f"  [OASIS] ❌ {self.name} error: {e}")


# ======================================================================
# Backend 3: ExternalExpert — direct call to external OpenAI-compatible API
#   name = "title#ext#id"
#   Does NOT go through local mini_timebot agent.
#   Calls external api_url directly using httpx + OpenAI chat format.
#   ACP agent support: tag (openclaw/codex) determines the ACP binary.
# ======================================================================

# ── ACP long-lived connection helpers (inline from acptest4.py) ──

if _ACP_AVAILABLE:
    class _SecureStreamReader(asyncio.StreamReader):
        """Wraps subprocess stdout, only passing JSON-RPC lines (starts with '{').

        CLI tools (e.g. openclaw/codex acp) may print decorative banners or logs to
        stdout alongside JSON-RPC messages. This filter discards non-JSON lines
        so the ACP protocol layer only sees valid messages.
        """
        def __init__(self, real_reader, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._real_reader = real_reader

        async def readline(self):
            while True:
                line = await self._real_reader.readline()
                if not line:
                    return b""
                if line.strip().startswith(b'{'):
                    return line
                continue

    class _ACPClient(Client):
        """ACP protocol callback handler — collects streaming text chunks."""
        def __init__(self):
            self.chunks: list[str] = []

        async def session_update(self, session_id, update, **kwargs):
            if isinstance(update, AgentMessageChunk) and hasattr(update.content, 'text'):
                self.chunks.append(update.content.text)

        def get_and_clear_text(self) -> str:
            text = "".join(self.chunks)
            self.chunks = []
            return text


class ExternalExpert:
    """
    Expert backed by an external OpenAI-compatible API or ACP long-lived connection.

    Unlike SessionExpert (which calls the local mini_timebot agent),
    ExternalExpert directly calls any OpenAI-compatible endpoint (DeepSeek,
    GPT-4, Moonshot, Ollama, another mini_timebot instance, etc).

    **ACP Agent Support**: When the ``model`` field matches
    ``agent:<agent_name>`` or ``agent:<agent_name>:<session>``, ACP
    long-lived subprocess connections are preferred. If ACP is unavailable
    (binary not found or start failed), falls back to HTTP API when
    ``api_url`` is configured. The ``tag`` field (e.g. "openclaw", "codex")
    determines which CLI binary is used for the ACP subprocess. Session
    defaults to the team name if not specified in the model string.

    The subprocess is started once during ``acp_start()``, messages are
    sent via ``acp_send()``, and the process is cleaned up during
    ``acp_stop()``.

    Session management is handled by the ACP connection internally —
    users cannot and do not need to specify session IDs.

    The external service is assumed to be **stateful** (maintaining its own
    conversation history server-side). Therefore this class sends only
    incremental context: first call sends full forum state + identity;
    subsequent calls send only new posts since last participation.
    No local message history is accumulated.

    Features:
      - ACP agents: persistent long-lived connection (start/send/stop lifecycle)
      - HTTP fallback: when ACP unavailable but api_url is configured
      - Non-agent externals: direct HTTP API call
      - Incremental context (first call = full, subsequent = delta only)
      - Identity injection via system prompt on first call (persona from presets)
    - Works in both discussion mode and execute mode (both require teamclaw_type JSON)
      - Supports custom headers via YAML for service-specific needs

    The external service does NOT need to support session_id or any
    non-standard fields — just standard /v1/chat/completions.
    """

    # Regex to match ACP agent model format: agent:<agent_name> or agent:<agent_name>:<session>
    # Group 1 = agent_name (ignored — real name comes from global_name in JSON)
    # Group 2 (optional) = session suffix (defaults to team name if omitted)
    _AGENT_MODEL_RE = re.compile(r"^agent:([^:]+)(?::(.+))?$")

    # Oasis reply protocol: require agent to reply with JSON containing "teamclaw_type" field
    # Supported types: "oasis reply" (discussion), "oasis choose" (choice/vote)
    # Works in both discussion mode (JSON reply/vote) and execute mode
    _OASIS_REPLY_INSTRUCTION = (
        "\n\n⚠️ IMPORTANT — OASIS JSON reply protocol:\n"
        "当你需要发布给其他 agent 或公开的信息时，必须在回复中包含一个 JSON 对象。\n"
        "JSON 的 \"teamclaw_type\" 字段决定回复类型：\n\n"
        "1. 讨论发言（teamclaw_type=\"oasis reply\"）：\n"
        '{\n'
        '  "teamclaw_type": "oasis reply",\n'
        '  "reply_to": 2,\n'
        '  "content": "你的观点（200字以内，观点鲜明）",\n'
        '  "votes": [{"post_id": 1, "direction": "up"}]\n'
        '}\n\n'
        "2. 选择/投票（teamclaw_type=\"oasis choose\"）：\n"
        '{\n'
        '  "teamclaw_type": "oasis choose",\n'
        '  "choose": {"option": "A", "reason": "理由"},\n'
        '  "content": "补充说明（可选）"\n'
        '}\n\n'
        "注意：\n"
        "- 一轮只能回复一次 JSON，teamclaw_type 字段区分于其他协议的 type 字段\n"
        "- JSON 前后可以有其他文字，系统会自动提取 JSON 部分\n"
        "- ⚠️ JSON 必须是合法的单行 JSON：content 等字符串字段内不能有实际换行，请把所有内容写在同一行内（需要换行请用 \\n 转义）\n"
        "- 没有合规 JSON 的回复不会被发布\n"
        "- 回复最后必须添加三行 end padding 防止传输截断：\n"
        "[end padding]\n"
        "[end padding]\n"
        "[end padding]\n"
    )
    _OASIS_REPLY_MAX_RETRIES = 3

    # Known ACP-capable tool tags: the tag in YAML (e.g. "openclaw", "codex")
    # maps to the CLI binary name used for ACP subprocess.
    _ACP_TOOL_TAGS = {"openclaw", "codex"}

    def __init__(
        self,
        name: str,
        ext_id: str,
        api_url: str,
        api_key: str = "",
        model: str = "gpt-3.5-turbo",
        persona: str = "",
        timeout: float | None = None,
        tag: str = "",
        extra_headers: dict[str, str] | None = None,
        oc_agent_name: str = "",
        team: str = "",
    ):
        self.title = name
        self.ext_id = ext_id
        self.name = f"{name}#ext#{ext_id}"
        self.persona = persona
        self.timeout = timeout or 500.0
        self.tag = tag
        self.model = model
        self._team = team
        self._extra_headers = extra_headers or {}

        # Detect ACP agent model pattern: agent:<name> or agent:<name>:<session>
        # The tag (e.g. "openclaw", "codex") determines which CLI tool to use.
        m = self._AGENT_MODEL_RE.match(model)
        if m:
            self._is_acp_agent = True
            if not oc_agent_name:
                raise ValueError(
                    f"Agent model '{model}' requires a global_name in "
                    f"external_agents.json, but none was found for '{name}'."
                )
            self._oc_agent_name = oc_agent_name

            # Session suffix: explicit from model > team name > "main"
            self._acp_session_suffix = m.group(2) or team or "main"

            # Determine ACP tool binary from tag (openclaw, codex, etc.)
            tag_lower = tag.lower()
            if tag_lower in self._ACP_TOOL_TAGS:
                self._acp_tool_name = tag_lower
            else:
                # Default: use "openclaw" as the ACP tool
                self._acp_tool_name = "openclaw"
            self._acp_bin = shutil.which(self._acp_tool_name)

            # ── ACP long-lived connection state (initialized later via acp_start) ──
            self._acp_available = _ACP_AVAILABLE and bool(self._acp_bin)
            self._acp_proc = None       # subprocess handle
            self._acp_conn = None       # ACP connection
            self._acp_session_id = None # ACP session_id
            self._acp_client = None     # _ACPClient callback handler
            self._acp_started = False   # True after successful acp_start()

            status = "ACP ready" if self._acp_available else f"⚠️ {self._acp_tool_name} not found"
            print(f"  [OASIS] 🔌 ACP agent detected: name={self._oc_agent_name}"
                  f" session={self._acp_session_suffix}"
                  f" tool={self._acp_tool_name}"
                  f" — {status}")
        else:
            self._is_acp_agent = False
            self._oc_agent_name = ""
            self._acp_tool_name = ""
            self._acp_bin = None
            self._acp_available = False
            self._acp_started = False

        # Normalize api_url: strip trailing slash, build full URL
        if api_url:
            api_url = api_url.rstrip("/")
            if not api_url.endswith("/v1/chat/completions"):
                if not api_url.endswith("/v1"):
                    api_url += "/v1"
                api_url += "/chat/completions"
        self._api_url = api_url
        self._api_key = api_key

        # Track state for incremental context (external service holds history)
        self._initialized = False
        self._seen_post_ids: set[int] = set()
        self._acp_dispatch_tasks: set[asyncio.Task] = set()

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self._api_key:
            h["Authorization"] = f"Bearer {self._api_key}"
        h.update(self._extra_headers)
        return h

    # ── ACP long-lived connection lifecycle ──

    async def acp_start(self):
        """Start ACP subprocess and establish persistent connection.

        This should be called once during engine initialization (before any
        participate() calls). The subprocess stays alive across multiple
        send() calls, maintaining conversation context server-side.

        Call order: acp_start() → [participate() * N] → acp_stop()
        """
        if not self._acp_available or not self._is_acp_agent:
            return  # Not an ACP agent, nothing to do

        if self._acp_started:
            print(f"  [OASIS] ⚠️ ACP already started for {self.name}, skipping")
            return

        try:
            # Build the ACP command: <tool> acp --session agent:<name>:<session>
            acp_session_arg = f"agent:{self._oc_agent_name}:{self._acp_session_suffix}"
            cmd = [self._acp_bin, "acp", "--session", acp_session_arg, "--no-prefix-cwd"]

            print(f"  [OASIS] 🔌 Starting ACP connection for {self.name}: "
                  f"{' '.join(cmd)}")

            self._acp_proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,  # capture stderr to avoid noise
            )

            # Wrap stdout with filter that only passes JSON-RPC lines
            safe_stdout = _SecureStreamReader(self._acp_proc.stdout)
            self._acp_client = _ACPClient()
            self._acp_conn = connect_to_agent(
                self._acp_client, self._acp_proc.stdin, safe_stdout
            )

            # ACP handshake: exchange protocol version and capabilities
            await self._acp_conn.initialize(
                protocol_version=PROTOCOL_VERSION,
                client_capabilities=ClientCapabilities(),
                client_info=Implementation(
                    name=f"oasis-expert-{self.ext_id}", version="1.0"
                ),
            )

            # Create a new ACP session
            session = await self._acp_conn.new_session(
                mcp_servers=[], cwd=os.getcwd()
            )
            self._acp_session_id = session.session_id
            self._acp_started = True

            print(f"  [OASIS] ✅ ACP connection established for {self.name} "
                  f"(session_id={self._acp_session_id})")

        except Exception as e:
            print(f"  [OASIS] ❌ ACP start failed for {self.name} (tool={self._acp_tool_name}): {e}")
            self._acp_started = False
            self._acp_available = False  # Disable ACP for this instance
            # Clean up partial state
            await self._acp_cleanup_proc()

    async def acp_send(self, message: str) -> str:
        """Send a message via the ACP persistent connection.

        Requires acp_start() to have been called successfully.
        Returns the agent's response text.
        """
        if not self._acp_started or not self._acp_conn:
            raise RuntimeError(f"ACP not started for {self.name}")

        await self._acp_conn.prompt(
            session_id=self._acp_session_id,
            prompt=[text_block(message)],
        )
        return self._acp_client.get_and_clear_text()

    async def acp_stop(self):
        """Stop the ACP subprocess and release resources.

        Should be called once after all participate() calls are done
        (typically in engine cleanup / finally block).
        Safe to call multiple times — subsequent calls are no-ops.
        """
        if not self._acp_started:
            return

        print(f"  [OASIS] 🔌 Stopping ACP connection for {self.name}")
        self._acp_started = False
        await self._acp_cleanup_proc()

    async def _acp_cleanup_proc(self):
        """Internal helper: forcefully clean up the ACP subprocess."""
        proc = self._acp_proc
        if proc is None or proc.returncode is not None:
            return
        try:
            # Feed EOF to break the SecureStreamReader's read loop
            proc.stdout.feed_eof()
            # Close stdin
            if proc.stdin:
                proc.stdin.close()
            # Terminate gracefully, then force-kill if needed
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=0.5)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
        except Exception as e:
            print(f"  [OASIS] ⚠️ ACP cleanup error for {self.name}: {e}")
        finally:
            self._acp_proc = None
            self._acp_conn = None
            self._acp_session_id = None
            self._acp_client = None

    async def _call_api(self, messages: list[dict], timeout_override: float | None = ...) -> str:
        """Send messages to external API and return the assistant response text.

        For ACP agent-type externals (model="agent:<name>" with tag openclaw/codex/etc):
          - Prefers ACP persistent connection when available.
          - Falls back to HTTP API if ACP not started and api_url is configured.
          - Raises RuntimeError only when neither ACP nor HTTP is available.

        For non-agent externals: direct HTTP API call.

        Args:
            timeout_override: Explicit timeout value. None = no timeout;
                              ... (default sentinel) = use self.timeout.
        """
        effective_timeout = self.timeout if timeout_override is ... else timeout_override

        # ── ACP agent type: keep legacy user-only extraction for sync paths ──
        if self._is_acp_agent:
            cli_message = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    cli_message = msg.get("content", "")
                    break
            if not cli_message:
                cli_message = messages[-1].get("content", "") if messages else ""

            if self._acp_started:
                reply = await self.acp_send(cli_message)
                print(f"  [OASIS] 🔌 ACP send success for {self.name} ({len(reply)} chars)")
                return reply
            else:
                # ACP not available — try HTTP fallback
                if self._api_url:
                    print(f"  [OASIS] ⚠️ ACP not started for {self.name}, falling back to HTTP API")
                else:
                    raise RuntimeError(
                        f"ACP connection not started for agent {self.name} "
                        f"(agent={self._oc_agent_name}, tool={self._acp_tool_name}) "
                        f"and no api_url configured for HTTP fallback."
                    )

        # ── HTTP API call (non-agent type, or ACP agent HTTP fallback) ──
        if not self._api_url:
            raise RuntimeError(f"No api_url configured for external expert {self.name}")
        body = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(timeout=effective_timeout)) as client:
                resp = await client.post(self._api_url, json=body, headers=self._headers())
            if resp.status_code != 200:
                raise RuntimeError(f"External API error {resp.status_code}: {resp.text[:300]}")
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as api_err:
            raise RuntimeError(f"API call failed for {self.name}: {api_err}")

    def _inject_oasis_reply_instruction(self, messages: list[dict]) -> None:
        """Append OASIS JSON reply instruction to the last user message (ACP agent only)."""
        if not self._is_acp_agent:
            return
        for msg in reversed(messages):
            if msg.get("role") == "user":
                msg["content"] = msg["content"] + self._OASIS_REPLY_INSTRUCTION
                return

    def _build_callback_hint(self, forum: DiscussionForum, round_num: int) -> str:
        """Return the CLI template ACP agents should use for explicit OASIS callback."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        topic_id = shlex.quote(forum.topic_id)
        user_id = shlex.quote(forum.user_id or "anonymous")
        author = shlex.quote(self.name)
        return (
            f"cd {shlex.quote(project_root)}\n"
            f"uv run scripts/cli.py -u {user_id} topics callback --topic-id {topic_id} --author {author} "
            f"--round-num {round_num} --data '<JSON对象>'"
        )

    def _compose_acp_prompt(self, messages: list[dict]) -> str:
        """Compose the transient ACP prompt for one round without replaying old turns."""
        parts: list[str] = []
        for msg in messages:
            content = (msg.get("content") or "").strip()
            if not content:
                continue
            if msg.get("role") == "system":
                parts.append(f"[系统设定]\n{content}")
            else:
                parts.append(content)
        return "\n\n".join(parts).strip()

    async def _run_ephemeral_acp_prompt(self, prompt_text: str) -> None:
        """Dispatch one ACP prompt, then close immediately without waiting for reply."""
        if not self._acp_available or not self._acp_bin:
            raise RuntimeError(f"ACP unavailable for {self.name}")

        proc = None
        prompt_task: asyncio.Task | None = None
        try:
            acp_session_arg = f"agent:{self._oc_agent_name}:{self._acp_session_suffix}"
            cmd = [self._acp_bin, "acp", "--session", acp_session_arg, "--no-prefix-cwd"]
            print(f"  [OASIS] 🚀 Dispatch ACP prompt for {self.name}: {' '.join(cmd)}")

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            safe_stdout = _SecureStreamReader(proc.stdout)
            client = _ACPClient()
            conn = connect_to_agent(client, proc.stdin, safe_stdout)
            await conn.initialize(
                protocol_version=PROTOCOL_VERSION,
                client_capabilities=ClientCapabilities(),
                client_info=Implementation(name=f"oasis-expert-{self.ext_id}", version="1.0"),
            )
            session = await conn.new_session(mcp_servers=[], cwd=os.getcwd())
            prompt_task = asyncio.create_task(
                conn.prompt(
                    session_id=session.session_id,
                    prompt=[text_block(prompt_text)],
                )
            )
            # Give the protocol layer a brief chance to flush the outgoing prompt,
            # then close the ACP process regardless of whether the agent replied.
            await asyncio.sleep(0.15)
        except Exception as e:
            print(f"  [OASIS] ❌ ACP dispatch failed for {self.name}: {e}")
        finally:
            if prompt_task and not prompt_task.done():
                prompt_task.cancel()
            if proc is not None and proc.returncode is None:
                try:
                    proc.stdout.feed_eof()
                    if proc.stdin:
                        proc.stdin.close()
                    proc.terminate()
                    try:
                        await asyncio.wait_for(proc.wait(), timeout=0.5)
                    except asyncio.TimeoutError:
                        proc.kill()
                        await proc.wait()
                except Exception as cleanup_err:
                    print(f"  [OASIS] ⚠️ ACP cleanup error for {self.name}: {cleanup_err}")

    def _dispatch_acp_prompt(self, prompt_text: str) -> asyncio.Task:
        """Start one transient ACP dispatch task and keep a reference until completion."""
        task = asyncio.create_task(self._run_ephemeral_acp_prompt(prompt_text))
        self._acp_dispatch_tasks.add(task)
        task.add_done_callback(lambda t: self._acp_dispatch_tasks.discard(t))
        return task

    async def _call_api_with_agent_callback(
        self,
        forum: DiscussionForum,
        messages: list[dict],
        timeout_override: float | None = ...,
    ) -> None:
        """Dispatch ACP work, then wait until the agent callbacks or times out."""
        effective_timeout = self.timeout if timeout_override is ... else timeout_override
        round_num = forum.current_round
        before_count = await forum.count_posts_by_author(self.name, round_num=round_num)
        prompt_text = self._compose_acp_prompt(messages)
        dispatch_task = self._dispatch_acp_prompt(prompt_text)
        wait_timeout = effective_timeout if effective_timeout is not None else self.timeout
        callback_ok = await forum.wait_for_author_post(
            self.name,
            round_num=round_num,
            min_count=before_count + 1,
            timeout=max(float(wait_timeout or 0.0), 0.0),
        )

        if callback_ok:
            print(f"  [OASIS] ✅ {self.name} callback applied for round {round_num}")
            return

        print(f"  [OASIS] ⏰ {self.name} callback timeout at round {round_num}")
        if dispatch_task.done() and dispatch_task.exception():
            print(f"  [OASIS] ⚠️ {self.name} ACP task exception: {dispatch_task.exception()}")

    # Regex to strip [end padding] lines (may be partially truncated)
    _END_PADDING_RE = re.compile(r"\[end\s*padding\]", re.IGNORECASE)

    @staticmethod
    def _extract_oasis_json(text: str) -> tuple[str, dict | None]:
        """Try to extract a valid OASIS JSON object from agent reply text.

        Tolerant parsing: the JSON can appear anywhere in the text surrounded
        by arbitrary prose.  We look for the first '{' ... '}' that contains
        a recognised "teamclaw_type" field ("oasis reply" or "oasis choose").

        Returns (status, parsed_dict):
          - ("found", dict)   — valid JSON with recognised teamclaw_type extracted
          - ("missing", None) — no valid JSON found
        """
        # Strip [end padding] lines first (they are anti-truncation padding)
        cleaned = ExternalExpert._END_PADDING_RE.sub("", text).strip()

        # Strategy 1: find all top-level { ... } candidates
        # We use a simple brace-depth scanner for robustness
        candidates = []
        depth = 0
        start_idx = -1
        for i, ch in enumerate(cleaned):
            if ch == '{':
                if depth == 0:
                    start_idx = i
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and start_idx >= 0:
                    candidates.append(cleaned[start_idx:i + 1])
                    start_idx = -1

        # Also try regex fallback for nested/malformed cases
        if not candidates:
            m = re.search(r"\{[\s\S]*\}", cleaned)
            if m:
                candidates.append(m.group(0))

        for candidate in candidates:
            # Try direct parse first, then with control-char fix for tolerance
            for text in (candidate, _fix_json_control_chars(candidate)):
                try:
                    obj = json.loads(text)
                    if isinstance(obj, dict) and obj.get("teamclaw_type") in ("oasis reply", "oasis choose"):
                        return ("found", obj)
                except (json.JSONDecodeError, ValueError):
                    continue

        return ("missing", None)

    async def _call_api_with_oasis_check(self, messages: list[dict], **kwargs) -> str | dict:
        """Call API up to _OASIS_REPLY_MAX_RETRIES times within one participate turn.

        For ACP agents, inject the OASIS JSON protocol instruction, then:
          1. Strict extraction: look for JSON with recognised "teamclaw_type" → return dict
          2. Tolerant extraction: try _parse_expert_response (any valid JSON) → return dict
          3. Both failed → ask agent to retry with correct format
          4. After all retries exhausted → return raw text of the LAST reply

        This "tolerant-first" strategy avoids wasting retries when the agent
        returns valid JSON that simply lacks the teamclaw_type field.

        No cross-reply buffering: each retry is independent.
        Each participate() call is independent; no state carries across rounds.
        """
        if not self._is_acp_agent:
            return await self._call_api(messages, **kwargs)

        self._inject_oasis_reply_instruction(messages)

        last_raw = ""
        for attempt in range(1, self._OASIS_REPLY_MAX_RETRIES + 1):
            raw_reply = await self._call_api(messages, **kwargs)
            last_raw = raw_reply

            # Step 1: strict extraction — look for teamclaw_type JSON
            status, parsed = self._extract_oasis_json(raw_reply)
            if status == "found":
                print(f"  [OASIS] ✅ {self.name} valid OASIS JSON extracted "
                      f"(teamclaw_type={parsed.get('teamclaw_type')}, attempt {attempt}/{self._OASIS_REPLY_MAX_RETRIES})")
                return parsed

            # Step 2: tolerant extraction — accept any valid JSON
            try:
                tolerant_result = _parse_expert_response(raw_reply)
                if isinstance(tolerant_result, dict):
                    print(f"  [OASIS] ✅ {self.name} tolerant JSON extracted "
                          f"(no teamclaw_type, attempt {attempt}/{self._OASIS_REPLY_MAX_RETRIES})")
                    return tolerant_result
            except json.JSONDecodeError:
                pass

            # Step 3: no valid JSON at all — ask agent to retry
            print(f"  [OASIS] 💭 {self.name} no valid JSON found "
                  f"(attempt {attempt}/{self._OASIS_REPLY_MAX_RETRIES})")

            # Feed reply back and ask for correct format
            messages.append({"role": "assistant", "content": raw_reply})
            messages.append({"role": "user", "content": (
                "你的回复中没有检测到合规的 OASIS JSON。请严格按照以下格式重新回复：\n\n"
                "在你的回复中包含一个 JSON 对象，其中 \"teamclaw_type\" 字段为 \"oasis reply\" 或 \"oasis choose\"。\n"
                "⚠️ JSON 必须写在一行内，content 字段中不能有实际换行符（需要换行请用 \\n 转义），否则系统无法解析。\n"
                "例如：\n"
                '{"teamclaw_type": "oasis reply", "reply_to": 2, "content": "你的观点", "votes": []}\n\n'
                "JSON 前后可以有其他文字。回复最后必须添加：\n"
                "[end padding]\n"
                "[end padding]\n"
                "[end padding]\n"
            )})

        # All attempts exhausted — return raw text of the last reply
        print(f"  [OASIS] ⚠️ {self.name} {self._OASIS_REPLY_MAX_RETRIES} retries without "
              f"valid JSON, returning last raw reply")
        return last_raw.strip()

    async def participate(
        self,
        forum: DiscussionForum,
        instruction: str = "",
        discussion: bool = True,
        visible_authors: set[str] | None = None,
        from_round: int | None = None,
    ):
        others = await forum.browse(
            viewer=self.name,
            exclude_self=True,
            visible_authors=visible_authors if not discussion else None,
            from_round=from_round if not discussion else None,
        )

        if not discussion:
            # ── Execute mode (also requires teamclaw_type JSON protocol) ──
            new_posts = [p for p in others if p.id not in self._seen_post_ids]
            self._seen_post_ids.update(p.id for p in others)

            if self._is_acp_agent:
                callback_hint = self._build_callback_hint(forum, forum.current_round)
                messages: list[dict] = []
                if not self._initialized:
                    identity_prompt = _build_identity_prompt(self.title, self.persona).strip()
                    if identity_prompt:
                        messages.append({"role": "system", "content": identity_prompt})
                    messages.append({
                        "role": "user",
                        "content": _build_execute_callback_prompt(
                            forum.question,
                            _format_posts(others) if others else "",
                            callback_hint,
                            instruction=instruction,
                            first_turn=True,
                        ),
                    })
                    self._initialized = True
                else:
                    messages.append({
                        "role": "user",
                        "content": _build_execute_callback_prompt(
                            forum.question,
                            _format_posts(new_posts) if new_posts else "",
                            callback_hint,
                            instruction=instruction,
                            first_turn=False,
                        ),
                    })

                try:
                    await self._call_api_with_agent_callback(forum, messages, timeout_override=None)
                except Exception as e:
                    print(f"  [OASIS] ❌ {self.name} (external ACP execute) error: {e}")
                return

            _EXEC_JSON_HINT = (
                '\n\n请将你的执行结果用以下 JSON 格式返回'
                '（不要包含 markdown 代码块标记，不要包含注释）：\n'
                '⚠️ JSON 必须写在一行内，content 字段中不能有实际换行符（需要换行请用 \\n 转义）。\n'
                '{"teamclaw_type": "oasis reply", "reply_to": null, '
                '"content": "你的执行结果", "votes": []}\n'
                'JSON 前后可以有其他文字。回复最后请添加：\n'
                '[end padding]\n'
                '[end padding]\n'
                '[end padding]\n'
            )

            messages: list[dict] = []
            if not self._initialized:
                if self.persona:
                    messages.append({"role": "system", "content": _build_identity_prompt(self.title, self.persona).strip()})
                task_parts = [f"任务主题: {forum.question}"]
                if instruction:
                    task_parts.append(f"\n执行指令: {instruction}")
                if others:
                    task_parts.append(f"\n前序 agent 的执行结果:\n{_format_posts(others)}")
                task_parts.append("\n请直接执行任务并返回结果。")
                task_parts.append(_EXEC_JSON_HINT)
                task_parts.append(_BEHAVIOR_RULES)
                messages.append({"role": "user", "content": "\n".join(task_parts)})
                self._initialized = True
            else:
                ctx_parts = [f"【第 {forum.current_round} 轮】"]
                if instruction:
                    ctx_parts.append(f"执行指令: {instruction}")
                if new_posts:
                    ctx_parts.append(f"其他 agent 的新结果:\n{_format_posts(new_posts)}")
                ctx_parts.append("请继续执行任务并返回结果。")
                ctx_parts.append(_EXEC_JSON_HINT)
                ctx_parts.append(_BEHAVIOR_RULES)
                messages.append({"role": "user", "content": "\n".join(ctx_parts)})

            try:
                reply = await self._call_api_with_oasis_check(messages, timeout_override=None)
                if isinstance(reply, dict):
                    result = reply
                else:
                    result = _parse_expert_response(reply)
                await _apply_response(result, self.name, forum, others)
            except json.JSONDecodeError as e:
                print(f"  [OASIS] ⚠️ {self.name} (external execute) JSON parse error: {e}")
                raw_content = reply if isinstance(reply, str) else str(reply)
                try:
                    await forum.publish(author=self.name, content=raw_content.strip()[:2048])
                except Exception:
                    pass
            except Exception as e:
                print(f"  [OASIS] ❌ {self.name} (external) error: {e}")
            return

        # ── Discussion mode ──
        new_posts = [p for p in others if p.id not in self._seen_post_ids]
        self._seen_post_ids.update(p.id for p in others)

        if self._is_acp_agent:
            callback_hint = self._build_callback_hint(forum, forum.current_round)
            messages: list[dict] = []
            if not self._initialized:
                posts_text = _format_posts(others) if others else "(还没有其他人发言，你来开启讨论吧)"
                system_prompt, user_prompt = _build_discuss_callback_prompt(
                    self.title,
                    self.persona,
                    forum.question,
                    posts_text,
                    callback_hint,
                    instruction=instruction,
                )
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": user_prompt})
                self._initialized = True
            else:
                if new_posts:
                    posts_text = _format_posts(new_posts)
                else:
                    posts_text = "本轮没有新的帖子。如果你没有新的观点，可以跳过本轮 callback。"
                system_prompt, user_prompt = _build_discuss_callback_prompt(
                    self.title,
                    self.persona,
                    forum.question,
                    posts_text,
                    callback_hint,
                    instruction=instruction,
                )
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": user_prompt})

            try:
                await self._call_api_with_agent_callback(forum, messages)
            except Exception as e:
                print(f"  [OASIS] ❌ {self.name} (external ACP discussion) error: {e}")
            return

        messages: list[dict] = []
        if not self._initialized:
            posts_text = _format_posts(others) if others else "(还没有其他人发言，你来开启讨论吧)"
            system_prompt, user_prompt = _build_discuss_prompt(
                self.title, self.persona, forum.question, posts_text, split=True,
            )
            if instruction:
                user_prompt += f"\n\n📋 本轮你的专项指令：{instruction}\n请在回复中重点关注和执行这个指令。"
            messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_prompt})
            self._initialized = True
        else:
            if new_posts:
                new_text = _format_posts(new_posts)
                prompt = (
                    f"【第 {forum.current_round} 轮讨论更新】\n"
                    f"以下是自你上次发言后的 {len(new_posts)} 条新帖子：\n\n"
                    f"{new_text}\n\n"
                    "请基于这些新观点以及你之前看到的讨论内容，在回复中包含一个 JSON 对象"
                    "（不要包含 markdown 代码块标记，不要包含注释）：\n"
                    '{"teamclaw_type": "oasis reply", "reply_to": <某个帖子ID>, '                    '"content": "你的观点（200字以内，观点鲜明）", '
                    '"votes": [{"post_id": <ID>, "direction": "up或down"}]}\n\n'                    "JSON 前后可以有其他文字。回复最后请添加：\n"
                    "[end padding]\n"
                    "[end padding]\n"
                    "[end padding]\n"
                )
            else:
                prompt = (
                    f"【第 {forum.current_round} 轮讨论更新】\n"
                    "本轮没有新的帖子。如果你有新的想法或补充，可以继续发言；"
                    "如果没有，回复一个空 content 即可。\n"
                    '{"teamclaw_type": "oasis reply", "reply_to": null, "content": "", "votes": []}\n\n'
                    "回复最后请添加：\n"                    "[end padding]\n"
                    "[end padding]\n"
                    "[end padding]\n"
                )
            if instruction:
                prompt += f"\n📋 本轮你的专项指令：{instruction}\n请在回复中重点关注和执行这个指令。"
            messages.append({"role": "user", "content": prompt})

        try:
            reply = await self._call_api_with_oasis_check(messages)
            # If _call_api_with_oasis_check already returned a parsed dict, use it directly
            if isinstance(reply, dict):
                result = reply
            else:
                result = _parse_expert_response(reply)
            await _apply_response(result, self.name, forum, others)
        except json.JSONDecodeError as e:
            print(f"  [OASIS] ⚠️ {self.name} (external) JSON parse error: {e}")
            raw_content = reply if isinstance(reply, str) else str(reply)
            try:
                await forum.publish(author=self.name, content=raw_content.strip()[:2048])
            except Exception:
                pass
        except Exception as e:
            print(f"  [OASIS] ❌ {self.name} (external) error: {e}")

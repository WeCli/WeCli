import asyncio
import base64
import json
import os
import re
import secrets
import shutil
import time
from typing import Any, Callable, Literal

import httpx
from fastapi import HTTPException

from auth_utils import extract_user_password_session, is_internal_bearer, parse_bearer_parts
from checkpoint_repository import list_thread_ids_by_prefix
from group_repository import (
    add_group_member,
    clear_group_members,
    create_group_with_members,
    delete_group as delete_group_records,
    get_group,
    get_group_member_by_global_id,
    get_group_owner,
    group_exists,
    init_group_db as init_group_db_repo,
    insert_group_message,
    list_group_member_targets,
    list_group_members,
    list_group_messages_after,
    list_groups_for_user,
    list_recent_group_messages,
    remove_group_member,
    update_group_name,
)
from group_models import Attachment, GroupCreateRequest, GroupAddMemberRequest, GroupMessageRequest, GroupUpdateRequest
from logging_utils import get_logger
from session_summary import first_human_title

logger = get_logger("group_service")

# Known ACP-compatible tool binaries (must match CLI status platforms list)
_ACP_KNOWN_TOOLS: frozenset = frozenset({"openclaw", "codex", "claude", "gemini", "aider"})

# ACP long-lived connection support
try:
    from acp import PROTOCOL_VERSION, Client, connect_to_agent, text_block, image_block, audio_block
    from acp.schema import ClientCapabilities, Implementation, AgentMessageChunk
    _ACP_AVAILABLE = True
except ImportError:
    _ACP_AVAILABLE = False

# Project root for team-scoped paths
_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

# ── Text MIME helpers (shared with system_service) ──
_TEXT_MIME_PREFIXES = ("text/",)
_TEXT_MIME_EXACT = {
    "application/json", "application/xml", "application/javascript",
    "application/typescript", "application/x-yaml", "application/yaml",
    "application/toml", "application/x-toml",
    "application/sql", "application/graphql",
    "application/x-sh", "application/x-python",
    "application/csv", "application/x-csv",
    "application/ld+json", "application/manifest+json",
}


def _is_text_mime(mime_type: str) -> bool:
    """判断 MIME 类型是否为文本类。"""
    mime = mime_type.lower().strip()
    if any(mime.startswith(p) for p in _TEXT_MIME_PREFIXES):
        return True
    if mime in _TEXT_MIME_EXACT:
        return True
    if mime.endswith("+json") or mime.endswith("+xml"):
        return True
    return False


def _decode_att_text(att_data: str, max_chars: int = 50000) -> str | None:
    """尝试将附件 base64 数据解码为 UTF-8 文本。失败返回 None。"""
    try:
        raw = base64.b64decode(att_data)
        text = raw.decode("utf-8")
        if len(text) > max_chars:
            text = text[:max_chars] + f"\n\n... (文件过长，已截断，共 {len(raw)} 字节)"
        return text
    except Exception:
        return None


def _load_team_internal_agents(user_id: str, team: str) -> list[dict]:
    """Load internal agents from team's internal_agents.json.

    Returns list of {"user_id": user_id, "global_id": session, "short_name": name, "member_type": "oasis", "tag": ...}
    """
    if not user_id or not team:
        return []
    path = os.path.join(_PROJECT_ROOT, "data", "user_files", user_id, "teams", team, "internal_agents.json")
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        result = []
        for a in data:
            if not isinstance(a, dict) or "session" not in a:
                continue
            result.append({
                "user_id": user_id,
                "global_id": a.get("session", ""),
                "short_name": a.get("name", ""),
                "member_type": "oasis",
                "tag": a.get("tag", ""),
            })
        return result
    except Exception:
        return []


def _load_team_external_agents(user_id: str, team: str) -> list[dict]:
    """Load external agents from team's external_agents.json.

    Returns list of {"user_id": "ext", "global_id": global_name, "short_name": name, "member_type": "ext", ...}
    """
    if not user_id or not team:
        return []
    path = os.path.join(_PROJECT_ROOT, "data", "user_files", user_id, "teams", team, "external_agents.json")
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        result = []
        for a in data:
            if not isinstance(a, dict) or "name" not in a:
                continue
            # Support both "config" and "meta" field names for external agent config
            ext_config = a.get("config") or a.get("meta") or {}
            result.append({
                "user_id": "ext",
                "global_id": a.get("global_name", ""),
                "short_name": a.get("name", ""),
                "member_type": "ext",
                "tag": a.get("tag", ""),
                "global_name": a.get("global_name", ""),
                "api_url": ext_config.get("api_url", ""),
                "api_key": ext_config.get("api_key", ""),
                "model": ext_config.get("model", ""),
            })
        return result
    except Exception:
        return []


def _load_team_members(user_id: str, team: str) -> list[dict]:
    """Load all team members (internal + external agents).

    Returns list of member dicts with user_id, session_id, member_type, etc.
    """
    internal = _load_team_internal_agents(user_id, team)
    external = _load_team_external_agents(user_id, team)
    return internal + external


async def init_group_db(group_db_path: str) -> None:
    """初始化群聊数据库表结构。"""
    await init_group_db_repo(group_db_path)


# ACP connection cache: key = (user_id, team, agent_name), value = ACP connection info
_acp_connections: dict[tuple, dict] = {}


if _ACP_AVAILABLE:
    class _SecureStreamReader(asyncio.StreamReader):
        """Wraps subprocess stdout, only passing JSON-RPC lines."""
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


class GroupService:
    def __init__(
        self,
        *,
        internal_token: str,
        verify_password: Callable[[str, str], bool],
        checkpoint_db_path: str,
        group_db_path: str,
        agent: Any,
    ):
        self.internal_token = internal_token
        self.verify_password = verify_password
        self.checkpoint_db_path = checkpoint_db_path
        self.group_db_path = group_db_path
        self.agent = agent
        self.group_muted: set[str] = set()

    def parse_group_auth(self, authorization: str | None):
        """从 Bearer token 解析用户认证，返回 (user_id, password, session_id)。"""
        parts = parse_bearer_parts(authorization)
        if not parts:
            raise HTTPException(status_code=401, detail="Missing Authorization header")
        if len(parts) < 2:
            raise HTTPException(status_code=401, detail="Invalid token format")

        if is_internal_bearer(parts, self.internal_token):
            uid = parts[1] if len(parts) >= 2 and parts[1] else "system"
            sid = parts[2] if len(parts) > 2 else "default"
            return uid, "", sid

        parsed = extract_user_password_session(parts, default_session="default")
        if not parsed:
            raise HTTPException(status_code=401, detail="Invalid token format")
        uid, pw, sid = parsed
        if not self.verify_password(uid, pw):
            raise HTTPException(status_code=401, detail="认证失败")
        return uid, pw, sid

    async def get_agent_title(self, user_id: str, session_id: str) -> str:
        """从 checkpoint 提取 agent 的 session title（第一条非系统触发 HumanMessage 前50字）。"""
        tid = f"{user_id}#{session_id}"
        try:
            config = {"configurable": {"thread_id": tid}}
            snapshot = await self.agent.agent_app.aget_state(config)
            msgs = snapshot.values.get("messages", []) if snapshot and snapshot.values else []
            title = first_human_title(
                msgs,
                skip_prefixes=("[系统触发]", "[外部学术会议邀请]", "[群聊"),
                title_len=50,
                list_fallback="",
                default=session_id,
            )
            return title
        except Exception:
            pass
        return session_id

    async def _send_to_acp_agent(
        self,
        agent_info: dict,
        message: str,
        attachments: list[Attachment] | None = None,
        metadata: dict | None = None,
    ) -> str | None:
        """Send message to external agent via ACP protocol.

        Args:
            agent_info: {"global_name", "tag", "api_url", "api_key", "model", ...}
            message: The message to send (already contains teamclaw_type instruction in prompt)
            attachments: Optional list of Attachment objects (images/audio/files)
            metadata: Optional dict for ACP _meta field control (e.g., resetSession)

        Returns:
            Agent response text, or None if failed.
        """
        if not _ACP_AVAILABLE:
            logger.warning("ACP not available, falling back to HTTP for %s", agent_info.get("name"))
            return await self._send_to_http_agent(agent_info, message, attachments=attachments)

        tag = agent_info.get("tag", "").lower()
        global_name = agent_info.get("global_name", "")
        if not global_name:
            logger.warning("No global_name for external agent %s", agent_info.get("name"))
            return None

        # Determine ACP tool binary from tag
        acp_tool = tag if tag in _ACP_KNOWN_TOOLS else "openclaw"
        acp_bin = shutil.which(acp_tool)
        if not acp_bin:
            logger.warning("ACP binary '%s' not found, falling back to HTTP", acp_tool)
            return await self._send_to_http_agent(agent_info, message, attachments=attachments)

        # Build ACP session arg
        acp_session = f"agent:{global_name}:group_chat"

        try:
            cmd = [acp_bin, "acp", "--session", acp_session, "--no-prefix-cwd"]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            safe_stdout = _SecureStreamReader(proc.stdout)
            client = _ACPClient()
            conn = connect_to_agent(client, proc.stdin, safe_stdout)

            # ACP handshake
            await conn.initialize(
                protocol_version=PROTOCOL_VERSION,
                client_capabilities=ClientCapabilities(),
                client_info=Implementation(name="teamclaw-group", version="1.0"),
            )

            # Support resetSession via _meta field
            session = await conn.new_session(
                mcp_servers=[],
                cwd=os.getcwd(),
                metadata=metadata
            )

            # Build prompt blocks: text + optional multimodal attachments
            prompt_blocks = [text_block(message)]
            if attachments:
                for att in attachments:
                    if att.type == "image":
                        prompt_blocks.append(image_block(att.data, att.mime_type))
                    elif att.type == "audio":
                        prompt_blocks.append(audio_block(att.data, att.mime_type))
                    else:
                        # file type: try to decode text content, fallback to description
                        if _is_text_mime(att.mime_type):
                            decoded = _decode_att_text(att.data)
                            if decoded is not None:
                                prompt_blocks.append(text_block(
                                    f"\n📄 附件「{att.name}」内容:\n```\n{decoded}\n```"
                                ))
                            else:
                                prompt_blocks.append(text_block(f"[附件: {att.name} ({att.mime_type}), 解码失败]"))
                        else:
                            prompt_blocks.append(text_block(f"[附件: {att.name} ({att.mime_type}), 二进制文件无法展示]"))

            await conn.prompt(
                session_id=session.session_id,
                prompt=prompt_blocks,
                metadata=metadata,
            )

            reply = client.get_and_clear_text()

            # Cleanup
            proc.stdout.feed_eof()
            if proc.stdin:
                proc.stdin.close()
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=0.5)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()

            return reply if reply else None

        except Exception as e:
            logger.warning("ACP send failed for %s: %s", global_name, e)
            return await self._send_to_http_agent(agent_info, message, attachments=attachments)

    async def _send_to_http_agent(
        self,
        agent_info: dict,
        message: str,
        attachments: list[Attachment] | None = None,
    ) -> str | None:
        """Fallback: send message to external agent via HTTP API.
        
        Message already contains teamclaw_type instruction from caller.
        Supports multimodal content via OpenAI image_url / input_audio format.
        """
        api_url = agent_info.get("api_url", "")
        api_key = agent_info.get("api_key", "")
        model = agent_info.get("model", "gpt-3.5-turbo")

        if not api_url:
            logger.warning("No api_url for external agent %s", agent_info.get("name"))
            return None

        # Normalize URL
        api_url = api_url.rstrip("/")
        if not api_url.endswith("/v1/chat/completions"):
            if not api_url.endswith("/v1"):
                api_url += "/v1"
            api_url += "/chat/completions"

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # Build message content (multimodal if attachments present)
        if attachments:
            content_parts: list[dict] = [{"type": "text", "text": message}]
            for att in attachments:
                if att.type == "image":
                    data_uri = f"data:{att.mime_type};base64,{att.data}"
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {"url": data_uri},
                    })
                elif att.type == "audio":
                    content_parts.append({
                        "type": "input_audio",
                        "input_audio": {
                            "data": att.data,
                            "format": att.mime_type.split("/")[-1],
                        },
                    })
                else:
                    # Generic file: try to decode text content, fallback to description
                    if _is_text_mime(att.mime_type):
                        decoded = _decode_att_text(att.data)
                        if decoded is not None:
                            content_parts.append({
                                "type": "text",
                                "text": f"\n📄 附件「{att.name}」内容:\n```\n{decoded}\n```",
                            })
                        else:
                            content_parts.append({
                                "type": "text",
                                "text": f"[附件: {att.name} ({att.mime_type}), 解码失败]",
                            })
                    else:
                        content_parts.append({
                            "type": "text",
                            "text": f"[附件: {att.name} ({att.mime_type}), 二进制文件无法展示]",
                        })
            msg_content: str | list = content_parts
        else:
            msg_content = message

        body = {
            "model": model,
            "messages": [{"role": "user", "content": msg_content}],
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(api_url, json=body, headers=headers)
            if resp.status_code != 200:
                logger.warning("HTTP API error %d for %s: %s", resp.status_code, agent_info.get("name"), resp.text[:200])
                return None
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning("HTTP send failed for %s: %s", agent_info.get("name"), e)
            return None

    async def _handle_external_agent_reply(
        self,
        group_id: str,
        agent_info: dict,
        message: str,
        agent_name: str,
        attachments: list[Attachment] | None = None,
    ):
        """Send message to external agent and handle reply.

        ACP response is NOT automatically posted to group.
        Agent should use CLI tool `groups send` to send messages if needed.
        """
        # Send message (no type instruction - agent decides based on prompt)
        reply = await self._send_to_acp_agent(agent_info, message, attachments=attachments)
        if not reply:
            logger.info("External agent %s did not reply", agent_name)
            return

        # Log the reply but don't post to group
        # Agent should use CLI tool to send messages to group
        logger.info("External agent %s replied (not auto-posting to group): %s", agent_name, reply[:200] if reply else "")

    async def broadcast_to_group(
        self,
        group_id: str,
        sender: str,
        content: str,
        exclude_sender_display: str = "",
        mentions: list[str] | None = None,
        user_id: str = "",
        attachments: list[Attachment] | None = None,
    ):
        """向群内 agent 成员广播消息（异步 fire-and-forget）。

        members 直接从数据库读取，包含 global_id / short_name / tag / member_type。
        exclude_sender_display: 用 tag#type#short_name 格式排除发送者自己，
        避免 global_id 在不同 agent 平台间可能冲突的问题。
        """
        if group_id in self.group_muted:
            logger.info("群 %s 已静音，跳过广播", group_id)
            return
        members = await list_group_member_targets(self.group_db_path, group_id)
        member_count = len(members)
        is_private_chat = member_count <= 2  # owner + 1 agent = 私聊

        # Build external agent config map by global_id (need api_url etc. for ACP/HTTP)
        # We need to load external agent configs from the owner's team files
        # since api_url/api_key are not stored in DB
        external_agents_map: dict[str, dict] = {}
        if user_id:
            owner = user_id
            # Scan all teams for this owner to find external agent configs
            teams_dir = os.path.join(_PROJECT_ROOT, "data", "user_files", owner, "teams")
            if os.path.isdir(teams_dir):
                for team_dir in os.listdir(teams_dir):
                    for ea in _load_team_external_agents(owner, team_dir):
                        gid = ea.get("global_id", "")
                        if gid:
                            external_agents_map[gid] = ea

        for user_id_member, global_id, is_agent, member_type, short_name, tag in members:
            if group_id in self.group_muted:
                logger.info("群 %s 广播中途被静音，停止", group_id)
                return
            if not is_agent:
                continue
            # 用 tag#type#short_name#global_id 排除发送者自己
            member_display = f"{tag}#{member_type}#{short_name}#{global_id}" if tag else f"#{member_type}#{short_name}#{global_id}"
            if exclude_sender_display and member_display == exclude_sender_display:
                continue

            if mentions and global_id not in mentions:
                continue

            # Build message - use prompt instructions to guide agent behavior
            agent_identity = f"你是「{short_name}」"
            sender_display = f"{tag}#{member_type}#{short_name}#{global_id}" if tag else f"#{member_type}#{short_name}#{global_id}"
            cli_hint = (f"cd {_PROJECT_ROOT} && "
                        f"uv run scripts/cli.py groups send --group-id {group_id} --sender '{sender_display}' --message '你的回复内容'")

            if is_private_chat:
                # 私聊：不需要群聊标记，直接告知是私信
                msg_prefix = f"[私聊] {sender} 说:\n"
                msg_suffix = (f"\n\n{agent_identity}，这是用户发给你的私信，请认真回复。\n"
                              "请先 cd 到项目目录，然后使用 CLI 工具发送消息：\n"
                              f"{cli_hint}\n"
                              "注意：不要在 ACP 响应中直接输出内容，系统不会自动发布你的回复。\n"
                              "[end padding]\n[end padding]\n[end padding]")
            elif mentions and global_id in mentions:
                msg_prefix = f"[群聊 {group_id} 成员数:{member_count}] {sender} @你 说:\n"
                msg_suffix = (f"\n\n⚠️ 这是专门 @你 的消息，你必须回复！{agent_identity}。\n"
                              "请先 cd 到项目目录，然后使用 CLI 工具发送消息到群里：\n"
                              f"{cli_hint}\n"
                              "注意：不要在 ACP 响应中直接输出群聊内容，系统不会自动发布你的回复。\n"
                              "[end padding]\n[end padding]\n[end padding]")
            else:
                msg_prefix = f"[群聊 {group_id} 成员数:{member_count}] {sender} 说:\n"
                msg_suffix = (f"\n\n{agent_identity}，仅当消息与你直接相关时才回复。\n"
                              "💡 尽量等待人类用户发起讨论或提出问题后再参与，不要主动发起新话题。\n"
                              "如果需要回复，请先 cd 到项目目录，然后使用 CLI 工具发送消息到群里：\n"
                              f"{cli_hint}\n"
                              "⚠️ 回复时尽量精准 @具体的人，不要给群中所有人发消息。"
                              "例如消息末尾加上 @某人名字 来指定回复对象。\n"
                              "注意：不要在 ACP 响应中直接输出群聊内容，系统不会自动发布你的回复。\n"
                              "[end padding]\n[end padding]\n[end padding]")

            msg_text = msg_prefix + content + msg_suffix

            # Append attachment descriptions to text message
            if attachments:
                attach_desc = "\n".join(
                    f"  📎 {att.name} ({att.type}/{att.mime_type})" for att in attachments
                )
                msg_text = msg_prefix + content + f"\n\n[随消息附件]\n{attach_desc}" + msg_suffix

            # Handle different member types
            if member_type == "ext":
                # External agent: use ACP or HTTP
                agent_info = external_agents_map.get(global_id, {})
                if not agent_info:
                    # Minimal info from DB
                    agent_info = {"global_name": global_id, "name": short_name, "tag": tag}
                asyncio.create_task(
                    self._handle_external_agent_reply(
                        group_id, agent_info, msg_text, short_name,
                        attachments=attachments,
                    )
                )
            else:
                # Internal oasis agent: use HTTP trigger
                trigger_url = f"http://127.0.0.1:{os.getenv('PORT_AGENT', '51200')}/system_trigger"

                trigger_suffix = ("\n\n如果需要回复，请使用 send_to_group 工具发送消息到群里：\n"
                                  f"  send_to_group(group_id=\"{group_id}\", content=\"你的回复内容\")\n"
                                  "注意：username 和 source_session 会自动注入，不要手动设置。\n"
                                  "系统不会自动发布你的回复，必须调用 send_to_group 工具。\n"
                                  "[end padding]\n[end padding]\n[end padding]")

                attach_hint = ""
                if attachments:
                    attach_desc = "\n".join(
                        f"  📎 {att.name} ({att.type}/{att.mime_type})" for att in attachments
                    )
                    attach_hint = f"\n\n[随消息附件]\n{attach_desc}"

                if is_private_chat:
                    trigger_msg = (f"[私聊] {sender} 说:\n{content}{attach_hint}\n\n"
                                   f"(这是用户发给你的私信，你是「{short_name}」，请认真回复。)"
                                   f"{trigger_suffix}")
                elif mentions and global_id in mentions:
                    trigger_msg = (f"[群聊 {group_id} 成员数:{member_count}] {sender} @你 说:\n{content}{attach_hint}\n\n"
                                   f"(⚠️ 这是专门 @你 的消息，你必须回复！"
                                   f"你在群聊中的身份/角色是「{short_name}」，回复时请体现你的专业角色视角。)"
                                   f"{trigger_suffix}")
                else:
                    trigger_msg = (f"[群聊 {group_id} 成员数:{member_count}] {sender} 说:\n{content}{attach_hint}\n\n"
                                   f"(你在群聊中的身份/角色是「{short_name}」，回复时请体现你的专业角色视角。"
                                   f"仅当消息与你直接相关、点名你、向你提问、或面向所有人时，"
                                   f"才需要回复。其他情况请忽略，不要回应。\n"
                                   f"💡 尽量等待人类用户发起讨论或提出问题后再参与，不要主动发起新话题。\n"
                                   f"⚠️ 回复时尽量精准 @具体的人，不要给群中所有人发消息。"
                                   f"例如在 send_to_group 的 content 末尾加上 @某人名字 来指定回复对象。)"
                                   f"{trigger_suffix}")

                try:
                    trigger_body: dict = {
                        "user_id": user_id_member,
                        "session_id": global_id,
                        "text": trigger_msg,
                    }
                    if attachments:
                        trigger_body["attachments"] = [
                            a.model_dump() for a in attachments
                        ]
                    async with httpx.AsyncClient(timeout=30) as client:
                        await client.post(
                            trigger_url,
                            headers={"X-Internal-Token": self.internal_token},
                            json=trigger_body,
                        )
                except Exception as e:
                    logger.warning("广播到 %s (global_id=%s) 失败: %s", short_name, global_id, e)

    async def create_group(self, req: GroupCreateRequest, authorization: str | None):
        uid, _, _ = self.parse_group_auth(authorization)

        # Private chat (custom_name starts with "private_"): create empty group,
        # the caller will add the single target agent via POST /members afterwards.
        # Regular group chat: load all team members from config using team_name.
        is_private = req.custom_name and req.custom_name.startswith("private_")
        if is_private:
            members = []
        elif req.team_name:
            members = _load_team_members(uid, req.team_name)
        else:
            members = []

        # group_id = owner::name_safe  (确定性、URL 安全)
        name_safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", req.name).strip("_") or "group"
        group_id = f"{uid}::{name_safe}"

        if await group_exists(self.group_db_path, group_id):
            return {"group_id": group_id, "name": req.name, "owner": uid, "exists": True}
        now = time.time()
        await create_group_with_members(
            self.group_db_path,
            group_id=group_id,
            name=req.name,
            owner=uid,
            created_at=now,
            members=members,
        )
        return {"group_id": group_id, "name": req.name, "owner": uid, "member_count": len(members)}

    async def list_groups(self, authorization: str | None):
        uid, _, _ = self.parse_group_auth(authorization)
        return await list_groups_for_user(self.group_db_path, uid)

    async def get_group(self, group_id: str, authorization: str | None):
        self.parse_group_auth(authorization)
        group = await get_group(self.group_db_path, group_id)
        if not group:
            raise HTTPException(status_code=404, detail="群聊不存在")

        members = await list_group_members(self.group_db_path, group_id)
        # title 直接用数据库里的 short_name，不需要再查 json
        for member in members:
            if member.get("is_agent"):
                member["title"] = member.get("short_name") or member.get("global_id") or "未命名"
            else:
                member["title"] = member.get("user_id") or "群主"

        messages = await list_recent_group_messages(self.group_db_path, group_id, limit=100)
        return {**group, "members": members, "messages": messages}

    async def get_group_messages(self, group_id: str, after_id: int, authorization: str | None):
        self.parse_group_auth(authorization)
        messages = await list_group_messages_after(self.group_db_path, group_id, after_id, limit=200)
        return {"messages": messages}

    async def post_group_message(
        self,
        group_id: str,
        req: GroupMessageRequest,
        authorization: str | None,
        x_internal_token: str | None,
    ):
        sender = ""
        sender_display = req.sender_display or ""

        if x_internal_token and x_internal_token == self.internal_token:
            sender = req.sender or "agent"
            uid = "agent"

            # 自动补全 sender_display：
            # MCP tool 传入的 sender 格式为 "username#session_id"，sender_display 为 "#session_id"
            # CLI 传入的 sender 已经是完整的 "tag#type#short_name#global_id" 格式
            # 判断：sender_display 段数 < 3 说明不完整，需要根据 global_id 查成员信息补全
            sd_parts = sender_display.split("#") if sender_display else []
            if len(sd_parts) < 3 and sender and "#" in sender:
                _parts = sender.split("#", 1)
                source_global_id = _parts[1] if len(_parts) > 1 else ""
                if source_global_id:
                    member_info = await get_group_member_by_global_id(
                        self.group_db_path, group_id, source_global_id
                    )
                    if member_info:
                        tag = member_info.get("tag") or ""
                        mtype = member_info.get("member_type") or "oasis"
                        sname = member_info.get("short_name") or ""
                        gid = member_info.get("global_id") or ""
                        sender_display = f"{tag}#{mtype}#{sname}#{gid}" if tag else f"#{mtype}#{sname}#{gid}"
                        sender = sender_display
        else:
            uid, _, sid = self.parse_group_auth(authorization)
            sender = req.sender or uid
            # 人类发消息 sender_display 为空（前端用这个判断是否 agent）

        now = time.time()
        if not await group_exists(self.group_db_path, group_id):
            raise HTTPException(status_code=404, detail="群聊不存在")

        # Resolve real owner user_id for loading external agent configs
        broadcast_uid = uid
        if uid == "agent":
            owner = await get_group_owner(self.group_db_path, group_id)
            broadcast_uid = owner or ""

        # Serialize attachments for DB storage
        attachments_json = "[]"
        if req.attachments:
            attachments_json = json.dumps([a.model_dump() for a in req.attachments])

        msg_id = await insert_group_message(
            self.group_db_path,
            group_id=group_id,
            sender=sender,
            sender_display=sender_display,
            content=req.content,
            attachments=attachments_json,
            timestamp=now,
        )

        # ── Auto-resolve @mentions from message content ──
        # Instead of regex-parsing @name tokens (which breaks on spaces /
        # special chars), we fetch the member list first and then check
        # whether "@<short_name>" appears anywhere in the content.
        # This works for all channels (frontend, CLI, MCP send_to_group).
        resolved_mentions = list(req.mentions) if req.mentions else []
        if "@" in req.content:
            members = await list_group_members(self.group_db_path, group_id)
            content_lower = req.content.lower()
            # Build list sorted by name length desc so longer names match first
            # (e.g. "@Code Reviewer" before "@Code")
            # Include ALL members (agents + humans) so that @human also
            # populates mentions, preventing broadcast to unrelated agents.
            name_gid_pairs: list[tuple[str, str]] = []
            for m in members:
                sname = (m.get("short_name") or "").strip()
                gid = m.get("global_id") or ""
                if sname and gid:
                    name_gid_pairs.append((sname, gid))
            name_gid_pairs.sort(key=lambda x: len(x[0]), reverse=True)
            for sname, gid in name_gid_pairs:
                if f"@{sname.lower()}" in content_lower and gid not in resolved_mentions:
                    resolved_mentions.append(gid)
        final_mentions = resolved_mentions if resolved_mentions else None

        # 用 sender_display (tag#type#short_name) 排除发送者自己
        # 不用 global_id 排除，因为不同 agent 平台的 global_id 可能冲突
        exclude_display = sender_display or ""
        asyncio.create_task(
            self.broadcast_to_group(
                group_id,
                sender_display or sender,
                req.content,
                exclude_sender_display=exclude_display,
                mentions=final_mentions,
                user_id=broadcast_uid,
                attachments=req.attachments,
            )
        )

        return {"status": "sent", "sender": sender, "sender_display": sender_display, "timestamp": now, "id": msg_id}

    async def update_group(self, group_id: str, req: GroupUpdateRequest, authorization: str | None):
        uid, _, _ = self.parse_group_auth(authorization)
        owner = await get_group_owner(self.group_db_path, group_id)
        if not owner:
            raise HTTPException(status_code=404, detail="群聊不存在")
        if owner != uid:
            raise HTTPException(status_code=403, detail="只有群主可以修改群设置")

        if req.name:
            await update_group_name(self.group_db_path, group_id, req.name)

        return {"status": "updated"}

    async def delete_group(self, group_id: str, authorization: str | None):
        uid, _, _ = self.parse_group_auth(authorization)
        owner = await get_group_owner(self.group_db_path, group_id)
        if not owner:
            raise HTTPException(status_code=404, detail="群聊不存在")
        if owner != uid:
            raise HTTPException(status_code=403, detail="只有群主可以删除群")
        await delete_group_records(self.group_db_path, group_id)
        return {"status": "deleted"}

    async def sync_group_members(self, group_id: str, authorization: str | None, team_name: str = ""):
        """Sync group members from team configuration.

        This will:
        1. Clear all existing non-owner members
        2. Reload members from team config (internal_agents.json + external_agents.json)
        3. Add the reloaded members to the group

        team_name must be provided by the caller (no longer stored in DB).
        """
        uid, _, _ = self.parse_group_auth(authorization)
        owner = await get_group_owner(self.group_db_path, group_id)
        if not owner:
            raise HTTPException(status_code=404, detail="群聊不存在")
        if owner != uid:
            raise HTTPException(status_code=403, detail="只有群主可以同步群成员")

        if not team_name:
            raise HTTPException(status_code=400, detail="需要提供 team_name")

        # Load current members from team config
        new_members = _load_team_members(uid, team_name)

        # Clear existing non-owner members
        await clear_group_members(self.group_db_path, group_id=group_id, keep_owners=True)

        # Add new members
        now = time.time()
        added_count = 0
        for m in new_members:
            m_global = m.get("global_id", "")
            m_short = m.get("short_name", "")
            m_uid = m.get("user_id", "")
            m_type = m.get("member_type", "oasis")
            m_tag = m.get("tag", "")
            if m_global:
                await add_group_member(
                    self.group_db_path,
                    group_id=group_id,
                    user_id=m_uid,
                    short_name=m_short,
                    global_id=m_global,
                    member_type=m_type,
                    tag=m_tag,
                    joined_at=now,
                )
                added_count += 1

        return {
            "status": "synced",
            "group_id": group_id,
            "added_members": added_count,
        }

    async def mute_group(self, group_id: str, authorization: str | None):
        self.parse_group_auth(authorization)
        self.group_muted.add(group_id)
        return {"status": "muted", "group_id": group_id}

    async def unmute_group(self, group_id: str, authorization: str | None):
        self.parse_group_auth(authorization)
        self.group_muted.discard(group_id)
        return {"status": "unmuted", "group_id": group_id}

    async def group_mute_status(self, group_id: str, authorization: str | None):
        self.parse_group_auth(authorization)
        return {"muted": group_id in self.group_muted}

    async def list_available_sessions(self, group_id: str, authorization: str | None):
        uid, _, _ = self.parse_group_auth(authorization)
        prefix = f"{uid}#"
        sessions = []
        try:
            rows = await list_thread_ids_by_prefix(self.checkpoint_db_path, prefix)

            for thread_id in rows:
                sid = thread_id[len(prefix):]
                config = {"configurable": {"thread_id": thread_id}}
                snapshot = await self.agent.agent_app.aget_state(config)
                msgs = snapshot.values.get("messages", []) if snapshot and snapshot.values else []
                first_human = first_human_title(
                    msgs,
                    skip_prefixes=("[系统触发]", "[外部学术会议邀请]"),
                    title_len=80,
                    list_fallback="(图片消息)",
                    default="",
                )

                sessions.append({
                    "session_id": sid,
                    "title": first_human or f"Session {sid}",
                })
        except Exception as e:
            return {"sessions": [], "error": str(e)}

        return {"sessions": sessions}

    async def add_single_member(self, group_id: str, req: GroupAddMemberRequest, authorization: str | None):
        """向群聊中添加单个 agent 成员。"""
        uid, _, _ = self.parse_group_auth(authorization)
        owner = await get_group_owner(self.group_db_path, group_id)
        if not owner:
            raise HTTPException(status_code=404, detail="群聊不存在")
        if owner != uid:
            raise HTTPException(status_code=403, detail="只有群主可以添加成员")

        # 判断 user_id：内部 agent 的 user_id 是群主 uid，外部 agent 的 user_id 是 "ext"
        m_uid = "ext" if req.member_type == "ext" else uid

        await add_group_member(
            self.group_db_path,
            group_id=group_id,
            user_id=m_uid,
            short_name=req.short_name,
            global_id=req.global_id,
            member_type=req.member_type,
            tag=req.tag,
            joined_at=time.time(),
        )
        return {"status": "added", "global_id": req.global_id, "short_name": req.short_name}

    async def remove_single_member(self, group_id: str, global_id: str, authorization: str | None):
        """从群聊中移除单个 agent 成员（通过 global_id）。"""
        uid, _, _ = self.parse_group_auth(authorization)
        owner = await get_group_owner(self.group_db_path, group_id)
        if not owner:
            raise HTTPException(status_code=404, detail="群聊不存在")
        if owner != uid:
            raise HTTPException(status_code=403, detail="只有群主可以移除成员")

        await remove_group_member(
            self.group_db_path,
            group_id=group_id,
            global_id=global_id,
        )
        return {"status": "removed", "global_id": global_id}

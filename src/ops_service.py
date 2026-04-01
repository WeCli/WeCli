import asyncio
import json
import os
import shutil
from typing import Any, Callable

import httpx
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from auth_utils import extract_user_password_session, is_internal_bearer, parse_bearer_parts
from llm_factory import get_provider_audio_defaults, infer_provider
from logging_utils import get_logger
from ops_models import ACPControlRequest, ACPStatusRequest, CancelRequest, LoginRequest, TTSRequest

logger = get_logger("ops_service")

# Project root for team-scoped paths
_PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

# Known ACP-compatible tool binaries (must match CLI status platforms list)
_ACP_KNOWN_TOOLS: frozenset = frozenset({"openclaw", "codex", "claude", "gemini", "aider"})

# ACP protocol support (optional)
try:
    from acp import PROTOCOL_VERSION, Client, connect_to_agent
    from acp.schema import ClientCapabilities, Implementation, AgentMessageChunk
    _ACP_AVAILABLE = True
except ImportError:
    _ACP_AVAILABLE = False


if _ACP_AVAILABLE:
    class _SecureStreamReader(asyncio.StreamReader):
        """包装 subprocess stdout，只传递 JSON-RPC 行。"""
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
        """ACP 协议客户端，用于控制操作。"""
        def __init__(self):
            self.chunks: list[str] = []

        async def session_update(self, session_id, update, **kwargs):
            if isinstance(update, AgentMessageChunk) and hasattr(update.content, 'text'):
                self.chunks.append(update.content.text)


def _load_team_external_agents(user_id: str, team: str) -> list[dict]:
    """Load external agents from team's external_agents.json."""
    team = (team or "").strip()
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
        for agent in data:
            if not isinstance(agent, dict) or "name" not in agent:
                continue
            ext_config = agent.get("config") or agent.get("meta") or {}
            result.append({
                "user_id": "ext",
                "session_id": agent.get("name", ""),
                "member_type": "ext",
                "name": agent.get("name", ""),
                "tag": agent.get("tag", ""),
                "global_name": agent.get("global_name", ""),
                "api_url": ext_config.get("api_url", ""),
                "api_key": ext_config.get("api_key", ""),
                "model": ext_config.get("model", ""),
            })
        return result
    except Exception:
        return []


def _find_external_agent(agents: list[dict], agent_key: str) -> dict | None:
    """Match external agent by short name first, then global_name."""
    agent_key = (agent_key or "").strip()
    if not agent_key:
        return None
    for agent in agents:
        if (agent.get("name") or "").strip() == agent_key:
            return agent
    for agent in agents:
        if (agent.get("global_name") or "").strip() == agent_key:
            return agent
    return None


def _find_external_agent_across_teams(user_id: str, agent_key: str) -> dict | None:
    """Search all team folders when the primary team hint misses the agent."""
    if not user_id or not agent_key:
        return None
    team_base = os.path.join(_PROJECT_ROOT, "data", "user_files", user_id, "teams")
    if not os.path.isdir(team_base):
        return None
    for entry in sorted(os.listdir(team_base)):
        path = os.path.join(team_base, entry)
        if not os.path.isdir(path):
            continue
        found = _find_external_agent(_load_team_external_agents(user_id, entry), agent_key)
        if found:
            return found
    return None


class OpsService:
    """操作服务类，提供工具列表、登录、TTS、ACP 外部 agent 控制等功能。"""

    def __init__(
        self,
        *,
        internal_token: str,
        agent: Any,
        verify_password: Callable[[str, str], bool],
        verify_auth_or_token: Callable[[str, str, str | None], None],
    ):
        self.internal_token = internal_token
        self.agent = agent
        self.verify_password = verify_password
        self.verify_auth_or_token = verify_auth_or_token

    async def get_tools_list(self, x_internal_token: str | None, authorization: str | None):
        """获取可用工具列表。

        :param x_internal_token: 内部令牌（可选）
        :param authorization: Bearer 授权头（可选）
        :return: 包含工具列表的字典
        :raises HTTPException: 认证失败时抛出 403 异常
        """
        if x_internal_token and x_internal_token == self.internal_token:
            return {"status": "success", "tools": self.agent.get_tools_info()}
        parts = parse_bearer_parts(authorization)
        if parts:
            if is_internal_bearer(parts, self.internal_token):
                return {"status": "success", "tools": self.agent.get_tools_info()}
            parsed = extract_user_password_session(parts, default_session="default")
            if parsed and self.verify_password(parsed[0], parsed[1]):
                return {"status": "success", "tools": self.agent.get_tools_info()}
        raise HTTPException(status_code=403, detail="认证失败")

    async def login(self, req: LoginRequest):
        """用户登录验证。

        :param req: 登录请求，包含 user_id 和 password
        :return: 登录成功状态
        :raises HTTPException: 密码错误时抛出 401 异常
        """
        if self.verify_password(req.user_id, req.password):
            logger.info("login success user=%s", req.user_id)
            return {"status": "success", "message": "登录成功"}
        logger.warning("login failed user=%s", req.user_id)
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    async def cancel_agent(self, req: CancelRequest, x_internal_token: str | None):
        """取消指定用户的运行中任务。

        :param req: 取消请求，包含 user_id、session_id、password
        :param x_internal_token: 内部令牌（可选）
        :return: 取消操作结果
        """
        self.verify_auth_or_token(req.user_id, req.password, x_internal_token)
        task_key = f"{req.user_id}#{req.session_id}"
        logger.info("cancel user=%s session=%s", req.user_id, req.session_id)
        actually_cancelled = await self.agent.cancel_task(task_key)
        if actually_cancelled:
            return {"status": "success", "message": "已终止", "cancelled": True}
        return {"status": "success", "message": "当前没有运行中的任务", "cancelled": False}

    async def text_to_speech(self, req: TTSRequest, x_internal_token: str | None):
        """文本转语音（TTS）服务。

        :param req: TTS 请求，包含 text、voice 等
        :param x_internal_token: 内部令牌（可选）
        :return: 音频流响应
        :raises HTTPException: 未配置 API 或文本为空时抛出异常
        """
        self.verify_auth_or_token(req.user_id, req.password, x_internal_token)

        tts_text = req.text.strip()
        if not tts_text:
            raise HTTPException(status_code=400, detail="文本不能为空")
        if len(tts_text) > 4000:
            tts_text = tts_text[:4000]

        api_key = os.getenv("LLM_API_KEY", "")
        base_url = os.getenv("LLM_BASE_URL", "").rstrip("/")
        provider = infer_provider(
            model=os.getenv("LLM_MODEL", ""),
            base_url=base_url,
            provider=os.getenv("LLM_PROVIDER", ""),
            api_key=api_key,
        )
        audio_defaults = get_provider_audio_defaults(provider)
        tts_model = os.getenv("TTS_MODEL", "").strip() or audio_defaults["tts_model"]
        tts_voice = req.voice or os.getenv("TTS_VOICE", "").strip() or audio_defaults["tts_voice"]

        if not api_key or not base_url:
            raise HTTPException(status_code=500, detail="TTS API 未配置")
        if not tts_model:
            raise HTTPException(
                status_code=500,
                detail="TTS_MODEL 未配置，且当前 LLM provider 没有可自动推断的音频默认值",
            )

        tts_url = f"{base_url}/audio/speech"

        async def audio_stream():
            payload = {
                "model": tts_model,
                "input": tts_text,
                "response_format": "mp3",
            }
            if tts_voice:
                payload["voice"] = tts_voice

            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    tts_url,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                ) as resp:
                    if resp.status_code != 200:
                        error_body = await resp.aread()
                        raise HTTPException(
                            status_code=resp.status_code,
                            detail=f"TTS API 错误: {error_body.decode('utf-8', errors='replace')[:200]}",
                        )
                    async for chunk in resp.aiter_bytes(chunk_size=4096):
                        yield chunk

        return StreamingResponse(
            audio_stream(),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=tts_output.mp3"},
        )

    # ------------------------------------------------------------------
    # ACP external agent management
    # ------------------------------------------------------------------

    async def acp_control(self, req: ACPControlRequest, x_internal_token: str | None):
        """对外部 ACP agent 执行 /new 或 /stop。

        Session routing 通过命令行 --session 参数传入（bridge 当前版本不处理 _meta.sessionKey）。
        reset_session 通过命令行 --reset-session 标志实现。
        stop 通过在 new_session 时建立连接后直接 cancel(session_id) 实现，
        因为 bridge 不支持 session/list 方法。
        """
        self.verify_auth_or_token(req.user_id, req.password, x_internal_token)

        team_hint = (req.team or "").strip()
        agent_key = (req.agent_name or "").strip()
        agents = _load_team_external_agents(req.user_id, team_hint) if team_hint else []
        agent_info = _find_external_agent(agents, agent_key)
        if not agent_info:
            agent_info = _find_external_agent_across_teams(req.user_id, agent_key)
        if not agent_info:
            raise HTTPException(
                status_code=404,
                detail=f"外部 agent '{agent_key}' 未找到（team={team_hint or '(空)'}，已在全部 team 目录中查找）",
            )

        global_name = agent_info.get("global_name", "")
        if not global_name:
            raise HTTPException(status_code=400, detail="该 agent 未配置 global_name")

        tag = agent_info.get("tag", "").lower()
        acp_tool = tag if tag in _ACP_KNOWN_TOOLS else "openclaw"
        acp_bin = shutil.which(acp_tool)
        if not acp_bin:
            raise HTTPException(status_code=500, detail=f"ACP 工具 '{acp_tool}' 未安装")

        if not _ACP_AVAILABLE:
            raise HTTPException(status_code=500, detail="ACP 协议库不可用")

        acp_session = f"agent:{global_name}:teamclawchat"
        logger.info("acp_control action=%s agent=%s session=%s", req.action, agent_key, acp_session)

        proc = None
        try:
            # 通过命令行传入 session key（bridge 只认命令行 --session，不处理 _meta.sessionKey）
            cmd = [acp_bin, "acp", "--session", acp_session, "--no-prefix-cwd"]
            # new/reset 都强制重置持久化上下文；否则 new 只会复用旧线程状态
            if req.action == "new":
                cmd.append("--reset-session")
                logger.info("acp_control reset_session=true for %s", agent_key)

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            safe_stdout = _SecureStreamReader(proc.stdout)
            client = _ACPClient()
            conn = connect_to_agent(client, proc.stdin, safe_stdout)

            await asyncio.wait_for(
                conn.initialize(
                    protocol_version=PROTOCOL_VERSION,
                    client_capabilities=ClientCapabilities(),
                    client_info=Implementation(name="teamclaw-ops", version="1.0"),
                ),
                timeout=10,
            )

            result: dict = {}
            if req.action == "new":
                async def _do_new_session():
                    try:
                        return await conn.new_session(
                            mcp_servers=[],
                            cwd=os.getcwd(),
                            metadata={"resetSession": True},
                        )
                    except TypeError:
                        return await conn.new_session(
                            mcp_servers=[],
                            cwd=os.getcwd(),
                        )

                new_session = await asyncio.wait_for(_do_new_session(), timeout=10)
                session_id = getattr(new_session, "session_id", str(new_session))
                result = {
                    "session_id": session_id,
                    "acp_session": acp_session,
                    "message": f"已为 {agent_key} 创建新 session（已请求重置持久化上下文）",
                }
                logger.info("acp_control new session_id=%s acp_session=%s", session_id, acp_session)

            elif req.action == "stop":
                # bridge 不支持 session/list，直接用 new_session 建立连接后 cancel 该 session
                new_session = await asyncio.wait_for(
                    conn.new_session(
                        mcp_servers=[],
                        cwd=os.getcwd(),
                    ),
                    timeout=10,
                )
                session_id = getattr(new_session, "session_id", str(new_session))
                await asyncio.wait_for(
                    conn.cancel(session_id=session_id),
                    timeout=10,
                )
                result = {
                    "cancelled_session": session_id,
                    "acp_session": acp_session,
                    "message": f"已取消 {agent_key} 的当前操作",
                }
                logger.info("acp_control stop cancelled session_id=%s", session_id)

            return {"status": "success", "action": req.action, **result}

        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="ACP 操作超时")
        except Exception as e:
            logger.warning("acp_control failed: %s", e)
            raise HTTPException(status_code=500, detail=f"ACP 操作失败: {e}")
        finally:
            if proc:
                try:
                    proc.stdout.feed_eof()
                    if proc.stdin:
                        proc.stdin.close()
                    proc.terminate()
                    try:
                        await asyncio.wait_for(proc.wait(), timeout=1)
                    except asyncio.TimeoutError:
                        proc.kill()
                        await proc.wait()
                except Exception:
                    pass

    async def acp_status(self, req: ACPStatusRequest, x_internal_token: str | None):
        """查询外部 agent 的 session 状态列表。

        优先走 CLI `openclaw sessions --all-agents --json` 获取全局状态，
        如 CLI 不支持则逐个通过 ACP 协议 list_sessions。

        :param req: 状态查询请求，包含 user_id、team、agent_name（可选）
        :param x_internal_token: 内部令牌（可选）
        :return: agent 状态列表
        """
        self.verify_auth_or_token(req.user_id, req.password, x_internal_token)

        team_hint = (req.team or "").strip()
        agents = _load_team_external_agents(req.user_id, team_hint) if team_hint else []
        if req.agent_name:
            agent_key = req.agent_name.strip()
            one = _find_external_agent(agents, agent_key)
            if not one:
                one = _find_external_agent_across_teams(req.user_id, agent_key)
            agents = [one] if one else []

        if not agents:
            return {"status": "success", "agents": []}

        results = []

        # 方案 A: 尝试 CLI 快速获取
        cli_data = await self._acp_status_via_cli(agents)
        if cli_data is not None:
            return {"status": "success", "agents": cli_data}

        # 方案 B: 逐个走 ACP 协议
        for agent_info in agents:
            status_info = await self._acp_status_single(agent_info)
            results.append(status_info)

        return {"status": "success", "agents": results}

    async def _acp_status_via_cli(self, agents: list[dict]) -> list[dict] | None:
        """尝试通过 CLI 获取所有 agent sessions（一次调用，高效）。

        :param agents: 外部 agent 配置列表
        :return: agent 状态列表，获取失败时返回 None
        """
        # 取第一个 agent 的 tag 来决定 binary
        first_tag = agents[0].get("tag", "").lower() if agents else ""
        acp_tool = first_tag if first_tag in _ACP_KNOWN_TOOLS else "openclaw"
        acp_bin = shutil.which(acp_tool)
        if not acp_bin:
            return None

        try:
            proc = await asyncio.create_subprocess_exec(
                acp_bin, "sessions", "--all-agents", "--json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=8)
            if proc.returncode != 0:
                return None

            raw = json.loads(stdout.decode("utf-8", errors="replace"))
            # CLI may return {"sessions": [...]} or a bare list
            if isinstance(raw, dict):
                all_sessions = raw.get("sessions", [])
            elif isinstance(raw, list):
                all_sessions = raw
            else:
                return None

            # Build global_name -> agent_info mapping
            gname_map = {a["global_name"]: a for a in agents if a.get("global_name")}

            results = []
            for agent_info in agents:
                gn = agent_info.get("global_name", "")
                agent_sessions = [s for s in all_sessions if s.get("agent") == gn]
                results.append({
                    "name": agent_info["name"],
                    "global_name": gn,
                    "tag": agent_info.get("tag", ""),
                    "status": "online" if agent_sessions else "idle",
                    "session_count": len(agent_sessions),
                    "sessions": agent_sessions,
                })
            return results

        except (asyncio.TimeoutError, json.JSONDecodeError, Exception) as e:
            logger.debug("CLI status fallback: %s", e)
            return None

    async def _acp_status_single(self, agent_info: dict) -> dict:
        """通过 CLI 查询单个外部 agent 的 session 列表。

        bridge 不支持 session/list 方法，改用 `openclaw sessions --json` 过滤
        对应 agent 的 session key 前缀来判断状态。

        :param agent_info: 外部 agent 配置信息
        :return: 该 agent 的详细状态信息
        """
        name = agent_info.get("name", "")
        global_name = agent_info.get("global_name", "")
        tag = agent_info.get("tag", "").lower()

        base_result = {
            "name": name,
            "global_name": global_name,
            "tag": agent_info.get("tag", ""),
        }

        if not global_name:
            return {**base_result, "status": "unavailable", "reason": "no global_name"}

        acp_tool = tag if tag in _ACP_KNOWN_TOOLS else "openclaw"
        acp_bin = shutil.which(acp_tool)
        if not acp_bin:
            return {**base_result, "status": "unavailable", "reason": f"binary '{acp_tool}' not found"}

        # 用 CLI sessions --json 列出所有 session，过滤 agent:<global_name>: 前缀
        session_prefix = f"agent:{global_name}:"
        try:
            proc = await asyncio.create_subprocess_exec(
                acp_bin, "sessions", "--json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=8)
            if proc.returncode != 0:
                return {**base_result, "status": "unavailable", "reason": "CLI sessions failed"}

            raw = json.loads(stdout.decode("utf-8", errors="replace"))
            # CLI returns {"sessions": [...], ...} or bare list
            if isinstance(raw, dict):
                all_sessions = raw.get("sessions", [])
            elif isinstance(raw, list):
                all_sessions = raw
            else:
                return {**base_result, "status": "unavailable", "reason": "unexpected CLI output"}

            # 过滤属于该 agent 的 session（key 以 agent:<global_name>: 开头）
            agent_sessions = [
                s for s in all_sessions
                if str(s.get("key", s.get("session_key", ""))).startswith(session_prefix)
            ]

            return {
                **base_result,
                "status": "online" if agent_sessions else "idle",
                "session_count": len(agent_sessions),
                "sessions": [
                    {
                        "session_id": s.get("sessionId", s.get("session_id", s.get("id", ""))),
                        "key": s.get("key", s.get("session_key", "")),
                        "age": s.get("ageMs", s.get("age", "")),
                    }
                    for s in agent_sessions
                ],
            }

        except asyncio.TimeoutError:
            return {**base_result, "status": "timeout", "reason": "CLI sessions timeout"}
        except (json.JSONDecodeError, Exception) as e:
            return {**base_result, "status": "error", "reason": str(e)}

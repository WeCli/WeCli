from typing import Any, Callable

from fastapi import HTTPException

from checkpoint_repository import (
    delete_thread_records,
    delete_thread_records_like,
    list_thread_ids_by_prefix,
)
from logging_utils import get_logger
from session_models import (
    DeleteSessionRequest,
    SessionHistoryRequest,
    SessionListRequest,
    SessionStatusRequest,
)
from session_summary import build_session_summary

logger = get_logger("session_service")


class SessionService:
    def __init__(
        self,
        *,
        db_path: str,
        agent: Any,
        verify_auth_or_token: Callable[[str, str, str | None], None],
        extract_text: Callable[[Any], str],
    ):
        self.db_path = db_path
        self.agent = agent
        self.verify_auth_or_token = verify_auth_or_token
        self.extract_text = extract_text

    async def list_sessions(self, req: SessionListRequest, x_internal_token: str | None):
        self.verify_auth_or_token(req.user_id, req.password, x_internal_token)
        logger.info("list_sessions user=%s", req.user_id)

        prefix = f"{req.user_id}#"
        sessions = []

        rows = await list_thread_ids_by_prefix(self.db_path, prefix)

        for thread_id in rows:
            sid = thread_id[len(prefix):]

            config = {"configurable": {"thread_id": thread_id}}
            snapshot = await self.agent.agent_app.aget_state(config)
            msgs = snapshot.values.get("messages", []) if snapshot and snapshot.values else []

            summary = build_session_summary(
                msgs,
                skip_prefixes=("[系统触发]", "[外部学术会议邀请]"),
                title_len=50,
                last_len=50,
                list_fallback="(图片消息)",
            )
            first_human = summary["first_human"]
            last_human = summary["last_human"]
            msg_count = summary["msg_count"]

            if not first_human:
                continue

            sessions.append({
                "session_id": sid,
                "title": first_human,
                "last_message": last_human,
                "message_count": msg_count,
            })

        return {"status": "success", "sessions": sessions}

    async def sessions_status(self, req: SessionListRequest, x_internal_token: str | None):
        self.verify_auth_or_token(req.user_id, req.password, x_internal_token)

        prefix = f"{req.user_id}#"
        all_status = self.agent.get_all_thread_status(prefix)

        result = []
        for thread_id, info in all_status.items():
            sid = thread_id[len(prefix):]
            result.append({
                "session_id": sid,
                "busy": info["busy"],
                "source": info["source"],       # "user" | "system" | ""
                "pending_system": info["pending_system"],
            })

        return {"status": "success", "sessions": result}

    async def get_session_history(self, req: SessionHistoryRequest, x_internal_token: str | None):
        self.verify_auth_or_token(req.user_id, req.password, x_internal_token)

        thread_id = f"{req.user_id}#{req.session_id}"
        config = {"configurable": {"thread_id": thread_id}}
        snapshot = await self.agent.agent_app.aget_state(config)

        if not snapshot or not snapshot.values:
            return {"status": "success", "messages": []}

        msgs = snapshot.values.get("messages", [])
        result = []
        for m in msgs:
            msg_type = type(m).__name__
            if msg_type == "HumanMessage":
                result.append({"role": "user", "content": m.content})
            elif msg_type == "AIMessage":
                content = self.extract_text(m.content)
                tool_calls = []
                if hasattr(m, "tool_calls") and m.tool_calls:
                    for tc in m.tool_calls:
                        tool_calls.append({
                            "name": tc.get("name", ""),
                            "args": tc.get("args", {}),
                        })
                if content or tool_calls:
                    entry = {"role": "assistant", "content": content}
                    if tool_calls:
                        entry["tool_calls"] = tool_calls
                    result.append(entry)
            elif msg_type == "ToolMessage":
                content = self.extract_text(m.content)
                tool_name = getattr(m, "name", "")
                result.append({
                    "role": "tool",
                    "content": content,
                    "tool_name": tool_name,
                })

        return {"status": "success", "messages": result}

    async def delete_session(self, req: DeleteSessionRequest, x_internal_token: str | None):
        self.verify_auth_or_token(req.user_id, req.password, x_internal_token)
        logger.info("delete_session user=%s session=%s", req.user_id, req.session_id or "ALL")

        try:
            if req.session_id:
                task_key = f"{req.user_id}#{req.session_id}"
                await self.agent.cancel_task(task_key)

                thread_id = f"{req.user_id}#{req.session_id}"
                await delete_thread_records(self.db_path, thread_id)
                return {"status": "success", "message": f"会话 {req.session_id} 已删除"}

            prefix = f"{req.user_id}#"
            keys_to_cancel = self.agent.list_active_task_keys(prefix)
            for k in keys_to_cancel:
                await self.agent.cancel_task(k)

            pattern = f"{req.user_id}#%"
            await delete_thread_records_like(self.db_path, pattern)
            return {"status": "success", "message": f"用户 {req.user_id} 的所有会话已删除"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"删除失败: {e}")

    async def session_status(self, req: SessionStatusRequest, x_internal_token: str | None):
        self.verify_auth_or_token(req.user_id, req.password, x_internal_token)
        thread_id = f"{req.user_id}#{req.session_id}"
        has_new = self.agent.has_pending_system_messages(thread_id)
        busy = self.agent.is_thread_busy(thread_id)
        pending_count = self.agent.consume_pending_system_messages(thread_id) if has_new else 0
        busy_source = self.agent.get_thread_busy_source(thread_id) if busy else ""
        return {
            "has_new_messages": has_new,
            "pending_count": pending_count,
            "busy": busy,
            "busy_source": busy_source,
        }

"""
TeamBot runtime routes for subagent inspection and policy management.
"""

from typing import Any, Callable

from fastapi import APIRouter, Header
from starlette.websockets import WebSocket, WebSocketDisconnect

from teambot_models import (
    TeamBotApprovalResolutionRequest,
    TeamBotBridgeAttachRequest,
    TeamBotBridgeDetachRequest,
    TeamBotBuddyActionRequest,
    TeamBotDreamRequest,
    TeamBotKairosUpdateRequest,
    TeamBotPlanUpdateRequest,
    TeamBotRunInterruptRequest,
    TeamBotSessionInboxDeliverRequest,
    TeamBotSessionInboxListRequest,
    TeamBotSessionInboxSendRequest,
    TeamBotSessionModeUpdateRequest,
    TeamBotSessionRuntimeRequest,
    TeamBotSubagentHistoryRequest,
    TeamBotSubagentRefRequest,
    TeamBotTodoUpdateRequest,
    TeamBotToolPolicyUpdateRequest,
    TeamBotVerificationCreateRequest,
    TeamBotVoiceStateUpdateRequest,
    TeamBotWorkflowPresetApplyRequest,
)
from teambot_bridge import bridge_hub, get_bridge_record_for_user
from teambot_service import TeamBotService


def create_teambot_router(
    *,
    agent: Any,
    verify_auth_or_token: Callable[[str, str, str | None], None],
    extract_text: Callable[[Any], str],
) -> APIRouter:
    router = APIRouter()
    service = TeamBotService(
        agent=agent,
        verify_auth_or_token=verify_auth_or_token,
        extract_text=extract_text,
    )

    @router.get("/teambot/subagents")
    async def list_subagents(
        user_id: str,
        password: str = "",
        x_internal_token: str | None = Header(None),
    ):
        return await service.list_subagents(user_id, password, x_internal_token)

    @router.post("/teambot/subagents/history")
    async def get_subagent_history(
        req: TeamBotSubagentHistoryRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.get_subagent_history(req, x_internal_token)

    @router.post("/teambot/subagents/cancel")
    async def cancel_subagent(
        req: TeamBotSubagentRefRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.cancel_subagent(req, x_internal_token)

    @router.get("/teambot/tool-policy")
    async def get_tool_policy(
        user_id: str,
        password: str = "",
        x_internal_token: str | None = Header(None),
    ):
        return await service.get_tool_policy(user_id, password, x_internal_token)

    @router.post("/teambot/tool-policy")
    async def update_tool_policy(
        req: TeamBotToolPolicyUpdateRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.update_tool_policy(req, x_internal_token)

    @router.get("/teambot/session-runtime")
    async def get_session_runtime(
        user_id: str,
        session_id: str,
        password: str = "",
        x_internal_token: str | None = Header(None),
    ):
        return await service.get_session_runtime(user_id, session_id, password, x_internal_token)

    @router.post("/teambot/session-mode")
    async def update_session_mode(
        req: TeamBotSessionModeUpdateRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.update_session_mode(req, x_internal_token)

    @router.get("/teambot/workflow-presets")
    async def list_session_workflow_presets(
        user_id: str,
        password: str = "",
        x_internal_token: str | None = Header(None),
    ):
        return await service.list_session_workflow_presets(user_id, password, x_internal_token)

    @router.post("/teambot/workflow-presets/apply")
    async def apply_session_workflow_preset(
        req: TeamBotWorkflowPresetApplyRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.apply_session_workflow_preset(req, x_internal_token)

    @router.get("/teambot/session-inbox")
    async def get_session_inbox(
        user_id: str,
        session_id: str,
        target_ref: str = "",
        status: str = "queued",
        limit: int = 20,
        password: str = "",
        x_internal_token: str | None = Header(None),
    ):
        req = TeamBotSessionInboxListRequest(
            user_id=user_id,
            password=password,
            session_id=session_id,
            target_ref=target_ref,
            status=status,
            limit=limit,
        )
        return await service.get_session_inbox(req, x_internal_token)

    @router.post("/teambot/session-inbox/send")
    async def send_session_inbox(
        req: TeamBotSessionInboxSendRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.send_session_inbox(req, x_internal_token)

    @router.post("/teambot/session-inbox/deliver")
    async def deliver_session_inbox(
        req: TeamBotSessionInboxDeliverRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.deliver_session_inbox(req, x_internal_token)

    @router.post("/teambot/runs/interrupt")
    async def interrupt_run(
        req: TeamBotRunInterruptRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.interrupt_run(req, x_internal_token)

    @router.post("/teambot/session-plan")
    async def update_session_plan(
        req: TeamBotPlanUpdateRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.update_session_plan(req, x_internal_token)

    @router.delete("/teambot/session-plan")
    async def clear_session_plan(
        req: TeamBotSessionRuntimeRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.clear_session_plan(req, x_internal_token)

    @router.post("/teambot/session-todos")
    async def update_session_todos(
        req: TeamBotTodoUpdateRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.update_session_todos(req, x_internal_token)

    @router.delete("/teambot/session-todos")
    async def clear_session_todos(
        req: TeamBotSessionRuntimeRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.clear_session_todos(req, x_internal_token)

    @router.post("/teambot/verifications")
    async def record_verification(
        req: TeamBotVerificationCreateRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.record_verification(req, x_internal_token)

    @router.post("/teambot/voice")
    async def update_voice_state(
        req: TeamBotVoiceStateUpdateRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.update_voice_state(req, x_internal_token)

    @router.post("/teambot/bridge/attach")
    async def create_bridge_attach(
        req: TeamBotBridgeAttachRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.create_bridge_attach(req, x_internal_token)

    @router.post("/teambot/bridge/detach")
    async def detach_bridge(
        req: TeamBotBridgeDetachRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.detach_bridge(req, x_internal_token)

    @router.post("/teambot/kairos")
    async def update_kairos_state(
        req: TeamBotKairosUpdateRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.update_kairos_state(req, x_internal_token)

    @router.post("/teambot/dream")
    async def run_dream(
        req: TeamBotDreamRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.run_dream(req, x_internal_token)

    @router.post("/teambot/buddy")
    async def buddy_action(
        req: TeamBotBuddyActionRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.buddy_action(req, x_internal_token)

    @router.post("/teambot/tool-approvals/resolve")
    async def resolve_tool_approval(
        req: TeamBotApprovalResolutionRequest,
        x_internal_token: str | None = Header(None),
    ):
        return await service.resolve_tool_approval(req, x_internal_token)

    @router.websocket("/teambot/ws/{user_id}/{bridge_id}")
    async def teambot_bridge_socket(websocket: WebSocket, user_id: str, bridge_id: str):
        record = get_bridge_record_for_user(user_id, bridge_id)
        if record is None:
            await websocket.close(code=4404)
            return
        await bridge_hub.connect(record, websocket)
        try:
            snapshot = service._serialize_session_runtime(user_id, record.session_id)
            await websocket.send_json(
                {
                    "type": "connected",
                    "bridge_id": record.bridge_id,
                    "session_id": record.session_id,
                    "role": record.role,
                }
            )
            await websocket.send_json(
                {
                    "type": "runtime_snapshot",
                    "bridge_id": record.bridge_id,
                    "session_id": record.session_id,
                    "changed_session_id": record.session_id,
                    "runtime": snapshot,
                }
            )
            while True:
                message = await websocket.receive_json()
                msg_type = str(message.get("type") or "").strip().lower()
                if msg_type == "ping":
                    await websocket.send_json({"type": "pong", "bridge_id": record.bridge_id})
                elif msg_type == "refresh":
                    await websocket.send_json(
                        {
                            "type": "runtime_snapshot",
                            "bridge_id": record.bridge_id,
                            "session_id": record.session_id,
                            "changed_session_id": record.session_id,
                            "runtime": service._serialize_session_runtime(user_id, record.session_id),
                        }
                    )
                else:
                    await websocket.send_json({"type": "ack", "bridge_id": record.bridge_id, "message": message})
        except WebSocketDisconnect:
            pass
        finally:
            await bridge_hub.disconnect(record, websocket)

    return router

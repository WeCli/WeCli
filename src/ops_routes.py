from typing import Any, Callable

from fastapi import APIRouter, Header

from ops_models import ACPControlRequest, ACPStatusRequest, CancelRequest, LoginRequest, TTSRequest
from ops_service import OpsService


def create_ops_router(
    *,
    internal_token: str,
    agent: Any,
    verify_password: Callable[[str, str], bool],
    verify_auth_or_token: Callable[[str, str, str | None], None],
) -> APIRouter:
    """构建基础运维/认证相关路由。"""
    router = APIRouter()
    service = OpsService(
        internal_token=internal_token,
        agent=agent,
        verify_password=verify_password,
        verify_auth_or_token=verify_auth_or_token,
    )

    @router.get("/tools")
    async def get_tools_list(
        x_internal_token: str | None = Header(None),
        authorization: str | None = Header(None),
    ):
        return await service.get_tools_list(x_internal_token, authorization)

    @router.post("/login")
    async def login(req: LoginRequest):
        return await service.login(req)

    @router.post("/cancel")
    async def cancel_agent(req: CancelRequest, x_internal_token: str | None = Header(None)):
        return await service.cancel_agent(req, x_internal_token)

    @router.post("/tts")
    async def text_to_speech(req: TTSRequest, x_internal_token: str | None = Header(None)):
        return await service.text_to_speech(req, x_internal_token)

    @router.post("/acp_control")
    async def acp_control(req: ACPControlRequest, x_internal_token: str | None = Header(None)):
        return await service.acp_control(req, x_internal_token)

    @router.post("/acp_status")
    async def acp_status(req: ACPStatusRequest, x_internal_token: str | None = Header(None)):
        return await service.acp_status(req, x_internal_token)

    return router

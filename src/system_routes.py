from typing import Any, Callable

from fastapi import APIRouter, Header

from system_models import SystemTriggerRequest
from system_service import SystemService


def create_system_router(
    *,
    agent: Any,
    verify_internal_token: Callable[[str | None], None],
) -> APIRouter:
    """构建系统触发相关路由。"""
    router = APIRouter()
    service = SystemService(
        agent=agent,
        verify_internal_token=verify_internal_token,
    )

    @router.post("/system_trigger")
    async def system_trigger(req: SystemTriggerRequest, x_internal_token: str | None = Header(None)):
        return await service.system_trigger(req, x_internal_token)

    return router

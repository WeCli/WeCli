from typing import Callable

from fastapi import APIRouter, Header

from settings_models import SettingsUpdateRequest
from settings_service import SettingsService


def create_settings_router(
    *,
    env_path: str,
    verify_auth_or_token: Callable[[str, str, str | None], None],
) -> APIRouter:
    """构建 settings 相关路由。"""
    router = APIRouter()
    service = SettingsService(
        env_path=env_path,
        verify_auth_or_token=verify_auth_or_token,
    )

    @router.get("/settings")
    async def get_settings(user_id: str, password: str = "", x_internal_token: str | None = Header(None)):
        return await service.get_settings(user_id, password, x_internal_token)

    @router.post("/settings")
    async def update_settings(req: SettingsUpdateRequest, x_internal_token: str | None = Header(None)):
        return await service.update_settings(req, x_internal_token)

    @router.get("/settings/full")
    async def get_settings_full(user_id: str, password: str = "", x_internal_token: str | None = Header(None)):
        return await service.get_settings_full(user_id, password, x_internal_token)

    @router.post("/settings/full")
    async def update_settings_full(req: SettingsUpdateRequest, x_internal_token: str | None = Header(None)):
        return await service.update_settings_full(req, x_internal_token)

    @router.post("/restart")
    async def restart_services(req: SettingsUpdateRequest, x_internal_token: str | None = Header(None)):
        return await service.restart_services(req, x_internal_token)

    return router

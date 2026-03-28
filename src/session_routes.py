from typing import Any, Callable

from fastapi import APIRouter, Header

from session_models import (
    DeleteSessionRequest,
    SessionHistoryRequest,
    SessionListRequest,
    SessionStatusRequest,
)
from session_service import SessionService


def create_session_router(
    *,
    db_path: str,
    agent: Any,
    verify_auth_or_token: Callable[[str, str, str | None], None],
    extract_text: Callable[[Any], str],
) -> APIRouter:
    """构建会话相关路由。"""
    router = APIRouter()
    service = SessionService(
        db_path=db_path,
        agent=agent,
        verify_auth_or_token=verify_auth_or_token,
        extract_text=extract_text,
    )

    @router.post("/sessions")
    async def list_sessions(req: SessionListRequest, x_internal_token: str | None = Header(None)):
        return await service.list_sessions(req, x_internal_token)

    @router.post("/sessions_status")
    async def sessions_status(req: SessionListRequest, x_internal_token: str | None = Header(None)):
        return await service.sessions_status(req, x_internal_token)

    @router.post("/session_history")
    async def get_session_history(req: SessionHistoryRequest, x_internal_token: str | None = Header(None)):
        return await service.get_session_history(req, x_internal_token)

    @router.post("/delete_session")
    async def delete_session(req: DeleteSessionRequest, x_internal_token: str | None = Header(None)):
        return await service.delete_session(req, x_internal_token)

    @router.post("/session_status")
    async def session_status(req: SessionStatusRequest, x_internal_token: str | None = Header(None)):
        return await service.session_status(req, x_internal_token)

    return router

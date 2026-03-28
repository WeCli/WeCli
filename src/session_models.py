from pydantic import BaseModel


class SessionListRequest(BaseModel):
    user_id: str
    password: str = ""  # Optional when using X-Internal-Token


class SessionHistoryRequest(BaseModel):
    user_id: str
    password: str = ""  # Optional when using X-Internal-Token
    session_id: str


class DeleteSessionRequest(BaseModel):
    user_id: str
    password: str = ""  # Optional when using X-Internal-Token
    session_id: str = ""  # 为空则删除该用户所有会话


class SessionStatusRequest(BaseModel):
    user_id: str
    password: str = ""  # Optional when using X-Internal-Token
    session_id: str = "default"

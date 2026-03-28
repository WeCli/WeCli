from typing import Any, Literal, Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    user_id: str
    password: str


class CancelRequest(BaseModel):
    user_id: str
    password: str = ""  # Optional when using X-Internal-Token
    session_id: str = "default"


class TTSRequest(BaseModel):
    user_id: str
    password: str = ""  # Optional when using X-Internal-Token
    text: str
    voice: Optional[str] = None


class ACPControlRequest(BaseModel):
    """对外部 ACP agent 执行 /new (新建 session) 或 /stop (取消当前操作) 命令。

    Session routing 通过命令行 --session 参数传入（bridge 当前版本不处理 _meta.sessionKey）。
    - reset_session: 通过命令行 --reset-session 标志强制生成新 session ID（同 key 下刷新状态）
    """
    user_id: str
    password: str = ""
    team: str                              # 群组/团队名
    agent_name: str                        # 外部 agent 的 name (= session_id in members)
    action: Literal["new", "stop"]         # new=新建session, stop=取消当前操作
    reset_session: bool = False            # 重置会话（通过 --reset-session 命令行标志实现）


class ACPStatusRequest(BaseModel):
    """查询外部 agent 的 session 列表 / 运行状态。"""
    user_id: str
    password: str = ""
    team: str
    agent_name: str = ""                   # 为空则查所有外部 agent

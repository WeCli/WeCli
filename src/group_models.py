from typing import Optional

from pydantic import BaseModel, Field


class Attachment(BaseModel):
    """群聊消息附件（图片/音频/文件）"""
    type: str          # "image" | "audio" | "file"
    name: str          # 文件名，如 "photo.png"
    data: str          # base64 编码内容（不含 data:...;base64, 前缀）
    mime_type: str     # "image/png", "application/pdf", "audio/mp3" 等


class GroupCreateRequest(BaseModel):
    name: str
    team_name: Optional[str] = None  # 用于从 team 快速加载成员，不存库
    custom_name: Optional[str] = None  # 自定义群聊标识


class GroupUpdateRequest(BaseModel):
    name: Optional[str] = None


class GroupMessageRequest(BaseModel):
    content: str
    sender: Optional[str] = None       # 人类发消息时可省略（自动取 owner）
    sender_display: Optional[str] = ""  # agent 发言显示名: tag#type#short_name
    mentions: Optional[list[str]] = None  # 被 @ 的 agent global_id 列表
    attachments: Optional[list[Attachment]] = None  # 附件列表（图片/音频/文件）


class GroupAddMemberRequest(BaseModel):
    short_name: str                     # agent 短名 (如 testtool, xl1)
    global_id: str                      # 唯一标识 (内部=session, 外部=global_name)
    member_type: str = "oasis"          # "oasis" (内部) 或 "ext" (外部)
    tag: str = ""                       # agent 的 tag

from dataclasses import dataclass
from typing import Any, Optional

from pydantic import BaseModel


class ChatMessageContent(BaseModel):
    """OpenAI 消息内容部分（text / image_url / input_audio / file）"""
    type: str
    text: Optional[str] = None
    image_url: Optional[dict] = None
    input_audio: Optional[dict] = None
    file: Optional[dict] = None


class ChatMessage(BaseModel):
    """OpenAI 格式的消息"""
    role: str  # "system" | "user" | "assistant" | "tool"
    content: Optional[Any] = None  # str 或 list[ChatMessageContent]
    name: Optional[str] = None
    tool_calls: Optional[list[dict]] = None
    tool_call_id: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    """OpenAI /v1/chat/completions 请求格式"""
    model: Optional[str] = None
    messages: list[ChatMessage]
    stream: bool = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    tools: Optional[list[dict]] = None
    tool_choice: Optional[Any] = None
    user: Optional[str] = None
    session_id: Optional[str] = "default"
    password: Optional[str] = None
    enabled_tools: Optional[list[str]] = None
    # Per-request LLM model override (used by OASIS SessionExpert)
    llm_override: Optional[dict] = None


@dataclass
class OpenAIExecutionContext:
    user_id: str
    session_id: str
    thread_id: str
    config: dict
    user_input: dict
    model_name: str
    external_tool_names: set[str]
    thread_lock: Any

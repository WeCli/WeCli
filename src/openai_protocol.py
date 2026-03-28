import json
import os
import time
import uuid
from typing import Any, Callable, Dict, Optional, Set

from langchain_core.messages import AIMessage, HumanMessage

from openai_models import ChatMessage


class OpenAIProtocolHelper:
    """OpenAI compatibility protocol helpers (message transform + response encoding)."""

    def __init__(
        self,
        *,
        build_human_message: Callable[[str, Optional[list], Optional[list], Optional[list]], HumanMessage],
    ):
        self.build_human_message = build_human_message

    def openai_msg_to_human_message(self, msg: ChatMessage) -> HumanMessage:
        content = msg.content
        if content is None:
            return HumanMessage(content="(空消息)")
        if isinstance(content, str):
            return HumanMessage(content=content)

        text_parts = []
        image_parts = []
        audio_parts = []
        file_parts = []
        for part in content:
            p = part if isinstance(part, dict) else part.dict()
            ptype = p.get("type", "")
            if ptype == "text":
                text_parts.append(p.get("text", ""))
            elif ptype == "image_url":
                image_parts.append(p)
            elif ptype == "input_audio":
                audio_parts.append(p.get("input_audio", {}))
            elif ptype == "file":
                file_parts.append(p)

        if not image_parts and not audio_parts and not file_parts:
            return HumanMessage(content="\n".join(text_parts) or "(空消息)")

        combined_text = "\n".join(text_parts)

        images = []
        for ip in image_parts:
            url = ip.get("image_url", {}).get("url", "")
            if url:
                images.append(url)

        audios = []
        for ad in audio_parts:
            audios.append({
                "base64": ad.get("data", ""),
                "format": ad.get("format", "webm"),
                "name": "recording.{fmt}".format(fmt=ad.get("format", "webm")),
            })

        media_exts = {
            ".avi",
            ".mp4",
            ".mkv",
            ".mov",
            ".webm",
            ".mp3",
            ".wav",
            ".flac",
            ".ogg",
            ".aac",
        }
        files = []
        for fp in file_parts:
            fdata = fp.get("file", {})
            fname = fdata.get("filename", "file")
            ext = os.path.splitext(fname)[1].lower()
            if fname.endswith(".pdf"):
                ftype = "pdf"
            elif ext in media_exts:
                ftype = "media"
            else:
                ftype = "text"
            files.append({
                "name": fname,
                "content": fdata.get("file_data", ""),
                "type": ftype,
            })

        return self.build_human_message(combined_text, images or None, files or None, audios or None)

    @staticmethod
    def make_completion_id() -> str:
        return "chatcmpl-{suffix}".format(suffix=uuid.uuid4().hex[:24])

    def make_openai_response(
        self,
        content: str,
        *,
        model: str = "teambot",
        finish_reason: str = "stop",
        tool_calls: Optional[list] = None,
    ) -> Dict[str, Any]:
        message: Dict[str, Any] = {"role": "assistant", "content": content}
        if tool_calls:
            message["tool_calls"] = tool_calls
            finish_reason = "tool_calls"
        return {
            "id": self.make_completion_id(),
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": message,
                "finish_reason": finish_reason,
            }],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    def make_openai_chunk(
        self,
        *,
        completion_id: str,
        content: str = "",
        model: str = "teambot",
        finish_reason: Optional[str] = None,
        meta: Optional[dict] = None,
    ) -> str:
        delta: Dict[str, Any] = {}
        if content:
            delta["content"] = content
        if meta:
            delta["meta"] = meta
        if finish_reason is None and not content and not meta:
            delta["role"] = "assistant"
        chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "delta": delta,
                "finish_reason": finish_reason,
            }],
        }
        return "data: {payload}\n\n".format(payload=json.dumps(chunk, ensure_ascii=False))

    @staticmethod
    def extract_external_tool_names(tools: Optional[list]) -> Set[str]:
        if not tools:
            return set()
        names: Set[str] = set()
        for tool in tools:
            if tool.get("type") == "function":
                names.add(tool["function"]["name"])
            elif tool.get("name"):
                names.add(tool["name"])
        return names

    @staticmethod
    def format_tool_calls_for_openai(ai_msg: AIMessage, external_names: Set[str]) -> Optional[list]:
        if not hasattr(ai_msg, "tool_calls") or not ai_msg.tool_calls:
            return None
        external_calls = []
        for tc in ai_msg.tool_calls:
            if tc["name"] in external_names:
                external_calls.append({
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": json.dumps(tc.get("args", {}), ensure_ascii=False),
                    },
                })
        return external_calls or None

    @staticmethod
    def make_tool_calls_chunk(*, completion_id: str, model: str, tool_calls: list) -> str:
        chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {"tool_calls": tool_calls},
                "finish_reason": "tool_calls",
            }],
        }
        return "data: {payload}\n\n".format(payload=json.dumps(chunk, ensure_ascii=False))

    @staticmethod
    def list_models_payload() -> Dict[str, Any]:
        return {
            "object": "list",
            "data": [{
                "id": "teambot",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "teambot",
            }],
        }

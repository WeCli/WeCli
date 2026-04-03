import asyncio
import contextlib
import json
import os
import shlex
import shutil
import tempfile
from typing import Any


class AcpxError(RuntimeError):
    pass


class AcpxAdapter:
    """Minimal async wrapper around acpx CLI sessions/prompt."""

    def __init__(self, *, cwd: str | None = None):
        self._acpx_bin = shutil.which("acpx")
        self._cwd = cwd or os.getcwd()
        if not self._acpx_bin:
            raise AcpxError("acpx binary not found in PATH")

    @property
    def available(self) -> bool:
        return bool(self._acpx_bin)

    @staticmethod
    def to_acpx_session_name(*, tool: str, session_key: str) -> str:
        # Use business session key directly as acpx transport session.
        return session_key

    async def ensure_session(self, *, tool: str, session_key: str, acpx_session: str) -> None:
        await self._run_json(
            self._command_prefix(tool=tool, session_key=session_key) + ["sessions", "ensure", "--name", acpx_session],
            timeout_sec=20,
            allow_nonzero=False,
        )

    async def close_session(self, *, tool: str, session_key: str, acpx_session: str) -> None:
        # close is best-effort; missing session should not fail callers
        await self._run_json(
            self._command_prefix(tool=tool, session_key=session_key) + ["sessions", "close", acpx_session],
            timeout_sec=10,
            allow_nonzero=True,
        )

    async def prompt(
        self,
        *,
        tool: str,
        session_key: str,
        prompt_text: str,
        timeout_sec: int = 180,
        reset_session: bool = False,
        attachments: list[dict] | None = None,
    ) -> str:
        """
        Send a prompt to the agent.
        
        Args:
            tool: Agent tool name (openclaw, claude, codex, etc.)
            session_key: Session key
            prompt_text: Text prompt
            timeout_sec: Timeout in seconds
            reset_session: Whether to reset the session
            attachments: List of attachments with keys:
                - type: "image" | "audio" | "text"
                - mime_type: MIME type string
                - data: base64-encoded content
                - name: filename
        """
        acpx_session = self.to_acpx_session_name(tool=tool, session_key=session_key)
        if reset_session:
            await self.close_session(tool=tool, session_key=session_key, acpx_session=acpx_session)

        # Ensure transport session on every call
        await self.ensure_session(tool=tool, session_key=session_key, acpx_session=acpx_session)

        # Build multimodal prompt content (JSON array)
        content_blocks = [{"type": "text", "text": prompt_text.strip() or "(empty prompt)"}]
        
        # Add attachment blocks for images
        if attachments:
            for att in attachments:
                att_type = att.get("type", "")
                mime_type = att.get("mime_type", "")
                data = att.get("data", "")

                # 处理带 data: 前缀的 base64（如前端 "data:image/png;base64,xxx"）
                if data.startswith("data:"):
                    # 提取 mime type 和纯 base64
                    header, b64data = data.split(",", 1)
                    if ";" in header:
                        # 提取 mime type，如 "data:image/png;base64" → "image/png"
                        incoming_mime = header.replace("data:", "").split(";")[0]
                        if not mime_type:
                            mime_type = incoming_mime
                    data = b64data
                
                if att_type == "image" and data:
                    content_blocks.append({
                        "type": "image",
                        "mimeType": mime_type or "image/png",
                        "data": data,
                    })
                elif att_type == "audio" and data:
                    content_blocks.append({
                        "type": "input_audio",
                        "mimeType": mime_type or "audio/wav",
                        "data": data,
                    })
        
        # Always use --file mode for multimodal content to avoid argument length limits
        # Also use unique filename to avoid conflicts when multiple agents are running
        json_content = json.dumps(content_blocks, ensure_ascii=False)
        
        # Generate unique temp file name with timestamp to avoid conflicts
        import time
        import uuid
        unique_suffix = f"{int(time.time()*1000)}_{uuid.uuid4().hex[:8]}"
        temp_path = os.path.join(tempfile.gettempdir(), f"acpx_prompt_{unique_suffix}.json")
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(json_content)
        
        prompt_args = self._command_prefix(tool=tool, session_key=session_key)
        prompt_args += ["prompt", "-s", acpx_session, "--file", temp_path]
        try:
            output = await self._run_json(
                prompt_args,
                timeout_sec=timeout_sec,
                allow_nonzero=False,
            )
        finally:
            try:
                os.unlink(temp_path)
            except Exception:
                pass
        
        text = self._extract_text(output)
        if text is None:
            return output.strip()
        return text

    async def _run_json(self, args: list[str], *, timeout_sec: int, allow_nonzero: bool) -> str:
        assert self._acpx_bin is not None
        cmd = [
            self._acpx_bin,
            "--cwd",
            self._cwd,
            "--format",
            "json",
            "--json-strict",
            *args,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_sec)
        except asyncio.TimeoutError as e:
            with contextlib.suppress(Exception):
                proc.kill()
            raise AcpxError(f"acpx timeout after {timeout_sec}s: {' '.join(shlex.quote(x) for x in cmd)}") from e

        out = out_b.decode("utf-8", errors="replace")
        err = err_b.decode("utf-8", errors="replace")
        if proc.returncode != 0 and not allow_nonzero:
            msg = err.strip() or out.strip() or f"exit={proc.returncode}"
            raise AcpxError(f"acpx failed ({proc.returncode}): {msg}")
        return out

    @staticmethod
    def _command_prefix(*, tool: str, session_key: str) -> list[str]:
        # openclaw must use raw --agent command in this environment.
        if tool == "openclaw":
            raw = f"openclaw acp --session {shlex.quote(session_key)}"
            return ["--agent", raw]
        return [tool]

    @staticmethod
    def _extract_text(output: str) -> str | None:
        # acpx may emit one or multiple JSON lines. Pick the last line with textual payload.
        text: str | None = None
        for line in output.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            cand = AcpxAdapter._pick_text(obj)
            if cand:
                text = cand
        return text

    @staticmethod
    def _pick_text(obj: Any) -> str | None:
        if isinstance(obj, dict):
            for key in ("text", "content", "message", "summary", "reply"):
                val = obj.get(key)
                if isinstance(val, str) and val.strip():
                    return val
            result = obj.get("result")
            if isinstance(result, dict):
                return AcpxAdapter._pick_text(result)
            if isinstance(result, str) and result.strip():
                return result
        return None


_adapter_singleton: AcpxAdapter | None = None


def get_acpx_adapter(*, cwd: str | None = None) -> AcpxAdapter:
    global _adapter_singleton
    if _adapter_singleton is None:
        _adapter_singleton = AcpxAdapter(cwd=cwd)
    return _adapter_singleton

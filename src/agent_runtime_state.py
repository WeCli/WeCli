import asyncio
from typing import Dict, List, Optional


class TaskRegistry:
    """Track and control active async tasks by key."""

    def __init__(self):
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._task_lock: Optional[asyncio.Lock] = None

    async def _get_task_lock(self) -> asyncio.Lock:
        if self._task_lock is None:
            self._task_lock = asyncio.Lock()
        return self._task_lock

    async def cancel(self, task_key: str, timeout_seconds: float = 5.0) -> bool:
        """Cancel the active task for *task_key*.

        Returns ``True`` if a running task was actually found and cancelled,
        ``False`` if no active task existed for the key.
        """
        lock = await self._get_task_lock()
        async with lock:
            task = self._active_tasks.get(task_key)
            actually_cancelled = False
            if task and not task.done():
                task.cancel()
                actually_cancelled = True
                try:
                    await asyncio.wait_for(
                        asyncio.ensure_future(self._wait_task(task)),
                        timeout=timeout_seconds,
                    )
                except asyncio.TimeoutError:
                    # 超时：task 仍未结束，再发一次 cancel 并强制移除，
                    # 避免僵尸协程残留在注册表中。
                    import logging
                    logging.getLogger("TaskRegistry").warning(
                        "Task %s did not finish within %.1fs after cancel; "
                        "sending another cancel and removing from registry.",
                        task_key, timeout_seconds,
                    )
                    task.cancel()
                    # 仍然 fall through 到下面的 pop
                except (asyncio.CancelledError, Exception):
                    pass
            self._active_tasks.pop(task_key, None)
            return actually_cancelled

    @staticmethod
    async def _wait_task(task: asyncio.Task) -> None:
        """等待 task 结束，吞掉其 CancelledError/Exception。

        与直接 await task 的区别：外层 wait_for 超时时可以正常
        cancel 这个 wrapper coroutine，而不会影响原 task 本身
        （原 task 已经在上面收到了 cancel 信号，这里只是旁观等待）。
        """
        try:
            await task
        except (asyncio.CancelledError, Exception):
            pass

    def register(self, task_key: str, task: asyncio.Task) -> None:
        self._active_tasks[task_key] = task

    def unregister(self, task_key: str) -> None:
        self._active_tasks.pop(task_key, None)

    def list_keys(self, prefix: str = "") -> List[str]:
        if not prefix:
            return list(self._active_tasks.keys())
        return [key for key in self._active_tasks.keys() if key.startswith(prefix)]


class ThreadStateRegistry:
    """Manage per-thread lock, busy source, and pending system-message counters."""

    def __init__(self):
        self._thread_locks: Dict[str, asyncio.Lock] = {}
        self._thread_locks_guard: Optional[asyncio.Lock] = None
        self._thread_busy_source: Dict[str, str] = {}
        self._pending_system_messages: Dict[str, int] = {}

    async def _get_locks_guard(self) -> asyncio.Lock:
        if self._thread_locks_guard is None:
            self._thread_locks_guard = asyncio.Lock()
        return self._thread_locks_guard

    async def get_lock(self, thread_id: str) -> asyncio.Lock:
        guard = await self._get_locks_guard()
        async with guard:
            if thread_id not in self._thread_locks:
                self._thread_locks[thread_id] = asyncio.Lock()
            return self._thread_locks[thread_id]

    def add_pending_system_message(self, thread_id: str) -> None:
        self._pending_system_messages[thread_id] = self._pending_system_messages.get(thread_id, 0) + 1

    def consume_pending_system_messages(self, thread_id: str) -> int:
        return self._pending_system_messages.pop(thread_id, 0)

    def has_pending_system_messages(self, thread_id: str) -> bool:
        return self._pending_system_messages.get(thread_id, 0) > 0

    def is_thread_busy(self, thread_id: str) -> bool:
        lock = self._thread_locks.get(thread_id)
        return lock is not None and lock.locked()

    def set_thread_busy_source(self, thread_id: str, source: str) -> None:
        self._thread_busy_source[thread_id] = source

    def clear_thread_busy_source(self, thread_id: str) -> None:
        self._thread_busy_source.pop(thread_id, None)

    def get_thread_busy_source(self, thread_id: str) -> str:
        if not self.is_thread_busy(thread_id):
            return ""
        return self._thread_busy_source.get(thread_id, "unknown")

    def get_all_thread_status(self, prefix: str) -> Dict[str, Dict[str, object]]:
        result: Dict[str, Dict[str, object]] = {}
        for thread_id, lock in self._thread_locks.items():
            if not thread_id.startswith(prefix):
                continue
            busy = lock.locked()
            result[thread_id] = {
                "busy": busy,
                "source": self._thread_busy_source.get(thread_id, "") if busy else "",
                "pending_system": self._pending_system_messages.get(thread_id, 0),
            }
        return result

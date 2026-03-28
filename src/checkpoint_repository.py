import sqlite3

import aiosqlite


def _is_missing_table_error(exc: sqlite3.OperationalError) -> bool:
    return "no such table" in str(exc).lower()


async def list_thread_ids_by_prefix(db_path: str, prefix: str) -> list[str]:
    """按 thread_id 前缀查询会话列表。"""
    async with aiosqlite.connect(db_path) as db:
        try:
            cursor = await db.execute(
                "SELECT DISTINCT thread_id FROM checkpoints WHERE thread_id LIKE ? ORDER BY thread_id",
                (f"{prefix}%",),
            )
            rows = await cursor.fetchall()
        except sqlite3.OperationalError as exc:
            if _is_missing_table_error(exc):
                return []
            raise
    return [row[0] for row in rows]


async def delete_thread_records(db_path: str, thread_id: str) -> None:
    """删除指定 thread 在 checkpoints/writes 中的记录。"""
    async with aiosqlite.connect(db_path) as db:
        for table in ("checkpoints", "writes"):
            try:
                await db.execute(f"DELETE FROM {table} WHERE thread_id = ?", (thread_id,))
            except sqlite3.OperationalError as exc:
                if not _is_missing_table_error(exc):
                    raise
        await db.commit()


async def delete_thread_records_like(db_path: str, pattern: str) -> None:
    """按 LIKE 模式删除 checkpoints/writes 记录。"""
    async with aiosqlite.connect(db_path) as db:
        for table in ("checkpoints", "writes"):
            try:
                await db.execute(f"DELETE FROM {table} WHERE thread_id LIKE ?", (pattern,))
            except sqlite3.OperationalError as exc:
                if not _is_missing_table_error(exc):
                    raise
        await db.commit()


async def purge_old_checkpoints(db_path: str, thread_id: str, keep: int = 1) -> int:
    """
    清理指定 thread 的旧 checkpoint，只保留最近 `keep` 个。

    LangGraph 的 AsyncSqliteSaver 每次 graph 执行都会写入新的 checkpoint，
    随着对话进行，checkpoint 数量会无限增长。此函数删除旧的 checkpoint 及其
    关联的 writes 记录，只保留最新的 `keep` 个。

    返回删除的 checkpoint 数量。
    """
    deleted = 0
    async with aiosqlite.connect(db_path) as db:
        try:
            # 找出该 thread 的所有 checkpoint_id，按 checkpoint_id 倒序排列
            # （LangGraph 的 checkpoint_id 是递增的 UUID/时间戳，越新越大）
            cursor = await db.execute(
                "SELECT checkpoint_id FROM checkpoints "
                "WHERE thread_id = ? "
                "ORDER BY checkpoint_id DESC",
                (thread_id,),
            )
            all_ids = [row[0] for row in await cursor.fetchall()]
        except sqlite3.OperationalError as exc:
            if _is_missing_table_error(exc):
                return 0
            raise

        if len(all_ids) <= keep:
            return 0  # 没有需要删除的

        # 要删除的 checkpoint_id
        ids_to_delete = all_ids[keep:]

        # 批量删除 checkpoints 和 writes
        placeholders = ",".join("?" for _ in ids_to_delete)
        for table in ("checkpoints", "writes"):
            try:
                await db.execute(
                    f"DELETE FROM {table} WHERE thread_id = ? AND checkpoint_id IN ({placeholders})",
                    [thread_id] + ids_to_delete,
                )
            except sqlite3.OperationalError as exc:
                if not _is_missing_table_error(exc):
                    raise
        await db.commit()
        deleted = len(ids_to_delete)

    return deleted

"""LangGraph Checkpoint Saver — MySQL 实现

直接使用原始 aiomysql 连接和游标，绕过 MySQLConnection 包装层，
避免 'Command Out of Sync' 错误。
"""

import asyncio
import base64
import json
import logging
from typing import Any, AsyncIterator, Sequence

import aiomysql
from langgraph.checkpoint.base import (
  BaseCheckpointSaver,
  CheckpointTuple,
  Checkpoint,
  CheckpointMetadata,
)
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

logger = logging.getLogger(__name__)

SERIALIZER = JsonPlusSerializer()


class MySQLSaver(BaseCheckpointSaver):
  """LangGraph Checkpoint Saver — MySQL 后端（原始连接模式）"""

  def __init__(self):
    super().__init__(serde=SERIALIZER)
    self._conn: aiomysql.Connection | None = None
    self._init_lock = asyncio.Lock()
    # 操作锁：序列化所有数据库访问，防止并发协程争用同一连接
    self._op_lock = asyncio.Lock()

  async def _ensure_conn(self) -> aiomysql.Connection:
    if self._conn is not None:
      return self._conn
    async with self._init_lock:
      if self._conn is not None:
        return self._conn
      from app.common.core.database import MySQLDatabase
      mgr = await MySQLDatabase.get_instance()
      self._conn = await mgr._pool.acquire()
    return self._conn

  async def _close_cursor(self, cursor: aiomysql.DictCursor | None) -> None:
    if cursor is None:
      return
    try:
      try:
        await cursor.fetchall()
      except Exception:
        pass
    finally:
      try:
        await cursor.close()
      except Exception:
        pass

  async def _commit(self) -> None:
    conn = await self._ensure_conn()
    cur = await conn.cursor(aiomysql.DictCursor)
    try:
      await cur.execute("COMMIT")
    finally:
      await self._close_cursor(cur)

  # ─── BaseCheckpointSaver 接口实现 ────────────────────────────

  async def aget_tuple(self, config: dict) -> CheckpointTuple | None:
    async with self._op_lock:
      conn = await self._ensure_conn()
      thread_id = config["configurable"]["thread_id"]
      checkpoint_id = config["configurable"].get("checkpoint_id", "")

      cursor = await conn.cursor(aiomysql.DictCursor)
      try:
        if checkpoint_id:
          await cursor.execute(
            "SELECT type, checkpoint, metadata, parent_checkpoint_id "
            "FROM langgraph_checkpoints "
            "WHERE thread_id = %s AND checkpoint_id = %s",
            (thread_id, checkpoint_id),
          )
        else:
          await cursor.execute(
            "SELECT type, checkpoint, metadata, parent_checkpoint_id "
            "FROM langgraph_checkpoints "
            "WHERE thread_id = %s "
            "ORDER BY created_at DESC LIMIT 1",
            (thread_id,),
          )

        row = await cursor.fetchone()
        if not row:
          return None

        checkpoint_raw = row["checkpoint"]
        if isinstance(checkpoint_raw, str):
          try:
            serialized = base64.b64decode(checkpoint_raw)
          except Exception:
            serialized = checkpoint_raw
        else:
          serialized = checkpoint_raw
        checkpoint = SERIALIZER.loads_typed((row["type"], serialized))
        metadata = row["metadata"] if isinstance(row["metadata"], dict) else json.loads(row["metadata"] or "{}")

        parent_config = None
        if row.get("parent_checkpoint_id"):
          parent_config = {
            "configurable": {
              "thread_id": thread_id,
              "checkpoint_id": row["parent_checkpoint_id"],
            }
          }

        return CheckpointTuple(
          config={"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint["id"]}},
          checkpoint=checkpoint,
          metadata=metadata,
          parent_config=parent_config,
        )
      finally:
        await self._close_cursor(cursor)

  async def alist(
    self,
    config: dict,
    *,
    filter: dict | None = None,
    before: dict | None = None,
    limit: int | None = None,
  ) -> AsyncIterator[CheckpointTuple]:
    async with self._op_lock:
      conn = await self._ensure_conn()
      thread_id = config["configurable"]["thread_id"]

      query = "SELECT type, checkpoint, metadata, parent_checkpoint_id FROM langgraph_checkpoints WHERE thread_id = %s"
      params: list[Any] = [thread_id]

      if before and "checkpoint_id" in before.get("configurable", {}):
        query += " AND created_at < (SELECT created_at FROM langgraph_checkpoints WHERE thread_id = %s AND checkpoint_id = %s)"
        params.extend([thread_id, before["configurable"]["checkpoint_id"]])

      query += " ORDER BY created_at DESC"
      if limit:
        query += " LIMIT %s"
        params.append(limit)

      cursor = await conn.cursor(aiomysql.DictCursor)
      try:
        await cursor.execute(query, tuple(params))
        rows = await cursor.fetchall()
      finally:
        await self._close_cursor(cursor)

      for row in (rows or []):
        checkpoint_raw = row["checkpoint"]
        if isinstance(checkpoint_raw, str):
          try:
            serialized = base64.b64decode(checkpoint_raw)
          except Exception:
            serialized = checkpoint_raw
        else:
          serialized = checkpoint_raw
        checkpoint = SERIALIZER.loads_typed((row["type"], serialized))
        metadata = row["metadata"] if isinstance(row["metadata"], dict) else json.loads(row["metadata"] or "{}")
        parent_config = None
        if row.get("parent_checkpoint_id"):
          parent_config = {
            "configurable": {
              "thread_id": thread_id,
              "checkpoint_id": row["parent_checkpoint_id"],
            }
          }
        yield CheckpointTuple(
          config={"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint["id"]}},
          checkpoint=checkpoint,
          metadata=metadata,
          parent_config=parent_config,
        )

  async def aput(
    self,
    config: dict,
    checkpoint: Checkpoint,
    metadata: CheckpointMetadata,
    new_versions: dict,
  ) -> dict:
    async with self._op_lock:
      conn = await self._ensure_conn()
      thread_id = config["configurable"]["thread_id"]
      parent_checkpoint_id = config["configurable"].get("checkpoint_id", "")

      checkpoint_id = checkpoint["id"]
      type_, serialized = SERIALIZER.dumps_typed(checkpoint)

      if isinstance(serialized, bytes):
        checkpoint_data = json.dumps(base64.b64encode(serialized).decode('ascii'))
      elif isinstance(serialized, dict):
        checkpoint_data = json.dumps(serialized, ensure_ascii=False)
      else:
        checkpoint_data = json.dumps(serialized, ensure_ascii=False, default=str)

      cursor = await conn.cursor(aiomysql.DictCursor)
      try:
        await cursor.execute(
          "INSERT INTO langgraph_checkpoints "
          "(thread_id, checkpoint_id, parent_checkpoint_id, type, checkpoint, metadata) "
          "VALUES (%s, %s, %s, %s, %s, %s) AS new "
          "ON DUPLICATE KEY UPDATE checkpoint = new.checkpoint, metadata = new.metadata",
          (
            thread_id,
            checkpoint_id,
            parent_checkpoint_id or None,
            type_,
            checkpoint_data,
            json.dumps(metadata, ensure_ascii=False),
          ),
        )
      finally:
        await self._close_cursor(cursor)

      await self._commit()

      return {
        "configurable": {
          "thread_id": thread_id,
          "checkpoint_id": checkpoint_id,
        }
      }

  async def aput_writes(
    self,
    config: dict,
    writes: Sequence[tuple[str, Any]],
    task_id: str,
  ) -> None:
    async with self._op_lock:
      conn = await self._ensure_conn()
      thread_id = config["configurable"]["thread_id"]
      checkpoint_id = config["configurable"]["checkpoint_id"]

      cursor = await conn.cursor(aiomysql.DictCursor)
      try:
        await cursor.execute(
          "DELETE FROM langgraph_checkpoint_writes "
          "WHERE thread_id = %s AND checkpoint_id = %s AND task_id = %s",
          (thread_id, checkpoint_id, task_id),
        )
      finally:
        await self._close_cursor(cursor)

      for idx, (channel, value) in enumerate(writes):
        c = await conn.cursor(aiomysql.DictCursor)
        try:
          await c.execute(
            "INSERT INTO langgraph_checkpoint_writes "
            "(thread_id, checkpoint_id, task_id, idx, channel, type, value) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
              thread_id,
              checkpoint_id,
              task_id,
              idx,
              channel,
              type(value).__name__,
              json.dumps(value, ensure_ascii=False, default=str),
            ),
          )
        finally:
          await self._close_cursor(c)

      await self._commit()

  async def adelete_thread(self, thread_id: str) -> None:
    async with self._op_lock:
      conn = await self._ensure_conn()
      cursor = await conn.cursor(aiomysql.DictCursor)
      try:
        await cursor.execute("DELETE FROM langgraph_checkpoint_writes WHERE thread_id = %s", (thread_id,))
      finally:
        await self._close_cursor(cursor)

      cursor = await conn.cursor(aiomysql.DictCursor)
      try:
        await cursor.execute("DELETE FROM langgraph_checkpoints WHERE thread_id = %s", (thread_id,))
      finally:
        await self._close_cursor(cursor)

      await self._commit()

  async def aclose(self) -> None:
    if self._conn:
      from app.common.core.database import MySQLDatabase
      mgr = await MySQLDatabase.get_instance()
      if mgr._pool and self._conn:
        mgr._pool.release(self._conn)
      self._conn = None


async def init_checkpoint_tables() -> None:
  """初始化 LangGraph checkpoint MySQL 表"""
  from app.common.core.database import MySQLDatabase, CREATE_TABLES_SQL
  mgr = await MySQLDatabase.get_instance()
  raw_conn = await mgr._pool.acquire()
  cursor = await raw_conn.cursor(aiomysql.DictCursor)
  try:
    for stmt in CREATE_TABLES_SQL.strip().split(";"):
      stmt = stmt.strip()
      if stmt and "langgraph" in stmt.lower():
        await cursor.execute(stmt)
    await raw_conn.commit()
    logger.info("LangGraph checkpoint MySQL 表初始化完成")
  finally:
    await cursor.close()
    mgr._pool.release(raw_conn)

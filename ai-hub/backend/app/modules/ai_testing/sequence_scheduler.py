"""生成序列调度器 — 免费模型串行 / 付费模型并行

设计要点：
  - 一个序列 = 需求按章节拆分出的 N 个子生成任务（testing_generation_tasks）
  - 调度并发策略由模型 tier 决定：
      free → max_parallel = 1（单任务序列，严格按 seq_index 顺序执行）
      paid → max_parallel = min(子任务数, SEQUENCE_MAX_PARALLEL_PAID)
  - 子任务执行复用单任务 4 步流水线（_run_pipeline_events + _persist_and_finish）
  - 取消/状态以 DB 为准（多 worker 安全）；SSE 通过进程内广播器推送快照
  - 服务重启后的残留 running 任务由 database.recover_interrupted_tasks 回收
"""

import asyncio
import json
import logging
import re
import time
import uuid
from datetime import datetime
from typing import Any, AsyncGenerator

from app.common.core.database import get_db_context
from app.common.core.llm_factory import get_model_tier
from app.config import get_settings
from app.common.utils.sse_helper import format_sse_event
from app.modules.ai_testing.repository import TestingRepo
from app.modules.ai_testing.service import TestingService
from app.modules.ai_testing.sse_stream import (
  _load_task,
  _persist_and_finish,
  _run_pipeline_events,
  _parse_model_field,
)

logger = logging.getLogger(__name__)


# ─── 需求拆分 ────────────────────────────────────────────────


def split_requirement(text: str, desired: int | None = None) -> list[tuple[str, str]]:
  """把需求文档拆分为子任务序列 [(title, content), ...]

  策略：
    1. 优先按 Markdown 一级/二级标题切分章节
    2. 章节不足时按空行段落聚合
    3. desired 指定时尽量聚合为 desired 个子任务
  """
  text = (text or "").strip()
  if not text:
    return []

  # 1) 按标题切分
  sections: list[tuple[str, str]] = []
  current_title, current_lines = "概述", []
  for line in text.splitlines():
    m = re.match(r'^(#{1,2})\s+(.+)$', line.strip())
    if m:
      if "\n".join(current_lines).strip():
        sections.append((current_title, "\n".join(current_lines).strip()))
      current_title = m.group(2).strip()[:120]
      current_lines = [line]
    else:
      current_lines.append(line)
  if "\n".join(current_lines).strip():
    sections.append((current_title, "\n".join(current_lines).strip()))

  usable = [s for s in sections if len(s[1].strip()) > 20] or sections

  # 2) 无结构长文按段落聚合
  if len(usable) <= 1:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(paras) > 1:
      usable = [(f"片段 {i + 1}", p) for i, p in enumerate(paras)]
    else:
      return [("完整需求", text)]

  # 3) 聚合到目标数量
  target = max(1, min(desired or len(usable), len(usable), 20))
  if len(usable) > target:
    merged: list[tuple[str, str]] = []
    per = -(-len(usable) // target)  # ceil
    for i in range(0, len(usable), per):
      group = usable[i:i + per]
      title = group[0][0] if len(group) == 1 else f"{group[0][0]} 等 {len(group)} 节"
      merged.append((title, "\n\n".join(c for _, c in group)))
    usable = merged

  return usable


# ─── SSE 广播器 ─────────────────────────────────────────────


class _SequenceHub:
  """进程内序列事件广播中心：scheduler 推送，SSE 端点订阅"""

  def __init__(self) -> None:
    self._subs: dict[str, list[asyncio.Queue]] = {}
    self._lock = asyncio.Lock()

  async def subscribe(self, seq_id: str) -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue(maxsize=512)
    async with self._lock:
      self._subs.setdefault(seq_id, []).append(q)
    return q

  async def unsubscribe(self, seq_id: str, q: asyncio.Queue) -> None:
    async with self._lock:
      subs = self._subs.get(seq_id, [])
      if q in subs:
        subs.remove(q)

  async def publish(self, seq_id: str, event: str, data: dict) -> None:
    payload = format_sse_event(event, data)
    async with self._lock:
      subs = list(self._subs.get(seq_id, []))
    for q in subs:
      try:
        q.put_nowait(payload)
      except asyncio.QueueFull:
        logger.warning("[seq-hub] 订阅队列溢出，丢弃事件 seq=%s", seq_id)


sequence_hub = _SequenceHub()


# ─── 调度器 ─────────────────────────────────────────────────


class SequenceScheduler:
  """每序列一个 asyncio 调度协程；Semaphore 控制并行度"""

  def __init__(self) -> None:
    self._running: dict[str, asyncio.Task] = {}

  def is_running(self, seq_id: str) -> bool:
    t = self._running.get(seq_id)
    return bool(t and not t.done())

  async def start(self, seq_id: str) -> bool:
    """启动序列调度；返回是否新启动（False = 已在运行）"""
    if self.is_running(seq_id):
      return False
    task = asyncio.create_task(self._run_sequence(seq_id))
    self._running[seq_id] = task
    return True

  # ── 内部执行 ──

  async def _seq_status(self, seq_id: str) -> str:
    async with get_db_context() as db:
      seq = await TestingRepo(db).get_generation_sequence(seq_id)
      return (seq or {}).get("status", "")

  async def _publish_counts(self, seq_id: str, **extra: Any) -> None:
    """聚合计数并广播 sequence_progress 快照"""
    async with get_db_context() as db:
      repo = TestingRepo(db)
      counts = await repo.get_sequence_progress_counts(seq_id)
      await repo.update_generation_sequence(seq_id, **counts)
    await sequence_hub.publish(seq_id, "sequence_progress", {
      "sequence_id": seq_id, **counts, **extra,
    })

  async def _run_sequence(self, seq_id: str) -> None:
    try:
      async with get_db_context() as db:
        repo = TestingRepo(db)
        seq = await repo.get_generation_sequence(seq_id)
        if not seq:
          logger.error("[seq] 序列 %s 不存在", seq_id)
          return
        if seq["status"] == "cancelled":
          return
        await repo.update_generation_sequence(seq_id, status="running")
        max_parallel = max(1, int(seq.get("max_parallel") or 1))

      await self._publish_counts(seq_id, strategy=seq["strategy"],
                                 tier=seq["model_tier"], max_parallel=max_parallel)

      # 严格按 seq_index 顺序领取任务
      async with get_db_context() as db:
        subtasks = await TestingRepo(db).list_sequence_subtasks(seq_id)

      pending = [t for t in subtasks if t["status"] in ("pending", "running")]
      semaphore = asyncio.Semaphore(max_parallel)
      slots = set(range(max_parallel))
      slots_lock = asyncio.Lock()

      async def run_one(sub: dict) -> str:
        if await self._seq_status(seq_id) == "cancelled":
          return "cancelled"
        async with semaphore:
          if await self._seq_status(seq_id) == "cancelled":
            return "cancelled"
          # 分配展示槽位（前端并行泳道用）
          async with slots_lock:
            slot = min(slots) if slots else 0
            slots.discard(slot)
          try:
            return await self._run_subtask(seq_id, sub, slot, max_parallel)
          finally:
            async with slots_lock:
              slots.add(slot)

      results = await asyncio.gather(
        *(run_one(t) for t in pending), return_exceptions=True,
      )
      for sub, r in zip(pending, results):
        if isinstance(r, Exception):
          logger.error("[seq] 子任务 %s 调度异常: %s", sub["id"], r, exc_info=r)

      # 汇总终态
      await self._publish_counts(seq_id)
      async with get_db_context() as db:
        repo = TestingRepo(db)
        final = await repo.get_sequence_progress_counts(seq_id)
        if await repo.get_generation_sequence(seq_id) is None:
          return
        if final["cancelled_count"] == final["total"]:
          status = "cancelled"
        elif final["failed_count"] > 0:
          status = "partial_failed"
        elif final["success_count"] == final["total"]:
          status = "completed"
        else:
          status = "partial_failed"
        await repo.update_generation_sequence(seq_id, status=status, running_count=0)
      await sequence_hub.publish(seq_id, "sequence_done", {
        "sequence_id": seq_id, "status": status, **final,
      })
    except Exception as e:
      logger.error("[seq] 序列 %s 调度崩溃: %s", seq_id, e, exc_info=True)
      try:
        async with get_db_context() as db:
          await TestingRepo(db).update_generation_sequence(
            seq_id, status="interrupted", error_message=str(e)[:480], running_count=0)
        await sequence_hub.publish(seq_id, "sequence_done", {
          "sequence_id": seq_id, "status": "interrupted", "message": str(e)[:200],
        })
      except Exception:
        pass
    finally:
      self._running.pop(seq_id, None)

  async def _run_subtask(self, seq_id: str, sub: dict, slot: int, max_parallel: int) -> str:
    """执行单个子任务（复用 4 步流水线），广播阶段进度"""
    task_id = sub["id"]
    seq_index = sub["seq_index"]

    async def sub_event(status: str, stage: str | None = None, **extra: Any) -> None:
      await sequence_hub.publish(seq_id, "sequence_subtask", {
        "task_id": task_id, "seq_index": seq_index, "status": status,
        "stage": stage, "slot": slot, "max_parallel": max_parallel, **extra,
      })

    await sub_event("running", sub.get("seq_stage"))
    try:
      input_state = await _load_task(task_id)
      if input_state is None:
        async with get_db_context() as db:
          await TestingRepo(db).update_generation_task(
            task_id, status="failed", error_message="子任务加载失败")
        await sub_event("failed")
        return "failed"

      done_data: dict | None = None
      async for event_type, data in _run_pipeline_events(task_id, input_state):
        if event_type == "_done":
          done_data = data
        elif event_type == "testing_stage":
          stage = data.get("stage", "")
          async with get_db_context() as db:
            await TestingRepo(db).update_task_stage(task_id, stage)
          await sub_event("running", stage)

      if done_data:
        events = await _persist_and_finish(task_id, done_data)
        del events  # 序列模式下 SSE 事件由 hub 另行广播，此处仅持久化

      async with get_db_context() as db:
        repo = TestingRepo(db)
        task = await repo.get_generation_task(task_id)
        status = (task or {}).get("status", "failed")
        count = (task or {}).get("generated_count", 0) or 0
      async with get_db_context() as db:
        await TestingRepo(db).update_task_stage(task_id, None)
      await sub_event(status, None, generated_count=count)
      await self._publish_counts(seq_id)
      return status if status in ("completed", "cancelled") else "failed"
    except Exception as e:
      logger.error("[seq] 子任务 %s 执行异常: %s", task_id, e, exc_info=True)
      try:
        async with get_db_context() as db:
          await TestingRepo(db).update_generation_task(
            task_id, status="failed", error_message=str(e)[:480])
      except Exception:
        pass
      await sub_event("failed", None, message=str(e)[:160])
      await self._publish_counts(seq_id)
      return "failed"


sequence_scheduler = SequenceScheduler()


# ─── 序列创建辅助（供 service 调用） ─────────────────────────


def decide_strategy(model_field: str) -> tuple[str, int]:
  """按模型 tier 决定调度策略 → (strategy, max_parallel)"""
  provider, model_name = _parse_model_field(model_field)
  tier = get_model_tier(provider, model_name)
  if tier == "free":
    return "sequential", 1
  max_paid = max(1, get_settings().sequence_max_parallel_paid)
  return "parallel", max_paid


# ─── 定时任务 Cron 循环 ──────────────────────────────────────


async def scheduled_task_cron_loop(stop_event: asyncio.Event) -> None:
  """轻量 cron 调度循环：每 30s 扫描到期任务并真实执行。

  使用 croniter 计算 next_run_at；单进程内即可覆盖单机部署场景。
  """
  try:
    from croniter import croniter
  except ImportError:
    logger.warning("[cron] 未安装 croniter，定时任务自动调度已禁用（手动执行仍可用）")
    return

  while not stop_event.is_set():
    try:
      await _run_due_scheduled_tasks(croniter)
    except Exception as e:
      logger.warning("[cron] 调度扫描失败: %s", e)
    try:
      await asyncio.wait_for(stop_event.wait(), timeout=30)
    except asyncio.TimeoutError:
      pass


async def _run_due_scheduled_tasks(croniter_cls: Any) -> None:
  now = datetime.now()
  due: list[dict] = []
  async with get_db_context() as db:
    repo = TestingRepo(db)
    tasks = await repo.list_scheduled_tasks()
    for t in tasks:
      if not t.get("enabled"):
        continue
      try:
        cron = croniter_cls(t.get("cron_expr") or "0 8 * * *", now)
      except (ValueError, KeyError):
        continue
      next_run = t.get("next_run_at")
      if not next_run:
        # 首次登记：只写 next_run_at，不立即执行
        await repo.update_scheduled_task(
          t["id"], next_run_at=cron.get_next(datetime).isoformat(sep=" "))
        continue
      if isinstance(next_run, datetime):
        due_dt = next_run
      else:
        due_dt = datetime.fromisoformat(str(next_run))
      if due_dt <= now:
        due.append(t)
        await repo.update_scheduled_task(
          t["id"], last_run_at=now.isoformat(sep=" "),
          next_run_at=cron.get_next(datetime).isoformat(sep=" "))

  for t in due:
    logger.info("[cron] 定时任务 %s(%s) 到期，自动执行", t["id"], t.get("name"))
    try:
      async with get_db_context() as db:
        svc = TestingService(db)
        await svc.execute_scheduled_task(t["id"], operator="cron")
    except Exception as e:
      logger.warning("[cron] 定时任务 %s 执行失败: %s", t["id"], e)

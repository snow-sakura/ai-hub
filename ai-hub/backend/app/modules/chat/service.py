"""聊天 Service - 核心编排逻辑"""

import uuid
import json
from pathlib import Path
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage, AIMessage

from app.modules.chat.graph import get_agent_graph
from app.modules.comfort.graph import get_comfort_graph
from app.shared.core.database import get_db
from app.shared.service.conversation_service import ConversationService
from app.config import get_settings
from app.shared.utils.file_parser import parse_file
from app.shared.utils.sse_helper import (
  format_sse_event,
  format_token_event,
  format_tool_start_event,
  format_tool_result_event,
  format_thinking_event,
  format_reasoning_token_event,
  format_progress_event,
  format_done_event,
  format_error_event,
  format_emotion_event,
  format_forgiveness_event,
)


class ChatService:
  """聊天编排服务"""

  async def stream_chat(
    self,
    message: str,
    conversation_id: str,
    model_provider: str = "deepseek",
    model_name: str = "",
    knowledge_doc_ids: list[str] | None = None,
    attachments: list[str] | None = None,
    comfort_mode: bool = False,
    reasoning_effort: str = "high",
    web_search_enabled: bool = False,
    deep_thinking_enabled: bool = True,
  ) -> AsyncGenerator[str, None]:
    """流式处理聊天消息，返回 SSE 事件流"""
    try:
      db = await get_db()
      conv_service = ConversationService(db)

      try:
        await conv_service.get(conversation_id)
      except Exception:
        conv = await conv_service.create("新会话")
        conversation_id = conv["id"]

      await conv_service.save_message(conversation_id, "user", message)

      # 选择图：哄哄模拟器 or 普通 Agent
      if comfort_mode:
        graph = await get_comfort_graph()
        # 加载哄哄会话元数据
        comfort_meta = await self._load_comfort_metadata(db, conversation_id)
      else:
        graph = await get_agent_graph()
        comfort_meta = None
      config = {
        "configurable": {"thread_id": conversation_id},
        "recursion_limit": 100,
      }

      # 处理附件：解析文件内容
      attachment_contents = []
      if attachments:
        for file_id in attachments:
          content = await self._load_attachment(file_id)
          if content:
            attachment_contents.append(content)
            yield format_thinking_event("observation", f"已加载附件: {content['filename']}")

      input_state = {
        "messages": [HumanMessage(content=message)],
        "model_provider": model_provider,
        "model_name": model_name,
        "rag_context": None,
        "knowledge_doc_ids": knowledge_doc_ids,
        "attachment_contents": attachment_contents or None,
        "thinking_steps": [],
        "progress": None,
        "current_tool_calls": [],
        "reasoning_effort": reasoning_effort,
        "web_search_enabled": web_search_enabled,
        "deep_thinking_enabled": deep_thinking_enabled,
        "emotion_result": None,
        "forgiveness_result": None,
        "comfort_metadata": comfort_meta,
      }

      full_response = ""
      message_id = str(uuid.uuid4())

      # comfort 模式仅捕获 comfort_agent 节点的 token，避免情绪分析 LLM 输出泄露
      agent_node_name = "comfort_agent" if comfort_mode else "agent"

      # 先思考后输出：思考期间缓存 token，思考结束（reasoning_end）后一次性释放
      thinking_active = deep_thinking_enabled and not comfort_mode
      token_buffer: list[str] = []

      async for event in graph.astream_events(input_state, config=config, version="v2"):
        kind = event.get("event", "")

        # 1. 处理 LLM 流式 token（仅来自 agent 节点）
        if kind == "on_chat_model_stream":
          node_name = event.get("metadata", {}).get("langgraph_node", "")
          if node_name != agent_node_name:
            continue
          chunk = event.get("data", {}).get("chunk")
          if chunk and hasattr(chunk, "content") and chunk.content:
            token = chunk.content
            full_response += token
            if thinking_active:
              token_buffer.append(token)
            else:
              yield format_token_event(token)

        # 2. 处理 dispatch_custom_event 写入的自定义事件
        elif kind == "on_custom_event":
          event_type = event.get("name", "")
          inner = event.get("data", {})
          if isinstance(inner, dict):

            if event_type == "tool_start":
              yield format_tool_start_event(
                inner.get("tool_name", ""),
                inner.get("tool_call_id", ""),
                inner.get("display", "执行中..."),
                inner.get("input"),
              )
            elif event_type == "tool_result":
              yield format_tool_result_event(
                inner.get("tool_name", ""),
                inner.get("tool_call_id", ""),
                inner.get("summary", ""),
                inner.get("result"),
              )
            elif event_type == "thinking":
              yield format_thinking_event(
                inner.get("step", "thought"),
                inner.get("content", ""),
              )
            elif event_type == "progress":
              yield format_progress_event(
                inner.get("current", 0),
                inner.get("total", 1),
                inner.get("message", ""),
              )
            elif event_type == "reasoning_token":
              thinking_active = True
              yield format_reasoning_token_event(
                inner.get("content", ""),
              )
            elif event_type == "reasoning_end" and thinking_active:
              # 思考结束：刷新之前缓存的 content token
              thinking_active = False
              for t in token_buffer:
                yield format_token_event(t)
              token_buffer = []
              yield format_sse_event("reasoning_end", {})

      if full_response:
        await conv_service.save_message(
          conversation_id, "assistant", full_response,
          metadata={"message_id": message_id},
        )

      # 哄哄模式：发送情绪和原谅值事件，并更新元数据
      if comfort_mode:
        async for event_str in self._handle_comfort_post(
          db, conversation_id, input_state, graph, config
        ):
          yield event_str

      yield format_done_event(message_id)

    except Exception as e:
      import traceback
      error_detail = traceback.format_exc()
      yield format_error_event("CHAT_ERROR", f"{str(e)}\n{error_detail[-500:]}")
    finally:
      # 【修复】确保数据库连接总是被关闭
      if db is not None:
        try:
          await db.close()
        except Exception:
          pass  # 忽略关闭时的错误

  async def _load_attachment(self, file_id: str) -> dict | None:
    """加载并解析附件文件内容"""
    settings = get_settings()
    attach_dir = Path(settings.upload_dir) / "chat_attachments"
    if not attach_dir.exists():
      return None

    # 匹配 file_id_* 的文件
    for f in attach_dir.iterdir():
      if f.name.startswith(file_id + "_"):
        content_bytes = f.read_bytes()
        filename = f.name[len(file_id) + 1:]
        file_type = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"
        text = parse_file(content_bytes, file_type)
        return {
          "file_id": file_id,
          "filename": filename,
          "content": text,
        }
    return None

  async def _load_comfort_metadata(
    self, db, conv_id: str
  ) -> dict:
    """加载哄哄会话的完整元数据（场景/角色/原谅值/记忆）"""
    from app.modules.comfort.repository import ComfortRepo
    repo = ComfortRepo(db)
    meta = await repo.get_conversation_metadata(conv_id)
    if not meta or "scene_id" not in meta:
      return {}
    scene = await repo.get_scene(meta.get("scene_id", ""))
    character = await repo.get_character(meta.get("character_id", ""))
    memories = await repo.list_memories(conv_id)
    meta["scene"] = scene or {}
    meta["character"] = character or {}
    meta["memories"] = memories[:5]
    return meta

  async def _handle_comfort_post(
    self, db, conv_id: str, input_state: dict, graph, config: dict,
  ) -> AsyncGenerator[str, None]:
    """处理哄哄模式后置逻辑：发送情绪/原谅值事件，更新元数据"""
    from app.modules.comfort.repository import ComfortRepo
    from datetime import date
    try:
      repo = ComfortRepo(db)
      final_state = await graph.aget_state(config)
      values = final_state.values if final_state else {}
      emotion_data = values.get("emotion_result")
      forgiveness_data = values.get("forgiveness_result")
      if emotion_data:
        yield format_emotion_event(
          label=emotion_data.get("label", "calm"),
          intensity=emotion_data.get("intensity", 0.5),
          emoji=emotion_data.get("emoji", "😐"),
        )
      if forgiveness_data:
        yield format_forgiveness_event(
          current=forgiveness_data.get("current", 50.0),
          delta=forgiveness_data.get("delta", 0.0),
          reason=forgiveness_data.get("reason", ""),
          trend=forgiveness_data.get("trend", "stable"),
        )
      meta = await repo.get_conversation_metadata(conv_id)
      if meta and "scene_id" in meta:
        if forgiveness_data:
          meta["forgiveness"] = forgiveness_data.get("current", meta.get("forgiveness", 50.0))
        meta["turn_count"] = meta.get("turn_count", 0) + 1
        if emotion_data:
          emotion_log = meta.get("emotion_log", [])
          emotion_log.append({
            "label": emotion_data.get("label"),
            "intensity": emotion_data.get("intensity"),
            "turn": meta["turn_count"],
          })
          meta["emotion_log"] = emotion_log[-50:]
        await repo.update_conversation_metadata(conv_id, meta)
        if emotion_data:
          today = date.today().isoformat()
          await repo.upsert_emotion_stat(
            user_date=today,
            emotion_label=emotion_data.get("label", "calm"),
            intensity=emotion_data.get("intensity", 0.5),
            comfort_score=forgiveness_data.get("current") if forgiveness_data else None,
          )
    except Exception as e:
      yield format_thinking_event(
        "observation", f"哄哄后处理警告: {str(e)[:100]}"
      )

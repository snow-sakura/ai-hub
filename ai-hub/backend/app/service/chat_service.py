"""聊天 Service - 核心编排逻辑"""

import uuid
import json
from pathlib import Path
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage, AIMessage

from app.agent.graph import get_agent_graph
from app.core.database import get_db
from app.service.conversation_service import ConversationService
from app.config import get_settings
from app.utils.file_parser import parse_file
from app.utils.sse_helper import (
  format_token_event,
  format_tool_start_event,
  format_tool_result_event,
  format_thinking_event,
  format_progress_event,
  format_done_event,
  format_error_event,
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

      graph = await get_agent_graph()
      config = {"configurable": {"thread_id": conversation_id}}

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
      }

      full_response = ""
      message_id = str(uuid.uuid4())

      async for event in graph.astream_events(input_state, config=config, version="v2"):
        kind = event.get("event", "")

        # 1. 处理 LLM 流式 token
        if kind == "on_chat_model_stream":
          chunk = event.get("data", {}).get("chunk")
          if chunk and hasattr(chunk, "content") and chunk.content:
            token = chunk.content
            full_response += token
            yield format_token_event(token)

        # 2. 处理 StreamWriter 写入的自定义事件
        elif kind == "on_custom_event":
          custom_data = event.get("data", {})
          if isinstance(custom_data, dict):
            inner = custom_data.get("input", custom_data)
            if isinstance(inner, dict):
              event_type = inner.get("type", "")

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

        # 3. 处理 chain stream 中的 tool_calls
        elif kind == "on_chain_stream":
          data = event.get("data", {})
          if isinstance(data, dict):
            output = data.get("output")
            if isinstance(output, dict) and "messages" in output:
              for msg in output.get("messages", []):
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                  for tc in msg.tool_calls:
                    yield format_thinking_event(
                      "action",
                      f"计划调用: {tc['name']}",
                    )

      if full_response:
        await conv_service.save_message(
          conversation_id, "assistant", full_response,
          metadata={"message_id": message_id},
        )

      yield format_done_event(message_id)

    except Exception as e:
      import traceback
      error_detail = traceback.format_exc()
      yield format_error_event("CHAT_ERROR", f"{str(e)}\n{error_detail[-500:]}")
    finally:
      if "db" in locals():
        await db.close()

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

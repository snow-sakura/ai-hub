"""SSE 格式化辅助函数"""

import json
from typing import Any


def format_sse_event(event_type: str, data: dict[str, Any]) -> str:
  """格式化 SSE 事件字符串"""
  data_json = json.dumps(data, ensure_ascii=False)
  return f"event: {event_type}\ndata: {data_json}\n\n"


def format_token_event(content: str) -> str:
  """格式化 token 事件"""
  return format_sse_event("token", {"content": content})


def format_tool_start_event(tool_name: str, tool_call_id: str,
                             display: str, input_data: dict | None = None) -> str:
  """格式化工具调用开始事件"""
  return format_sse_event("tool_start", {
    "tool_name": tool_name,
    "tool_call_id": tool_call_id,
    "display": display,
    "input": input_data,
  })


def format_tool_result_event(tool_name: str, tool_call_id: str,
                              summary: str, result: dict | None = None) -> str:
  """格式化工具调用结果事件"""
  return format_sse_event("tool_result", {
    "tool_name": tool_name,
    "tool_call_id": tool_call_id,
    "summary": summary,
    "result": result,
  })


def format_thinking_event(step: str, content: str) -> str:
  """格式化思考过程事件"""
  return format_sse_event("thinking", {"step": step, "content": content})


def format_progress_event(current: int, total: int, message: str) -> str:
  """格式化进度事件"""
  return format_sse_event("progress", {
    "current": current,
    "total": total,
    "message": message,
  })


def format_done_event(message_id: str) -> str:
  """格式化完成事件"""
  return format_sse_event("done", {"message_id": message_id})


def format_error_event(code: str, message: str) -> str:
  """格式化错误事件"""
  return format_sse_event("error", {"code": code, "message": message})

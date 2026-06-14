"""LangGraph Agent 共享工具函数"""

import json
import uuid


def merge_tool_call_chunks(chunks: list) -> list[dict]:
  """将 stream() 中跨 chunk 的 tool_call_chunks 聚合成完整的 tool_calls"""
  merged: dict[int, dict] = {}
  for chunk in chunks:
    idx = getattr(chunk, "index", 0) or 0
    if idx not in merged:
      merged[idx] = {"name": "", "args": "", "id": ""}
    if getattr(chunk, "name", None):
      merged[idx]["name"] = chunk.name
    if getattr(chunk, "args", None):
      merged[idx]["args"] += chunk.args
    if getattr(chunk, "id", None):
      merged[idx]["id"] = chunk.id

  tool_calls = []
  for idx in sorted(merged.keys()):
    tc = merged[idx]
    try:
      args = json.loads(tc["args"]) if tc["args"] else {}
    except json.JSONDecodeError:
      args = {}
    tool_calls.append({
      "name": tc["name"],
      "args": args,
      "id": tc["id"] or f"call_{uuid.uuid4().hex[:12]}",
      "type": "tool_call",
    })
  return tool_calls

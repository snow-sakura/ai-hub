"""工具执行节点"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.messages import ToolMessage
from langchain_core.callbacks.manager import dispatch_custom_event

from app.common.agent.state import AgentState
from app.common.tools import TOOL_REGISTRY


DISPLAY_NAMES = {
  "web_search": "正在联网搜索",
  "file_read": "正在读取文件",
  "file_write": "正在写入文件",
  "web_scraper": "正在抓取网页",
  "download_resource": "正在下载资源",
  "terminal_exec": "正在执行命令",
  "pdf_generate": "正在生成 PDF",
  "image_search": "正在搜索图片",
}


def tool_node(state: AgentState) -> dict:
  """执行工具调用并返回结果（并行执行，带进度追踪）"""
  messages = state["messages"]
  last_message = messages[-1]
  tool_calls = last_message.tool_calls
  total_tools = len(tool_calls)
  results: list[ToolMessage] = []

  # Phase 1: 同步发送所有 tool_start / thinking 事件（建立前端卡片）
  for idx, tc in enumerate(tool_calls):
    display = DISPLAY_NAMES.get(tc["name"], f"正在执行 {tc['name']}")
    dispatch_custom_event("progress", {
      "current": idx, "total": total_tools,
      "message": f"{display}...",
    })
    dispatch_custom_event("tool_start", {
      "tool_name": tc["name"],
      "tool_call_id": tc["id"],
      "display": f"{display}...",
      "input": tc["args"],
    })
    dispatch_custom_event("thinking", {
      "step": "action",
      "content": f"步骤 {idx + 1}/{total_tools}: 执行 {tc['name']}",
    })

  # Phase 2: 并行执行所有工具
  def _run_one(tc: dict) -> tuple:
    name = tc["name"]
    tool_call_id = tc["id"]
    args = tc["args"]
    try:
      tool_func = TOOL_REGISTRY.get(name)
      result = tool_func.invoke(args) if tool_func else f"未知工具: {name}"
      return (tool_call_id, name, result, None)
    except Exception as e:
      return (tool_call_id, name, None, str(e))

  done_count = 0
  with ThreadPoolExecutor(max_workers=min(total_tools, 4)) as pool:
    futures = [pool.submit(_run_one, tc) for tc in tool_calls]
    for future in as_completed(futures):
      done_count += 1
      tool_call_id, name, result, error = future.result()

      if error:
        summary = error[:200]
        dispatch_custom_event("tool_result", {
          "tool_name": name,
          "tool_call_id": tool_call_id,
          "summary": summary,
          "result": {"error": error},
        })
        results.append(ToolMessage(content=error, tool_call_id=tool_call_id))
      else:
        summary = result[:200] if len(result) > 200 else result
        dispatch_custom_event("tool_result", {
          "tool_name": name,
          "tool_call_id": tool_call_id,
          "summary": summary,
          "result": {"output": result[:1000]},
        })
        dispatch_custom_event("thinking", {
          "step": "observation",
          "content": f"{name} 结果: {summary}",
        })
        results.append(ToolMessage(content=result, tool_call_id=tool_call_id))

      dispatch_custom_event("progress", {
        "current": done_count, "total": total_tools,
        "message": f"已完成 {done_count}/{total_tools} 个步骤",
      })

  return {"messages": results}

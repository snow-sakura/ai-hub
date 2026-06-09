"""工具执行节点"""

import json
from langchain_core.messages import ToolMessage
from langgraph.types import StreamWriter

from app.agent.state import AgentState
from app.agent.tools import TOOL_REGISTRY


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


def tool_node(state: AgentState, writer: StreamWriter) -> dict:
  """执行工具调用并返回结果，带进度追踪"""
  messages = state["messages"]
  last_message = messages[-1]
  results = []
  total_tools = len(last_message.tool_calls)

  for idx, tool_call in enumerate(last_message.tool_calls):
    tool_name = tool_call["name"]
    tool_call_id = tool_call["id"]
    tool_args = tool_call["args"]
    display = DISPLAY_NAMES.get(tool_name, f"正在执行 {tool_name}")

    # 发送进度事件
    writer({
      "type": "progress",
      "current": idx,
      "total": total_tools,
      "message": f"{display}...",
    })

    writer({
      "type": "tool_start",
      "tool_name": tool_name,
      "tool_call_id": tool_call_id,
      "display": f"{display}...",
      "input": tool_args,
    })

    writer({
      "type": "thinking",
      "step": "action",
      "content": f"步骤 {idx + 1}/{total_tools}: 执行 {tool_name}",
    })

    try:
      tool_func = TOOL_REGISTRY.get(tool_name)
      if tool_func:
        result = tool_func.invoke(tool_args)
      else:
        result = f"未知工具: {tool_name}"

      summary = result[:200] if len(result) > 200 else result

      writer({
        "type": "tool_result",
        "tool_name": tool_name,
        "tool_call_id": tool_call_id,
        "summary": summary,
        "result": {"output": result[:1000]},
      })

      writer({
        "type": "thinking",
        "step": "observation",
        "content": f"{tool_name} 结果: {summary}",
      })

      results.append(ToolMessage(content=result, tool_call_id=tool_call_id))
    except Exception as e:
      error_msg = f"工具执行错误: {str(e)}"
      writer({
        "type": "tool_result",
        "tool_name": tool_name,
        "tool_call_id": tool_call_id,
        "summary": error_msg,
        "result": {"error": str(e)},
      })
      results.append(ToolMessage(content=error_msg, tool_call_id=tool_call_id))

  # 所有工具执行完成
  writer({
    "type": "progress",
    "current": total_tools,
    "total": total_tools,
    "message": "所有步骤执行完成",
  })

  return {"messages": results}

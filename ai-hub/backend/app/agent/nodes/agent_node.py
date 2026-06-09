"""LLM 推理节点 - Agent 决策核心"""

import json
from langchain_core.messages import SystemMessage
from langgraph.types import StreamWriter

from app.agent.state import AgentState
from app.agent.prompts import SYSTEM_PROMPT, RAG_CONTEXT_TEMPLATE
from app.core.llm_factory import LLMFactory
from app.agent.tools import get_all_tools


def agent_node(state: AgentState, writer: StreamWriter) -> dict:
  """LLM 推理节点：根据当前状态决定下一步行动，
  流式捕获 LLM 推理文本作为思考过程"""
  provider = state.get("model_provider", "deepseek")
  model_name = state.get("model_name", "")
  llm = LLMFactory.create(provider, model_name)
  tools = get_all_tools()
  llm_with_tools = llm.bind_tools(tools)

  rag_context = state.get("rag_context")
  rag_text = ""
  if rag_context:
    rag_text = RAG_CONTEXT_TEMPLATE.format(context=rag_context)

  # 注入附件内容
  attachment_text = ""
  attachment_contents = state.get("attachment_contents")
  if attachment_contents:
    parts = []
    for att in attachment_contents:
      parts.append(f"## 附件: {att['filename']}\n{att['content']}")
    attachment_text = "\n\n---\n\n".join(parts)

  system_msg = SystemMessage(content=SYSTEM_PROMPT.format(
    rag_context=rag_text,
    attachment_context=attachment_text,
  ))
  messages = [system_msg] + state["messages"]

  # 流式获取 LLM 推理文本（捕获真实思考过程）
  reasoning_buffer = ""
  for chunk in llm_with_tools.stream(messages):
    if chunk.content:
      token_text = chunk.content
      reasoning_buffer += token_text
    # 检查 tool_calls（有些模型在最后一个 chunk 才给出 tool_calls）
    if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
      pass  # tool_calls 会在最终 response 中完整返回

  # 如果 LLM 有输出文本（非工具调用），将其作为思考过程发送
  if reasoning_buffer.strip():
    # 截取前 500 字符作为思考摘要，避免过长
    thinking_summary = reasoning_buffer[:500]
    writer({
      "type": "thinking",
      "step": "thought",
      "content": thinking_summary,
    })

  # 使用 invoke 获取完整 response（含 tool_calls）
  response = llm_with_tools.invoke(messages)

  if response.tool_calls:
    # 发送进度信息：有多少个工具调用
    total_tools = len(response.tool_calls)
    writer({
      "type": "progress",
      "current": 0,
      "total": total_tools,
      "message": f"规划执行 {total_tools} 个步骤...",
    })

    for i, tc in enumerate(response.tool_calls):
      args_preview = json.dumps(tc.get("args", {}), ensure_ascii=False)
      if len(args_preview) > 100:
        args_preview = args_preview[:100] + "..."
      writer({
        "type": "thinking",
        "step": "action",
        "content": f"步骤 {i + 1}/{total_tools}: 调用 {tc['name']}({args_preview})",
      })

  return {"messages": [response]}

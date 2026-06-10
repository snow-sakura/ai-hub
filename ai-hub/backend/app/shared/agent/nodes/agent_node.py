"""LLM 推理节点 - Agent 决策核心"""

import json
import uuid
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.types import StreamWriter

from app.shared.agent.state import AgentState
from app.shared.agent.prompts import SYSTEM_PROMPT, RAG_CONTEXT_TEMPLATE, KNOWLEDGE_SECTION, KNOWLEDGE_RULE
from app.shared.core.llm_factory import LLMFactory
from app.shared.agent.tools import get_all_tools


def _merge_tool_call_chunks(chunks: list) -> list[dict]:
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


def agent_node(state: AgentState, writer: StreamWriter) -> dict:
  """LLM 推理节点：根据当前状态决定下一步行动，
  流式捕获 LLM 推理文本作为思考过程"""
  provider = state.get("model_provider", "deepseek")
  model_name = state.get("model_name", "")
  llm = LLMFactory.create(provider, model_name)
  tools = get_all_tools()
  llm_with_tools = llm.bind_tools(tools)

  rag_context = state.get("rag_context")
  knowledge_doc_ids = state.get("knowledge_doc_ids")
  has_knowledge = bool(knowledge_doc_ids and len(knowledge_doc_ids) > 0)

  # 知识库相关行：仅在用户选择了文档时才告诉 LLM 有知识库能力
  knowledge_section = KNOWLEDGE_SECTION if has_knowledge else ""
  knowledge_rule = KNOWLEDGE_RULE if has_knowledge else ""

  rag_text = ""
  if rag_context and has_knowledge:
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
    knowledge_section=knowledge_section,
    knowledge_rule=knowledge_rule,
    rag_context=rag_text,
    attachment_context=attachment_text,
  ))
  messages = [system_msg] + state["messages"]

  # 单次 stream() 获取所有输出，无需额外 invoke（消除双重调用卡顿）
  content_buffer = ""
  tool_call_chunks_acc = []
  for chunk in llm_with_tools.stream(messages):
    if chunk.content:
      content_buffer += chunk.content
    if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
      tool_call_chunks_acc.extend(chunk.tool_call_chunks)

  # 将前 500 字符作为思考摘要发送
  if content_buffer.strip():
    thinking_summary = content_buffer[:500]
    writer({
      "type": "thinking",
      "step": "thought",
      "content": thinking_summary,
    })

  # 从 tool_call_chunks 重构完整的 tool_calls
  final_tool_calls = _merge_tool_call_chunks(tool_call_chunks_acc)

  if final_tool_calls:
    total_tools = len(final_tool_calls)
    writer({
      "type": "progress",
      "current": 0,
      "total": total_tools,
      "message": f"规划执行 {total_tools} 个步骤...",
    })

    for i, tc in enumerate(final_tool_calls):
      args_preview = json.dumps(tc.get("args", {}), ensure_ascii=False)
      if len(args_preview) > 100:
        args_preview = args_preview[:100] + "..."
      writer({
        "type": "thinking",
        "step": "action",
        "content": f"步骤 {i + 1}/{total_tools}: 调用 {tc['name']}({args_preview})",
      })

  response = AIMessage(content=content_buffer, tool_calls=final_tool_calls)
  return {"messages": [response]}

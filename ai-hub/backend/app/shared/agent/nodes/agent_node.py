"""LLM 推理节点 - Agent 决策核心"""

import json
import uuid
from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.callbacks.manager import dispatch_custom_event

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


def agent_node(state: AgentState) -> dict:
  """LLM 推理节点：根据当前状态决定下一步行动，
  实时流式输出 reasoning_content 和 content token"""
  provider = state.get("model_provider", "deepseek")
  model_name = state.get("model_name", "")
  reasoning_effort = state.get("reasoning_effort", "high")
  web_search_enabled = state.get("web_search_enabled", False)
  deep_thinking_enabled = state.get("deep_thinking_enabled", True)

  llm = LLMFactory.create(provider, model_name, reasoning_effort)

  # 条件绑定工具：web_search_enabled=False 时移除 web_search
  tools = get_all_tools()
  if not web_search_enabled:
    tools = [t for t in tools if getattr(t, "name", "") != "web_search"]
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
  reasoning_content = ""  # DeepSeek thinking mode 推理内容
  for chunk in llm_with_tools.stream(messages):
    if chunk.content:
      content_buffer += chunk.content
    if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
      tool_call_chunks_acc.extend(chunk.tool_call_chunks)
    # 实时向前端推送 reasoning_content（DeepSeek 思考过程）
    if hasattr(chunk, "additional_kwargs") and chunk.additional_kwargs:
      rc = chunk.additional_kwargs.get("reasoning_content", "")
      if rc:
        reasoning_content += rc
        if deep_thinking_enabled:
          dispatch_custom_event("reasoning_token", {"content": rc})

  # 从 tool_call_chunks 重构完整的 tool_calls
  final_tool_calls = _merge_tool_call_chunks(tool_call_chunks_acc)

  # 标记思考阶段结束，让 service 层刷新缓存的 content token
  dispatch_custom_event("reasoning_end", {})

  if final_tool_calls:
    total_tools = len(final_tool_calls)
    dispatch_custom_event("progress", {
      "current": 0, "total": total_tools,
      "message": f"规划执行 {total_tools} 个步骤...",
    })

    for i, tc in enumerate(final_tool_calls):
      args_preview = json.dumps(tc.get("args", {}), ensure_ascii=False)
      if len(args_preview) > 100:
        args_preview = args_preview[:100] + "..."
      dispatch_custom_event("thinking", {
        "step": "action",
        "content": f"步骤 {i + 1}/{total_tools}: 调用 {tc['name']}({args_preview})",
      })

  additional_kwargs = {}
  if reasoning_content:
    additional_kwargs["reasoning_content"] = reasoning_content
  response = AIMessage(content=content_buffer, tool_calls=final_tool_calls, additional_kwargs=additional_kwargs)
  return {"messages": [response]}

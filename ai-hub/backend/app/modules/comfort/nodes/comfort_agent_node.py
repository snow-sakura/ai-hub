"""哄哄模拟器 Agent 节点 - 角色扮演的 LLM 推理"""

import json
import uuid
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.types import StreamWriter

from app.shared.agent.state import AgentState
from app.modules.comfort.prompts import COMFORT_SYSTEM_PROMPT, COMFORT_MEMORY_PROMPT, COMFORT_TIPS_PROMPT
from app.shared.core.llm_factory import LLMFactory
from app.shared.agent.tools.web_search import web_search
from app.shared.agent.tools.image_search import image_search


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


def comfort_agent_node(state: AgentState, writer: StreamWriter) -> dict:
  """哄哄模拟器 Agent：注入角色人设 prompt 进行角色扮演推理"""
  provider = state.get("model_provider", "deepseek")
  model_name = state.get("model_name", "")
  llm = LLMFactory.create(provider, model_name)

  # 受限工具集：仅 web_search 和 image_search
  tools = [web_search, image_search]
  llm_with_tools = llm.bind_tools(tools)

  # 从 comfort_metadata 获取角色和场景信息
  comfort_meta = state.get("comfort_metadata", {})
  character = comfort_meta.get("character", {})
  scene = comfort_meta.get("scene", {})

  character_name = character.get("name", "对方")
  character_age = character.get("age", "未知")
  character_identity = character.get("identity", "")
  personality_tags = ", ".join(character.get("personality_tags", []))
  speaking_style = character.get("speaking_style", "")
  backstory = character.get("backstory", "")
  scene_prompt = scene.get("initial_prompt", "")

  # RAG 上下文
  rag_context = state.get("rag_context")
  rag_text = ""
  if rag_context:
    rag_text = f"## 参考知识\n{rag_context}"

  # 记忆注入
  memories = comfort_meta.get("memories", [])
  memory_text = ""
  if memories:
    mem_parts = [f"- {m.get('content', '')}" for m in memories[:5]]
    memory_text = COMFORT_MEMORY_PROMPT.format(memories="\n".join(mem_parts))

  # 构建 System Prompt
  system_msg = SystemMessage(content=COMFORT_SYSTEM_PROMPT.format(
    character_name=character_name,
    character_age=character_age,
    character_identity=character_identity,
    personality_tags=personality_tags,
    speaking_style=speaking_style,
    backstory=backstory,
    scene_prompt=scene_prompt,
    rag_context=rag_text,
  ) + "\n" + memory_text + "\n" + COMFORT_TIPS_PROMPT)

  messages = [system_msg] + state["messages"]

  # comfort 模式下不发送 thinking 事件，避免原始推理内容泄露到前端

  # 单次 stream() 获取所有输出 + tool_call_chunks，无需额外 invoke
  content_buffer = ""
  tool_call_chunks_acc = []
  reasoning_content = ""  # DeepSeek thinking mode 推理内容
  for chunk in llm_with_tools.stream(messages):
    if chunk.content:
      content_buffer += chunk.content
    if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
      tool_call_chunks_acc.extend(chunk.tool_call_chunks)
    # 保留 DeepSeek reasoning_content，后续发回 API 时必需
    if hasattr(chunk, "additional_kwargs") and chunk.additional_kwargs:
      rc = chunk.additional_kwargs.get("reasoning_content", "")
      if rc:
        reasoning_content += rc

  final_tool_calls = _merge_tool_call_chunks(tool_call_chunks_acc)
  additional_kwargs = {}
  if reasoning_content:
    additional_kwargs["reasoning_content"] = reasoning_content
  response = AIMessage(content=content_buffer, tool_calls=final_tool_calls, additional_kwargs=additional_kwargs)
  return {"messages": [response]}

"""RAG 检索增强节点"""

from langchain_core.callbacks.manager import dispatch_custom_event

from app.shared.agent.state import AgentState
from app.shared.repository.knowledge_repo import KnowledgeRepo
from app.shared.core.embedding_factory import EmbeddingFactory


def rag_node(state: AgentState) -> dict:
  """RAG 检索节点：从知识库中检索相关内容注入上下文"""
  messages = state["messages"]
  if not messages:
    return {"rag_context": None}

  last_user_msg = None
  for msg in reversed(messages):
    if hasattr(msg, "type") and msg.type == "human":
      last_user_msg = msg.content
      break

  if not last_user_msg:
    return {"rag_context": None}

  try:
    embedding = EmbeddingFactory.get_instance()
    repo = KnowledgeRepo.get_instance(embedding)

    knowledge_doc_ids = state.get("knowledge_doc_ids")
    if knowledge_doc_ids and len(knowledge_doc_ids) > 0:
      # 按选中的文档 ID 过滤
      results = repo.query_with_filter(
        last_user_msg, n_results=5,
        filter_criteria={"doc_id": {"$in": knowledge_doc_ids}},
      )
      dispatch_custom_event("thinking", {
        "step": "observation",
        "content": f"从 {len(knowledge_doc_ids)} 个选中文档中检索知识库",
      })
    else:
      # 全库搜索（默认行为）
      results = repo.query(last_user_msg, n_results=5)

    if results and results["documents"] and results["documents"][0]:
      chunks = results["documents"][0]
      sources = results["metadatas"][0] if results.get("metadatas") else []

      context_parts = []
      for i, chunk in enumerate(chunks):
        source = sources[i].get("source_file", "未知来源") if i < len(sources) else "未知来源"
        context_parts.append(f"[来源: {source}]\n{chunk}")

      rag_context = "\n\n---\n\n".join(context_parts)
      dispatch_custom_event("thinking", {
        "step": "observation",
        "content": f"从知识库检索到 {len(chunks)} 个相关片段",
      })
      return {"rag_context": rag_context}
  except Exception as e:
    dispatch_custom_event("thinking", {
      "step": "observation",
      "content": f"知识库检索跳过: {str(e)[:100]}",
    })

  return {"rag_context": None}

"""知识库数据访问层 - ChromaDB"""

from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings


class KnowledgeRepo:
  """ChromaDB 知识库 Repository"""

  _instance: "KnowledgeRepo | None" = None
  _collection = None

  def __init__(self, embedding_fn=None):
    settings = get_settings()
    persist_dir = Path(settings.chroma_persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)

    self.client = chromadb.PersistentClient(
      path=str(persist_dir),
      settings=ChromaSettings(anonymized_telemetry=False),
    )

    self.collection = self.client.get_or_create_collection(
      name="knowledge_base",
      embedding_function=embedding_fn,
      metadata={"hnsw:space": "cosine"},
    )

  @classmethod
  def get_instance(cls, embedding_fn=None) -> "KnowledgeRepo":
    """获取单例"""
    if cls._instance is None:
      cls._instance = cls(embedding_fn)
    return cls._instance

  def upsert_documents(self, doc_id: str, chunks: list[str],
                       metadatas: list[dict], ids: list[str]) -> int:
    """存储文档切片到 ChromaDB"""
    self.collection.upsert(
      documents=chunks,
      metadatas=metadatas,
      ids=ids,
    )
    return len(chunks)

  def query(self, query_text: str, n_results: int = 5) -> dict:
    """查询相似文档"""
    return self.collection.query(
      query_texts=[query_text],
      n_results=n_results,
    )

  def query_with_filter(self, query_text: str, n_results: int = 5,
                         filter_criteria: dict | None = None) -> dict:
    """按条件过滤查询相似文档（用于知识库文档隔离）"""
    kwargs = {
      "query_texts": [query_text],
      "n_results": n_results,
    }
    if filter_criteria:
      kwargs["where"] = filter_criteria
    return self.collection.query(**kwargs)

  def delete_by_doc_id(self, doc_id: str) -> None:
    """根据文档 ID 删除所有相关 chunks"""
    self.collection.delete(where={"doc_id": doc_id})

  def get_all_doc_ids(self) -> list[str]:
    """获取所有唯一文档 ID"""
    result = self.collection.get(include=["metadatas"])
    doc_ids = set()
    if result and result["metadatas"]:
      for meta in result["metadatas"]:
        if meta and "doc_id" in meta:
          doc_ids.add(meta["doc_id"])
    return list(doc_ids)

  def clear_all(self) -> None:
    """清空所有数据"""
    self.client.delete_collection("knowledge_base")
    self.collection = self.client.get_or_create_collection(
      name="knowledge_base",
      metadata={"hnsw:space": "cosine"},
    )

"""Embedding 模型工厂 - 使用本地模型，无需 API Key"""

from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


class EmbeddingFactory:
  """Embedding 模型工厂"""

  _instance = None

  @classmethod
  def get_instance(cls):
    """获取 Embedding 单例（本地 all-MiniLM-L6-v2）"""
    if cls._instance is None:
      cls._instance = DefaultEmbeddingFunction()
    return cls._instance

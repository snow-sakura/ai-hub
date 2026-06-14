"""知识库 Service - RAG 全流程管理"""

import uuid
from typing import Any

from fastapi import UploadFile

from app.config import get_settings
from app.common.core.database import get_db
from app.common.core.embedding_factory import EmbeddingFactory
from app.common.repository.knowledge_repo import KnowledgeRepo
from app.common.domain.exceptions import KnowledgeDocNotFoundError
from app.common.utils.file_parser import parse_file
from app.common.utils.text_splitter import split_text

import logging
logger = logging.getLogger(__name__)


class KnowledgeService:
  """知识库业务逻辑"""

  async def upload_and_process(self, file: UploadFile) -> dict[str, Any]:
    """上传、解析、切分、向量化并存储文档"""
    settings = get_settings()
    upload_dir = settings.upload_dir

    content = await file.read()
    file_size = len(content)

    filename = file.filename or "unnamed"
    file_type = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"

    text = parse_file(content, file_type)
    chunks = split_text(text)

    doc_id = str(uuid.uuid4())
    embedding = EmbeddingFactory.get_instance()
    repo = KnowledgeRepo.get_instance(embedding)

    chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [
      {"doc_id": doc_id, "source_file": filename, "chunk_index": i}
      for i in range(len(chunks))
    ]

    repo.upsert_documents(doc_id, chunks, metadatas, chunk_ids)

    db = await get_db()
    try:
      await db.execute(
        "INSERT INTO knowledge_docs (id, filename, file_type, file_size, chunk_count) "
        "VALUES (?, ?, ?, ?, ?)",
        (doc_id, filename, file_type, file_size, len(chunks)),
      )
      await db.commit()
    finally:
      await db.close()

    return {
      "id": doc_id,
      "filename": filename,
      "file_type": file_type,
      "file_size": file_size,
      "chunk_count": len(chunks),
    }

  async def list_documents(self) -> list[dict[str, Any]]:
    """获取知识库文档列表"""
    db = await get_db()
    try:
      cursor = await db.execute(
        "SELECT id, filename, file_type, file_size, chunk_count, created_at "
        "FROM knowledge_docs ORDER BY created_at DESC"
      )
      rows = await cursor.fetchall()
      return [dict(row) for row in rows]
    finally:
      await db.close()

  async def delete_document(self, doc_id: str) -> None:
    """删除知识库文档"""
    db = await get_db()
    try:
      cursor = await db.execute(
        "DELETE FROM knowledge_docs WHERE id = ?", (doc_id,)
      )
      await db.commit()
      if cursor.rowcount == 0:
        raise KnowledgeDocNotFoundError(doc_id)
    finally:
      await db.close()

    try:
      repo = KnowledgeRepo.get_instance()
      repo.delete_by_doc_id(doc_id)
    except Exception as e:
      logger.error("ChromaDB 删除文档失败: doc_id=%s, 错误=%s", doc_id, e, exc_info=True)

  async def rebuild_index(self) -> dict[str, str]:
    """重建知识库索引"""
    repo = KnowledgeRepo.get_instance()
    repo.clear_all()
    return {"status": "success", "message": "知识库索引已重建"}

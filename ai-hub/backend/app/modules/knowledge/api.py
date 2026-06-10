"""知识库 API 端点"""

from typing import Any

from fastapi import APIRouter, UploadFile, File

from app.shared.api.schemas.common import ApiResponse
from app.shared.api.schemas.knowledge import KnowledgeUploadResponse, KnowledgeItemResponse
from app.shared.service.knowledge_service import KnowledgeService

router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> ApiResponse[KnowledgeUploadResponse]:
  """上传文档到知识库"""
  service = KnowledgeService()
  result = await service.upload_and_process(file)
  return ApiResponse(data=KnowledgeUploadResponse(**result))


@router.get("")
async def list_documents() -> ApiResponse[list[dict[str, Any]]]:
  """获取知识库文档列表"""
  service = KnowledgeService()
  data = await service.list_documents()
  return ApiResponse(data=data)


@router.delete("/{doc_id}")
async def delete_document(doc_id: str) -> ApiResponse[bool]:
  """删除知识库文档"""
  service = KnowledgeService()
  await service.delete_document(doc_id)
  return ApiResponse(data=True)


@router.post("/rebuild")
async def rebuild_knowledge() -> ApiResponse[dict[str, str]]:
  """重建知识库索引"""
  service = KnowledgeService()
  result = await service.rebuild_index()
  return ApiResponse(data=result)

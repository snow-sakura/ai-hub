"""知识库 API 端点"""

from io import BytesIO
from typing import Any
from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.common.api.schemas.common import ApiResponse
from app.common.api.schemas.knowledge import KnowledgeUploadResponse, KnowledgeItemResponse
from app.common.service.knowledge_service import KnowledgeService
from app.common.logs import get_logger
from app.common.utils.file_validator import (
  validate_file_magic,
  has_path_traversal,
  safe_filename,
)

logger = get_logger("knowledge.api")

router = APIRouter()

# ===== 知识库文件上传安全配置 =====
KNOWLEDGE_MAX_FILE_SIZE = 50 * 1024 * 1024  # 最大文件大小：50MB
KNOWLEDGE_ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'md'}
KNOWLEDGE_ALLOWED_MIME_TYPES = {
  'application/pdf',
  'text/plain',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/markdown',
}


@router.post("/upload")
async def upload_document(request: Request, file: UploadFile = File(...)) -> ApiResponse[KnowledgeUploadResponse]:
  """上传文档到知识库

  安全校验：
  - 文件大小限制（最大 50MB）
  - MIME 类型白名单
  - 文件扩展名白名单
  - 文件名安全检查
  """
  # 1. 检查文件名
  raw_name = safe_filename(file.filename) if file.filename else ""
  if not raw_name:
    raise HTTPException(status_code=400, detail="文件名不能为空")
  if has_path_traversal(raw_name):
    raise HTTPException(status_code=400, detail="非法的文件名")

  # 2. 检查文件扩展名
  ext = raw_name.rsplit(".", 1)[-1].lower() if "." in raw_name else ""
  if ext not in KNOWLEDGE_ALLOWED_EXTENSIONS:
    raise HTTPException(
      status_code=400,
      detail=f"不支持的文件类型: {ext}。允许的格式: {', '.join(sorted(KNOWLEDGE_ALLOWED_EXTENSIONS))}"
    )

  # 3. Content-Length 预检
  content_length = file.size
  if content_length is not None and content_length > KNOWLEDGE_MAX_FILE_SIZE:
    raise HTTPException(
      status_code=413,
      detail=f"文件过大（{content_length / 1024 / 1024:.1f}MB）。最大允许 {KNOWLEDGE_MAX_FILE_SIZE / 1024 / 1024}MB"
    )

  # 4. 读取文件内容并检查大小
  content = await file.read()
  if len(content) > KNOWLEDGE_MAX_FILE_SIZE:
    raise HTTPException(
      status_code=413,
      detail=f"文件过大（{len(content) / 1024 / 1024:.1f}MB）。最大允许 {KNOWLEDGE_MAX_FILE_SIZE / 1024 / 1024}MB"
    )

  # 4. 文件魔数验证
  if not validate_file_magic(content, ext):
    raise HTTPException(
      status_code=400,
      detail="文件内容与扩展名不符，请检查文件格式"
    )

  # 6. 检查 MIME 类型（严格校验）
  mime_type = file.content_type or "application/octet-stream"
  if mime_type not in KNOWLEDGE_ALLOWED_MIME_TYPES:
    raise HTTPException(
      status_code=400,
      detail=f"不支持的 MIME 类型: {mime_type}"
    )

  # 7. 处理文件
  new_file = StarletteUploadFile(
    filename=raw_name,
    file=BytesIO(content),
    headers={"content-type": file.content_type} if file.content_type else {},
  )

  service = KnowledgeService()
  result = await service.upload_and_process(new_file)
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

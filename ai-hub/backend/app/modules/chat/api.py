"""聊天 API 端点"""

import uuid
import os
import stat
from pathlib import Path
from fastapi import APIRouter, Request, UploadFile, File, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse

from app.modules.chat.schemas import ChatRequest
from app.common.api.schemas.common import ApiResponse
from app.modules.chat.service import ChatService
from app.config import get_settings
from app.common.logs import get_logger
from app.common.utils.file_validator import (
  validate_file_magic,
  has_path_traversal,
  safe_filename,
  sanitize_filename_component,
)

logger = get_logger("chat.api")

router = APIRouter()
chat_service = ChatService()

# ===== 文件上传安全配置 =====
MAX_FILE_SIZE = 10 * 1024 * 1024  # 最大文件大小：10MB
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'}
ALLOWED_DOCUMENT_TYPES = {
  'application/pdf',
  'text/plain',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}
ALLOWED_EXTENSIONS = {
  # 图片
  'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg',
  # 文档
  'pdf', 'txt', 'doc', 'docx',
}


@router.post("/send")
async def send_chat(
    request: Request,
    body: ChatRequest):
  """发送消息并流式返回 AI 响应（SSE）"""
  return StreamingResponse(
    chat_service.stream_chat(
      message=body.message,
      conversation_id=body.conversation_id,
      model_provider=body.model_provider,
      model_name=body.model_name,
      knowledge_doc_ids=body.knowledge_doc_ids,
      attachments=body.attachments,
      comfort_mode=body.comfort_mode,
      reasoning_effort=body.reasoning_effort,
      web_search_enabled=body.web_search_enabled,
      deep_thinking_enabled=body.deep_thinking_enabled,
    ),
    media_type="text/event-stream",
    headers={
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "X-Accel-Buffering": "no",
    },
  )


@router.post("/upload")
async def upload_chat_attachment(
    request: Request,
    file: UploadFile = File(...)) -> ApiResponse[dict]:
  """上传聊天附件，返回 file_id 供后续发送消息时引用

  安全校验：
  - 文件大小限制（最大 10MB）
  - MIME 类型白名单
  - 文件扩展名白名单
  - 文件名安全检查（防止路径遍历）
  """
  # 1. 检查文件名
  if not file.filename:
    raise HTTPException(status_code=400, detail="文件名不能为空")

  # 2. 安全检查文件名
  raw_name = safe_filename(file.filename) if file.filename else ""
  if not raw_name:
    raise HTTPException(status_code=400, detail="文件名不能为空")
  if has_path_traversal(raw_name):
    raise HTTPException(status_code=400, detail="非法的文件名")

  # 3. 检查文件扩展名
  ext = raw_name.rsplit(".", 1)[-1].lower() if "." in raw_name else ""
  if ext not in ALLOWED_EXTENSIONS:
    raise HTTPException(
      status_code=400,
      detail=f"不支持的文件类型: {ext}。允许的格式: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
    )

  # 4. Content-Length 预检（快速拒绝超大文件）
  content_length = file.size
  if content_length is not None and content_length > MAX_FILE_SIZE:
    raise HTTPException(
      status_code=413,
      detail=f"文件过大（{content_length / 1024 / 1024:.1f}MB）。最大允许 {MAX_FILE_SIZE / 1024 / 1024}MB"
    )

  # 5. 读取文件内容并检查大小
  content = await file.read()
  if len(content) > MAX_FILE_SIZE:
    raise HTTPException(
      status_code=413,
      detail=f"文件过大（{len(content) / 1024 / 1024:.1f}MB）。最大允许 {MAX_FILE_SIZE / 1024 / 1024}MB"
    )

  # 6. 文件魔数验证
  if not validate_file_magic(content, ext):
    raise HTTPException(
      status_code=400,
      detail="文件内容与扩展名不符，请检查文件格式"
    )

  # 7. 检查 MIME 类型（严格校验）
  mime_type = file.content_type or "application/octet-stream"
  if mime_type not in ALLOWED_IMAGE_TYPES | ALLOWED_DOCUMENT_TYPES:
    raise HTTPException(
      status_code=400,
      detail=f"不支持的 MIME 类型: {mime_type}"
    )

  # 8. 保存文件
  settings = get_settings()
  upload_dir = Path(settings.upload_dir) / "chat_attachments"
  upload_dir.mkdir(parents=True, exist_ok=True)

  file_id = str(uuid.uuid4())
  safe_name = sanitize_filename_component(raw_name)
  file_path = upload_dir / f"{file_id}_{safe_name}"
  file_path.write_bytes(content)

  # 设置安全的文件权限（仅所有者可读写）
  os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)

  return ApiResponse(data={
    "file_id": file_id,
    "filename": raw_name,
    "file_type": ext,
    "file_size": len(content),
  })

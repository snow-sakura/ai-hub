"""聊天 API 端点"""

import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse

from app.api.schemas.chat import ChatRequest
from app.api.schemas.common import ApiResponse
from app.service.chat_service import ChatService
from app.config import get_settings

router = APIRouter()
chat_service = ChatService()


@router.post("/send")
async def send_chat(request: ChatRequest):
  """发送消息并流式返回 AI 响应（SSE）"""
  return StreamingResponse(
    chat_service.stream_chat(
      message=request.message,
      conversation_id=request.conversation_id,
      model_provider=request.model_provider,
      model_name=request.model_name,
      knowledge_doc_ids=request.knowledge_doc_ids,
      attachments=request.attachments,
    ),
    media_type="text/event-stream",
    headers={
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "X-Accel-Buffering": "no",
    },
  )


@router.post("/upload")
async def upload_chat_attachment(file: UploadFile = File(...)) -> ApiResponse[dict]:
  """上传聊天附件，返回 file_id 供后续发送消息时引用"""
  settings = get_settings()
  upload_dir = Path(settings.upload_dir) / "chat_attachments"
  upload_dir.mkdir(parents=True, exist_ok=True)

  file_id = str(uuid.uuid4())
  content = await file.read()
  filename = file.filename or f"attachment_{file_id}"
  file_type = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"

  # 保存原始文件
  file_path = upload_dir / f"{file_id}_{filename}"
  file_path.write_bytes(content)

  return ApiResponse(data={
    "file_id": file_id,
    "filename": filename,
    "file_type": file_type,
    "file_size": len(content),
  })

"""模型管理 API 端点"""

from fastapi import APIRouter, Depends

from app.common.api.schemas.common import ApiResponse
from app.common.core.llm_factory import LLMFactory

router = APIRouter()


@router.get("")
async def list_models() -> ApiResponse[list[dict[str, str]]]:
  """获取可用模型列表"""
  models = LLMFactory.get_available_models()
  return ApiResponse(data=models)

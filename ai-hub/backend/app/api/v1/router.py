"""v1 路由汇总"""

from fastapi import APIRouter

from app.api.v1.chat import router as chat_router
from app.api.v1.conversation import router as conversation_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.models import router as models_router
from app.api.v1.tools import router as tools_router

api_router = APIRouter()

api_router.include_router(chat_router, prefix="/chat", tags=["聊天"])
api_router.include_router(conversation_router, prefix="/conversations", tags=["会话"])
api_router.include_router(knowledge_router, prefix="/knowledge", tags=["知识库"])
api_router.include_router(models_router, prefix="/models", tags=["模型"])
api_router.include_router(tools_router, prefix="/tools", tags=["工具"])

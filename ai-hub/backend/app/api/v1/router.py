"""v1 路由汇总 — 注册所有模块路由"""

from fastapi import APIRouter

# ── 6 个功能模块 ───────────────────────────────────
from app.modules.system.api import auth_router                # /auth — 认证
from app.modules.system.api import system_router              # /system — 系统管理
from app.modules.chat.api import router as chat_router        # /chat — AI聊天室
from app.modules.comfort.api import router as comfort_router  # /comfort — 哄哄模拟器
from app.modules.knowledge.api import router as knowledge_router  # /knowledge — 知识管理
from app.modules.ai_testing.api import router as testing_router   # /testing — AI智能测试
from app.modules.config_center.api import router as config_router    # /config — 配置中心

# ── 共享路由（跨模块公共能力） ────────────────────────────
from app.common.api.v1.conversation import router as conversation_router  # 会话
from app.common.api.v1.models import router as models_router             # 模型
from app.common.api.v1.tools import router as tools_router               # 工具
from app.common.api.v1.modules import router as modules_router           # 模块列表

api_router = APIRouter()

# ── 功能模块路由 ──────────────────────────────────────────
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(system_router, prefix="/system", tags=["系统管理"])
api_router.include_router(chat_router, prefix="/chat", tags=["聊天"])
api_router.include_router(comfort_router, prefix="/comfort", tags=["哄哄模拟器"])
api_router.include_router(knowledge_router, prefix="/knowledge", tags=["知识库"])
api_router.include_router(testing_router, prefix="/testing", tags=["AI测试"])
api_router.include_router(config_router, prefix="/config", tags=["配置中心"])

# ── 共享路由 ──────────────────────────────────────────────
api_router.include_router(conversation_router, prefix="/conversations", tags=["会话"])
api_router.include_router(models_router, prefix="/models", tags=["模型"])
api_router.include_router(tools_router, prefix="/tools", tags=["工具"])
api_router.include_router(modules_router, prefix="/modules", tags=["模块"])

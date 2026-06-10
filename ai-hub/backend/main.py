"""FastAPI 应用入口"""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.shared.core.database import init_db
from app.modules.comfort.database import init_comfort_tables
from app.modules.comfort.scene_seed import seed_builtin_data
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
  """应用生命周期管理"""
  await init_db()
  await init_comfort_tables()
  await seed_builtin_data()
  try:
    yield
  finally:
    # 清理 LangGraph 数据库连接，避免资源泄漏
    from app.modules.chat.graph import close_agent_graph
    from app.modules.comfort.graph import close_comfort_graph
    await close_agent_graph()
    await close_comfort_graph()


settings = get_settings()

# 解析 CORS 允许的域名列表
def parse_cors_origins(origins_str: str) -> list[str]:
  """解析 CORS 配置：支持逗号分隔的多个域名，* 表示允许所有"""
  if origins_str.strip() == "*":
    return ["*"]
  return [origin.strip() for origin in origins_str.split(",") if origin.strip()]

app = FastAPI(
  title="AI 测试平台",
  description="AI 测试平台后端 API",
  version="1.0.0",
  lifespan=lifespan,
)

cors_origins = parse_cors_origins(settings.cors_allowed_origins)
allow_all = cors_origins == ["*"]

# 生产环境禁止使用 *
if not settings.app_debug and allow_all:
  raise RuntimeError(
    "CRITICAL: CORS_ALLOWED_ORIGINS='*' is not allowed in production! "
    "Set specific domains in .env file."
  )

app.add_middleware(
  CORSMiddleware,
  allow_origins=cors_origins,
  allow_credentials=not allow_all,  # allow_all=true 时不能设置 credentials=true
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
  uvicorn.run(
    "main:app",
    host=settings.app_host,
    port=settings.app_port,
    reload=settings.app_debug,
  )

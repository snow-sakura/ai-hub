"""FastAPI 应用入口"""

import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.common.core.database import init_db
from app.modules.comfort.database import init_comfort_tables
from app.modules.comfort.scene_seed import seed_builtin_data
from app.modules.ai_testing.database import init_testing_tables
from app.modules.config_center.database import init_config_tables
from app.modules.system.database import init_system_tables
from app.api.v1.router import api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
  """应用生命周期管理"""
  await init_db()
  await init_comfort_tables()
  await seed_builtin_data()
  await init_testing_tables()

  # MySQL DDL 初始化 + Admin 账号播种（共用同一连接）
  from app.common.core.database import get_db
  db = await get_db()
  try:
    await init_config_tables()
    await init_system_tables(db)

  except Exception as e:
    logger.warning("MySQL 初始化失败: %s", e)
  finally:
    await db.close()

  try:
    yield
  finally:
    # 清理 LangGraph 数据库连接，避免资源泄漏
    from app.modules.chat.graph import close_agent_graph
    from app.modules.comfort.graph import close_comfort_graph
    from app.modules.ai_testing.graph import close_testing_graph
    await close_agent_graph()
    await close_comfort_graph()
    await close_testing_graph()


settings = get_settings()

# ─── CORS 安全配置 ────────────────────────────────────
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
ALLOWED_HEADERS = [
  "Content-Type",
  "Authorization",
  "X-Requested-With",
  "Accept",
  "Origin",
]


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
  allow_credentials=not allow_all,
  allow_methods=ALLOWED_METHODS,
  allow_headers=ALLOWED_HEADERS,
)


# ─── 安全 Headers 中间件 ────────────────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
  """添加安全相关的 HTTP 响应头"""
  response = await call_next(request)
  response.headers["X-Content-Type-Options"] = "nosniff"
  response.headers["X-Frame-Options"] = "DENY"
  # 浏览器已废弃 X-XSS-Protection，设为 0 禁用反射型 XSS 过滤器
  response.headers["X-XSS-Protection"] = "0"
  response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
  response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
  # API 服务不渲染 HTML，无需 script/style nonce
  response.headers["Content-Security-Policy"] = (
    "default-src 'none'; "
    "frame-ancestors 'none'"
  )
  if not settings.app_debug:
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
  return response


app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
  uvicorn.run(
    "main:app",
    host=settings.app_host,
    port=settings.app_port,
    reload=settings.app_debug,
  )

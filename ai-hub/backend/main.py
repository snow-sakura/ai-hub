"""FastAPI 应用入口"""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.database import init_db
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
  """应用生命周期管理"""
  await init_db()
  yield


settings = get_settings()

app = FastAPI(
  title="AI 测试平台",
  description="AI 测试平台后端 API",
  version="1.0.0",
  lifespan=lifespan,
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
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

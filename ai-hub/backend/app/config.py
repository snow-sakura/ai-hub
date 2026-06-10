"""应用配置模块 - 使用 Pydantic Settings 从环境变量读取配置"""

from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

# 始终以 backend/ 目录为基准查找 .env，避免 CWD 问题
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
  """应用全局配置"""

  # OpenAI
  openai_api_key: str = ""
  openai_base_url: str = "https://api.openai.com/v1"

  # DeepSeek
  deepseek_api_key: str = ""
  deepseek_base_url: str = "https://api.deepseek.com/v1"

  # Qwen
  qwen_api_key: str = ""
  qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

  # Zhipu
  zhipu_api_key: str = ""
  zhipu_base_url: str = "https://open.bigmodel.cn/api/paas/v4"

  # Ollama
  ollama_base_url: str = "http://localhost:11434"

  # Pexels
  pexels_api_key: str = ""

  # Unsplash
  unsplash_access_key: str = ""

  # App
  app_host: str = "0.0.0.0"
  app_port: int = 8000
  app_debug: bool = True

  # Database
  sqlite_db_path: str = "./data/sqlite/app.db"

  # ChromaDB
  chroma_persist_dir: str = "./data/chroma"

  # File Storage
  upload_dir: str = "./data/uploads"
  workspace_dir: str = "./data/workspace"

  # CORS 配置
  cors_allowed_origins: str = "http://localhost:5173"

  model_config = {
    "env_file": str(ENV_FILE) if ENV_FILE.exists() else ".env",
    "env_file_encoding": "utf-8",
    "extra": "ignore",
  }


@lru_cache
def get_settings() -> Settings:
  """获取全局配置单例"""
  return Settings()

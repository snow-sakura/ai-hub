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
  openai_api_key: str = "CHANGE_ME"
  openai_base_url: str = "https://api.openai.com/v1"

  # DeepSeek
  deepseek_api_key: str = "CHANGE_ME"
  deepseek_base_url: str = "https://api.deepseek.com/v1"

  # Qwen
  qwen_api_key: str = "CHANGE_ME"
  qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

  # Zhipu
  zhipu_api_key: str = "CHANGE_ME"
  zhipu_base_url: str = "https://open.bigmodel.cn/api/paas/v4"

  # Ollama
  ollama_base_url: str = "http://localhost:11434"

  # Pexels
  pexels_api_key: str = "CHANGE_ME"

  # Unsplash
  unsplash_access_key: str = "CHANGE_ME"

  # App
  app_host: str = "0.0.0.0"
  app_port: int = 8000
  app_debug: bool = False

  # MySQL Database (主数据存储)
  mysql_host: str = "127.0.0.1"
  mysql_port: int = 3306
  mysql_user: str = "root"
  mysql_password: str = ""
  mysql_database: str = "ai_hub"

  # LangGraph checkpoint 后端选择 (mysql / sqlite)
  langgraph_checkpoint_backend: str = "mysql"

  # SQLite (回退选项，langgraph_checkpoint_backend=sqlite 时使用)
  sqlite_db_path: str = "./data/sqlite/app.db"

  # MySQL 连接池调优
  mysql_pool_size: int = 10
  mysql_pool_recycle: int = 3600

  # ChromaDB
  chroma_persist_dir: str = "./data/chroma"

  # File Storage（按类别组织）
  upload_dir: str = "./data/storage/attachments"
  workspace_dir: str = "./data/storage/workspace"


  # CORS 配置
  cors_allowed_origins: str = "http://localhost:5173"

  # JWT
  jwt_secret_key: str = "CHANGE_ME"

  # Operation Logs
  operation_log_dir: str = "./logs/operations"

  model_config = {
    "env_file": str(ENV_FILE) if ENV_FILE.exists() else ".env",
    "env_file_encoding": "utf-8",
    "extra": "forbid",
  }


@lru_cache
def get_settings() -> Settings:
  """获取全局配置单例"""
  return Settings()

"""结构化日志配置模块

注意：使用懒加载模式，避免模块导入时立即加载配置（防止循环导入）。
"""
import logging
import sys
from pathlib import Path


def setup_logging() -> logging.Logger:
  """配置应用日志系统

  使用懒加载：首次从 app.config 获取设置，
  之后直接从 Logger 单例读取。

  - 开发环境：输出到控制台，DEBUG 级别
  - 生产环境：同时输出到文件和控制台，INFO 级别
  """
  from app.config import get_settings  # 延迟导入，避免循环依赖

  settings = get_settings()
  logger = logging.getLogger("ai_hub")

  if logger.handlers:
    return logger

  log_level = logging.DEBUG if settings.app_debug else logging.INFO
  logger.setLevel(log_level)

  formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
  )

  console_handler = logging.StreamHandler(sys.stdout)
  console_handler.setFormatter(formatter)
  console_handler.setLevel(log_level)
  logger.addHandler(console_handler)

  if not settings.app_debug:
    log_dir = Path("./logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.WARNING)
    logger.addHandler(file_handler)

  return logger


# 全局 logger 实例（懒加载）
_logger: logging.Logger | None = None


def get_logger(name: str) -> logging.Logger:
  """获取子模块 logger（自动初始化全局 logger）"""
  global _logger
  if _logger is None:
    _logger = setup_logging()
  child = logging.getLogger(f"ai_hub.{name}")
  child.setLevel(_logger.level)
  return child

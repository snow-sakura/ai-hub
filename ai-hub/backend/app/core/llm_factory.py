"""LLM 模型工厂 - 按 provider 创建模型实例"""

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

from app.config import get_settings, ENV_FILE
from app.domain.entities import ModelConfig


AVAILABLE_MODELS: list[ModelConfig] = [
  # ---- DeepSeek V4 系列（2026） ----
  # deepseek-chat / deepseek-reasoner 将于 2026-07-24 停用
  ModelConfig(
    provider="deepseek", model="deepseek-v4-flash",
    display_name="DeepSeek V4 Flash",
  ),
  ModelConfig(
    provider="deepseek", model="deepseek-v4-pro",
    display_name="DeepSeek V4 Pro",
  ),
  # ---- 通义千问 Qwen3.7 系列（2026.05） ----
  ModelConfig(
    provider="qwen", model="qwen3.7-max",
    display_name="通义千问 3.7 Max",
  ),
  ModelConfig(
    provider="qwen", model="qwen3.7-plus",
    display_name="通义千问 3.7 Plus",
  ),
  # ---- 智谱 GLM-4 系列 ----
  ModelConfig(
    provider="zhipu", model="glm-4-plus",
    display_name="智谱 GLM-4 Plus",
  ),
  ModelConfig(
    provider="zhipu", model="glm-4-flash",
    display_name="智谱 GLM-4 Flash",
  ),
  # ---- Ollama 本地模型 ----
  ModelConfig(
    provider="ollama", model="qwen2.5:7b",
    display_name="Ollama Qwen2.5 7B",
  ),
]

# 各 provider 所需的配置字段
_PROVIDER_REQUIRED_FIELDS: dict[str, tuple[str, str]] = {
  "openai": ("openai_api_key", "OPENAI_API_KEY"),
  "deepseek": ("deepseek_api_key", "DEEPSEEK_API_KEY"),
  "qwen": ("qwen_api_key", "QWEN_API_KEY"),
  "zhipu": ("zhipu_api_key", "ZHIPU_API_KEY"),
}


class LLMFactory:
  """LLM 模型工厂"""

  @staticmethod
  def create(provider: str, model_name: str = "") -> BaseChatModel:
    """根据 provider 创建 LLM 实例"""
    settings = get_settings()

    # 统一校验 API Key（Ollama 不需要）
    if provider in _PROVIDER_REQUIRED_FIELDS:
      field, env_name = _PROVIDER_REQUIRED_FIELDS[provider]
      api_key = getattr(settings, field, "")
      if not api_key:
        raise ValueError(
          f"【{provider}】的 API Key 未配置。"
          f"请在 {ENV_FILE} 中设置 {env_name}=your-key，"
          f"或在环境变量中设置 {env_name}=your-key"
        )

    if provider == "openai":
      return ChatOpenAI(
        model=model_name or "gpt-4o-mini",
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        streaming=True,
        temperature=0.7,
      )
    elif provider == "deepseek":
      return ChatOpenAI(
        model=model_name or "deepseek-chat",
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        streaming=True,
        temperature=0.7,
      )
    elif provider == "qwen":
      return ChatOpenAI(
        model=model_name or "qwen-plus",
        api_key=settings.qwen_api_key,
        base_url=settings.qwen_base_url,
        streaming=True,
        temperature=0.7,
      )
    elif provider == "zhipu":
      return ChatOpenAI(
        model=model_name or "glm-4-flash",
        api_key=settings.zhipu_api_key,
        base_url=settings.zhipu_base_url,
        streaming=True,
        temperature=0.7,
      )
    elif provider == "ollama":
      return ChatOllama(
        model=model_name or "qwen2.5:7b",
        base_url=settings.ollama_base_url,
        temperature=0.7,
      )
    else:
      # 默认 fallback 到国产 DeepSeek
      if not settings.deepseek_api_key:
        raise ValueError(
          "未指定模型 provider，且默认 DeepSeek 的 API Key 未配置。"
          f"请在 {ENV_FILE} 中设置 DEEPSEEK_API_KEY=your-key，"
          "或设置其他已配置的 provider"
        )
      return ChatOpenAI(
        model=model_name or "deepseek-chat",
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        streaming=True,
        temperature=0.7,
      )

  @staticmethod
  def get_available_models() -> list[dict[str, str]]:
    """获取可用模型列表"""
    return [
      {
        "provider": m.provider,
        "model": m.model,
        "display_name": m.display_name,
      }
      for m in AVAILABLE_MODELS
    ]

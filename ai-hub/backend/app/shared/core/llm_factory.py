"""LLM 模型工厂 - 按 provider 创建模型实例"""

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

from app.config import get_settings, ENV_FILE
from app.shared.domain.entities import ModelConfig

# --------------------------------------------------------------
# Monkey-patch: DeepSeek thinking mode 适配
#
# DeepSeek 要求将 reasoning_content 回传给 API，但 LangChain 的
# ChatOpenAI 实现不处理该字段（README 明确标注"not extracted"）。
#
# 需要补丁两处：
#   1. _convert_delta_to_message_chunk — 从 stream delta 中提取
#      reasoning_content 存入 additional_kwargs（捕获阶段）
#   2. _convert_message_to_dict — 从 additional_kwargs 注入到
#      序列化的消息 dict（回传阶段）
# --------------------------------------------------------------
import langchain_openai.chat_models.base as _lc_base

# ---- 补丁 1：从 stream delta 捕获 reasoning_content ----
_original_convert_delta = _lc_base._convert_delta_to_message_chunk


def _patched_convert_delta_to_message_chunk(_dict, default_class):
    chunk = _original_convert_delta(_dict, default_class)
    if isinstance(chunk, AIMessageChunk):
        rc = _dict.get("reasoning_content", "")
        if rc:
            chunk.additional_kwargs["reasoning_content"] = rc
    return chunk


_lc_base._convert_delta_to_message_chunk = _patched_convert_delta_to_message_chunk

# ---- 补丁 2：序列化时将 reasoning_content 注入消息 dict ----
_original_convert = _lc_base._convert_message_to_dict


def _patched_convert_message_to_dict(message, api="chat/completions"):
    result = _original_convert(message, api)
    if isinstance(message, AIMessage):
        rc = message.additional_kwargs.get("reasoning_content", "")
        if rc:
            result["reasoning_content"] = rc
    return result


_lc_base._convert_message_to_dict = _patched_convert_message_to_dict
# --------------------------------------------------------------


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
  def create(provider: str, model_name: str = "",
             reasoning_effort: str = "high",
             api_key: str | None = None) -> BaseChatModel:
    """根据 provider 创建 LLM 实例

    Args:
      provider: 模型提供商
      model_name: 模型名称
      reasoning_effort: DeepSeek thinking 深度（high/max/disabled），其他 provider 忽略
      api_key: 自定义 API Key（非空时覆盖全局 settings 中的 key，仅对 key-based provider 生效）
    """
    settings = get_settings()

    # 统一校验 API Key（Ollama 不需要）
    if provider in _PROVIDER_REQUIRED_FIELDS:
      field, env_name = _PROVIDER_REQUIRED_FIELDS[provider]
      effective_key = api_key or getattr(settings, field, "")
      if not effective_key:
        raise ValueError(
          f"【{provider}】的 API Key 未配置。"
          f"请在 {ENV_FILE} 中设置 {env_name}=your-key，"
          f"或在环境变量中设置 {env_name}=your-key"
        )

    if provider == "openai":
      return ChatOpenAI(
        model=model_name or "gpt-4o-mini",
        api_key=api_key or settings.openai_api_key,
        base_url=settings.openai_base_url,
        streaming=True,
        temperature=0.7,
        timeout=60,
        max_retries=2,
        stream_usage=True,
      )
    elif provider == "deepseek":
      # DeepSeek thinking mode：
      #   - reasoning_effort 作为显式参数（high / max）
      #   - thinking 放入 extra_body（DeepSeek 特有，非 OpenAI 标准参数）
      extra_body = {}
      effort = reasoning_effort
      if reasoning_effort == "disabled":
        extra_body["thinking"] = {"type": "disabled"}
        effort = None
      else:
        extra_body["thinking"] = {"type": "enabled"}
      return ChatOpenAI(
        model=model_name or "deepseek-v4-flash",
        api_key=api_key or settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        streaming=True,
        reasoning_effort=effort,
        extra_body=extra_body,
        timeout=60,
        max_retries=2,
        stream_usage=True,
      )
    elif provider == "qwen":
      return ChatOpenAI(
        model=model_name or "qwen-plus",
        api_key=api_key or settings.qwen_api_key,
        base_url=settings.qwen_base_url,
        streaming=True,
        temperature=0.7,
        timeout=60,
        max_retries=2,
        stream_usage=True,
      )
    elif provider == "zhipu":
      return ChatOpenAI(
        model=model_name or "glm-4-flash",
        api_key=api_key or settings.zhipu_api_key,
        base_url=settings.zhipu_base_url,
        streaming=True,
        temperature=0.7,
        timeout=60,
        max_retries=2,
        stream_usage=True,
      )
    elif provider == "ollama":
      return ChatOllama(
        model=model_name or "qwen2.5:7b",
        base_url=settings.ollama_base_url,
        streaming=True,
        temperature=0.7,
        timeout=60,
      )
    else:
      # 默认 fallback 到国产 DeepSeek
      effective_key = api_key or settings.deepseek_api_key
      if not effective_key:
        raise ValueError(
          "未指定模型 provider，且默认 DeepSeek 的 API Key 未配置。"
          f"请在 {ENV_FILE} 中设置 DEEPSEEK_API_KEY=your-key，"
          "或设置其他已配置的 provider"
        )
      return ChatOpenAI(
        model=model_name or "deepseek-v4-flash",
        api_key=api_key or settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        streaming=True,
        temperature=0.7,
        timeout=60,
        max_retries=2,
        stream_usage=True,
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

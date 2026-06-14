"""配置中心模块 Pydantic 请求/响应模型"""

from datetime import datetime
from pydantic import BaseModel, Field


# ── AI 模型配置 ─────────────────────────────────────────────

class ModelConfigCreate(BaseModel):
    provider: str = Field(min_length=1, max_length=50)
    model_name: str = ""
    api_key: str = ""
    api_base_url: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096
    enabled: bool = True
    sort_order: int = 0


class ModelConfigUpdate(BaseModel):
    provider: str | None = None
    model_name: str | None = None
    api_key: str | None = None
    api_base_url: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    enabled: bool | None = None
    sort_order: int | None = None


class ModelConfigResponse(BaseModel):
    id: str
    provider: str
    model_name: str
    api_key: str
    api_base_url: str
    temperature: float
    max_tokens: int
    enabled: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime


# ── 提示词配置 ─────────────────────────────────────────────

class PromptConfigCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    stage: str = ""
    content: str
    enabled: bool = True
    description: str = ""


class PromptConfigUpdate(BaseModel):
    name: str | None = None
    stage: str | None = None
    content: str | None = None
    enabled: bool | None = None
    description: str | None = None


class PromptConfigResponse(BaseModel):
    id: str
    name: str
    stage: str
    content: str
    enabled: bool
    description: str
    created_at: datetime
    updated_at: datetime


# ── 生成行为配置 ───────────────────────────────────────────

class BehaviorConfigUpdate(BaseModel):
    key: str = Field(min_length=1, max_length=255)
    value: str
    description: str = ""


class BehaviorConfigResponse(BaseModel):
    key: str
    value: str
    description: str
    updated_at: datetime


# ── AI 聊天室配置 ─────────────────────────────────────────

class ChatConfigUpdate(BaseModel):
    model_provider: str | None = None
    model_name: str | None = None
    system_prompt: str | None = None
    max_history: int | None = None
    enable_rag: bool | None = None
    rag_top_k: int | None = None
    enable_web_search: bool | None = None
    temperature: float | None = None


class ChatConfigResponse(BaseModel):
    model_provider: str
    model_name: str
    system_prompt: str
    max_history: int
    enable_rag: bool
    rag_top_k: int
    enable_web_search: bool
    temperature: float
    updated_at: datetime


# ── UI 环境配置 ───────────────────────────────────────────

class UiEnvConfigCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    base_url: str = ""
    browser_type: str = "chromium"
    headless: bool = True
    viewport_width: int = 1280
    viewport_height: int = 720
    timeout_ms: int = 30000
    screenshot_on_failure: bool = True


class UiEnvConfigUpdate(BaseModel):
    name: str | None = None
    base_url: str | None = None
    browser_type: str | None = None
    headless: bool | None = None
    viewport_width: int | None = None
    viewport_height: int | None = None
    timeout_ms: int | None = None
    screenshot_on_failure: bool | None = None


class UiEnvConfigResponse(BaseModel):
    id: str
    name: str
    base_url: str
    browser_type: str
    headless: bool
    viewport_width: int
    viewport_height: int
    timeout_ms: int
    screenshot_on_failure: bool
    created_at: datetime
    updated_at: datetime


# ── APP 环境配置 ──────────────────────────────────────────

class AppEnvConfigCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    platform: str = "android"
    app_package: str = ""
    app_activity: str = ""
    device_serial: str = ""
    appium_url: str = "http://localhost:4723"
    timeout_ms: int = 30000
    screenshot_on_failure: bool = True


class AppEnvConfigUpdate(BaseModel):
    name: str | None = None
    platform: str | None = None
    app_package: str | None = None
    app_activity: str | None = None
    device_serial: str | None = None
    appium_url: str | None = None
    timeout_ms: int | None = None
    screenshot_on_failure: bool | None = None


class AppEnvConfigResponse(BaseModel):
    id: str
    name: str
    platform: str
    app_package: str
    app_activity: str
    device_serial: str
    appium_url: str
    timeout_ms: int
    screenshot_on_failure: bool
    created_at: datetime
    updated_at: datetime

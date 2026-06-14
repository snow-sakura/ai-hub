"""配置中心模块业务逻辑层"""

from typing import Any

from app.modules.config_center.repository import ConfigCenterRepository
from app.common.core.database import MySQLConnection


class ConfigCenterService:
    """配置中心服务"""

    def __init__(self, db: MySQLConnection):
        self.db = db
        self.repo = ConfigCenterRepository(db)

    # ── AI 模型配置 ──────────────────────────────────────────

    async def list_models(self) -> list[dict[str, Any]]:
        rows = await self.repo.list_models()
        return [{
            "id": r["id"], "provider": r["provider"],
            "model_name": r.get("model_name", ""),
            "api_key": r.get("api_key", ""),
            "api_base_url": r.get("api_base_url", ""),
            "temperature": float(r.get("temperature", 0.7)),
            "max_tokens": int(r.get("max_tokens", 4096)),
            "enabled": bool(r.get("enabled", True)),
            "sort_order": int(r.get("sort_order", 0)),
            "created_at": r["created_at"], "updated_at": r["updated_at"],
        } for r in rows]

    async def get_model(self, model_id: str) -> dict[str, Any] | None:
        r = await self.repo.get_model(model_id)
        if not r:
            return None
        return {
            "id": r["id"], "provider": r["provider"],
            "model_name": r.get("model_name", ""),
            "api_key": r.get("api_key", ""),
            "api_base_url": r.get("api_base_url", ""),
            "temperature": float(r.get("temperature", 0.7)),
            "max_tokens": int(r.get("max_tokens", 4096)),
            "enabled": bool(r.get("enabled", True)),
            "sort_order": int(r.get("sort_order", 0)),
            "created_at": r["created_at"], "updated_at": r["updated_at"],
        }

    async def create_model(self, data: dict[str, Any]) -> dict[str, Any]:
        model_id = await self.repo.create_model(data)
        return await self.get_model(model_id)  # type: ignore[return-value]

    async def update_model(self, model_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        ok = await self.repo.update_model(model_id, data)
        if not ok:
            return None
        return await self.get_model(model_id)

    async def delete_model(self, model_id: str) -> None:
        await self.repo.delete_model(model_id)

    # ── 提示词配置 ──────────────────────────────────────────

    async def list_prompts(self) -> list[dict[str, Any]]:
        rows = await self.repo.list_prompts()
        return [{
            "id": r["id"], "name": r["name"], "stage": r.get("stage", ""),
            "content": r["content"], "enabled": bool(r.get("enabled", True)),
            "description": r.get("description", ""),
            "created_at": r["created_at"], "updated_at": r["updated_at"],
        } for r in rows]

    async def get_prompt(self, prompt_id: str) -> dict[str, Any] | None:
        r = await self.repo.get_prompt(prompt_id)
        if not r:
            return None
        return {
            "id": r["id"], "name": r["name"], "stage": r.get("stage", ""),
            "content": r["content"], "enabled": bool(r.get("enabled", True)),
            "description": r.get("description", ""),
            "created_at": r["created_at"], "updated_at": r["updated_at"],
        }

    async def create_prompt(self, data: dict[str, Any]) -> dict[str, Any]:
        prompt_id = await self.repo.create_prompt(data)
        return await self.get_prompt(prompt_id)  # type: ignore[return-value]

    async def update_prompt(self, prompt_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        ok = await self.repo.update_prompt(prompt_id, data)
        if not ok:
            return None
        return await self.get_prompt(prompt_id)

    async def delete_prompt(self, prompt_id: str) -> None:
        await self.repo.delete_prompt(prompt_id)

    # ── 生成行为配置 ──────────────────────────────────────────

    async def list_behaviors(self) -> list[dict[str, Any]]:
        rows = await self.repo.list_behaviors()
        return [{
            "key": r["key"], "value": r["value"],
            "description": r.get("description", ""),
            "updated_at": r["updated_at"],
        } for r in rows]

    async def upsert_behavior(self, key: str, value: str, description: str = "") -> dict[str, Any]:
        await self.repo.upsert_behavior(key, value, description)
        return {"key": key, "value": value, "description": description}

    async def delete_behavior(self, key: str) -> None:
        await self.repo.delete_behavior(key)

    # ── AI 聊天室配置 ──────────────────────────────────────────

    async def get_chat_config(self) -> dict[str, Any]:
        r = await self.repo.get_chat_config()
        if not r:
            return {
                "model_provider": "deepseek", "model_name": "",
                "system_prompt": "", "max_history": 20,
                "enable_rag": False, "rag_top_k": 3,
                "enable_web_search": False, "temperature": 0.7,
            }
        return {
            "model_provider": r.get("model_provider", "deepseek"),
            "model_name": r.get("model_name", ""),
            "system_prompt": r.get("system_prompt", ""),
            "max_history": int(r.get("max_history", 20)),
            "enable_rag": bool(r.get("enable_rag", False)),
            "rag_top_k": int(r.get("rag_top_k", 3)),
            "enable_web_search": bool(r.get("enable_web_search", False)),
            "temperature": float(r.get("temperature", 0.7)),
        }

    async def update_chat_config(self, data: dict[str, Any]) -> dict[str, Any]:
        await self.repo.upsert_chat_config(data)
        return await self.get_chat_config()

    # ── UI 环境配置 ──────────────────────────────────────────

    async def list_ui_envs(self) -> list[dict[str, Any]]:
        rows = await self.repo.list_ui_envs()
        return [self._format_ui_env(r) for r in rows]

    async def get_ui_env(self, env_id: str) -> dict[str, Any] | None:
        r = await self.repo.get_ui_env(env_id)
        return self._format_ui_env(r) if r else None

    async def create_ui_env(self, data: dict[str, Any]) -> dict[str, Any]:
        env_id = await self.repo.create_ui_env(data)
        return await self.get_ui_env(env_id)  # type: ignore[return-value]

    async def update_ui_env(self, env_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        ok = await self.repo.update_ui_env(env_id, data)
        if not ok:
            return None
        return await self.get_ui_env(env_id)

    async def delete_ui_env(self, env_id: str) -> None:
        await self.repo.delete_ui_env(env_id)

    def _format_ui_env(self, r: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": r["id"], "name": r["name"],
            "base_url": r.get("base_url", ""),
            "browser_type": r.get("browser_type", "chromium"),
            "headless": bool(r.get("headless", True)),
            "viewport_width": int(r.get("viewport_width", 1280)),
            "viewport_height": int(r.get("viewport_height", 720)),
            "timeout_ms": int(r.get("timeout_ms", 30000)),
            "screenshot_on_failure": bool(r.get("screenshot_on_failure", True)),
            "created_at": r["created_at"], "updated_at": r["updated_at"],
        }

    # ── APP 环境配置 ──────────────────────────────────────────

    async def list_app_envs(self) -> list[dict[str, Any]]:
        rows = await self.repo.list_app_envs()
        return [self._format_app_env(r) for r in rows]

    async def get_app_env(self, env_id: str) -> dict[str, Any] | None:
        r = await self.repo.get_app_env(env_id)
        return self._format_app_env(r) if r else None

    async def create_app_env(self, data: dict[str, Any]) -> dict[str, Any]:
        env_id = await self.repo.create_app_env(data)
        return await self.get_app_env(env_id)  # type: ignore[return-value]

    async def update_app_env(self, env_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        ok = await self.repo.update_app_env(env_id, data)
        if not ok:
            return None
        return await self.get_app_env(env_id)

    async def delete_app_env(self, env_id: str) -> None:
        await self.repo.delete_app_env(env_id)

    def _format_app_env(self, r: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": r["id"], "name": r["name"],
            "platform": r.get("platform", "android"),
            "app_package": r.get("app_package", ""),
            "app_activity": r.get("app_activity", ""),
            "device_serial": r.get("device_serial", ""),
            "appium_url": r.get("appium_url", "http://localhost:4723"),
            "timeout_ms": int(r.get("timeout_ms", 30000)),
            "screenshot_on_failure": bool(r.get("screenshot_on_failure", True)),
            "created_at": r["created_at"], "updated_at": r["updated_at"],
        }

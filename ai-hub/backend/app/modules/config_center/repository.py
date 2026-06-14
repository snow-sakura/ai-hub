"""配置中心模块数据访问层"""

import uuid
from datetime import datetime
from typing import Any

from app.common.core.database import MySQLConnection


class ConfigCenterRepository:
    """配置中心仓储"""

    def __init__(self, db: MySQLConnection):
        self.db = db

    # ── AI 模型配置 ──────────────────────────────────────────

    async def list_models(self) -> list[dict[str, Any]]:
        cursor = await self.db.execute(
            "SELECT * FROM config_models ORDER BY sort_order, created_at"
        )
        rows = await cursor.fetchall()
        return rows if rows else []

    async def get_model(self, model_id: str) -> dict[str, Any] | None:
        cursor = await self.db.execute(
            "SELECT * FROM config_models WHERE id = %s", (model_id,)
        )
        return await cursor.fetchone()

    async def create_model(self, data: dict[str, Any]) -> str:
        model_id = str(uuid.uuid4())
        now = datetime.now()
        await self.db.execute(
            "INSERT INTO config_models (id, provider, model_name, api_key, api_base_url, "
            "temperature, max_tokens, enabled, sort_order, created_at, updated_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (model_id, data["provider"], data.get("model_name", ""),
             data.get("api_key", ""), data.get("api_base_url", ""),
             data.get("temperature", 0.7), data.get("max_tokens", 4096),
             data.get("enabled", True), data.get("sort_order", 0), now, now),
        )
        return model_id

    async def update_model(self, model_id: str, data: dict[str, Any]) -> bool:
        fields = []
        values = []
        for key in ("provider", "model_name", "api_key", "api_base_url",
                     "temperature", "max_tokens", "enabled", "sort_order"):
            if key in data:
                fields.append(f"{key} = %s")
                values.append(data[key])
        if not fields:
            return False
        fields.append("updated_at = %s")
        values.append(datetime.now())
        values.append(model_id)
        await self.db.execute(
            f"UPDATE config_models SET {', '.join(fields)} WHERE id = %s",
            tuple(values),
        )
        return True

    async def delete_model(self, model_id: str) -> None:
        await self.db.execute("DELETE FROM config_models WHERE id = %s", (model_id,))

    # ── 提示词配置 ──────────────────────────────────────────

    async def list_prompts(self) -> list[dict[str, Any]]:
        cursor = await self.db.execute(
            "SELECT * FROM config_prompts ORDER BY stage, created_at"
        )
        rows = await cursor.fetchall()
        return rows if rows else []

    async def get_prompt(self, prompt_id: str) -> dict[str, Any] | None:
        cursor = await self.db.execute(
            "SELECT * FROM config_prompts WHERE id = %s", (prompt_id,)
        )
        return await cursor.fetchone()

    async def create_prompt(self, data: dict[str, Any]) -> str:
        prompt_id = str(uuid.uuid4())
        now = datetime.now()
        await self.db.execute(
            "INSERT INTO config_prompts (id, name, stage, content, enabled, description, created_at, updated_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (prompt_id, data["name"], data.get("stage", ""),
             data["content"], data.get("enabled", True),
             data.get("description", ""), now, now),
        )
        return prompt_id

    async def update_prompt(self, prompt_id: str, data: dict[str, Any]) -> bool:
        fields = []
        values = []
        for key in ("name", "stage", "content", "enabled", "description"):
            if key in data:
                fields.append(f"{key} = %s")
                values.append(data[key])
        if not fields:
            return False
        fields.append("updated_at = %s")
        values.append(datetime.now())
        values.append(prompt_id)
        await self.db.execute(
            f"UPDATE config_prompts SET {', '.join(fields)} WHERE id = %s",
            tuple(values),
        )
        return True

    async def delete_prompt(self, prompt_id: str) -> None:
        await self.db.execute("DELETE FROM config_prompts WHERE id = %s", (prompt_id,))

    # ── 生成行为配置 ──────────────────────────────────────────

    async def list_behaviors(self) -> list[dict[str, Any]]:
        cursor = await self.db.execute(
            "SELECT * FROM config_behaviors ORDER BY `key`"
        )
        rows = await cursor.fetchall()
        return rows if rows else []

    async def upsert_behavior(self, key: str, value: str, description: str = "") -> None:
        now = datetime.now()
        await self.db.execute(
            "INSERT INTO config_behaviors (`key`, `value`, description, updated_at) "
            "VALUES (%s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE `value` = VALUES(`value`), "
            "description = VALUES(description), updated_at = VALUES(updated_at)",
            (key, value, description, now),
        )

    async def delete_behavior(self, key: str) -> None:
        await self.db.execute("DELETE FROM config_behaviors WHERE `key` = %s", (key,))

    # ── AI 聊天室配置 ──────────────────────────────────────────

    async def get_chat_config(self) -> dict[str, Any] | None:
        cursor = await self.db.execute("SELECT * FROM config_chat LIMIT 1")
        return await cursor.fetchone()

    async def upsert_chat_config(self, data: dict[str, Any]) -> str:
        cfg_id = str(uuid.uuid4())
        now = datetime.now()
        await self.db.execute(
            "INSERT INTO config_chat (id, model_provider, model_name, system_prompt, "
            "max_history, enable_rag, rag_top_k, enable_web_search, temperature, updated_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE "
            "model_provider = VALUES(model_provider), model_name = VALUES(model_name), "
            "system_prompt = VALUES(system_prompt), max_history = VALUES(max_history), "
            "enable_rag = VALUES(enable_rag), rag_top_k = VALUES(rag_top_k), "
            "enable_web_search = VALUES(enable_web_search), temperature = VALUES(temperature), "
            "updated_at = VALUES(updated_at)",
            (cfg_id, data.get("model_provider", "deepseek"),
             data.get("model_name", ""), data.get("system_prompt", ""),
             data.get("max_history", 20), data.get("enable_rag", False),
             data.get("rag_top_k", 3), data.get("enable_web_search", False),
             data.get("temperature", 0.7), now),
        )
        return cfg_id

    # ── UI 环境配置 ──────────────────────────────────────────

    async def list_ui_envs(self) -> list[dict[str, Any]]:
        cursor = await self.db.execute(
            "SELECT * FROM config_ui_env ORDER BY created_at"
        )
        rows = await cursor.fetchall()
        return rows if rows else []

    async def get_ui_env(self, env_id: str) -> dict[str, Any] | None:
        cursor = await self.db.execute(
            "SELECT * FROM config_ui_env WHERE id = %s", (env_id,)
        )
        return await cursor.fetchone()

    async def create_ui_env(self, data: dict[str, Any]) -> str:
        env_id = str(uuid.uuid4())
        now = datetime.now()
        await self.db.execute(
            "INSERT INTO config_ui_env (id, name, base_url, browser_type, headless, "
            "viewport_width, viewport_height, timeout_ms, screenshot_on_failure, created_at, updated_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (env_id, data["name"], data.get("base_url", ""),
             data.get("browser_type", "chromium"), data.get("headless", True),
             data.get("viewport_width", 1280), data.get("viewport_height", 720),
             data.get("timeout_ms", 30000), data.get("screenshot_on_failure", True), now, now),
        )
        return env_id

    async def update_ui_env(self, env_id: str, data: dict[str, Any]) -> bool:
        fields = []
        values = []
        for key in ("name", "base_url", "browser_type", "headless",
                     "viewport_width", "viewport_height", "timeout_ms", "screenshot_on_failure"):
            if key in data:
                fields.append(f"{key} = %s")
                values.append(data[key])
        if not fields:
            return False
        fields.append("updated_at = %s")
        values.append(datetime.now())
        values.append(env_id)
        await self.db.execute(
            f"UPDATE config_ui_env SET {', '.join(fields)} WHERE id = %s",
            tuple(values),
        )
        return True

    async def delete_ui_env(self, env_id: str) -> None:
        await self.db.execute("DELETE FROM config_ui_env WHERE id = %s", (env_id,))

    # ── APP 环境配置 ──────────────────────────────────────────

    async def list_app_envs(self) -> list[dict[str, Any]]:
        cursor = await self.db.execute(
            "SELECT * FROM config_app_env ORDER BY created_at"
        )
        rows = await cursor.fetchall()
        return rows if rows else []

    async def get_app_env(self, env_id: str) -> dict[str, Any] | None:
        cursor = await self.db.execute(
            "SELECT * FROM config_app_env WHERE id = %s", (env_id,)
        )
        return await cursor.fetchone()

    async def create_app_env(self, data: dict[str, Any]) -> str:
        env_id = str(uuid.uuid4())
        now = datetime.now()
        await self.db.execute(
            "INSERT INTO config_app_env (id, name, platform, app_package, app_activity, "
            "device_serial, appium_url, timeout_ms, screenshot_on_failure, created_at, updated_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (env_id, data["name"], data.get("platform", "android"),
             data.get("app_package", ""), data.get("app_activity", ""),
             data.get("device_serial", ""), data.get("appium_url", "http://localhost:4723"),
             data.get("timeout_ms", 30000), data.get("screenshot_on_failure", True), now, now),
        )
        return env_id

    async def update_app_env(self, env_id: str, data: dict[str, Any]) -> bool:
        fields = []
        values = []
        for key in ("name", "platform", "app_package", "app_activity",
                     "device_serial", "appium_url", "timeout_ms", "screenshot_on_failure"):
            if key in data:
                fields.append(f"{key} = %s")
                values.append(data[key])
        if not fields:
            return False
        fields.append("updated_at = %s")
        values.append(datetime.now())
        values.append(env_id)
        await self.db.execute(
            f"UPDATE config_app_env SET {', '.join(fields)} WHERE id = %s",
            tuple(values),
        )
        return True

    async def delete_app_env(self, env_id: str) -> None:
        await self.db.execute("DELETE FROM config_app_env WHERE id = %s", (env_id,))

"""配置值加密/解密工具

使用 Fernet（对称加密）保护存储在 testing_config 表中的敏感配置项，
如 API Key、Secret 等。加密密钥从 JWT_SECRET 派生。

用法：
  encrypted = encrypt_config_value("sk-xxx", "testing_config")
  plaintext = decrypt_config_value(encrypted, "testing_config")
"""

import base64
import hashlib
import re
import logging
from typing import Optional

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

# 标记为敏感字段的 key 正则匹配模式（匹配 _key、_secret、_password、_token 后缀）
SENSITIVE_KEY_PATTERN = re.compile(r"_(?:key|secret|password|token)$", re.IGNORECASE)


def _derive_fernet_key( salt: str = "testing_config" ) -> bytes:
    """从 JWT_SECRET 派生 Fernet 加密密钥

    Fernet 要求 32 字节 URL-safe base64 编码的密钥。
    使用 PBKDF2 从 JWT_SECRET 派生，确保密钥稳定且满足长度要求。
    """
    from app.config import get_settings

    try:
        secret = get_settings().jwt_secret
    except Exception:
        secret = "fallback-insecure-key-do-not-use-in-production"

    # SHA-256 哈希后取前 32 字节，base64 编码
    raw = hashlib.pbkdf2_hmac("sha256", secret.encode(), salt.encode(), iterations=100000, dklen=32)
    return base64.urlsafe_b64encode(raw)


def is_sensitive_key(key: str) -> bool:
    """判断配置 key 是否应加密存储（匹配 _key、_secret、_password、_token 后缀）"""
    return bool(SENSITIVE_KEY_PATTERN.search(key))


def encrypt_config_value(plaintext: str, salt: str = "testing_config") -> str:
    """加密配置值，返回字符串密文"""
    if not plaintext:
        return plaintext
    try:
        f = Fernet(_derive_fernet_key(salt))
        return f.encrypt(plaintext.encode()).decode()
    except Exception as e:
        logger.error("配置值加密失败: %s", e)
        return plaintext


def decrypt_config_value(ciphertext: str, salt: str = "testing_config") -> str:
    """解密配置值，返回明文字符串。解密失败返回原文（兼容未加密的老数据）。"""
    if not ciphertext:
        return ciphertext
    try:
        f = Fernet(_derive_fernet_key(salt))
        return f.decrypt(ciphertext.encode()).decode()
    except Exception:
        # 兼容旧数据（未加密的明文直接返回）
        return ciphertext

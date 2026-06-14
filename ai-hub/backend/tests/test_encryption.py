"""加密工具单元测试"""
import pytest
from app.common.utils.encryption import (
    encrypt_config_value,
    decrypt_config_value,
    is_sensitive_key,
)


class TestIsSensitiveKey:
    def test_api_key_matches(self):
        assert is_sensitive_key("provider_api_key") is True

    def test_secret_matches(self):
        assert is_sensitive_key("jwt_secret") is True

    def test_regular_key_does_not_match(self):
        assert is_sensitive_key("temperature") is False
        assert is_sensitive_key("model_name") is False
        assert is_sensitive_key("max_tokens") is False


class TestEncryptDecrypt:
    def test_roundtrip(self):
        original = "sk-test-api-key-12345"
        encrypted = encrypt_config_value(original)
        # 密文不应等于明文
        assert encrypted != original
        # 解密应还原
        decrypted = decrypt_config_value(encrypted)
        assert decrypted == original

    def test_empty_string(self):
        assert encrypt_config_value("") == ""
        assert decrypt_config_value("") == ""

    def test_compat_with_plaintext(self):
        # 未加密的旧数据应能直接返回
        assert decrypt_config_value("sk-plaintext") == "sk-plaintext"

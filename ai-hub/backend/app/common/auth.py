"""JWT 认证工具模块"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

import jwt
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import get_settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer Token 安全方案
security = HTTPBearer(auto_error=False)

# JWT 配置
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小时


def _get_jwt_secret() -> str:
    """从配置读取 JWT 密钥，确保生产环境已修改"""
    settings = get_settings()
    secret = settings.jwt_secret_key
    if secret == "CHANGE_ME":
        import logging
        logging.getLogger(__name__).warning(
            "JWT_SECRET_KEY 使用默认值，生产环境请通过 .env 文件配置！"
        )
        return "ai-hub-secret-key-change-in-production"
    return secret


def hash_password(password: str) -> str:
    """对密码进行哈希处理"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, username: str, role: str = "user") -> str:
    """创建 JWT access token"""
    secret = _get_jwt_secret()
    expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": user_id,
        "username": username,
        "role": role,
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(to_encode, secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """解码 JWT token"""
    try:
        secret = _get_jwt_secret()
        payload = jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
        return payload
    except PyJWTError:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """获取当前登录用户（依赖注入）"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
        )
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
        )
    return {
        "user_id": payload.get("sub"),
        "username": payload.get("username"),
        "role": payload.get("role", "user"),
    }


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    """可选地获取当前用户（不强制认证）"""
    if credentials is None:
        return None
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        return None
    return {
        "user_id": payload.get("sub"),
        "username": payload.get("username"),
        "role": payload.get("role", "user"),
    }

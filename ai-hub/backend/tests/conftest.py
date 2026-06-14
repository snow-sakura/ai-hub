"""pytest 共享测试配置

提供测试用的数据库 fixture 和通用工具函数。
测试数据库使用内存 MySQL 或独立的 SQLite 文件以避免污染开发数据。
"""

import pytest


@pytest.fixture(scope="session")
def anyio_backend():
    """为 async 测试提供 asyncio 后端"""
    return "asyncio"


@pytest.fixture(scope="function")
def sample_case_data() -> dict:
    """通用的测试用例数据"""
    return {
        "title": "用户登录-正常流程验证",
        "priority": "P1",
        "case_type": "functional",
        "preconditions": "用户已注册账号",
        "steps": "1. 打开登录页面\n2. 输入正确用户名密码\n3. 点击登录按钮",
        "expected_results": "成功跳转到首页，显示用户昵称",
        "status": "active",
    }


@pytest.fixture(scope="function")
def sample_project_data() -> dict:
    """通用的项目数据"""
    return {
        "name": "测试项目",
        "description": "用于单元测试的示例项目",
        "status": "active",
    }

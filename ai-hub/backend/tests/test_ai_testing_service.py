"""AI Testing 服务层单元测试（使用 Mock 避免真实数据库依赖）"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.modules.ai_testing.service import TestingService


@pytest.fixture
def mock_db():
    """Mock 数据库连接"""
    return MagicMock()


@pytest.fixture
def service(mock_db):
    """测试用的 TestingService 实例（repo 被 mock 替换）"""
    svc = TestingService(mock_db)
    svc.repo = AsyncMock()
    return svc


class TestProjectService:
    async def test_list_projects_returns_paginated(self, service):
        service.repo.list_projects.return_value = ([{"id": "1", "name": "P1"}], 1)
        result = await service.list_projects(page=1, page_size=20)
        assert result["total"] == 1
        assert len(result["items"]) == 1
        assert result["items"][0]["name"] == "P1"

    async def test_get_project_raises_on_missing(self, service):
        service.repo.get_project.return_value = None
        with pytest.raises(Exception):
            await service.get_project("nonexistent")


class TestCaseService:
    async def test_create_case(self, service):
        service.repo.create_case.return_value = "case-123"
        service.repo.get_case.return_value = {
            "id": "case-123", "title": "Test", "status": "active",
        }
        result = await service.create_case(title="Test", priority="P1")
        assert result["title"] == "Test"
        service.repo.create_case.assert_awaited_once()

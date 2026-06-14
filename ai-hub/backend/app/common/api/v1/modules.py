"""首页模块配置 API — 向前端返回可用模块列表"""

from fastapi import APIRouter

router = APIRouter()

MODULES = [
    {
        "id": "test-mgmt",
        "icon": "📋",
        "iconBg": "rgba(212,116,92,0.12)",
        "iconColor": "var(--danger)",
        "name": "AI 测试管理",
        "desc": "项目 · 版本 · 成员 · 数据看板",
        "count": "4 个功能模块",
        "route": "/ai-testing",
        "enabled": True,
    },
    {
        "id": "chat",
        "icon": "💬",
        "iconBg": "rgba(91,141,239,0.12)",
        "iconColor": "#5B8DEF",
        "name": "AI聊天室",
        "desc": "AI 对话 · 智能问答 · 场景交互",
        "count": "1 个功能模块",
        "route": "/chat",
        "enabled": True,
    },
    {
        "id": "api-test",
        "icon": "🔌",
        "iconBg": "rgba(198,123,92,0.12)",
        "iconColor": "#C67B5C",
        "name": "接口测试",
        "desc": "接口管理 · 自动化 · Mock · 环境 · 定时任务",
        "count": "8 个功能模块",
        "route": "/api-testing/overview",
        "enabled": True,
    },
    {
        "id": "ui-auto",
        "icon": "🖥️",
        "iconBg": "rgba(123,168,125,0.12)",
        "iconColor": "var(--success)",
        "name": "UI 自动化",
        "desc": "元素管理 · 用例录制 · 套件 · 报告 · 设备",
        "count": "10 个功能模块",
        "route": "/ui-automation",
        "enabled": True,
    },
    {
        "id": "app-auto",
        "icon": "📱",
        "iconBg": "rgba(212,165,116,0.12)",
        "iconColor": "#B8860B",
        "name": "APP 自动化",
        "desc": "用例编排 · 设备管理 · 多平台 · 定时回归",
        "count": "10 个功能模块",
        "route": "/app-automation",
        "enabled": True,
    },
    {
        "id": "knowledge",
        "icon": "📚",
        "iconBg": "rgba(180,150,120,0.12)",
        "iconColor": "var(--text-muted)",
        "name": "知识管理",
        "desc": "知识库 · 技术文档 · 测试资料",
        "count": "1 个功能模块",
        "route": "/knowledge",
        "enabled": True,
    },
    {
        "id": "comfort",
        "icon": "🎭",
        "iconBg": "rgba(212,116,92,0.12)",
        "iconColor": "var(--danger)",
        "name": "哄哄模拟器",
        "desc": "AI 情景模拟 · 沟通技巧 · 安抚练习",
        "count": "1 个功能模块",
        "route": "/comfort",
        "enabled": True,
    },
    {
        "id": "system",
        "icon": "⚙️",
        "iconBg": "rgba(180,150,120,0.12)",
        "iconColor": "var(--text-muted)",
        "name": "系统管理",
        "desc": "配置中心 · 用户 · 权限 · 日志 · 集成",
        "count": "6 个功能模块",
        "route": "/system",
        "enabled": True,
    },
]


@router.get("")
async def list_modules():
    """返回可用模块卡片配置列表"""
    return {"data": MODULES}

"""工具注册表 - 汇总所有内置工具"""

from langchain_core.tools import BaseTool

from app.agent.tools.web_search import web_search
from app.agent.tools.file_ops import file_read, file_write
from app.agent.tools.web_scraper import web_scraper
from app.agent.tools.downloader import download_resource
from app.agent.tools.terminal import terminal_exec
from app.agent.tools.pdf_generator import pdf_generate
from app.agent.tools.image_search import image_search


TOOL_REGISTRY: dict[str, BaseTool] = {
  "web_search": web_search,
  "file_read": file_read,
  "file_write": file_write,
  "web_scraper": web_scraper,
  "download_resource": download_resource,
  "terminal_exec": terminal_exec,
  "pdf_generate": pdf_generate,
  "image_search": image_search,
}


def get_all_tools() -> list[BaseTool]:
  """获取所有可用工具"""
  return list(TOOL_REGISTRY.values())


def get_tool_info_list() -> list[dict[str, str]]:
  """获取工具信息列表（供前端展示）"""
  info_map = {
    "web_search": {"display_name": "联网搜索", "icon": "search", "category": "search"},
    "file_read": {"display_name": "读取文件", "icon": "file-text", "category": "file"},
    "file_write": {"display_name": "写入文件", "icon": "file-edit", "category": "file"},
    "web_scraper": {"display_name": "网页抓取", "icon": "globe", "category": "web"},
    "download_resource": {"display_name": "资源下载", "icon": "download", "category": "web"},
    "terminal_exec": {"display_name": "终端执行", "icon": "terminal", "category": "system"},
    "pdf_generate": {"display_name": "PDF 生成", "icon": "file-pdf", "category": "file"},
    "image_search": {"display_name": "图片搜索", "icon": "image", "category": "search"},
  }
  result = []
  for name, tool_obj in TOOL_REGISTRY.items():
    info = info_map.get(name, {})
    result.append({
      "name": name,
      "display_name": info.get("display_name", name),
      "description": tool_obj.description or "",
      "icon": info.get("icon", "tool"),
      "category": info.get("category", "general"),
    })
  return result

"""图片搜索工具 - Pexels/Unsplash"""

import httpx
from langchain_core.tools import tool
from app.config import get_settings


@tool
def image_search(query: str, count: int = 3) -> str:
  """从 Pexels 或 Unsplash 搜索高质量图片。

  Args:
    query: 搜索关键词（英文效果更好）
    count: 返回图片数量，默认 3 张
  """
  settings = get_settings()

  if settings.pexels_api_key:
    return _search_pexels(query, count, settings.pexels_api_key)
  elif settings.unsplash_access_key:
    return _search_unsplash(query, count, settings.unsplash_access_key)
  else:
    return "未配置图片搜索 API 密钥。请在 .env 中设置 PEXELS_API_KEY 或 UNSPLASH_ACCESS_KEY。"


def _search_pexels(query: str, count: int, api_key: str) -> str:
  """Pexels 图片搜索"""
  try:
    with httpx.Client(timeout=15.0) as client:
      resp = client.get(
        "https://api.pexels.com/v1/search",
        params={"query": query, "per_page": count},
        headers={"Authorization": api_key},
      )
      resp.raise_for_status()
      data = resp.json()

    results = []
    for photo in data.get("photos", [])[:count]:
      results.append(
        f"![{photo.get('alt', query)}]({photo['src']['large']})\n"
        f"*摄影师: {photo.get('photographer', 'Unknown')}* | "
        f"[原图链接]({photo.get('url', '')})"
      )
    return "\n\n".join(results) if results else f"未找到与 '{query}' 相关的图片。"
  except Exception as e:
    return f"Pexels 搜索失败: {str(e)}"


def _search_unsplash(query: str, count: int, access_key: str) -> str:
  """Unsplash 图片搜索"""
  try:
    with httpx.Client(timeout=15.0) as client:
      resp = client.get(
        "https://api.unsplash.com/search/photos",
        params={"query": query, "per_page": count},
        headers={"Authorization": f"Client-ID {access_key}"},
      )
      resp.raise_for_status()
      data = resp.json()

    results = []
    for photo in data.get("results", [])[:count]:
      results.append(
        f"![{photo.get('alt_description', query)}]({photo['urls']['regular']})\n"
        f"*摄影师: {photo['user']['name']}* | "
        f"[原图链接]({photo.get('links', {}).get('html', '')})"
      )
    return "\n\n".join(results) if results else f"未找到与 '{query}' 相关的图片。"
  except Exception as e:
    return f"Unsplash 搜索失败: {str(e)}"

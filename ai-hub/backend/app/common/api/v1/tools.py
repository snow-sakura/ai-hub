"""工具相关 API 端点"""

import httpx
from fastapi import APIRouter, Query, Depends

from app.common.api.schemas.common import ApiResponse
from app.common.tools import get_tool_info_list
from app.config import get_settings

router = APIRouter()


@router.get("")
async def list_tools() -> ApiResponse[list[dict[str, str]]]:
  """获取工具列表"""
  tools = get_tool_info_list()
  return ApiResponse(data=tools)


@router.get("/image-search")
async def search_images(
  query: str = Query(..., description="搜索关键词"),
  count: int = Query(3, description="返回数量"),
) -> ApiResponse[list[dict[str, str]]]:
  """搜索图片（Pexels/Unsplash）"""
  settings = get_settings()
  results = []

  if settings.pexels_api_key:
    try:
      async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
          "https://api.pexels.com/v1/search",
          params={"query": query, "per_page": count},
          headers={"Authorization": settings.pexels_api_key},
        )
        resp.raise_for_status()
        data = resp.json()
      for photo in data.get("photos", [])[:count]:
        results.append({
          "url": photo["src"]["large"],
          "thumb": photo["src"]["medium"],
          "photographer": photo.get("photographer", ""),
          "source": "Pexels",
        })
    except Exception:
      pass

  if not results and settings.unsplash_access_key:
    try:
      async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
          "https://api.unsplash.com/search/photos",
          params={"query": query, "per_page": count},
          headers={"Authorization": f"Client-ID {settings.unsplash_access_key}"},
        )
        resp.raise_for_status()
        data = resp.json()
      for photo in data.get("results", [])[:count]:
        results.append({
          "url": photo["urls"]["regular"],
          "thumb": photo["urls"]["small"],
          "photographer": photo["user"]["name"],
          "source": "Unsplash",
        })
    except Exception:
      pass

  return ApiResponse(data=results)

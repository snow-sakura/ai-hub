"""联网搜索工具"""

import httpx
from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
  """在互联网上搜索信息，返回搜索结果摘要。适用于查找最新资讯、技术文档、事实核查等。

  Args:
    query: 搜索关键词
  """
  try:
    headers = {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
      resp = client.get(
        "https://html.duckduckgo.com/html/",
        params={"q": query},
        headers=headers,
      )
      resp.raise_for_status()
      text = resp.text

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(text, "html.parser")
    results = []
    for item in soup.select(".result__body")[:5]:
      title = item.select_one(".result__title")
      snippet = item.select_one(".result__snippet")
      if title and snippet:
        results.append(
          f"**{title.get_text(strip=True)}**\n{snippet.get_text(strip=True)}"
        )
    if results:
      return "\n\n".join(results)
    return f"搜索 '{query}' 未找到相关结果。"
  except Exception as e:
    return f"搜索失败: {str(e)}"

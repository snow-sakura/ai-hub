"""联网搜索工具"""

import httpx
from urllib.parse import urljoin
from langchain_core.tools import tool
from app.common.utils.url_validator import is_safe_url


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
    # SSRF 防护：禁用自动重定向，手动校验每跳
    with httpx.Client(timeout=15.0, follow_redirects=False) as client:
      resp = client.get(
        "https://html.duckduckgo.com/html/",
        params={"q": query},
        headers=headers,
      )
      max_redirects = 5
      for _ in range(max_redirects):
        if resp.is_redirect:
          next_url = resp.headers.get("Location", "")
          if not next_url:
            return "错误：搜索服务返回空重定向"
          next_url = urljoin(str(resp.url), next_url)
          if not is_safe_url(next_url):
            return "错误：重定向到不安全的地址"
          resp = client.get(next_url, headers=headers)
        else:
          break
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

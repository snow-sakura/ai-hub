"""网页抓取工具"""

import httpx
from langchain_core.tools import tool


@tool
def web_scraper(url: str) -> str:
  """抓取指定网页的内容，返回页面主要文本。

  Args:
    url: 要抓取的网页 URL
  """
  try:
    headers = {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
      resp = client.get(url, headers=headers)
      resp.raise_for_status()

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
      tag.decompose()

    title = soup.title.string if soup.title else "无标题"
    text = soup.get_text(separator="\n", strip=True)

    if len(text) > 8000:
      text = text[:8000] + "\n\n... (内容已截断)"

    return f"**页面标题**: {title}\n\n{text}"
  except Exception as e:
    return f"网页抓取失败: {str(e)}"

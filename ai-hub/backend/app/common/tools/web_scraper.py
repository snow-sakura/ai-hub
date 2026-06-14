"""网页抓取工具（含 SSRF 防护）"""

import httpx
from langchain_core.tools import tool
from urllib.parse import urljoin
from app.common.utils.url_validator import is_safe_url


@tool
def web_scraper(url: str) -> str:
  """抓取指定网页的内容，返回页面主要文本。

  Args:
    url: 要抓取的网页 URL
  """
  try:
    # SSRF 防护：校验 URL 是否指向内网
    if not is_safe_url(url):
      return "错误：不允许访问内网地址或不安全的 URL"
    headers = {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    # 禁用自动重定向，手动逐跳验证防止 SSRF 重定向绕过
    with httpx.Client(timeout=20.0, follow_redirects=False) as client:
      resp = client.get(url, headers=headers)
      # 手动处理重定向，每跳都做 SSRF 校验
      max_redirects = 5
      for _ in range(max_redirects):
        if resp.is_redirect:
          next_url = resp.headers.get("Location", "")
          if not next_url:
            return "错误：空重定向地址"
          # 解析相对 URL
          next_url = urljoin(str(resp.url), next_url)
          if not is_safe_url(next_url):
            return "错误：重定向到不安全的地址"
          resp = client.get(next_url, headers=headers)
        else:
          break
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

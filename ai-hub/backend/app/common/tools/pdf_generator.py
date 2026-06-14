"""PDF 生成工具"""

from pathlib import Path
from langchain_core.tools import tool
from app.config import get_settings


@tool
def pdf_generate(filename: str, title: str, content: str) -> str:
  """生成 PDF 文档。

  Args:
    filename: PDF 文件名（不含路径）
    title: 文档标题
    content: 文档正文内容（支持简单的段落文本）
  """
  settings = get_settings()
  workspace = Path(settings.workspace_dir).resolve()
  workspace.mkdir(parents=True, exist_ok=True)

  if not filename.endswith(".pdf"):
    filename += ".pdf"
  target = workspace / filename

  try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    c = canvas.Canvas(str(target), pagesize=A4)
    width, height = A4

    try:
      pdfmetrics.registerFont(TTFont("SimHei", "/System/Library/Fonts/PingFang.ttc", subfontIndex=0))
      font_name = "SimHei"
    except Exception:
      font_name = "Helvetica"

    c.setFont(font_name, 20)
    c.drawString(30 * mm, height - 30 * mm, title)

    c.setFont(font_name, 11)
    y = height - 50 * mm
    lines = content.split("\n")
    for line in lines:
      if y < 30 * mm:
        c.showPage()
        c.setFont(font_name, 11)
        y = height - 30 * mm

      while len(line) > 70:
        c.drawString(25 * mm, y, line[:70])
        line = line[70:]
        y -= 5 * mm
        if y < 30 * mm:
          c.showPage()
          c.setFont(font_name, 11)
          y = height - 30 * mm

      c.drawString(25 * mm, y, line)
      y -= 6 * mm

    c.save()
    return f"PDF 已生成: {filename}"
  except Exception as e:
    return f"PDF 生成失败: {str(e)}"

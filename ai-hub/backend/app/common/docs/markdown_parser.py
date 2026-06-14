"""Markdown 测试用例解析工具（消除 service.py 与 excel_handler.py 的重复逻辑）"""

import re
from typing import Any

_VALID_PRIORITIES = {"P0", "P1", "P2", "P3"}
_VALID_TYPES = {"functional", "performance", "security", "compatibility", "ui", "api"}


def _extract_field(block: str, pattern: str) -> str:
    """从 block 中提取正则匹配的第一个分组"""
    m = re.search(pattern, block, re.MULTILINE)
    return m.group(1).strip() if m else ""


def parse_markdown_to_cases(content: str, *, dedup: bool = True) -> list[dict[str, Any]]:
    """从 LLM 输出的 Markdown 中解析测试用例

    Args:
        content: Markdown 文本
        dedup: 是否按标题去重

    Returns:
        解析后的用例列表
    """
    cases: list[dict[str, Any]] = []
    seen_titles: set[str] = set()
    blocks = re.split(r'\n-{3,}\n', content)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        title = _extract_field(block, r'\*\*标题\*\*\s*:\s*(.+)')
        if not title:
            continue
        if dedup and title in seen_titles:
            continue
        seen_titles.add(title)

        priority_raw = _extract_field(block, r'\*\*优先级\*\*\s*:\s*(.+)')
        priority = priority_raw.upper() if priority_raw.upper() in _VALID_PRIORITIES else "P2"

        case_type = _extract_field(block, r'\*\*用例类型\*\*\s*:\s*(.+)') or "functional"
        if case_type not in _VALID_TYPES:
            case_type = "functional"

        preconditions = _extract_field(block, r'\*\*前置条件\*\*\s*:\s*(.*?)(?=\n\*\*)')
        steps = _extract_field(block, r'\*\*测试步骤\*\*\s*:\s*(.*?)(?=\n\*\*)')
        expected_results = _extract_field(block, r'\*\*预期结果\*\*\s*:\s*(.*?)(?=\n\*\*)')

        # 多行字段兜底（跨行匹配）
        if not steps:
            sm = re.search(r'\*\*测试步骤\*\*\s*:\s*(.+?)(?=\n\*\*|$)', block, re.DOTALL)
            steps = sm.group(1).strip() if sm else ""
        if not expected_results:
            em = re.search(r'\*\*预期结果\*\*\s*:\s*(.+?)(?=\n\*\*|$)', block, re.DOTALL)
            expected_results = em.group(1).strip() if em else ""

        tags_raw = _extract_field(block, r'\*\*标签\*\*\s*:\s*(.+)')
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else ["ai-generated"]

        cases.append({
            "title": title,
            "priority": priority,
            "case_type": case_type,
            "preconditions": preconditions,
            "steps": steps,
            "expected_results": expected_results,
            "tags": tags,
            "status": "pending",
        })

    return cases

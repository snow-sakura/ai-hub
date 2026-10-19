"""节点公共工具 — 流式 LLM 调用收集器

说明：LangGraph 的 astream_events 只有在底层真正走 _stream 路径时
才会产出 on_chat_model_stream 事件。节点若使用 chain.ainvoke，
token 流不会外泄到 SSE。统一改用 chain.astream 累积收集，
既保证节点返回完整文本，又让前端获得逐 token 流式显示。
"""

from typing import Any


async def astream_collect(chain: Any, inputs: dict) -> str:
    """以流式方式执行 chain，累积并返回完整文本内容"""
    pieces: list[str] = []
    async for chunk in chain.astream(inputs):
        content = getattr(chunk, "content", "")
        if isinstance(content, str) and content:
            pieces.append(content)
    return "".join(pieces)

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.clients.xuangu import XuanguClient
from src.services.normalization import normalize_screening_result


def register_screening_tools(server: FastMCP, xuangu_client: XuanguClient) -> None:
    @server.tool(
        name="screen_stocks",
        description=(
            "Screen Chinese stocks with Eastmoney XuanGu using a natural-language or "
            "condition-style query such as 'MACD金叉 且 市盈率 小于 30'."
        ),
    )
    async def screen_stocks(query: str, page_no: int = 1, page_size: int = 20) -> dict:
        payload = await xuangu_client.screen_stocks(query=query, page_no=page_no, page_size=page_size)
        return normalize_screening_result(
            query=query,
            payload=payload,
            page_no=page_no,
            page_size=page_size,
        ).model_dump()

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.clients.push2 import Push2Client
from src.services.normalization import normalize_money_flow


def register_quote_tools(server: FastMCP, push2_client: Push2Client) -> None:
    @server.tool(
        name="get_quote",
        description="Get real-time quote data for a Chinese stock by 6-digit code.",
    )
    async def get_quote(stock_code: str) -> dict:
        quote = await push2_client.get_quote(stock_code)
        return quote.model_dump()

    @server.tool(
        name="get_money_flow",
        description="Get recent money flow rows for a Chinese stock by 6-digit code.",
    )
    async def get_money_flow(stock_code: str, limit: int = 5) -> dict:
        payload = await push2_client.get_money_flow(stock_code, limit=limit)
        return normalize_money_flow(
            identifier=(await push2_client.get_quote(stock_code)).identifier,
            payload=payload,
        ).model_dump()

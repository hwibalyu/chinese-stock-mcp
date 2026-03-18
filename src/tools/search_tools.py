from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.clients.search import SearchClient
from src.clients.xuangu import XuanguClient
from src.services.normalization import normalize_screening_result
from src.services.identifiers import build_identifier


SCREENING_HINTS = (
    "且",
    "并且",
    "大于",
    "小于",
    "高于",
    "低于",
    ">",
    "<",
    "=",
    "macd",
    "rsi",
    "kdj",
    "均线",
    "市盈率",
    "roe",
    "净利润",
    "营收",
    "换手率",
    "成交量",
    "主力资金",
    "筛选",
    "选股",
    "剔除",
    "不要",
)


def _market_from_search_result(item: dict) -> str | None:
    market_name = str(item.get("SecurityTypeName") or "")
    market_type = str(item.get("MarketType") or "")
    classify = str(item.get("Classify") or "")
    if "京" in market_name or market_type == "_TB" or classify == "NEEQ":
        return "BJ"
    if "沪" in market_name:
        return "SH"
    if "深" in market_name:
        return "SZ"
    return None


def _looks_like_screening_query(query: str) -> bool:
    normalized = query.strip().lower()
    if not normalized:
        return False
    if any(token in normalized for token in SCREENING_HINTS):
        return True
    return len(normalized.split()) >= 3


def register_search_tools(
    server: FastMCP, search_client: SearchClient, xuangu_client: XuanguClient
) -> None:
    @server.tool(
        name="search_stock",
        description=(
            "Search a Chinese stock by code, Chinese name, or ticker-like query. "
            "If the query looks like a screening condition, this tool can fall back to "
            "Eastmoney XuanGu screening results."
        ),
    )
    async def search_stock(query: str, count: int = 10) -> dict:
        payload = await search_client.search_stock(query=query, count=count)
        results = payload.get("QuotationCodeTable", {}).get("Data", [])
        items = []
        for item in results:
            code = item.get("Code")
            if not code or not code.isdigit() or len(code) != 6:
                continue
            identifier = build_identifier(
                code,
                short_name=item.get("Name"),
                company_name=item.get("Name"),
                market=_market_from_search_result(item),
                source="searchapi",
            )
            items.append(
                {
                    "identifier": identifier.model_dump(),
                    "quote_id": item.get("QuoteID"),
                    "name": item.get("Name"),
                    "security_type_name": item.get("SecurityTypeName"),
                    "market_type": item.get("MktNum"),
                }
            )
        if items or not _looks_like_screening_query(query):
            return {"query": query, "count": count, "items": items, "match_mode": "searchapi"}

        screening_payload = await xuangu_client.screen_stocks(
            query=query,
            page_no=1,
            page_size=max(10, min(count, 50)),
        )
        screening = normalize_screening_result(
            query=query,
            payload=screening_payload,
            page_no=1,
            page_size=max(10, min(count, 50)),
        )
        fallback_items = []
        for item in screening.items[:count]:
            fallback_items.append(
                {
                    "identifier": item.identifier.model_dump(),
                    "quote_id": item.identifier.secid,
                    "name": item.name,
                    "security_type_name": item.market_short_name,
                    "market_type": None,
                    "screening_metrics": item.metrics,
                }
            )
        return {
            "query": query,
            "count": count,
            "items": fallback_items,
            "match_mode": "xuangu_screening_fallback",
            "screening_total": screening.total,
            "screening_columns": [column.model_dump() for column in screening.columns],
            "xc_id": screening.xc_id,
        }

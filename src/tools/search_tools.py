from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.clients.search import SearchClient
from src.services.identifiers import build_identifier


def register_search_tools(server: FastMCP, search_client: SearchClient) -> None:
    @server.tool(
        name="search_stock",
        description="Search a Chinese stock by code, Chinese name, or ticker-like query.",
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
        return {"query": query, "count": count, "items": items}

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.clients.notices import NoticeClient
from src.services.notice_reader import NoticeReader


def register_qa_tools(
    server: FastMCP, notice_client: NoticeClient, notice_reader: NoticeReader
) -> None:
    @server.tool(
        name="analyze_latest_quarterly_report",
        description=(
            "Find the latest quarterly notice for a stock and return compact facts and evidence."
        ),
    )
    async def analyze_latest_quarterly_report(stock_code: str) -> dict:
        quarterly = None
        checked_count = 0
        for page_index in range(1, 6):
            notices = await notice_client.get_notices(
                stock_code=stock_code,
                page_index=page_index,
                page_size=50,
            )
            checked_count += len(notices.items)
            quarterly = next(
                (
                    item
                    for item in notices.items
                    if "季度报告" in item.title or "半年度报告" in item.title
                ),
                None,
            )
            if quarterly is not None:
                break
        if quarterly is None:
            return {
                "ok": False,
                "reason": "No quarterly or half-year notice found in the recent notice set.",
                "checked_count": checked_count,
            }
        facts = await notice_reader.extract_facts(quarterly.art_code)
        return {
            "ok": True,
            "checked_count": checked_count,
            "selected_notice": quarterly.model_dump(),
            "facts": facts.model_dump(),
        }

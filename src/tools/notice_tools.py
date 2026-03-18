from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.clients.notices import NoticeClient
from src.services.notice_reader import NoticeReader


def register_notice_tools(
    server: FastMCP, notice_client: NoticeClient, notice_reader: NoticeReader
) -> None:
    @server.tool(
        name="get_notices",
        description="Get recent notices for a Chinese stock by 6-digit code.",
    )
    async def get_notices(
        stock_code: str, page_index: int = 1, page_size: int = 10, ann_type: str = "A"
    ) -> dict:
        result = await notice_client.get_notices(
            stock_code=stock_code,
            page_index=page_index,
            page_size=page_size,
            ann_type=ann_type,
        )
        return result.model_dump()

    @server.tool(
        name="get_notice_text_page",
        description="Get one text page of a notice by Eastmoney art_code.",
    )
    async def get_notice_text_page(art_code: str, page_index: int = 1) -> dict:
        result = await notice_client.get_notice_text_page(art_code=art_code, page_index=page_index)
        return result.model_dump()

    @server.tool(
        name="get_notice_text_full",
        description="Get the full text of a notice by combining notice text pages.",
    )
    async def get_notice_text_full(art_code: str, max_pages: int | None = None) -> dict:
        return await notice_reader.get_text_full(art_code=art_code, max_pages=max_pages)

    @server.tool(
        name="extract_notice_facts",
        description=(
            "Extract compact facts from a notice text page. Best for quarterly and half-year reports."
        ),
    )
    async def extract_notice_facts(art_code: str) -> dict:
        result = await notice_reader.extract_facts(art_code=art_code)
        return result.model_dump()

from __future__ import annotations

import atexit
import os

from mcp.server.fastmcp import FastMCP

from src.clients.dataapi import DataApiClient
from src.clients.datacenter import DatacenterClient
from src.clients.notices import NoticeClient
from src.clients.push2 import Push2Client
from src.clients.search import SearchClient
from src.services.notice_reader import NoticeReader
from src.settings import get_settings
from src.tools.f10_tools import register_f10_tools
from src.tools.notice_tools import register_notice_tools
from src.tools.qa_tools import register_qa_tools
from src.tools.quote_tools import register_quote_tools
from src.tools.search_tools import register_search_tools

settings = get_settings()

server = FastMCP(
    name="Chinese Stock MCP",
    instructions=(
        "Use these tools to answer questions about Chinese stocks with compact, evidence-backed data. "
        "Prefer notice text and structured facts over large raw payloads."
    ),
)

push2_client = Push2Client()
notice_client = NoticeClient()
datacenter_client = DatacenterClient()
search_client = SearchClient()
dataapi_client = DataApiClient()
notice_reader = NoticeReader(notice_client)

register_search_tools(server, search_client)
register_quote_tools(server, push2_client)
register_notice_tools(server, notice_client, notice_reader)
register_f10_tools(server, datacenter_client, dataapi_client)
register_qa_tools(server, notice_client, notice_reader)


async def _shutdown() -> None:
    await push2_client.close()
    await notice_client.close()
    await datacenter_client.close()
    await search_client.close()
    await dataapi_client.close()


def _close_clients() -> None:
    try:
        import anyio

        anyio.run(_shutdown)
    except Exception:
        pass


atexit.register(_close_clients)


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    server.run(transport=transport)

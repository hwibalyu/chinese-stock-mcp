from __future__ import annotations

from src.clients.eastmoney_base import EastmoneyBaseClient
from src.schemas.notice import NoticeList, NoticeTextPage
from src.services.identifiers import build_identifier
from src.services.normalization import normalize_notice_list, normalize_notice_text_page


class NoticeClient(EastmoneyBaseClient):
    LIST_URL = "https://np-anotice-pc.eastmoney.com/api/security/ann"
    CONTENT_URL = "https://np-cnotice-stock.eastmoney.com/api/content/ann"

    async def get_notices(
        self, stock_code: str, page_index: int = 1, page_size: int = 10, ann_type: str = "A"
    ) -> NoticeList:
        identifier = build_identifier(stock_code)
        payload = await self.get_json(
            self.LIST_URL,
            params={
                "sr": -1,
                "page_size": page_size,
                "page_index": page_index,
                "ann_type": ann_type,
                "stock_list": identifier.stock_code,
            },
        )
        return normalize_notice_list(identifier, payload["data"], page_index, page_size)

    async def get_notice_text_page(self, art_code: str, page_index: int = 1) -> NoticeTextPage:
        payload = await self.get_jsonp(
            self.CONTENT_URL,
            params={
                "art_code": art_code,
                "client_source": "web",
                "page_index": page_index,
            },
        )
        return normalize_notice_text_page(payload, page_index)

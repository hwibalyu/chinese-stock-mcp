from __future__ import annotations

from src.clients.notices import NoticeClient
from src.schemas.notice import NoticeFacts, NoticeTextPage
from src.services.fact_extraction import extract_notice_facts


class NoticeReader:
    def __init__(self, client: NoticeClient):
        self.client = client

    async def get_text_full(self, art_code: str, max_pages: int | None = None) -> dict:
        first_page = await self.client.get_notice_text_page(art_code, page_index=1)
        page_limit = min(first_page.page_size, max_pages or first_page.page_size)
        pages: list[NoticeTextPage] = [first_page]
        for page_index in range(2, page_limit + 1):
            pages.append(await self.client.get_notice_text_page(art_code, page_index=page_index))
        return {
            "art_code": art_code,
            "title": first_page.title,
            "notice_date": first_page.notice_date,
            "page_size": first_page.page_size,
            "pages": [
                {"page_index": page.page_index, "text": page.text}
                for page in pages
            ],
            "combined_text": "\n\n".join(page.text for page in pages).strip(),
            "pdf_url": first_page.pdf_url,
        }

    async def extract_facts(self, art_code: str) -> NoticeFacts:
        first_page = await self.client.get_notice_text_page(art_code, page_index=1)
        return extract_notice_facts(first_page)

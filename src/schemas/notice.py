from __future__ import annotations

from pydantic import BaseModel

from src.schemas.common import StockIdentifier


class NoticeItem(BaseModel):
    art_code: str
    title: str
    notice_date: str
    column_name: str | None = None
    short_name: str | None = None
    stock_code: str
    market_code: str | None = None


class NoticeList(BaseModel):
    identifier: StockIdentifier
    total_hits: int
    page_index: int
    page_size: int
    items: list[NoticeItem]


class NoticeTextPage(BaseModel):
    art_code: str
    page_index: int
    page_size: int
    title: str
    notice_date: str
    text: str
    pdf_url: str | None = None


class NoticeFacts(BaseModel):
    art_code: str
    title: str
    notice_date: str
    report_period: str | None = None
    report_type: str | None = None
    facts: dict[str, float | str | None]
    evidence: list[str]

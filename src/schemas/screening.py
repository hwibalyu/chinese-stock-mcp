from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from src.schemas.common import StockIdentifier


class ScreeningColumn(BaseModel):
    key: str
    title: str
    unit: str | None = None
    date_msg: str | None = None
    sortable: bool = False
    sort_way: str | None = None
    user_need: int | None = None


class ScreeningItem(BaseModel):
    identifier: StockIdentifier
    name: str | None = None
    market_short_name: str | None = None
    last_price: float | None = None
    change_percent: float | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)


class ScreeningResult(BaseModel):
    query: str
    total: int
    page_no: int
    page_size: int
    columns: list[ScreeningColumn]
    items: list[ScreeningItem]
    xc_id: str | None = None
    trace_id: str | None = None

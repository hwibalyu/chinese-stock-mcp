from __future__ import annotations

from pydantic import BaseModel

from src.schemas.common import StockIdentifier


class QuoteData(BaseModel):
    identifier: StockIdentifier
    last_price: float | None = None
    open_price: float | None = None
    high_price: float | None = None
    low_price: float | None = None
    previous_close: float | None = None
    volume_shares: float | None = None
    turnover_value: float | None = None
    total_market_cap: float | None = None
    float_market_cap: float | None = None
    pe_ratio_dynamic: float | None = None
    pb_ratio: float | None = None
    change_percent: float | None = None
    quote_time: str | None = None

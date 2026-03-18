from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class StockIdentifier(BaseModel):
    stock_code: str = Field(description="Numeric stock code, e.g. 603129")
    market: str = Field(description="SH or SZ")
    secid: str = Field(description="Eastmoney secid, e.g. 1.603129")
    symbol: str = Field(description="Market-qualified symbol, e.g. SH603129")
    short_name: str | None = None
    company_name: str | None = None
    source: str = "inferred"


class Evidence(BaseModel):
    label: str
    value: str


class ToolEnvelope(BaseModel):
    ok: bool = True
    source: str
    data: dict[str, Any]

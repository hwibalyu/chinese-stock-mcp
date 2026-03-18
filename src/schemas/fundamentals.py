from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from src.schemas.common import StockIdentifier


class CompanyOverview(BaseModel):
    identifier: StockIdentifier
    org_name: str | None = None
    listing_date: str | None = None
    found_date: str | None = None
    legal_person: str | None = None
    chairman: str | None = None
    general_manager: str | None = None
    industry: str | None = None
    main_business: str | None = None
    region: str | None = None
    website: str | None = None


class FinancialIndicatorRow(BaseModel):
    report_date: str
    report_type: str | None = None
    eps_basic: float | None = None
    bps: float | None = None
    operating_cashflow_per_share: float | None = None
    total_share: float | None = None
    free_share: float | None = None


class FinancialIndicators(BaseModel):
    identifier: StockIdentifier
    rows: list[FinancialIndicatorRow]


class MoneyFlowRow(BaseModel):
    trade_date: str
    main_net_inflow: float | None = None
    super_large_net_inflow: float | None = None
    large_net_inflow: float | None = None
    mid_net_inflow: float | None = None
    small_net_inflow: float | None = None


class MoneyFlowData(BaseModel):
    identifier: StockIdentifier
    rows: list[MoneyFlowRow]


class TableData(BaseModel):
    identifier: StockIdentifier
    report_name: str
    rows: list[dict[str, Any]]

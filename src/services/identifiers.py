from __future__ import annotations

import re

from src.schemas.common import StockIdentifier


def market_from_code(stock_code: str) -> str:
    if stock_code.startswith("92") or stock_code.startswith(("4", "8")):
        return "BJ"
    if stock_code.startswith(("5", "6", "9")):
        return "SH"
    return "SZ"


def secid_from_code(stock_code: str) -> str:
    market = market_from_code(stock_code)
    prefix = "1" if market == "SH" else "0"
    return f"{prefix}.{stock_code}"


def symbol_from_code(stock_code: str) -> str:
    market = market_from_code(stock_code)
    return f"{market}{stock_code}"


def normalize_stock_code(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) != 6:
        raise ValueError(f"Unsupported stock code format: {raw}")
    return digits


def build_identifier(
    stock_code: str,
    short_name: str | None = None,
    company_name: str | None = None,
    market: str | None = None,
    source: str = "inferred",
) -> StockIdentifier:
    normalized = normalize_stock_code(stock_code)
    resolved_market = market or market_from_code(normalized)
    prefix = "1" if resolved_market == "SH" else "0"
    return StockIdentifier(
        stock_code=normalized,
        market=resolved_market,
        secid=f"{prefix}.{normalized}",
        symbol=f"{resolved_market}{normalized}",
        short_name=short_name,
        company_name=company_name or short_name,
        source=source,
    )

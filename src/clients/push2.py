from __future__ import annotations

from src.clients.eastmoney_base import EastmoneyBaseClient
from src.schemas.quote import QuoteData
from src.services.identifiers import build_identifier


class Push2Client(EastmoneyBaseClient):
    QUOTE_URL = "https://push2.eastmoney.com/api/qt/stock/get"
    MONEY_FLOW_URL = "https://push2.eastmoney.com/api/qt/stock/fflow/kline/get"

    async def get_quote(self, stock_code: str) -> QuoteData:
        identifier = build_identifier(stock_code)
        payload = await self.get_json(
            self.QUOTE_URL,
            params={
                "secid": identifier.secid,
                "invt": 2,
                "fltt": 1,
                "fields": "f57,f58,f43,f44,f45,f46,f47,f48,f116,f117,f167,f168,f170,f171,f152",
            },
        )
        data = payload["data"]

        def scale_price(value: object) -> float | None:
            if value in (None, "-", ""):
                return None
            return round(float(value) / 100, 2)

        def number(value: object) -> float | None:
            if value in (None, "-", ""):
                return None
            return float(value)  # type: ignore[arg-type]

        return QuoteData(
            identifier=build_identifier(
                stock_code,
                short_name=data.get("f58"),
                company_name=data.get("f58"),
                source="push2",
            ),
            last_price=scale_price(data.get("f43")),
            high_price=scale_price(data.get("f44")),
            low_price=scale_price(data.get("f45")),
            open_price=scale_price(data.get("f46")),
            volume_shares=number(data.get("f47")),
            turnover_value=number(data.get("f48")),
            total_market_cap=number(data.get("f116")),
            float_market_cap=number(data.get("f117")),
            pe_ratio_dynamic=number(data.get("f167")),
            pb_ratio=number(data.get("f168")),
            change_percent=number(data.get("f170")),
            previous_close=scale_price(data.get("f60")),
            quote_time=str(data.get("f152")) if data.get("f152") else None,
        )

    async def get_money_flow(self, stock_code: str, limit: int = 5) -> dict:
        identifier = build_identifier(stock_code)
        return await self.get_json(
            self.MONEY_FLOW_URL,
            params={
                "secid": identifier.secid,
                "lmt": limit,
                "klt": 101,
                "fields1": "f1,f2,f3,f7",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63",
            },
        )

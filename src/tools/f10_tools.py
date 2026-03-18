from __future__ import annotations

import asyncio

from mcp.server.fastmcp import FastMCP

from src.clients.dataapi import DataApiClient
from src.clients.datacenter import DatacenterClient
from src.schemas.common import StockIdentifier
from src.services.identifiers import build_identifier
from src.services.normalization import (
    normalize_company_overview,
    normalize_financial_indicators,
    normalize_table_data,
)


def register_f10_tools(
    server: FastMCP, datacenter_client: DatacenterClient, dataapi_client: DataApiClient
) -> None:
    @server.tool(
        name="get_company_overview",
        description="Get company overview data for a Chinese stock by 6-digit code.",
    )
    async def get_company_overview(stock_code: str) -> dict:
        org_payload, basic_payload = await asyncio.gather(
            datacenter_client.get_company_orginfo(stock_code),
            datacenter_client.get_company_basicinfo(stock_code),
        )
        identifier: StockIdentifier = build_identifier(stock_code, source="datacenter")
        return normalize_company_overview(identifier, org_payload, basic_payload).model_dump()

    @server.tool(
        name="get_financial_indicators",
        description="Get recent financial indicator rows for a Chinese stock by 6-digit code.",
    )
    async def get_financial_indicators(stock_code: str, limit: int = 4) -> dict:
        payload = await datacenter_client.get_financial_indicators(stock_code, limit=limit)
        identifier = build_identifier(stock_code, source="datacenter")
        return normalize_financial_indicators(identifier, payload).model_dump()

    async def _table_tool(
        stock_code: str,
        report_name: str,
        fetcher,
        limit: int = 10,
        field_map: dict[str, str] | None = None,
        **kwargs,
    ) -> dict:
        payload = await fetcher(stock_code, limit=limit, **kwargs)
        identifier = build_identifier(stock_code, source="datacenter")
        return normalize_table_data(identifier, report_name, payload, field_map=field_map).model_dump()

    @server.tool(
        name="get_business_analysis",
        description="Get product-level business analysis rows for a Chinese stock.",
    )
    async def get_business_analysis(stock_code: str, limit: int = 10) -> dict:
        return await _table_tool(
            stock_code,
            "RPT_HS_MAINOP_PRODUCT",
            datacenter_client.get_business_analysis,
            limit=limit,
            field_map={
                "REPORT_DATE": "report_date",
                "MAINOP_TYPE": "segment_type",
                "ITEM_NAME": "item_name",
                "MAIN_BUSINESS_INCOME": "revenue",
                "MBI_RATIO": "revenue_ratio_pct",
                "MAIN_BUSINESS_COST": "cost",
                "MBC_RATIO": "cost_ratio_pct",
                "MAIN_BUSINESS_RPOFIT": "gross_profit",
                "MBR_RATIO": "gross_profit_ratio_pct",
                "GROSS_RPOFIT_RATIO": "gross_margin_pct",
            },
        )

    @server.tool(
        name="get_core_themes",
        description="Get core theme and competitive-positioning points for a Chinese stock.",
    )
    async def get_core_themes(stock_code: str, limit: int = 50) -> dict:
        return await _table_tool(
            stock_code,
            "RPT_F10_CORETHEME_CONTENT",
            datacenter_client.get_core_themes,
            limit=limit,
            field_map={
                "KEY_CLASSIF": "theme_group",
                "MAINPOINT": "main_point",
                "MAINPOINT_CONTENT": "content",
                "KEYWORD": "keyword",
            },
        )

    @server.tool(
        name="get_shareholder_research",
        description="Get free-float shareholder research rows for a Chinese stock.",
    )
    async def get_shareholder_research(stock_code: str, limit: int = 10) -> dict:
        return await _table_tool(
            stock_code,
            "RPT_F10_EH_FREEHOLDERS",
            datacenter_client.get_shareholder_research,
            limit=limit,
            field_map={
                "END_DATE": "end_date",
                "HOLDER_NAME": "holder_name",
                "HOLD_NUM": "hold_num",
                "FREE_HOLDNUM_RATIO": "float_ratio_pct",
                "XZCHANGE": "change_vs_prev",
            },
        )

    @server.tool(
        name="get_capital_structure",
        description="Get capital structure and share-class changes for a Chinese stock.",
    )
    async def get_capital_structure(stock_code: str, limit: int = 10) -> dict:
        return await _table_tool(
            stock_code,
            "RPT_F10_EH_EQUITY",
            datacenter_client.get_capital_structure,
            limit=limit,
        )

    @server.tool(
        name="get_industry_analysis",
        description="Get industry-relative valuation and ranking data for a Chinese stock.",
    )
    async def get_industry_analysis(stock_code: str) -> dict:
        payload = await datacenter_client.get_industry_analysis(stock_code)
        identifier = build_identifier(stock_code, source="datacenter")
        return normalize_table_data(
            identifier,
            "RPT_STOCK_INDUSTRY_STA",
            payload,
            field_map={
                "INDUSTRY_NAME": "industry_name",
                "TMC_RANK": "total_market_cap_rank",
                "PE_RATIO": "pe_ratio",
                "PB_RATIO": "pb_ratio",
                "ROE_WEIGHT": "roe_weight",
                "TOTAL_MARKET_CAP": "total_market_cap",
            },
        ).model_dump()

    @server.tool(
        name="get_market_average",
        description="Get market-wide average valuation reference rows.",
    )
    async def get_market_average() -> dict:
        payload = await datacenter_client.get_market_average()
        identifier = build_identifier("000001", source="datacenter")
        return normalize_table_data(identifier, "RPT_STOCK_MARKET_STA", payload).model_dump()

    @server.tool(
        name="get_billboard_trades",
        description="Get recent Dragon Tiger list rows for a Chinese stock.",
    )
    async def get_billboard_trades(stock_code: str, limit: int = 10) -> dict:
        return await _table_tool(
            stock_code,
            "RPT_BILLBOARD_PERFORMANCEHIS",
            datacenter_client.get_billboard_trades,
            limit=limit,
            field_map={
                "TRADE_DATE": "trade_date",
                "EXPLAIN": "explain",
                "CLOSE_PRICE": "close_price",
                "CHANGE_RATE": "change_rate_pct",
                "BILLBOARD_NET_AMT": "net_amount",
            },
        )

    @server.tool(
        name="get_block_trades",
        description="Get recent block trade rows for a Chinese stock.",
    )
    async def get_block_trades(stock_code: str, limit: int = 10) -> dict:
        return await _table_tool(
            stock_code,
            "RPT_DATA_BLOCKTRADE",
            datacenter_client.get_block_trades,
            limit=limit,
            field_map={
                "TRADE_DATE": "trade_date",
                "DEAL_PRICE": "deal_price",
                "PREMIUM_RATIO": "premium_ratio_pct",
                "DEAL_VOLUME": "deal_volume",
                "DEAL_AMT": "deal_amount",
                "BUYER_NAME": "buyer_name",
                "SELLER_NAME": "seller_name",
            },
        )

    @server.tool(
        name="get_margin_trading",
        description="Get recent margin financing and securities lending rows for a Chinese stock.",
    )
    async def get_margin_trading(stock_code: str, limit: int = 10) -> dict:
        return await _table_tool(
            stock_code,
            "RPTA_WEB_RZRQ_GGMX",
            datacenter_client.get_margin_trading,
            limit=limit,
            field_map={
                "DATE": "trade_date",
                "RZYE": "margin_balance",
                "RQYL": "short_balance_volume",
                "RZRQYE": "combined_balance",
                "RZJME": "margin_net_buy",
            },
        )

    @server.tool(
        name="get_institutional_positions",
        description="Get institutional holding detail rows for a Chinese stock.",
    )
    async def get_institutional_positions(
        stock_code: str, report_date: str | None = None, limit: int = 10
    ) -> dict:
        payload = await datacenter_client.get_institutional_positions(
            stock_code,
            report_date=report_date,
            limit=limit,
        )
        identifier = build_identifier(stock_code, source="datacenter")
        return normalize_table_data(
            identifier,
            "RPT_MAINDATA_MAIN_POSITIONDETAILS",
            payload,
            field_map={
                "REPORT_DATE": "report_date",
                "HOLDER_NAME": "holder_name",
                "HOLD_NUM": "hold_num",
                "HOLD_MARKET_CAP": "hold_market_cap",
                "FREE_SHARES_RATIO": "free_shares_ratio_pct",
            },
        ).model_dump()

    @server.tool(
        name="get_lockup_expirations",
        description="Get recent lockup expiration rows for a Chinese stock.",
    )
    async def get_lockup_expirations(stock_code: str, limit: int = 10) -> dict:
        return await _table_tool(
            stock_code,
            "RPT_LIFT_STAGE",
            datacenter_client.get_lockup_expirations,
            limit=limit,
            field_map={
                "FREE_DATE": "free_date",
                "CURRENT_FREE_SHARES": "current_free_shares",
                "ABLE_FREE_SHARES": "able_free_shares",
                "LIFT_MARKET_CAP": "lift_market_cap",
                "FREE_RATIO": "free_ratio_pct",
                "FREE_SHARES_TYPE": "free_shares_type",
            },
        )

    @server.tool(
        name="get_stock_calendar",
        description="Get stock calendar and major-event rows for a Chinese stock.",
    )
    async def get_stock_calendar(stock_code: str, limit: int = 10) -> dict:
        return await _table_tool(
            stock_code,
            "RPT_STOCKCALENDAR",
            datacenter_client.get_stock_calendar,
            limit=limit,
            field_map={
                "NOTICE_DATE": "notice_date",
                "EVENT_TYPE": "event_type",
                "EVENT_NAME": "event_name",
                "CONTENT": "content",
            },
        )

    @server.tool(
        name="get_org_survey",
        description="Get institutional survey rows for a Chinese stock.",
    )
    async def get_org_survey(stock_code: str, limit: int = 10) -> dict:
        return await _table_tool(
            stock_code,
            "RPT_ORG_SURVEY",
            datacenter_client.get_org_survey,
            limit=limit,
            field_map={
                "NOTICE_DATE": "notice_date",
                "RECEPTION_WAY": "reception_way",
                "RECEPTION_PLACE": "reception_place",
                "RECEPTION_OBJECT": "reception_object",
                "CONTENT": "content",
            },
        )

    @server.tool(
        name="get_related_trades",
        description="Get related-party trade rows for a Chinese stock.",
    )
    async def get_related_trades(stock_code: str, limit: int = 10) -> dict:
        return await _table_tool(
            stock_code,
            "RPT_RELATED_TRADE",
            datacenter_client.get_related_trades,
            limit=limit,
            field_map={
                "NOTICE_DATE": "notice_date",
                "RELATED_PARTY": "related_party",
                "TRADE_AMOUNT": "trade_amount",
                "TRADE_CONTENT": "trade_content",
            },
        )

    @server.tool(
        name="get_holder_count_history",
        description="Get shareholder-count history rows for a Chinese stock.",
    )
    async def get_holder_count_history(stock_code: str, limit: int = 10) -> dict:
        return await _table_tool(
            stock_code,
            "RPT_HOLDERNUM_DET",
            datacenter_client.get_holder_count_history,
            limit=limit,
            field_map={
                "END_DATE": "end_date",
                "HOLDER_NUM": "holder_num",
                "PRE_HOLDER_NUM": "prev_holder_num",
                "HOLDER_NUM_CHANGE": "holder_num_change",
                "HOLDER_NUM_RATIO": "holder_num_ratio_pct",
                "AVG_HOLD_NUM": "avg_hold_num",
            },
        )

    @server.tool(
        name="get_general_meetings",
        description="Get general meeting rows for a Chinese stock.",
    )
    async def get_general_meetings(stock_code: str, limit: int = 10) -> dict:
        return await _table_tool(
            stock_code,
            "RPT_GENERALMEETING_DETAIL",
            datacenter_client.get_general_meetings,
            limit=limit,
            field_map={
                "MEETING_TITLE": "meeting_title",
                "START_ADJUST_DATE": "start_date",
                "END_ADJUST_DATE": "end_date",
                "EQUITY_RECORD_DATE": "equity_record_date",
                "NOTICE_DATE": "notice_date",
            },
        )

    @server.tool(
        name="get_share_buybacks",
        description="Get share-buyback rows for a Chinese stock.",
    )
    async def get_share_buybacks(stock_code: str, limit: int = 10) -> dict:
        return await _table_tool(
            stock_code,
            "RPTA_WEB_GETHGLIST_NEW",
            datacenter_client.get_share_buybacks,
            limit=limit,
        )

    @server.tool(
        name="get_wealth_management",
        description="Get entrusted wealth-management rows for a Chinese stock.",
    )
    async def get_wealth_management(stock_code: str, limit: int = 10) -> dict:
        return await _table_tool(
            stock_code,
            "RPTA_WEB_WTLCMX",
            datacenter_client.get_wealth_management,
            limit=limit,
        )

    @server.tool(
        name="get_capital_operations",
        description="Get capital-operations and M&A rows for a Chinese stock.",
    )
    async def get_capital_operations(stock_code: str, limit: int = 10) -> dict:
        return await _table_tool(
            stock_code,
            "RPTA_WEB_BGCZMX",
            datacenter_client.get_capital_operations,
            limit=limit,
        )

    @server.tool(
        name="get_major_contracts",
        description="Get major-contract rows for a Chinese stock.",
    )
    async def get_major_contracts(stock_code: str, limit: int = 10) -> dict:
        return await _table_tool(
            stock_code,
            "RPTA_WEB_ZDHT_LIST",
            datacenter_client.get_major_contracts,
            limit=limit,
        )

    @server.tool(
        name="get_latest_results",
        description="Get recent earnings-result rows for a Chinese stock.",
    )
    async def get_latest_results(stock_code: str, limit: int = 10) -> dict:
        return await _table_tool(
            stock_code,
            "RPT_LICO_FN_CPD",
            datacenter_client.get_latest_results,
            limit=limit,
        )

    @server.tool(
        name="get_mixed_feed",
        description="Get a mixed feed of news, notices, reports, and IR Q&A for a Chinese stock.",
    )
    async def get_mixed_feed(stock_code: str) -> dict:
        identifier = build_identifier(stock_code, source="dataapi")
        payload = await dataapi_client.get_mixed_feed(stock_code)
        return {
            "identifier": identifier.model_dump(),
            "source": "data.eastmoney.com/dataapi/stockdata/zxgg",
            "data": payload,
        }

from __future__ import annotations

from src.clients.eastmoney_base import EastmoneyBaseClient
from src.services.identifiers import build_identifier


class DatacenterClient(EastmoneyBaseClient):
    BASE_URL = "https://datacenter.eastmoney.com/securities/api/data/v1/get"

    async def _get_report(
        self,
        report_name: str,
        *,
        columns: str = "ALL",
        filter_expr: str | None = None,
        sort_columns: str | None = None,
        sort_types: str | None = None,
        page_number: int = 1,
        page_size: int = 10,
        extra_params: dict | None = None,
    ) -> dict:
        params = {
            "reportName": report_name,
            "columns": columns,
            "source": "WEB",
            "client": "WEB",
            "pageNumber": page_number,
            "pageSize": page_size,
        }
        if filter_expr:
            params["filter"] = filter_expr
        if sort_columns:
            params["sortColumns"] = sort_columns
        if sort_types:
            params["sortTypes"] = sort_types
        if extra_params:
            params.update(extra_params)
        return await self.get_json(self.BASE_URL, params=params)

    async def get_company_orginfo(self, stock_code: str) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPT_HSF9_BASIC_ORGINFO",
            columns="HSF9_ORGINFO",
            filter_expr=f'(SECURITY_CODE="{identifier.stock_code}")',
        )

    async def get_company_basicinfo(self, stock_code: str) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPT_F10_ORG_BASICINFO",
            filter_expr=f'(SECURITY_CODE="{identifier.stock_code}")',
        )

    async def get_financial_indicators(self, stock_code: str, limit: int = 4) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPT_PCF10_FINANCEMAINFINADATA",
            columns=(
                "SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,ORG_CODE,"
                "REPORT_DATE,REPORT_TYPE,EPSJB,BPS,MGZBGJ,MGJYXJJE,TOTAL_SHARE,FREE_SHARE"
            ),
            filter_expr=f'(SECURITY_CODE="{identifier.stock_code}")',
            sort_columns="REPORT_DATE",
            sort_types="-1",
            page_size=limit,
        )

    async def get_business_analysis(self, stock_code: str, limit: int = 10) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPT_HS_MAINOP_PRODUCT",
            filter_expr=f'(SECURITY_CODE="{identifier.stock_code}")',
            sort_columns="MAIN_BUSINESS_INCOME",
            sort_types="-1",
            page_size=limit,
        )

    async def get_core_themes(self, stock_code: str, limit: int = 50) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPT_F10_CORETHEME_CONTENT",
            columns=(
                "SECUCODE,SECURITY_CODE,MAINPOINT,MAINPOINT_CONTENT,"
                "KEY_CLASSIF,KEY_CLASSIF_CODE,MAINPOINT_NUM,KEYWORD"
            ),
            filter_expr=f'(SECURITY_CODE="{identifier.stock_code}")',
            sort_columns="KEY_CLASSIF_CODE,MAINPOINT_RANK",
            sort_types="1,1",
            page_size=limit,
        )

    async def get_shareholder_research(self, stock_code: str, limit: int = 10) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPT_F10_EH_FREEHOLDERS",
            filter_expr=f'(SECURITY_CODE="{identifier.stock_code}")',
            sort_columns="END_DATE",
            sort_types="-1",
            page_size=limit,
        )

    async def get_capital_structure(self, stock_code: str, limit: int = 10) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPT_F10_EH_EQUITY",
            filter_expr=f'(SECURITY_CODE="{identifier.stock_code}")',
            sort_columns="END_DATE",
            sort_types="-1",
            page_size=limit,
        )

    async def get_industry_analysis(self, stock_code: str) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPT_STOCK_INDUSTRY_STA",
            filter_expr=f'(SECURITY_CODE="{identifier.stock_code}")',
        )

    async def get_market_average(self) -> dict:
        return await self._get_report("RPT_STOCK_MARKET_STA")

    async def get_billboard_trades(self, stock_code: str, limit: int = 10) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPT_BILLBOARD_PERFORMANCEHIS",
            filter_expr=f'(SECURITY_CODE="{identifier.stock_code}")',
            sort_columns="TRADE_DATE",
            sort_types="-1",
            page_size=limit,
        )

    async def get_block_trades(self, stock_code: str, limit: int = 10) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPT_DATA_BLOCKTRADE",
            filter_expr=f'(SECURITY_CODE="{identifier.stock_code}")',
            sort_columns="TRADE_DATE",
            sort_types="-1",
            page_size=limit,
        )

    async def get_margin_trading(self, stock_code: str, limit: int = 10) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPTA_WEB_RZRQ_GGMX",
            filter_expr=f"(scode={identifier.stock_code})",
            sort_columns="DATE",
            sort_types="-1",
            page_size=limit,
        )

    async def get_institutional_positions(
        self, stock_code: str, report_date: str | None = None, limit: int = 10
    ) -> dict:
        identifier = build_identifier(stock_code)
        filter_expr = f'(SECURITY_CODE="{identifier.stock_code}")'
        if report_date:
            filter_expr += f"(REPORT_DATE='{report_date}')"
        return await self._get_report(
            "RPT_MAINDATA_MAIN_POSITIONDETAILS",
            filter_expr=filter_expr,
            page_size=limit,
            sort_columns="HOLDER_CODE",
            sort_types="-1",
        )

    async def get_lockup_expirations(self, stock_code: str, limit: int = 10) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPT_LIFT_STAGE",
            columns=(
                "SECURITY_CODE,SECURITY_NAME_ABBR,FREE_DATE,CURRENT_FREE_SHARES,"
                "ABLE_FREE_SHARES,LIFT_MARKET_CAP,FREE_RATIO,NEW,B20_ADJCHRATE,"
                "A20_ADJCHRATE,FREE_SHARES_TYPE,TOTAL_RATIO,NON_FREE_SHARES,BATCH_HOLDER_NUM"
            ),
            filter_expr=f'(SECURITY_CODE="{identifier.stock_code}")',
            sort_columns="FREE_DATE",
            sort_types="1",
            page_size=limit,
        )

    async def get_stock_calendar(self, stock_code: str, limit: int = 10) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPT_STOCKCALENDAR",
            filter_expr=f'(SECURITY_CODE="{identifier.stock_code}")',
            sort_columns="NOTICE_DATE",
            sort_types="-1",
            page_size=limit,
            extra_params={"quoteColumns": ""},
        )

    async def get_org_survey(self, stock_code: str, limit: int = 10) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPT_ORG_SURVEY",
            filter_expr=f'(SECURITY_CODE="{identifier.stock_code}")',
            sort_columns="NOTICE_DATE",
            sort_types="-1",
            page_size=limit,
        )

    async def get_related_trades(self, stock_code: str, limit: int = 10) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPT_RELATED_TRADE",
            filter_expr=f'(SECURITY_CODE="{identifier.stock_code}")',
            sort_columns="NOTICE_DATE",
            sort_types="-1",
            page_size=limit,
        )

    async def get_holder_count_history(self, stock_code: str, limit: int = 10) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPT_HOLDERNUM_DET",
            columns=(
                "SECURITY_CODE,SECURITY_NAME_ABBR,CHANGE_SHARES,CHANGE_REASON,END_DATE,"
                "INTERVAL_CHRATE,AVG_MARKET_CAP,AVG_HOLD_NUM,TOTAL_MARKET_CAP,TOTAL_A_SHARES,"
                "HOLD_NOTICE_DATE,HOLDER_NUM,PRE_HOLDER_NUM,HOLDER_NUM_CHANGE,HOLDER_NUM_RATIO,"
                "END_DATE,PRE_END_DATE"
            ),
            filter_expr=f'(SECURITY_CODE="{identifier.stock_code}")',
            sort_columns="END_DATE",
            sort_types="-1",
            page_size=limit,
        )

    async def get_general_meetings(self, stock_code: str, limit: int = 10) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPT_GENERALMEETING_DETAIL",
            columns=(
                "SECURITY_CODE,SECURITY_NAME_ABBR,MEETING_TITLE,START_ADJUST_DATE,"
                "END_ADJUST_DATE,EQUITY_RECORD_DATE,ONSITE_RECORD_DATE,DECISION_NOTICE_DATE,"
                "NOTICE_DATE,WEB_START_DATE,WEB_END_DATE,SERIAL_NUM,PROPOSAL,PROPOSAL_CONTENT"
            ),
            filter_expr=f'(SECURITY_CODE="{identifier.stock_code}")',
            sort_columns="START_ADJUST_DATE",
            sort_types="-1",
            page_size=limit,
        )

    async def get_share_buybacks(self, stock_code: str, limit: int = 10) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPTA_WEB_GETHGLIST_NEW",
            filter_expr=f"(DIM_SCODE={identifier.stock_code})",
            sort_columns="UPD",
            sort_types="-1",
            page_size=limit,
        )

    async def get_wealth_management(self, stock_code: str, limit: int = 10) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPTA_WEB_WTLCMX",
            filter_expr=f"(scode={identifier.stock_code})",
            sort_columns="updatedate",
            sort_types="-1",
            page_size=limit,
        )

    async def get_capital_operations(self, stock_code: str, limit: int = 10) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPTA_WEB_BGCZMX",
            filter_expr=f"(scode={identifier.stock_code})",
            sort_columns="announdate",
            sort_types="-1",
            page_size=limit,
        )

    async def get_major_contracts(self, stock_code: str, limit: int = 10) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPTA_WEB_ZDHT_LIST",
            filter_expr=f"(SECURITYCODE={identifier.stock_code})",
            sort_columns="updatedate",
            sort_types="-1",
            page_size=limit,
        )

    async def get_latest_results(self, stock_code: str, limit: int = 10) -> dict:
        identifier = build_identifier(stock_code)
        return await self._get_report(
            "RPT_LICO_FN_CPD",
            filter_expr=f'(SECURITY_CODE="{identifier.stock_code}")',
            sort_columns="UPDATE_DATE",
            sort_types="-1",
            page_size=limit,
        )

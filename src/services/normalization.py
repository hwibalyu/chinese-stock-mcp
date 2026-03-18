from __future__ import annotations

from src.schemas.common import StockIdentifier
from src.schemas.fundamentals import (
    CompanyOverview,
    FinancialIndicatorRow,
    FinancialIndicators,
    MoneyFlowData,
    MoneyFlowRow,
    TableData,
)
from src.schemas.notice import NoticeFacts, NoticeItem, NoticeList, NoticeTextPage


def _to_float(value: object) -> float | None:
    if value in ("", None, "-"):
        return None
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def normalize_notice_list(
    identifier: StockIdentifier, payload: dict, page_index: int, page_size: int
) -> NoticeList:
    items = []
    for item in payload.get("list", []):
        codes = item.get("codes", [{}])
        columns = item.get("columns", [{}])
        code_info = codes[0] if codes else {}
        column_info = columns[0] if columns else {}
        items.append(
            NoticeItem(
                art_code=item["art_code"],
                title=item["title"],
                notice_date=item["notice_date"],
                column_name=column_info.get("column_name"),
                short_name=code_info.get("short_name"),
                stock_code=code_info.get("stock_code", identifier.stock_code),
                market_code=code_info.get("market_code"),
            )
        )
    return NoticeList(
        identifier=identifier,
        total_hits=payload.get("total_hits", len(items)),
        page_index=page_index,
        page_size=page_size,
        items=items,
    )


def normalize_notice_text_page(payload: dict, page_index: int) -> NoticeTextPage:
    data = payload["data"]
    return NoticeTextPage(
        art_code=data["art_code"],
        page_index=page_index,
        page_size=int(data.get("page_size", 1)),
        title=data["notice_title"],
        notice_date=data["notice_date"],
        text=data.get("notice_content", "").strip(),
        pdf_url=data.get("attach_url_web"),
    )


def normalize_company_overview(
    identifier: StockIdentifier, org_payload: dict, basic_payload: dict
) -> CompanyOverview:
    org_row = (org_payload.get("result", {}) or {}).get("data", [{}])[0]
    basic_row = (basic_payload.get("result", {}) or {}).get("data", [{}])[0]
    return CompanyOverview(
        identifier=identifier,
        org_name=org_row.get("ORG_NAME"),
        listing_date=org_row.get("LISTING_DATE"),
        found_date=org_row.get("FOUND_DATE"),
        legal_person=org_row.get("LEGAL_PERSON"),
        chairman=basic_row.get("CHAIRMAN"),
        general_manager=basic_row.get("GENERAL_MANAGER"),
        industry=basic_row.get("INDUSTRY"),
        main_business=basic_row.get("MAIN_BUSINESS"),
        region=basic_row.get("REGION"),
        website=basic_row.get("OFFICIAL_WEBSITE"),
    )


def normalize_financial_indicators(
    identifier: StockIdentifier, payload: dict
) -> FinancialIndicators:
    rows = []
    for row in (payload.get("result", {}) or {}).get("data", []):
        rows.append(
            FinancialIndicatorRow(
                report_date=row["REPORT_DATE"],
                report_type=row.get("REPORT_TYPE"),
                eps_basic=_to_float(row.get("EPSJB")),
                bps=_to_float(row.get("BPS")),
                operating_cashflow_per_share=_to_float(row.get("MGJYXJJE")),
                total_share=_to_float(row.get("TOTAL_SHARE")),
                free_share=_to_float(row.get("FREE_SHARE")),
            )
        )
    return FinancialIndicators(identifier=identifier, rows=rows)


def normalize_money_flow(identifier: StockIdentifier, payload: dict) -> MoneyFlowData:
    data = payload.get("data") or {}
    rows = []
    for line in data.get("klines", []):
        trade_date, main_net, super_large, large, mid, small, *_rest = line.split(",")
        rows.append(
            MoneyFlowRow(
                trade_date=trade_date,
                main_net_inflow=_to_float(main_net),
                super_large_net_inflow=_to_float(super_large),
                large_net_inflow=_to_float(large),
                mid_net_inflow=_to_float(mid),
                small_net_inflow=_to_float(small),
            )
        )
    return MoneyFlowData(identifier=identifier, rows=rows)


def normalize_table_data(
    identifier: StockIdentifier,
    report_name: str,
    payload: dict,
    field_map: dict[str, str] | None = None,
) -> TableData:
    rows: list[dict] = []
    for row in (payload.get("result", {}) or {}).get("data", []):
        item: dict = {}
        if field_map:
            for source_key, target_key in field_map.items():
                item[target_key] = row.get(source_key)
        else:
            item = dict(row)
        rows.append(item)
    return TableData(identifier=identifier, report_name=report_name, rows=rows)


def build_notice_facts(
    art_code: str,
    title: str,
    notice_date: str,
    report_period: str | None,
    report_type: str | None,
    facts: dict[str, float | str | None],
    evidence: list[str],
) -> NoticeFacts:
    return NoticeFacts(
        art_code=art_code,
        title=title,
        notice_date=notice_date,
        report_period=report_period,
        report_type=report_type,
        facts=facts,
        evidence=evidence,
    )

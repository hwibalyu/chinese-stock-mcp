from __future__ import annotations

import re

from src.schemas.notice import NoticeFacts, NoticeTextPage
from src.services.normalization import build_notice_facts


METRIC_PATTERNS: list[tuple[str, str]] = [
    ("revenue_q", r"营业收入\s+([0-9,]+\.[0-9]+)\s+[0-9.\-]+\s+([0-9,]+\.[0-9]+)\s+([0-9.\-]+)"),
    ("profit_total_q", r"利润总额\s+([0-9,]+\.[0-9]+)\s+[0-9.\-]+\s+([0-9,]+\.[0-9]+)\s+([0-9.\-]+)"),
    ("net_income_q", r"归属于上市公司股东的\s+([0-9,]+\.[0-9]+)\s+[0-9.\-]+\s+([0-9,]+\.[0-9]+)\s+([0-9.\-]+)\s+净利润"),
]


def _clean_number(raw: str) -> float | None:
    try:
        return float(raw.replace(",", ""))
    except ValueError:
        return None


def _extract_first(pattern: str, text: str) -> tuple[float | None, float | None, float | None] | None:
    match = re.search(pattern, text, flags=re.S)
    if not match:
        return None
    groups = match.groups()
    values = tuple(_clean_number(group) for group in groups[:3])
    return values  # type: ignore[return-value]


def extract_notice_facts(page: NoticeTextPage) -> NoticeFacts:
    text = page.text
    title = page.title
    compact_text = re.sub(r"\s+", " ", text).strip()

    report_period_match = re.search(r"(\d{4}\s*年第三季度报告|\d{4}\s*年半年度报告|\d{4}\s*年第一季度报告)", title)
    report_type = None
    if "第三季度报告" in title:
        report_type = "quarterly_q3"
    elif "半年度报告" in title:
        report_type = "half_year"
    elif "第一季度报告" in title:
        report_type = "quarterly_q1"
    elif "年度报告" in title:
        report_type = "annual"

    report_period = None
    if report_period_match:
        report_period = report_period_match.group(1).replace(" ", "")

    facts: dict[str, float | str | None] = {}
    evidence: list[str] = []

    metric_patterns = {
        "营业收入": (
            r"营业收入\s+([0-9,]+\.[0-9]+)\s+[0-9.\-]+\s+([0-9,]+\.[0-9]+)\s+([0-9.\-]+)",
            ("revenue_q", "revenue_ytd", "revenue_ytd_growth_pct"),
        ),
        "利润总额": (
            r"利润总额\s+([0-9,]+\.[0-9]+)\s+[0-9.\-]+\s+([0-9,]+\.[0-9]+)\s+([0-9.\-]+)",
            ("profit_total_q", "profit_total_ytd", "profit_total_ytd_growth_pct"),
        ),
        "净利润": (
            r"归属于上市公司股东的\s+([0-9,]+\.[0-9]+)\s+[0-9.\-]+\s+([0-9,]+\.[0-9]+)\s+([0-9.\-]+)\s+净利润",
            ("net_income_q", "net_income_ytd", "net_income_ytd_growth_pct"),
        ),
    }
    for _label, (pattern, (key_q, key_ytd, key_growth)) in metric_patterns.items():
        values = _extract_first(pattern, compact_text)
        if values:
            facts[key_q], facts[key_ytd], facts[key_growth] = values
            snippet_match = re.search(pattern, compact_text, flags=re.S)
            if snippet_match:
                evidence.append(re.sub(r"\s+", " ", snippet_match.group(0)).strip())

    cash_flow_match = re.search(
        r"经营活动产生的现金流\s+不适用\s+不适用\s+([0-9,]+\.[0-9]+)\s+([0-9.\-]+)",
        compact_text,
        flags=re.S,
    )
    if cash_flow_match:
        facts["operating_cashflow_ytd"] = _clean_number(cash_flow_match.group(1))
        facts["operating_cashflow_ytd_growth_pct"] = _clean_number(cash_flow_match.group(2))
        evidence.append(re.sub(r"\s+", " ", cash_flow_match.group(0)).strip())

    shareholder_match = re.search(r"报告期末普通股股东总数\s+([0-9,]+)", compact_text)
    if shareholder_match:
        facts["shareholder_count"] = _clean_number(shareholder_match.group(1))
        evidence.append(shareholder_match.group(0))

    return build_notice_facts(
        art_code=page.art_code,
        title=page.title,
        notice_date=page.notice_date,
        report_period=report_period,
        report_type=report_type,
        facts=facts,
        evidence=evidence[:5],
    )

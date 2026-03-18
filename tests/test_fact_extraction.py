from src.schemas.notice import NoticeTextPage
from src.services.fact_extraction import extract_notice_facts


def test_extract_notice_facts_from_quarterly_page() -> None:
    page = NoticeTextPage(
        art_code="AN_TEST",
        page_index=1,
        page_size=4,
        title="春风动力:春风动力2025年第三季度报告",
        notice_date="2025-10-17 00:00:00",
        text="""
        营业收入 5,040,899,274.75 28.56 14,896,332,446.98 30.10
        利润总额 506,946,567.80 20.15 1,743,847,920.64 41.92
        归属于上市公司股东的
        413,460,545.03 11.00 1,415,369,548.15 30.89 净利润
        经营活动产生的现金流 不适用 不适用 3,207,611,143.97 42.80
        报告期末普通股股东总数 13,264
        """,
        pdf_url=None,
    )

    facts = extract_notice_facts(page)

    assert facts.report_type == "quarterly_q3"
    assert facts.facts["revenue_ytd"] == 14896332446.98
    assert facts.facts["net_income_ytd"] == 1415369548.15
    assert facts.facts["operating_cashflow_ytd"] == 3207611143.97
    assert facts.facts["shareholder_count"] == 13264.0

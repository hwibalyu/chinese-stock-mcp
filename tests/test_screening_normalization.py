from src.services.identifiers import build_identifier
from src.services.normalization import normalize_screening_result


def test_build_identifier_supports_bj_market() -> None:
    identifier = build_identifier("920978", short_name="开特股份")

    assert identifier.market == "BJ"
    assert identifier.secid == "0.920978"
    assert identifier.symbol == "BJ920978"


def test_normalize_screening_result() -> None:
    payload = {
        "data": {
            "traceId": "trace-1",
            "xcId": "xc-123",
            "result": {
                "total": 1,
                "columns": [
                    {"key": "SECURITY_CODE", "title": "代码", "unit": "", "sortable": False},
                    {"key": "SECURITY_SHORT_NAME", "title": "名称", "unit": "", "sortable": False},
                    {"key": "MARKET_SHORT_NAME", "title": "市场简称", "unit": "", "sortable": False},
                    {"key": "NEWEST_PRICE", "title": "最新价", "unit": "元", "sortable": True},
                    {"key": "CHG", "title": "涨跌幅", "unit": "%", "sortable": True},
                    {
                        "key": "PETTM{2026-03-18}",
                        "title": "市盈率(TTM)(倍)",
                        "unit": "倍",
                        "sortable": True,
                    },
                    {
                        "key": "MACD_JIN_CHA{2026-03-18}",
                        "title": "macd金叉",
                        "unit": "",
                        "sortable": False,
                    },
                ],
                "dataList": [
                    {
                        "SECURITY_CODE": "920978",
                        "SECURITY_SHORT_NAME": "开特股份",
                        "MARKET_SHORT_NAME": "京A",
                        "NEWEST_PRICE": "26.67",
                        "CHG": "-1.51",
                        "PETTM{2026-03-18}": "27.97",
                        "MACD_JIN_CHA{2026-03-18}": "符合",
                    }
                ],
            },
        }
    }

    result = normalize_screening_result(
        query="MACD金叉 且 市盈率 小于 30",
        payload=payload,
        page_no=1,
        page_size=10,
    )

    assert result.total == 1
    assert result.xc_id == "xc-123"
    assert result.items[0].identifier.market == "BJ"
    assert result.items[0].last_price == 26.67
    assert result.items[0].change_percent == -1.51
    assert result.items[0].metrics["市盈率(TTM)(倍)"] == "27.97"
    assert result.items[0].metrics["macd金叉"] == "符合"

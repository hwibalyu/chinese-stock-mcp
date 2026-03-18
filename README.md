# Chinese Stock MCP

중국 주식 데이터를 MCP 서버로 제공하는 프로젝트입니다. 종목 검색, 조건 스크리닝, 실시간 시세, 공시 본문 조회, F10/재무 데이터, 최신 분기보고서 요약 같은 작업을 MCP 클라이언트에서 바로 호출할 수 있습니다.

## 무엇을 할 수 있나요?

- 종목 코드, 중국어 이름, 티커 비슷한 키워드로 종목 검색
- 자연어 조건으로 종목 스크리닝
- 실시간 시세와 최근 자금 흐름 조회
- 최근 공시 목록 조회와 공시 본문 읽기
- 최신 분기/반기 보고서 핵심 내용 요약
- 회사 개요, 재무지표, 지분 구조, 기관 보유, 블록딜, 자사주 매입 등 F10 데이터 조회
- 상하이, 선전뿐 아니라 북교소(`BJ`) 종목도 식별 가능

## 준비 사항

- Python 3.10 이상
- MCP를 지원하는 클라이언트
  - Codex
  - Claude Desktop
  - Cursor
  - 기타 MCP 호환 클라이언트

## 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

환경 변수는 없어도 기본값으로 실행됩니다. 필요하면 `.env` 파일에 아래처럼 설정할 수 있습니다.

```env
CHINA_STOCK_HTTP_TIMEOUT_SECONDS=15
CHINA_STOCK_QUOTE_CACHE_TTL_SECONDS=30
CHINA_STOCK_STATIC_CACHE_TTL_SECONDS=3600
CHINA_STOCK_NOTICE_CACHE_TTL_SECONDS=86400
```

## 로컬에서 실행

```bash
source .venv/bin/activate
python -m src.server
```

기본 전송 방식은 `stdio` 입니다. 대부분의 MCP 클라이언트에서 그대로 사용하면 됩니다.

## MCP 클라이언트에 연결하기

클라이언트 설정에 이 서버를 등록하면 됩니다. 핵심은 `python -m src.server` 를 MCP 서버 명령으로 넣는 것입니다.

예시:

```json
{
  "mcpServers": {
    "chinese-stock": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/absolute/path/to/chinese-stock-mcp"
    }
  }
}
```

직접 실행 파일 경로를 넣기 어렵다면 아래처럼 시스템 파이썬을 써도 됩니다.

```json
{
  "mcpServers": {
    "chinese-stock": {
      "command": "python3",
      "args": ["-m", "src.server"],
      "cwd": "/absolute/path/to/chinese-stock-mcp"
    }
  }
}
```

## 사용 방법

연결이 끝나면 MCP 클라이언트에서 자연어로 요청하면 됩니다.

예시 질문:

- `BYD 찾아줘`
- `开特股份 찾아줘`
- `603129 최근 공시 보여줘`
- `CFMOTO 최신 분기보고서 요약해줘`
- `贵州茅台 실시간 시세와 최근 자금 흐름 알려줘`
- `宁德时代 지분 구조 변화 보여줘`
- `중국 종목 중 최근 기관 조사 공시가 나온 회사 찾아줘`
- `MACD金叉 이고 시가총액이 너무 크지 않은 종목 찾아줘`
- `市盈率 小于 30 且 ROE 高于 15% 조건으로 스크리닝해줘`

## 검색과 스크리닝 차이

이 프로젝트는 `검색`과 `스크리닝`을 분리해서 생각하면 편합니다.

- `search_stock`
  - 종목 코드, 종목명, 티커 비슷한 질의에 적합합니다.
  - 예: `BYD`, `603129`, `春风动力`
- `screen_stocks`
  - 조건형 자연어 질의에 적합합니다.
  - 예: `MACD金叉 且 市盈率 小于 30`
  - 예: `최근 강한 상승 흐름이 있으면서 거래량이 붙은 종목`

추가로 `search_stock` 은 결과가 없고 질의가 조건형 문장처럼 보이면 `xuangu.eastmoney.com` 스크리닝 백엔드로 자동 폴백합니다. 그래서 사용자는 굳이 항상 도구를 구분하지 않아도 됩니다.

## 스크리닝 예시

아래처럼 바로 조건형 탐색이 가능합니다.

- `MACD金叉 且 市盈率 小于 30`
- `ROE 大于 15% 且 净利润增长率 为正`
- `최근 자사주 매입 공시가 있고 주가가 강한 종목 찾아줘`
- `중국 이륜차 관련 종목 중 최근 공시 흐름이 좋은 종목 추려줘`

추천 흐름은 이렇습니다.

1. `screen_stocks` 또는 자연어 질의로 후보군을 찾습니다.
2. 추린 종목을 `get_quote`, `get_notices`, `get_financial_indicators` 로 후속 분석합니다.
3. 필요하면 `analyze_latest_quarterly_report` 로 최신 분기보고서 핵심만 빠르게 확인합니다.

## 자주 쓰는 도구

대표 도구만 보면 아래와 같습니다.

- `search_stock`: 종목 검색
- `screen_stocks`: 자연어 조건 기반 종목 스크리닝
- `get_quote`: 실시간 시세
- `get_money_flow`: 최근 자금 흐름
- `get_notices`: 최근 공시 목록
- `get_notice_text_full`: 공시 본문 전체 읽기
- `extract_notice_facts`: 공시 핵심 수치 추출
- `analyze_latest_quarterly_report`: 최신 분기/반기 보고서 요약
- `get_company_overview`: 회사 개요
- `get_financial_indicators`: 최근 재무지표
- `get_capital_structure`: 자본 구조
- `get_institutional_positions`: 기관 보유 현황
- `get_holder_count_history`: 주주 수 추이
- `get_block_trades`: 블록딜
- `get_share_buybacks`: 자사주 매입
- `get_mixed_feed`: 뉴스/공시/리포트 혼합 피드

## 테스트

```bash
source .venv/bin/activate
pytest
```

## 프로젝트 구조

```text
src/
  clients/    # Eastmoney 계열 API 클라이언트
  schemas/    # 응답 스키마
  services/   # 정규화, 공시 본문 처리, 팩트 추출
  tools/      # MCP 도구 등록
  server.py   # MCP 서버 진입점
tests/
```

## 참고

- 데이터 소스는 Eastmoney 계열 공개 엔드포인트를 사용합니다.
- 조건 스크리닝은 `xuangu.eastmoney.com` 계열 백엔드를 사용합니다.
- 일부 시세/공시 응답은 외부 데이터 소스 상태에 따라 일시적으로 실패할 수 있습니다.
- 스크리닝 백엔드는 비공식 웹 엔드포인트 기반이라 응답 필드나 동작 방식이 바뀔 수 있습니다.
- 캐시 TTL은 `CHINA_STOCK_*` 환경 변수로 조정할 수 있습니다.

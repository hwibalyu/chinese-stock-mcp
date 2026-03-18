from __future__ import annotations

import json
import re
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.settings import get_settings


class EastmoneyBaseClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = httpx.AsyncClient(
            timeout=self.settings.http_timeout_seconds,
            headers={
                "User-Agent": self.settings.user_agent,
                "Accept": "application/json,text/plain,*/*",
                "Referer": "https://quote.eastmoney.com/",
            },
        )

    async def close(self) -> None:
        await self._client.aclose()

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        retry=retry_if_exception_type((httpx.HTTPError, ValueError)),
    )
    async def get_json(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = await self._client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        retry=retry_if_exception_type((httpx.HTTPError, ValueError)),
    )
    async def post_json(
        self,
        url: str,
        payload: dict[str, Any],
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = await self._client.post(url, params=params, json=payload)
        response.raise_for_status()
        return response.json()

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        retry=retry_if_exception_type((httpx.HTTPError, ValueError, json.JSONDecodeError)),
    )
    async def get_jsonp(
        self, url: str, params: dict[str, Any] | None = None, callback: str = "cb"
    ) -> dict[str, Any]:
        merged = dict(params or {})
        merged["cb"] = callback
        response = await self._client.get(url, params=merged)
        response.raise_for_status()
        body = response.text.strip()
        clean = re.sub(rf"^{re.escape(callback)}\(|\)$", "", body)
        return json.loads(clean)

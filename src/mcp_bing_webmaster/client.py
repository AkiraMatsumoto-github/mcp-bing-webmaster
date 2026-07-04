"""Thin HTTP client for the Bing Webmaster Tools JSON API.

By design this client only exposes read ("Get*") and non-destructive URL
submission ("Submit*") operations. No site/config mutation or deletion
endpoints are implemented, so an agent using this client cannot remove sites,
sitemaps, blocks, or trigger site moves.

API reference: https://learn.microsoft.com/en-us/bingwebmaster/
Endpoint form: https://ssl.bing.com/webmaster/api.svc/json/{Method}?apikey=KEY
Responses are wrapped as {"d": <payload>}; errors return HTTP 400 with
{"ErrorCode": <int>, "Message": <str>}.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

BASE_URL = "https://ssl.bing.com/webmaster/api.svc/json"
DEFAULT_TIMEOUT = 30.0


class BingWebmasterError(RuntimeError):
    """Raised when the Bing Webmaster API returns an error or is unreachable."""

    def __init__(
        self,
        message: str,
        *,
        error_code: int | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.status_code = status_code


class BingWebmasterClient:
    """Minimal synchronous client for the Bing Webmaster Tools JSON API."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.api_key = api_key or os.environ.get("BING_WEBMASTER_API_KEY", "")
        if not self.api_key:
            raise BingWebmasterError(
                "BING_WEBMASTER_API_KEY is not set. Generate a key at "
                "https://www.bing.com/webmasters -> Settings -> API access "
                "and expose it as the BING_WEBMASTER_API_KEY environment variable."
            )
        self.timeout = timeout

    # -- HTTP plumbing ----------------------------------------------------

    def get(self, method: str, params: dict[str, Any] | None = None) -> Any:
        """Call a read ("Get*") method via HTTP GET."""
        query: dict[str, Any] = {k: v for k, v in (params or {}).items() if v is not None}
        query["apikey"] = self.api_key
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(f"{BASE_URL}/{method}", params=query)
        return self._handle(resp)

    def post(self, method: str, body: dict[str, Any] | None = None) -> Any:
        """Call a submission ("Submit*") method via HTTP POST."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{BASE_URL}/{method}",
                params={"apikey": self.api_key},
                json=body or {},
            )
        return self._handle(resp)

    def _handle(self, resp: httpx.Response) -> Any:
        try:
            data = resp.json()
        except ValueError:
            raise BingWebmasterError(
                f"Bing API returned a non-JSON response (HTTP {resp.status_code}): "
                f"{resp.text[:200]}",
                status_code=resp.status_code,
            ) from None

        # Error payloads are {"ErrorCode": n, "Message": "..."} with HTTP 400.
        if isinstance(data, dict) and "ErrorCode" in data and "d" not in data:
            raise BingWebmasterError(
                f"Bing API error: {data.get('Message', 'unknown error')}",
                error_code=data.get("ErrorCode"),
                status_code=resp.status_code,
            )
        if resp.status_code >= 400:
            raise BingWebmasterError(
                f"Bing API HTTP {resp.status_code}: {resp.text[:200]}",
                status_code=resp.status_code,
            )

        # Successful payloads are wrapped as {"d": <value>}.
        if isinstance(data, dict) and "d" in data:
            return data["d"]
        return data

from __future__ import annotations

import re
from typing import Any

import httpx


class LMSApiClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _format_error(self, exc: Exception) -> str:
        if isinstance(exc, httpx.HTTPStatusError):
            status_code = exc.response.status_code
            reason = exc.response.reason_phrase or "HTTP error"
            return f"Backend error: HTTP {status_code} {reason}."

        if isinstance(exc, httpx.ConnectError):
            message = str(exc).lower()
            if "connection refused" in message:
                detail = "connection refused"
            elif "nodename nor servname provided" in message:
                detail = "host resolution failed"
            else:
                detail = "connection failed"
            return (
                f"Backend error: {detail} ({self.base_url}). "
                "Check that the services are running."
            )

        if isinstance(exc, httpx.TimeoutException):
            return (
                f"Backend error: request timed out ({self.base_url}). "
                "The backend may be overloaded or unavailable."
            )

        if isinstance(exc, httpx.HTTPError):
            return f"Backend error: {str(exc)}."

        return f"Backend error: {str(exc)}."

    async def get_items(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{self.base_url}/items/",
                headers=self._headers,
            )
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []

    async def get_pass_rates(self, lab: str) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{self.base_url}/analytics/pass-rates",
                params={"lab": lab},
                headers=self._headers,
            )
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []

    async def health_summary(self) -> str:
        try:
            items = await self.get_items()
        except Exception as exc:
            return self._format_error(exc)

        return f"Backend is healthy. {len(items)} items available."

    async def list_labs(self) -> list[str]:
        items = await self.get_items()
        labs = [item for item in items if item.get("type") == "lab"]
        results: list[str] = []

        for index, lab in enumerate(labs, start=1):
            title = str(lab.get("title", "")).strip()
            match = re.search(r"Lab\s*0?(\d+)", title, re.IGNORECASE)
            if match:
                code = f"lab-{int(match.group(1)):02d}"
                results.append(f"{code}: {title}")
            else:
                results.append(f"lab-{index:02d}: {title or 'Untitled lab'}")

        return results

    async def pass_rates_summary(self, lab: str) -> str:
        try:
            rows = await self.get_pass_rates(lab)
        except Exception as exc:
            return self._format_error(exc)

        if not rows:
            return (
                f"No pass-rate data found for {lab}. "
                "Check the lab code and make sure the backend has synced data."
            )

        lines = [f"Pass rates for {lab}:"]
        for row in rows:
            task = str(row.get("task", "Untitled task"))
            avg_score = float(row.get("avg_score", 0.0))
            attempts = int(row.get("attempts", 0))
            lines.append(f"- {task}: {avg_score:.1f}% ({attempts} attempts)")

        return "\n".join(lines)

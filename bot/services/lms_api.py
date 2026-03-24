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

    async def get_items(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{self.base_url}/items/",
                headers=self._headers,
            )
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []

    async def health_summary(self) -> str:
        try:
            items = await self.get_items()
        except httpx.HTTPStatusError as exc:
            return f"Backend is reachable but returned HTTP {exc.response.status_code}."
        except httpx.HTTPError:
            return "Backend is down or unreachable right now."

        return f"Backend is up. Retrieved {len(items)} items."

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

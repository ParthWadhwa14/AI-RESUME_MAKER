"""
AssetBridge — Downloads external assets and converts them to base64 data URIs.

The asset agent outputs a list of ``{url, target_path}`` dicts.  This service
fetches each URL, encodes the response body as a base64 data URI so that
Sandpack can embed the images without needing a network fetch, and returns a
mapping of ``target_path → data_uri``.
"""

from __future__ import annotations

import base64
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# A minimal 1×1 translucent SVG used when a download fails.
_PLACEHOLDER_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
    '<rect width="100" height="100" fill="#e2e8f0" rx="8"/>'
    '<text x="50" y="55" text-anchor="middle" font-size="12" fill="#94a3b8">'
    "img"
    "</text></svg>"
)
_PLACEHOLDER_DATA_URI = (
    "data:image/svg+xml;base64,"
    + base64.b64encode(_PLACEHOLDER_SVG.encode()).decode()
)

# Common content-type → extension mapping for MIME detection.
_MIME_MAP: dict[str, str] = {
    "image/png": "image/png",
    "image/jpeg": "image/jpeg",
    "image/gif": "image/gif",
    "image/svg+xml": "image/svg+xml",
    "image/webp": "image/webp",
    "image/x-icon": "image/x-icon",
    "image/vnd.microsoft.icon": "image/x-icon",
}


class AssetBridge:
    """Downloads assets and returns base64-encoded data URIs."""

    @staticmethod
    async def process_downloads(
        downloads: list[dict[str, Any]],
    ) -> dict[str, str]:
        """Fetch each URL and return *target_path → base64 data URI*.

        Parameters
        ----------
        downloads:
            List of dicts, each with at least ``url`` and ``target_path`` keys.

        Returns
        -------
        dict[str, str]
            Mapping of ``target_path`` to a ``data:<mime>;base64,…`` string.
        """

        results: dict[str, str] = {}

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(15.0, connect=10.0),
            follow_redirects=True,
        ) as client:
            for item in downloads:
                url: str = item.get("url", "")
                target: str = item.get("target_path", "")

                if not url or not target:
                    logger.warning("Skipping download entry with missing url/target: %s", item)
                    continue

                try:
                    resp = await client.get(url)
                    resp.raise_for_status()

                    content_type = resp.headers.get("content-type", "application/octet-stream")
                    # Strip parameters (e.g. "image/png; charset=utf-8" → "image/png")
                    mime = content_type.split(";")[0].strip()
                    mime = _MIME_MAP.get(mime, mime)

                    b64 = base64.b64encode(resp.content).decode()
                    results[target] = f"data:{mime};base64,{b64}"

                    logger.info("Downloaded %s → %s (%d bytes)", url, target, len(resp.content))

                except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                    logger.warning("Failed to download %s: %s — using placeholder", url, exc)
                    results[target] = _PLACEHOLDER_DATA_URI

        return results

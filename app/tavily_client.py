"""Tavily client — re-verify external references cited in an answer.

Optional. If TAVILY_API_KEY is not set, or the call fails / times out,
the caller degrades gracefully: the report notes live retrieval was
unavailable and the claim keeps the label the deterministic checker
gave it. Tavily never changes a label on its own.
"""
from __future__ import annotations

import os

import httpx

TAVILY_URL = "https://api.tavily.com/search"
TIMEOUT_SECS = 8.0


def tavily_available() -> bool:
    return bool(os.environ.get("TAVILY_API_KEY"))


def search(query: str, max_results: int = 3) -> dict:
    """Return {"available": bool, "results": [...], "note": str}."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return {"available": False, "results": [],
                "note": "Tavily API key not set — live re-verification skipped."}
    try:
        resp = httpx.post(
            TAVILY_URL,
            json={"api_key": api_key, "query": query,
                  "search_depth": "basic", "max_results": max_results},
            timeout=TIMEOUT_SECS,
        )
        resp.raise_for_status()
        data = resp.json()
        return {"available": True,
                "results": [{"title": r.get("title"), "url": r.get("url"),
                             "content": (r.get("content") or "")[:300]}
                            for r in data.get("results", [])],
                "note": "Live Tavily search completed."}
    except Exception as exc:  # network / timeout / API error: degrade, never crash
        return {"available": False, "results": [],
                "note": f"Tavily lookup failed ({exc}) — live re-verification unavailable."}

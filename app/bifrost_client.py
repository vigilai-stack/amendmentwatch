"""LLM via Bifrost gateway — claim explanations only.

Optional. Bifrost is an OpenAI-compatible gateway, so this client posts
to <BIFROST_BASE_URL>/chat/completions with BIFROST_API_KEY and
BIFROST_MODEL (default "gpt-4o-mini" — set the model your Bifrost
project actually routes to). If no key is set, or the call fails, the
caller falls back to the deterministic reason strings from checker.py.
The model never decides a label.
"""
from __future__ import annotations

import os

import httpx

TIMEOUT_SECS = 20.0


def bifrost_available() -> bool:
    return bool(os.environ.get("BIFROST_API_KEY"))


def explain(claim_text: str, label: str, reason: str) -> dict:
    """Return {"available": bool, "explanation": str}."""
    api_key = os.environ.get("BIFROST_API_KEY")
    base = os.environ.get("BIFROST_BASE_URL", "http://localhost:8080/v1").rstrip("/")
    model = os.environ.get("BIFROST_MODEL", "gpt-4o-mini")
    if not api_key:
        return {"available": False, "explanation": reason}
    try:
        resp = httpx.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model,
                  "messages": [
                      {"role": "system",
                       "content": "Explain a protocol freshness verdict in one plain sentence. "
                                  "Do not change the verdict and do not add facts."},
                      {"role": "user",
                       "content": f"Claim: {claim_text}\nVerdict: {label}\nReason: {reason}"},
                  ],
                  "temperature": 0},
            timeout=TIMEOUT_SECS,
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"].strip()
        return {"available": True, "explanation": text}
    except Exception:
        return {"available": False, "explanation": reason}

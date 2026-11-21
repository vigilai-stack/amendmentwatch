"""Claim extraction.

Deterministic, rule-based extraction is the default and always runs:
it scans pasted text for the six clause topics in SYNTH-201 plus the
known Unknown topic (pregnancy testing). Claim extraction is rule-based
only — no model extracts claims. OpenAI gpt-4o-mini, reached through the
Bifrost local gateway (see bifrost_client.py), is used only to explain a
verdict in plain language — it never overrides a label the checker settled.
If no Bifrost key is set, the report says so plainly and neither Bifrost
nor OpenAI runs.
"""
from __future__ import annotations

import re

# Each pattern: topic, regex with a numeric group (or None for text claims).
_PATTERNS = [
    ("washout", re.compile(r"washout[^0-9]{0,40}?(\d+)\s*days", re.I)),
    ("minimum_age", re.compile(r"(?:(\d+)\s*(?:years|yrs?)\s*(?:or older|and over|or over))|(?:adults?\s+(\d+)\s+and over)|(?:(\d+)\s+and over may enrol)", re.I)),
    ("hba1c", re.compile(r"hba1c[^0-9]{0,30}?(\d+(?:\.\d+)?)\s*%", re.I)),
    ("dose_hold_alt", re.compile(r"ALT[^0-9]{0,30}?(?:above|exceeds|over|>)\s*(\d+(?:\.\d+)?)\s*[x×]\s*ULN", re.I)),
    ("missed_visit", re.compile(r"(?:missed[^0-9]{0,40}?reschedule within|reschedule within)\s*(\d+)\s*days", re.I)),
    ("fasting", re.compile(r"(?:fast(?:ing)?[^0-9]{0,30}?(\d+)\s*hours)|(?:fasting is (\d+)\s*hours)", re.I)),
    ("notify_monitor", re.compile(r"notify the medical monitor the same day", re.I)),
    ("pregnancy_testing", re.compile(r"pregnancy test(?:ing)?[^0-9]{0,40}?(\d+)\s*days", re.I)),
]


def _first_number(match, groups=(1, 2, 3)):
    for g in groups:
        try:
            raw = match.group(g)
        except IndexError:
            continue
        if raw:
            return float(raw) if "." in raw else int(raw)
    return None


def extract_claims(text: str) -> list[dict]:
    """Return [{topic, value, text}] for every clause topic found in text."""
    claims: list[dict] = []
    seen: set[str] = set()
    for topic, pattern in _PATTERNS:
        for match in pattern.finditer(text):
            if topic in seen:
                continue
            seen.add(topic)
            if topic == "notify_monitor":
                claims.append({"topic": topic, "value": "same day",
                               "text": match.group(0).strip()})
            else:
                value = _first_number(match)
                if value is None:
                    continue
                claims.append({"topic": topic, "value": value,
                               "text": match.group(0).strip()})
    if not claims:
        # Nothing recognisable: one Unknown claim, so the report says so
        # instead of silently returning an empty verdict.
        claims.append({"topic": "unrecognised", "value": None,
                       "text": text.strip()[:200]})
    return claims

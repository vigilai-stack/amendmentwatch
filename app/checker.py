"""Deterministic version checker — the core of AmendmentWatch.

Labels, in order:
1. Value matches the protocol version in force (v3) -> Current.
2. Value matches an earlier version but conflicts with v3 -> Superseded.
3. Otherwise -> Unknown. There is no step that guesses.
The language model never decides a label the structured check settled.
"""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def _load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def load_protocols() -> dict[str, dict]:
    return {v: _load(f"protocol_v{v}.json") for v in ("1", "2", "3")}


def load_amendments() -> dict:
    return _load("amendments.json")


def load_seeded() -> dict:
    return _load("seeded_answers.json")


def clause_by_topic(protocol: dict, topic: str) -> dict | None:
    for clause in protocol["clauses"]:
        if clause["topic"] == topic:
            return clause
    return None


def amendment_for_topic(topic: str) -> str | None:
    for amendment in load_amendments()["amendments"]:
        for change in amendment["changes"]:
            if change["topic"] == topic:
                return amendment["id"]
    return None


def check_claim(topic: str, value, claim_text: str) -> dict:
    """Check one claim (topic + value) against v3, then v1/v2."""
    protocols = load_protocols()
    current = clause_by_topic(protocols["3"], topic)
    if current is None:
        return {
            "claim": claim_text,
            "topic": topic,
            "value": value,
            "label": "Unknown",
            "reason": "No clause in the protocol in force addresses this topic. "
                      "A human must confirm it before use.",
            "current_clause": None,
            "superseded_clause": None,
            "amendment": None,
        }
    if value == current["value"]:
        return {
            "claim": claim_text,
            "topic": topic,
            "value": value,
            "label": "Current",
            "reason": f"Matches §{current['section']} in protocol v3 (in force, "
                      f"effective {protocols['3']['effective_date']}).",
            "current_clause": current,
            "superseded_clause": None,
            "amendment": None,
        }
    # Does it match an earlier version? Then it was true once — now superseded.
    for version in ("2", "1"):
        old = clause_by_topic(protocols[version], topic)
        if old is not None and value == old["value"]:
            return {
                "claim": claim_text,
                "topic": topic,
                "value": value,
                "label": "Superseded",
                "reason": f"Matched §{old['section']} in protocol v{version}, "
                          f"but §{current['section']} in v3 (in force) says "
                          f"'{current['text']}'.",
                "current_clause": current,
                "superseded_clause": old,
                "amendment": amendment_for_topic(topic),
            }
    return {
        "claim": claim_text,
        "topic": topic,
        "value": value,
        "label": "Unknown",
        "reason": "The value does not match the protocol in force or any "
                  "earlier version. A human must confirm it before use.",
        "current_clause": current,
        "superseded_clause": None,
        "amendment": None,
    }


def verdict_for(labels: list[str]) -> str:
    if "Superseded" in labels:
        return "Do not use"
    if "Unknown" in labels:
        return "Needs human review"
    return "Safe to use"

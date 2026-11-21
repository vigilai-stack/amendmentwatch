"""Build the one-page freshness report from checked claims."""
from __future__ import annotations

from . import bifrost_client
from .checker import check_claim, verdict_for


def build_report(answer_text: str, claims: list[dict], live_mode: str) -> dict:
    checked = []
    for claim in claims:
        result = check_claim(claim["topic"], claim["value"], claim["text"])
        explanation = bifrost_client.explain(
            result["claim"], result["label"], result["reason"])
        result["explanation"] = explanation["explanation"]
        result["llm_used"] = explanation["available"]
        checked.append(result)
    labels = [c["label"] for c in checked]
    verdict = verdict_for(labels)
    corrected = []
    for c in checked:
        if c["label"] == "Current" and c["current_clause"]:
            corrected.append(c["current_clause"]["text"])
        elif c["label"] == "Superseded" and c["current_clause"]:
            corrected.append(c["current_clause"]["text"])
        # Unknown claims get no invented correction — only a flag.
    return {
        "answer": answer_text,
        "mode": live_mode,
        "verdict": verdict,
        "summary": {
            "total": len(checked),
            "current": labels.count("Current"),
            "superseded": labels.count("Superseded"),
            "unknown": labels.count("Unknown"),
        },
        "claims": checked,
        "corrected_answer": (
            " ".join(corrected) if corrected else
            "No corrected answer can be built from clauses in force — "
            "a human must confirm the claims first."
        ),
        "protocol_version_in_force": "3",
        "disclaimer": "AmendmentWatch checks text against a document. It does not "
                      "give medical advice. Decisions stay with the investigator "
                      "and medical monitor.",
    }

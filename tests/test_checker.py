"""Tests for AmendmentWatch — the six seeded answers must produce the
expected labels, plus the Unknown edge case and the verdict rules.
Run:  pytest -q
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.checker import check_claim, load_seeded, verdict_for
from app.claims import extract_claims
from app.report import build_report


def _labels_for(seeded_id):
    data = load_seeded()
    item = next(a for a in data["seeded_answers"] if a["id"] == seeded_id)
    return [check_claim(c["topic"], c["value"], c["text"])["label"]
            for c in item["claims"]], item["expected_verdict"]


def test_c1_all_current():
    labels, verdict = _labels_for("C1")
    assert labels == ["Current", "Current"]
    assert verdict_for(labels) == "Safe to use"


def test_c2_all_current():
    labels, verdict = _labels_for("C2")
    assert labels == ["Current", "Current"]
    assert verdict_for(labels) == "Safe to use"


def test_c3_all_current():
    labels, verdict = _labels_for("C3")
    assert labels == ["Current", "Current"]
    assert verdict_for(labels) == "Safe to use"


def test_s1_superseded_washout():
    labels, verdict = _labels_for("S1")
    assert labels == ["Superseded"]
    assert verdict_for(labels) == "Do not use"


def test_s2_both_superseded():
    labels, verdict = _labels_for("S2")
    assert labels == ["Superseded", "Superseded"]
    assert verdict_for(labels) == "Do not use"


def test_s3_both_superseded():
    labels, verdict = _labels_for("S3")
    assert labels == ["Superseded", "Superseded"]
    assert verdict_for(labels) == "Do not use"


def test_u1_unknown_edge_case():
    labels, verdict = _labels_for("U1")
    assert labels == ["Unknown"]
    assert verdict_for(labels) == "Needs human review"


def test_free_text_s1_matches_seeded():
    # Pasting S1 as free text must give the same verdict as the seeded button.
    text = "Washout is 14 days before randomisation."
    report = build_report(text, extract_claims(text), "seeded-offline")
    assert report["verdict"] == "Do not use"
    assert report["claims"][0]["label"] == "Superseded"


def test_free_text_c1_matches_seeded():
    text = "Washout is 28 days before randomisation, and participants must fast 10 hours before labs."
    report = build_report(text, extract_claims(text), "seeded-offline")
    assert report["verdict"] == "Safe to use"
    assert [c["label"] for c in report["claims"]] == ["Current", "Current"]


def test_corrected_answer_uses_current_clause_only():
    text = "Washout is 14 days before randomisation."
    report = build_report(text, extract_claims(text), "seeded-offline")
    assert "28 days" in report["corrected_answer"]
    assert "14 days" not in report["corrected_answer"]


def test_unknown_never_guessed():
    result = check_claim("pregnancy_testing", 14,
                         "Pregnancy testing must be repeated every 14 days.")
    assert result["label"] == "Unknown"

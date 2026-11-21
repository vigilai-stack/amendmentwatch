"""AmendmentWatch — a stale-answer detector for clinical trial protocols.

Endpoints:
  GET  /            one-page UI
  GET  /health      {"status": "ok", "protocol_version_in_force": "3", ...}
  GET  /api/seeded  the 6 seeded answers (+ U1 Unknown edge case)
  GET  /demo/{id}   full report for a seeded answer (offline seeded mode)
  POST /api/check   check a pasted answer (also aliased as /api/brief)
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import bifrost_client, tavily_client
from app.checker import load_protocols, load_seeded, verdict_for
from app.claims import extract_claims
from app.report import build_report

load_dotenv()
BASE = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="AmendmentWatch",
    description="Checks a protocol answer claim by claim against the protocol "
                "version in force. Synthetic data only — not medical advice.",
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


class CheckRequest(BaseModel):
    answer: str
    seeded_id: str | None = None


def _live_mode() -> str:
    if tavily_client.tavily_available() or bifrost_client.bifrost_available():
        return "live"
    return "seeded-offline"


def _seeded_report(seeded_id: str) -> dict:
    seeded = load_seeded()
    for item in seeded["seeded_answers"]:
        if item["id"] == seeded_id:
            claims = [{"topic": c["topic"], "value": c["value"], "text": c["text"]}
                      for c in item["claims"]]
            report = build_report(item["text"], claims, _live_mode())
            report["seeded_id"] = seeded_id
            report["expected_verdict"] = item["expected_verdict"]
            return report
    raise HTTPException(status_code=404, detail=f"No seeded answer {seeded_id}")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": "AmendmentWatch",
        "protocol": "SYNTH-201",
        "protocol_version_in_force": "3",
        "tavily_available": tavily_client.tavily_available(),
        "bifrost_available": bifrost_client.bifrost_available(),
        "mode": _live_mode(),
    }


@app.get("/")
def index():
    return FileResponse(BASE / "static" / "index.html")


@app.get("/api/seeded")
def seeded():
    data = load_seeded()
    return {"study": data["study"], "current_version": data["current_version"],
            "answers": [{"id": a["id"], "label": a["label"],
                         "text": a["text"],
                         "expected_verdict": a["expected_verdict"]}
                        for a in data["seeded_answers"]]}


@app.get("/demo/{seeded_id}")
def demo(seeded_id: str):
    return _seeded_report(seeded_id)


@app.post("/api/check")
def check(req: CheckRequest):
    if req.seeded_id:
        return _seeded_report(req.seeded_id)
    if not req.answer or not req.answer.strip():
        raise HTTPException(status_code=400, detail="Provide an answer to check.")
    claims = extract_claims(req.answer)
    report = build_report(req.answer, claims, _live_mode())
    # Tavily re-verification for external references, attached as evidence.
    # It never changes a label; a failed call degrades to a note.
    report["tavily"] = tavily_client.search(req.answer[:200])
    return report


@app.post("/api/brief")
def brief(req: CheckRequest):
    return check(req)


@app.get("/api/protocol")
def protocol():
    return load_protocols()

# AmendmentWatch

**Paste an AI-generated answer to a site question. AmendmentWatch checks every claim against the protocol version in force — and flags the ones that were true once, and are false now.**

Built for the Global AI Hackathon (HackCulture / Geek Room), theme **Stale-Answer Detector**, solo by Sangeeta Sinha. Submission deadline: Saturday, November 21, 2026, 11:59 p.m.

The worked example: under protocol version 2, the washout period is 14 days. Version 3 amends it to 28 days. A site that keeps quoting the version 2 answer enrols a participant too early — that can become a protocol deviation for every participant enrolled on the stale rule. 76% of Phase 2/3 protocols are amended, on average 3.3 times, and old answers are never re-checked.

## For judges — no Bifrost install, no API keys needed

**Judges: you do not need to install Bifrost, Tavily, or any API key.** AmendmentWatch runs fully in seeded-offline mode with no keys — see `JUDGES.md` for the 3-step run and the 60-second click-through. Bifrost and Tavily are optional live enhancements only; they never change a label. Pre-run outputs are in `demo/`.

Precise framing: **Bifrost is a local gateway, not a model** (code: `app/bifrost_client.py`, default `http://localhost:8080/v1`). **OpenAI gpt-4o-mini is the model Bifrost calls, for plain-language explanations only.** Claim extraction is rule-based (`app/claims.py`). The deterministic checker (`app/checker.py`) decides every label — Current / Superseded / Unknown. In seeded-offline mode neither Bifrost nor OpenAI runs at all. Tavily is a separate live search integration; it also never changes a label. Problem Statement 06 requires both Tavily and Bifrost integration — that is why Bifrost is named, as the gateway, not as a model.

## Labels

| Label | Meaning |
|---|---|
| **Current** | The claim matches protocol v3 (in force). Shown with the clause, section, version and effective date. |
| **Superseded** | The claim matched an earlier version but the rule has changed. Old and new clause shown side by side, with the amendment that changed it. |
| **Unknown** | The current protocol text does not settle this claim. A human must confirm it. AmendmentWatch never guesses. |

**Verdict rules:** any Superseded claim → **Do not use**. No Superseded but any Unknown → **Needs human review**. All Current → **Safe to use** against the version in force.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open http://127.0.0.1:8000 — click a seeded answer, or paste your own. Print / save as PDF from the page (print CSS included).

No API keys are needed to run the demo: without keys the app runs in **seeded-offline mode** and all six seeded answers work.

## API keys (optional, for live mode)

Copy `.env.example` to `.env` and fill in:

- `TAVILY_API_KEY` — Tavily, for re-verifying external references cited in an answer.
- `BIFROST_API_KEY` — the key Bifrost uses to call OpenAI gpt-4o-mini, for plain-language explanations of a verdict only. Claim extraction is rule-based, not done by the model.
- `BIFROST_BASE_URL` (default `http://localhost:8080/v1`), `BIFROST_MODEL` (default `gpt-4o-mini`).

If a live call fails or is slow, the demo degrades to seeded-offline mode and says so — it never crashes, and Tavily / the model never change a label the deterministic checker settled.

## Endpoints

| Endpoint | What it does |
|---|---|
| `GET /` | One-page UI: paste box, seeded buttons, report |
| `GET /health` | Status, protocol version in force, which APIs are available |
| `GET /api/seeded` | The 6 seeded answers (+ U1 Unknown edge case) |
| `GET /demo/{id}` | Full report for a seeded answer, e.g. `/demo/S1` |
| `POST /api/check` | Check a pasted answer `{"answer": "..."}` (aliased as `/api/brief`) |
| `GET /api/protocol` | Protocol v1–v3 as structured JSON |

## Try it

- **S1 (stale):** "Washout is 14 days before randomisation." → Superseded, §5.2 was 14 days in v1/v2, is 28 days in v3.
- **S2 (stale):** "Adults 18 and over may enrol; hold the dose only if ALT exceeds 3× ULN." → both claims Superseded (§4.1, §7.1).
- **S3 (stale):** "If a visit is missed, reschedule within 7 days; fasting is 8 hours." → both Superseded (§8.4 changed in v2, §9.2 in v3).
- **C1–C3 (current):** all Current → Safe to use.
- **U1 (unknown):** pregnancy-testing interval — the protocol never addresses it → Unknown, Needs human review.

## Clause changes across versions (SYNTH-201, fictional Phase 2 study)

| Clause | v1 | v2 | v3 — in force |
|---|---|---|---|
| §4.1 Minimum age | 18 years | 18 years | **21 years** |
| §5.2 Washout period | 14 days | 14 days | **28 days** |
| §6.3 HbA1c ceiling | 9.0% | 9.5% | 9.5% |
| §7.1 Dose hold (ALT) | > 3× ULN | > 3× ULN | **> 2× ULN** |
| §8.4 Missed visit window | 7 days | **5 days** | 5 days |
| §9.2 Fasting before labs | 8 hours | 8 hours | **10 hours** |

Amendment 1 (v1→v2, effective 2025-06-01): missed-visit window 7→5 days, HbA1c 9.0%→9.5%.
Amendment 2 (v2→v3, effective 2026-02-01): age 18→21, washout 14→28 days, dose-hold ALT 3×→2× ULN, fasting 8→10 hours.

## How it works

1. **Extract** claims from the answer with the rule-based extractor in `app/claims.py`. OpenAI gpt-4o-mini, reached through the Bifrost local gateway, explains a verdict in plain language — it never decides a label and never extracts claims.
2. **Check** each claim against v3 first, then v1/v2 — a match in an old version proves Superseded.
3. **Re-verify** external references with Tavily, attached as evidence.
4. **Score** Current / Superseded / Unknown, build the corrected answer from cited clauses only, and return the report.

Stack: FastAPI, Tavily, Bifrost (local gateway to OpenAI gpt-4o-mini, explanations only), no database, stateless per request. See `app/checker.py` for the deterministic core, `app/claims.py` for extraction, `app/tavily_client.py` and `app/bifrost_client.py` for the optional live calls, `app/report.py` for the report builder.

## Honest limits

- Synthetic data only: fictional protocol SYNTH-201, fictional answers, no real patient data, no real protocol or sponsor document.
- It checks text against a document; it does not give medical advice. Decisions stay with the investigator and medical monitor.
- Unknown means a human must check — the tool does not guess.
- Not tested with real sites, sponsors, or protocols. No users, pilots, customers, revenue, or results are claimed.

## Tests

```bash
pip install pytest
pytest -q
```

Tests assert the six seeded answers produce their expected labels (C1–C3 all Current, S1–S3 Superseded), the U1 Unknown edge case, that pasting S1/C1 as free text matches the seeded buttons, and that the corrected answer uses only clauses in force.

## AI disclosure

This project was built with AI assistance (Muse) — Sangeeta Sinha directed the design, reviewed the code, and owns the submission. The runtime AI is OpenAI gpt-4o-mini, reached through the Bifrost local gateway (explanations only), and Tavily search; drafting/build assistance is a tool, not authorship of the project.

## Future work

- Monitor amendment feeds and re-check a whole FAQ library on each amendment.
- Structured-clause import for real protocols (with validation and human review).
- CTMS / EDC integrations.

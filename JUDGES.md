# For judges — read this first (2 minutes)

**You do not need to install Bifrost. You do not need Tavily, OpenAI, or any API key. You do not need to install anything except Python packages.**

AmendmentWatch runs fully in **seeded-offline mode** with no keys and no Bifrost. The deterministic checker decides every label. Tavily and Bifrost are optional live enhancements only — they never change a label, and the demo is complete without them.

## Run it in 3 steps

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

Or one click: `./run.sh` (Mac/Linux) or `run.bat` (Windows).

Then open http://127.0.0.1:8000

## What to click (60 seconds)

The dashboard opens with a header showing the SYNTH-201 v3 badge and the
seeded-offline mode badge, a paste-an-answer box on the left, and the seven
seeded demo buttons underneath it — each with a one-line description and a
Stale / Current / Unknown tag. The report appears on the right.

1. Click **S1** — "Stale washout — 14 days (v2) vs 28 days (v3)" → red
   **Do not use** banner, freshness 0/100, old clause struck through beside
   the v3 clause, corrected answer: 28 days.
2. Click **C1** — "Current — washout 28 days, fasting 10 hours" → green
   **Safe to use** banner, freshness 100/100 on both claims.
3. Click **U1** — "Unknown — pregnancy-testing interval" → amber
   **Needs human review** banner, no freshness score — the tool never guesses.
4. Or paste any answer in the box and press **Check this answer** — the same
   verdict banner, claim table, old-vs-new clauses, and corrected answer appear.
   Print / save as PDF from the button above the seeded demos.

## No time to run it? Read the pre-run outputs

- `demo/demo-output-S1.json` — the exact report the app returns for S1, captured live with no keys.
- `demo/demo-output-C1.json` — the exact report for C1.

## What Bifrost and Tavily actually do here

- **Bifrost** is a local gateway the *developer* runs to reach an LLM for one-sentence explanations. Judges do not run it. If it is absent, explanations fall back to the deterministic reason strings — labels and verdicts are identical.
- **Tavily** re-verifies external references cited in an answer. With no key, that step is skipped and noted in the report. Labels and verdicts are identical.

`GET /health` proves this: with no keys it returns `"mode": "seeded-offline"`, `"tavily_available": false`, `"bifrost_available": false`, and the app still returns correct verdicts.

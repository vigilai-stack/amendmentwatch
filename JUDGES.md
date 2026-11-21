# For judges — read this first (2 minutes)

## Live demo — use this first

**Live demo: https://huggingface.co/spaces/ssinha/amendmentwatch** — Gradio, runs on ZeroGPU, no install, no API keys.

Verified live: **S1 → Do not use, C1 → Safe to use, U1 → Needs human review.**

**Judge note:** Hugging Face shows a "Guest quota reached" popup to visitors who are not logged in. Log in to Hugging Face with a free account first, then open the link — no PRO subscription is needed. If you do not want to log in, the fallback is the GitHub repo https://github.com/vigilai-stack/amendmentwatch — run `./run.sh` / `run.bat`, or read `demo/demo-output-S1.json` and `demo/demo-output-C1.json` for pre-run results.

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
seeded demo buttons underneath it — in a dark cyberpunk theme (neon cyan/magenta, monospace). The footer credits the builder in large bold neon text: Sangeeta Sinha, Sangeeta@vigilaisolutions.com. — each with a one-line description and a
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

- **Bifrost** is a local gateway, not a model — the *developer* runs it (default `http://localhost:8080/v1`) to reach OpenAI gpt-4o-mini for one-sentence explanations of a verdict the checker has already decided. It does not extract claims and does not decide labels. Judges do not run it. If it is absent, explanations fall back to the deterministic reason strings — labels and verdicts are identical. In seeded-offline mode neither Bifrost nor OpenAI runs at all.
- **Tavily** re-verifies external references cited in an answer. With no key, that step is skipped and noted in the report. Labels and verdicts are identical.

`GET /health` proves this: with no keys it returns `"mode": "seeded-offline"`, `"tavily_available": false`, `"bifrost_available": false`, and the app still returns correct verdicts.

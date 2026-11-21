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

1. Click **S1** — "Washout is 14 days" → **Do not use**. §5.2 was 14 days in v2, is 28 days in v3. Corrected answer: 28 days.
2. Click **C1** — all claims Current → **Safe to use**.
3. Click **U1** — pregnancy-testing interval → **Unknown, Needs human review**. The tool never guesses.

## No time to run it? Read the pre-run outputs

- `demo/demo-output-S1.json` — the exact report the app returns for S1, captured live with no keys.
- `demo/demo-output-C1.json` — the exact report for C1.

## What Bifrost and Tavily actually do here

- **Bifrost** is a local gateway the *developer* runs to reach an LLM for one-sentence explanations. Judges do not run it. If it is absent, explanations fall back to the deterministic reason strings — labels and verdicts are identical.
- **Tavily** re-verifies external references cited in an answer. With no key, that step is skipped and noted in the report. Labels and verdicts are identical.

`GET /health` proves this: with no keys it returns `"mode": "seeded-offline"`, `"tavily_available": false`, `"bifrost_available": false`, and the app still returns correct verdicts.

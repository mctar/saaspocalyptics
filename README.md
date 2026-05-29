# SaaSpocalyptics

A beautiful, daily-refreshed tracker for the post-**SaaSpocalypse** market — the
2026 software sell-off driven by fears that AI would make existing SaaS offerings
obsolete. It shows year-to-date performance for three buckets:

- **S&P 500 Software & Services** — the index incumbents (CRM, NOW, WDAY, ADBE, …)
- **Big SaaS Outside the Index** — large but excluded names (Snowflake, MongoDB, …)
- **Global System Integrators** — the consultancies in the same orbit (Accenture, Capgemini, …)

## How it works

Two halves joined by one static JSON file:

```
data/fetch.py   ──reads──> data/tickers.yaml
      │ (yfinance, YTD daily closes)
      └──writes──> public/data/market.json ──fetched at runtime──> React app (src/)
```

- **`data/fetch.py`** pulls YTD daily adjusted closes per ticker, computes YTD %,
  off-low %, off-high %, and a downsampled sparkline, and writes `market.json`.
  Tickers that return no data are logged and skipped — a bad symbol never breaks the run.
- **`src/`** is a React + Vite + Tailwind app that fetches `data/market.json` and renders
  sortable, searchable buckets with hand-coded SVG sparklines.

The universe lives in **`data/tickers.yaml`** — edit that file to add, remove, or
recategorise companies. No code changes needed.

## Develop

```bash
# data
python3 -m venv .venv
.venv/bin/pip install -r data/requirements.txt
.venv/bin/python data/fetch.py          # writes public/data/market.json
.venv/bin/python data/fetch.py --dry-run # fetch + summary, no write

# app
npm install
npm run dev      # http://localhost:5173
npm run build    # -> dist/ (includes data/market.json and CNAME)
```

## Deploy

Publishing mirrors the `vordur` pattern: build locally, push `dist/` to the
`gh-pages` branch. `deploy.sh` runs the whole chain (fetch → build → push).

One-time setup:

1. Create the GitHub repo and an empty `gh-pages` branch.
2. Set `REPO` in `deploy.sh` (default: `git@github.com:mctar/saaspocalyptics.git`).
3. Confirm the custom domain in `public/CNAME` (placeholder:
   `saaspocalyptics.btrbot.com`) and point a DNS CNAME at `mctar.github.io`.

Then wire a weekday cron entry (after the US close settles, ~21:30 UTC):

```cron
30 21 * * 1-5  /Users/thordur/experiments/saaspocalyptics/deploy.sh >> /tmp/saaspocalyptics.log 2>&1
```

## Notes

- Percentage changes are currency-neutral, so non-USD names (Capgemini, TCS) are
  shown in local-currency prices without FX conversion — honest and simple.
- `auto_adjust=True` means historical prices are split-adjusted, so YTD % stays
  correct across any 2026 stock splits.
- Not investment advice. A market-watching toy, not a terminal.

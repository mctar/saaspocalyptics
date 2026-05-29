---
name: saaspocalyptics
description: Pull live SaaSpocalyptics market data and write a short FT-style market brief on the SaaS sector's year-to-date performance. Use whenever Thordur says "saaspocalyptics", "saas brief", "saas market", "saaspocalypse", "how are the saas stocks doing", "software stocks YTD", "saas tracker", "market brief on saas", or asks how the tracked SaaS names / GSIs are performing this year. The skill fetches the public, hourly-refreshed feed at saaspocalyptics.btrbot.com (it never touches the backend), prints a numbers snapshot, and turns it into a tight editorial dek in the house voice. Also use to answer ad-hoc questions about a specific company, bucket, or the winners/losers spread — the snapshot has the figures. Do NOT use it to change the website or the data pipeline; this is a read-only client.
metadata:
  audience: Thordur Arnason — SaaS market reporting, ExCo updates
  owner: Thordur Arnason (Gervi Labs)
  version: "0.1"
  status: Working draft. Read-only client of the public saaspocalyptics.btrbot.com feed. Fetch + snapshot + brief. No backend coupling.
---

# SaaSpocalyptics Market Brief — Instruction

## 1. Purpose

Live SaaS market data in, a short editorial brief out.

[SaaSpocalyptics](https://saaspocalyptics.btrbot.com) tracks the year-to-date
performance of the major SaaS names — the S&P 500 software incumbents, the big
SaaS heavyweights outside the index (Snowflake's crowd), and the global system
integrators in their orbit — through the 2026 "SaaSpocalypse", the AI-driven
software sell-off and its uneven recovery.

This skill pulls that data and writes a brief about it: a tight, FT-style read on
where the sector stands today and which way the winners and losers are splitting.
It can also just answer a direct question ("how's Snowflake doing?", "which GSIs
are worst?") straight from the snapshot.

## 2. When to run

Trigger on any of: "saaspocalyptics", "saas brief", "saas market", "saaspocalypse",
"how are the saas stocks", "software stocks YTD", "saas tracker", "market brief on
saas", or any request for the state of the tracked SaaS names / GSIs this year.

For a brief, run the full pipeline. For a one-off factual question, run the script
and answer from the snapshot — no brief needed.

## 3. How it works

The data is a public, read-only JSON feed, regenerated hourly on the server
(hugin → GitHub Pages). This skill is purely a client of it:

```
https://saaspocalyptics.btrbot.com/data/market.json
```

It touches **nothing** on the backend — not hugin, the refresh timer, the webapp,
or the gh-pages branch. There is no API key and no local data file. Each run
reflects the latest published snapshot (its `asOf` / `generatedAt` stamps tell you
how fresh it is).

## 4. The pipeline

Three steps. Use a TodoList only if also answering follow-ups.

### Step 1 — Pull the snapshot

```bash
python scripts/market.py            # readable snapshot (default)
python scripts/market.py --json     # raw market.json, if you need every figure
```

The snapshot gives you: the `asOf` date, the spread (how many up / down <25% /
down 25%+), the median YTD, the overall biggest winner and loser, and per bucket
the median, the in-the-red count, and the top three winners and losers. That is
everything a brief needs.

If the host's CA store can't verify TLS (a stock macOS system python, say), add
`--insecure` — the feed is public and read-only, so nothing sensitive is exposed.

### Step 2 — Read the numbers

Read the snapshot. Note the `asOf` date (lead the brief with it). Pick the story
the data is telling today: Is the recovery broadening or still just a handful of
names? Which bucket is healthiest, which is still in the brimstone? Is the
standout winner real acceleration or a single outlier dominating the headline?

### Step 3 — Write the brief

Compose the brief in the house voice (see §5). Cite only figures that appear in
the snapshot — never invent or estimate a number. Hand it back in chat; do not
write files unless Thordur asks.

## 5. The brief — format and voice

The register is the website's: Financial Times editorial, dry and exact, never
hype. Structure:

- **Standfirst** — one or two sentences leading with the breadth ("As of 29 May,
  41 of 57 tracked names sit below where they started 2026…") and the day's
  divergence in plain terms.
- **Body** — 2–3 short paragraphs, ~120–160 words total. Walk the split: who's
  escaping the SaaSpocalypse (and why, if the data implies it — acceleration,
  AI demand), who's still under it, and how the three buckets compare. Name the
  standouts with their figures.
- **A caveat line** if an outlier distorts the picture (e.g. a single +200% name
  pulling the "biggest winner" headline) — call it out honestly.

Rules:

- **Verbatim figures only.** Every number comes from the snapshot.
- **No hype, no emojis, no exclamation marks.** Claret-and-ink tone, not a
  newsletter blast.
- **Not investment advice** — it's a market read. Don't recommend buying/selling.
- **Lead with the date.** Freshness is the point of a live feed.
- Keep it short. A brief is a brief.

## 6. Bundled script

| Script | Does |
|---|---|
| `scripts/market.py` | Fetches the live feed and prints a readable snapshot (default) or the raw JSON (`--json`). Stdlib only — no dependencies. `--url` overrides the feed; `--insecure` skips TLS verification for a broken CA store (public feed, safe). |

## 7. Environment notes and gotchas

- **Needs outbound internet** to reach `saaspocalyptics.btrbot.com`. The Cowork
  sandbox has it.
- **No dependencies.** Pure Python standard library; runs on any Python 3.9+.
- **The feed can be briefly stale.** It refreshes hourly and only republishes when
  prices move, so off-hours the `asOf`/`generatedAt` may be from the last change.
  If a server-side fetch is ever rate-limited, the backend keeps the last-good
  data rather than publishing empty — so the feed is always populated, just maybe
  an hour or two behind. Always quote the `asOf` date; don't imply live ticks.
- **Read-only.** This skill never writes to the site or the pipeline. To change
  what's tracked or how it's displayed, that's the saaspocalyptics repo, not here.

---

*Skill version 0.1 — read-only client of the saaspocalyptics.btrbot.com feed.*

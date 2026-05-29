#!/usr/bin/env python3
"""Smoke test for the saaspocalyptics skill.

Confirms the public feed is reachable and well-formed, and that the snapshot
renders. No dependencies, no side effects. Exit 0 = pass, 1 = fail.

  python smoke_test.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))
import market  # noqa: E402

REQUIRED_TOP = {"asOf", "generatedAt", "baselineDate", "buckets"}
REQUIRED_FIELDS = {"ticker", "name", "ytdPct", "last", "currency"}


def main() -> int:
    # Verify by default; fall back to insecure for a broken CA store (public feed).
    try:
        data = market.fetch(market.FEED_URL)
    except SystemExit:
        print("note: TLS verify failed; retrying --insecure (public feed)")
        data = market.fetch(market.FEED_URL, insecure=True)

    problems = []

    missing = REQUIRED_TOP - set(data)
    if missing:
        problems.append(f"missing top-level keys: {missing}")

    rows = market.all_rows(data)
    if not rows:
        problems.append("feed has zero companies (should never happen — backend keeps last-good)")

    for c in rows[:5]:
        miss = REQUIRED_FIELDS - set(c)
        if miss:
            problems.append(f"{c.get('ticker', '?')} missing fields: {miss}")
            break

    # Snapshot must render without throwing.
    try:
        text = market.snapshot(data)
        assert "SaaSpocalyptics" in text
    except Exception as exc:
        problems.append(f"snapshot render failed: {exc}")

    if problems:
        print("FAIL")
        for p in problems:
            print("  -", p)
        return 1

    print(f"PASS — {len(rows)} companies, as of {data['asOf']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

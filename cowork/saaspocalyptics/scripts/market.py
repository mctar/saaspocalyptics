#!/usr/bin/env python3
"""Pull live SaaSpocalyptics market data and print a snapshot to brief from.

Zero dependencies — Python standard library only. It reads the public, already
published feed at saaspocalyptics.btrbot.com and nothing else: it never touches
the backend (hugin, the systemd timer, the webapp, or the gh-pages branch). The
feed is regenerated hourly on the server, so each run reflects the latest data.

Usage:
  python scripts/market.py              # readable snapshot (default)
  python scripts/market.py --json       # raw market.json, pretty-printed
  python scripts/market.py --url <URL>  # override the feed URL (for testing)
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.request

FEED_URL = "https://saaspocalyptics.btrbot.com/data/market.json"


def fetch(url: str, insecure: bool = False) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "saaspocalyptics-skill/1.0"})
    # The feed is public and read-only, so TLS exists for integrity, not secrecy.
    # Verify by default; --insecure is an escape hatch for hosts with a broken
    # CA store (e.g. a stock macOS system python) and exposes no secrets.
    ctx = ssl._create_unverified_context() if insecure else None
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except ssl.SSLCertVerificationError:
        sys.exit(
            f"error: TLS verification failed fetching {url}\n"
            "  This host's CA store can't verify the cert. The feed is public and\n"
            "  read-only, so it's safe to retry with --insecure."
        )
    except Exception as exc:  # network, HTTP, JSON — all surface the same way
        sys.exit(f"error: could not fetch {url}\n  {exc}")


def all_rows(data: dict) -> list[dict]:
    return [c for b in data["buckets"].values() for c in b["members"]]


def median(values: list[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    mid = len(s) // 2
    return s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2


def fmt_pct(v: float) -> str:
    return f"{'+' if v > 0 else ''}{v:.1f}%"


def line(c: dict) -> str:
    cur = "" if c["currency"] == "USD" else f" {c['currency']}"
    return f"    {fmt_pct(c['ytdPct']):>7}  {c['ticker']:<8} {c['name']}{cur}"


def snapshot(data: dict) -> str:
    rows = all_rows(data)
    out: list[str] = []
    out.append(f"SaaSpocalyptics — YTD 2026 as of {data['asOf']}")
    out.append(f"(feed generated {data.get('generatedAt', '?')}, baseline {data['baselineDate']})")
    out.append("")

    up = [c for c in rows if c["ytdPct"] >= 0]
    deep = [c for c in rows if c["ytdPct"] <= -25]
    mild = [c for c in rows if -25 < c["ytdPct"] < 0]
    out.append(
        f"The spread — {len(rows)} companies: "
        f"{len(up)} up, {len(mild)} down <25%, {len(deep)} down 25%+"
    )
    out.append(f"Median YTD across all names: {fmt_pct(median([c['ytdPct'] for c in rows]))}")
    out.append("")

    srt = sorted(rows, key=lambda c: c["ytdPct"])
    loser, winner = srt[0], srt[-1]
    out.append(f"Biggest winner: {winner['name']} ({winner['ticker']}) {fmt_pct(winner['ytdPct'])}")
    out.append(f"Biggest loser:  {loser['name']} ({loser['ticker']}) {fmt_pct(loser['ytdPct'])}")
    out.append("")

    for bucket in data["buckets"].values():
        members = bucket["members"]
        if not members:
            continue
        ys = [c["ytdPct"] for c in members]
        in_red = sum(1 for y in ys if y < 0)
        s = sorted(members, key=lambda c: c["ytdPct"], reverse=True)
        out.append(f"## {bucket['label']}  ({len(members)} names)")
        out.append(f"   {bucket.get('blurb', '')}")
        out.append(f"   median {fmt_pct(median(ys))} · {in_red}/{len(members)} in the red")
        out.append("   winners:")
        out.extend(line(c) for c in s[:3])
        out.append("   losers:")
        out.extend(line(c) for c in s[-3:][::-1])
        out.append("")

    return "\n".join(out).rstrip()


def main() -> None:
    p = argparse.ArgumentParser(description="Pull live SaaSpocalyptics market data.")
    p.add_argument("--json", action="store_true", help="print raw market.json")
    p.add_argument("--url", default=FEED_URL, help="override the feed URL")
    p.add_argument("--insecure", action="store_true", help="skip TLS verification (public feed)")
    args = p.parse_args()

    data = fetch(args.url, insecure=args.insecure)
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(snapshot(data))


if __name__ == "__main__":
    main()

# Installing the SaaSpocalyptics skill

A read-only Cowork skill that pulls the live SaaSpocalyptics feed and writes a
short market brief. No dependencies, no API keys, no backend access.

## Install

1. In Cowork: **Settings → Skills → Install from file**.
2. Pick `saaspocalyptics.skill`.
3. Done. Trigger it by asking for a "saas brief", "saaspocalyptics", "how are the
   saas stocks doing", etc.

## Verify

From the skill folder:

```bash
python smoke_test.py            # PASS = feed reachable + well-formed
python scripts/market.py        # prints the current snapshot
```

If you see a TLS verification error (some stock Python installs ship without a
working CA store), add `--insecure` — the feed is public and read-only, so
nothing sensitive is exposed:

```bash
python scripts/market.py --insecure
```

## What it touches

Nothing but the public feed at `https://saaspocalyptics.btrbot.com/data/market.json`.
It does not connect to the server (hugin), the refresh timer, the webapp, or the
gh-pages branch. To change what's tracked, edit the saaspocalyptics repo instead.

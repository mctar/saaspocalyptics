#!/usr/bin/env bash
# Refresh market data, build the app, and publish dist/ to the gh-pages branch.
# Intended to be called by cron each weekday after the US close settles.
#
# One-time setup: create the GitHub repo and an empty gh-pages branch, then set
# REPO below. The CNAME lives in public/ so Vite copies it into dist/ on build.
set -euo pipefail

# Cron runs with a bare PATH; make sure Homebrew's node/npm are findable.
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SCRIPT_DIR/.venv/bin/python"
DIST_DIR="$SCRIPT_DIR/dist"
DEPLOY_DIR="/tmp/saaspocalyptics-ghp"
REPO="git@github.com:mctar/saaspocalyptics.git"

cd "$SCRIPT_DIR"

# 1. Refresh data, then build the static site (dist/ includes data/ and CNAME).
"$VENV" "$SCRIPT_DIR/data/fetch.py"
npm run build

# 2. Publish dist/ to gh-pages.
rm -rf "$DEPLOY_DIR"
git clone --branch gh-pages --single-branch --depth 1 "$REPO" "$DEPLOY_DIR" 2>/dev/null

# Replace contents wholesale (so removed files disappear), keep .git.
find "$DEPLOY_DIR" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +
cp -R "$DIST_DIR"/. "$DEPLOY_DIR"/

cd "$DEPLOY_DIR"
git add -A
if git diff --cached --quiet; then
    echo "No changes to deploy."
else
    git commit -m "Update market data $(date -u +%Y-%m-%d)"
    git push origin gh-pages
    echo "Deployed."
fi

rm -rf "$DEPLOY_DIR"

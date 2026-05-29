#!/usr/bin/env bash
# Build saaspocalyptics.skill (a zip with a .skill extension) from the skill
# folder here, ready to upload via Cowork's "Install from file".
#
# Output: ~/Desktop/saaspocalyptics.skill  (override with OUT=/path/to/x.skill)
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$HERE/saaspocalyptics"
OUT="${OUT:-$HOME/Desktop/saaspocalyptics.skill}"

if [[ ! -d "$SRC" ]]; then
  echo "error: $SRC does not exist" >&2
  exit 1
fi

# The zip's inner directory must be named after the skill (saaspocalyptics).
rm -f "$OUT"
( cd "$HERE" && zip -qr "$OUT" saaspocalyptics \
    -x "*.DS_Store" -x "*/__pycache__/*" )

echo "wrote $OUT"
echo "size: $(du -h "$OUT" | cut -f1)"
echo
echo "contents:"
unzip -l "$OUT" | sed 's/^/  /'
echo
echo "next: Cowork → Settings → Skills → Install from file → pick this .skill"

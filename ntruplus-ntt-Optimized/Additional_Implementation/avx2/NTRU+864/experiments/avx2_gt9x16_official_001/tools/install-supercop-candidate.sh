#!/bin/sh
set -eu
if [ "$#" -ne 1 ]; then
  echo "usage: $0 SUPERCOP_CAMPAIGN_ROOT" >&2
  exit 64
fi
experiment=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
repo=$(git -C "$experiment" rev-parse --show-toplevel)
exec python3 "$repo/scripts/install_supercop_candidate.py" \
  --campaign-root "$1" --experiment "$experiment" --parameter 864 \
  --implementation avx2-gt9x16-exp001

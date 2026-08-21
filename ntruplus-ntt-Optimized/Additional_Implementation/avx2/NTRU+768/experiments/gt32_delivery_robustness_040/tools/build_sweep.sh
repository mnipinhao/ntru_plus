#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
EXP=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SUPERCOP=${SUPERCOP:-/home/nuc/supercop-20260627}
BUILDER="$ROOT/experiments/gt32_compact_q24_037/tools/build_fixed_supercop.sh"
TARGET_ROOT="$SUPERCOP/crypto_kem/ntruplus768"

mkdir -p "$EXP/build"
for export in "$EXP"/exports/*; do
  name=$(basename "$export")
  target_name="avx2-040-$name"
  target="$TARGET_ROOT/$target_name"
  output="$EXP/build/$name-measure"
  if [ -e "$output" ]; then
    continue
  fi
  if [ -e "$target" ] || [ -L "$target" ]; then
    echo "temporary target already exists: $target" >&2
    exit 1
  fi
  ln -s "$export" "$target"
  cleanup() { unlink "$target" 2>/dev/null || true; }
  trap cleanup EXIT HUP INT TERM
  "$BUILDER" "$target_name" "$output"
  unlink "$target"
  trap - EXIT HUP INT TERM
done


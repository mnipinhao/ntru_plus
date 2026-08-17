#!/bin/sh
set -eu

supercop=${SUPERCOP:-/home/nuc/supercop-20260627}
name=${1:-avx2-gt-global-inverse-p-suffix}
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
target=$supercop/crypto_kem/ntruplus768/$name

"$root/tools/export_supercop_global_inverse.sh" "$target"
mv "$target/gt32_keygen.c" "$target/tile4_keygen_candidate.c"
cp "$root/src/tile4_keygen_candidate_p_suffix.c" "$target/gt32_keygen.c"
printf '%s\n' "$target"

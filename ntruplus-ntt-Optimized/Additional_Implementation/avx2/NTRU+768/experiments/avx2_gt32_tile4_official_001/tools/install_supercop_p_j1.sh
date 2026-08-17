#!/bin/sh
set -eu

supercop=${SUPERCOP:-/home/nuc/supercop-20260627}
name=${1:-avx2-gt-global-inverse-p-j1}
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
target=$supercop/crypto_kem/ntruplus768/$name

"$root/tools/export_supercop_global_inverse.sh" "$target"
mv "$target/gt32_keygen.c" "$target/tile4_keygen_candidate.inc"
cp "$root/src/tile4_keygen_candidate_p_j1.c" "$target/gt32_keygen.c"
cp "$root/src/tile4_baseinv_p_j1_soa_flat.c" "$target/gt32_baseinv_p_j1.c"
cp "$root/src/tile4_baseinv_p_j1_batch_asm.S" "$target/gt32_baseinv_p_j1_batch.s"
printf '%s\n' "$target"

#!/bin/sh
set -eu

supercop=${SUPERCOP:-/home/nuc/supercop-20260627}
name=${1:-avx2-hybrid-p-j1-official-enc-gt-dec}
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
target=$supercop/crypto_kem/ntruplus768/$name

"$root/tools/export_supercop_global_inverse.sh" "$target"
mv "$target/gt32_keygen.c" "$target/tile4_keygen_candidate.inc"
cp "$root/src/tile4_keygen_candidate_p_j1.c" "$target/gt32_keygen.c"
cp "$root/src/tile4_baseinv_p_j1_soa_flat.c" "$target/gt32_baseinv_p_j1.c"
cp "$root/src/tile4_baseinv_p_j1_batch_asm.S" "$target/gt32_baseinv_p_j1_batch.s"
cp "$root/src/tile4_official_enc_only.c" "$target/gt32_encap.c"
cp "$root/src/tile4_supercop_hybrid_api.c" "$target/gt32_kem_api.c"
printf '%s\n' "$target"

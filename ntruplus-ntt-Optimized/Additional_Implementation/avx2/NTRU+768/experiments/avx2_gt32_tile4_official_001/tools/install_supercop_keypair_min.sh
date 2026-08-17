#!/bin/sh
set -eu

supercop=${SUPERCOP:-/home/nuc/supercop-20260627}
name=${1:-avx2-gt-keypair-min}
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
official=$supercop/crypto_kem/ntruplus768/avx2
target=$supercop/crypto_kem/ntruplus768/$name

"$root/tools/export_supercop_global_inverse.sh" "$target"
mv "$target/gt32_keygen.c" "$target/tile4_keygen_candidate.inc"
cp "$root/src/tile4_keygen_candidate_p_j1.c" "$target/gt32_keygen.c"
cp "$root/src/tile4_baseinv_p_j1_soa_flat.c" "$target/gt32_baseinv_p_j1.c"
cp "$root/src/tile4_baseinv_p_j1_batch_asm.S" "$target/gt32_baseinv_p_j1_batch.s"
cp "$root/src/tile4_p_lambda_tables.c" "$target/gt32_p_lambda_tables.c"
rm -f "$target/gt32_encap.c" "$target/gt32_decap.c" \
	"$target/gt32_kem_api.c" "$target/gt32_baseinv_p.c" \
	"$target/gt32_baseinv_prepare.s" "$target/gt32_forward_bm_soa.s" \
	"$target/gt32_tile4_basemul.s" "$target/gt32_global_physical.s" \
	"$target/gt32_inverse_tail.s"
cp "$official/kem.c" "$target/tile4_official_kem.inc"
cp "$root/src/tile4_official_keypair_only.c" "$target/gt32_official_ops.c"
cp "$root/src/tile4_supercop_keypair_min_api.c" "$target/gt32_kem_api.c"

python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_tile4_core.s" \
	gt32_tile4_frontend_wide_raw_asm
python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_permutation_relaxed.s" \
	gt32_tile4_attr_forward_all_baseinv_p_l3_asm
python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_native_basemul.s" \
	gt_basemul_native_f0_j1_e0_asm_avx2
python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_q24_codec.s" \
	gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm

cat > "$target/CLEAN-MANIFEST.txt" <<'EOF'
implementation=avx2-gt-keypair-min
keypair=same CleanGT P-J1 BaseInv; finalizer-free F0xJ1 BM; SP1 Q24
encap=Official main
decap=Official main
variable=remove Encap-only and Decap-only GT code/data
EOF
find "$target" -maxdepth 1 -type f -print0 | sort -z | xargs -0 sha256sum \
	> "$target/SHA256SUMS"
printf '%s\n' "$target"

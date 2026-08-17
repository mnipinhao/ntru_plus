#!/bin/sh
set -eu

supercop=${SUPERCOP:-/home/nuc/supercop-20260627}
name=${1:-avx2-gt-encap-min}
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
official=$supercop/crypto_kem/ntruplus768/avx2
target=$supercop/crypto_kem/ntruplus768/$name

"$root/tools/export_supercop_global_inverse.sh" "$target"
rm -f "$target/gt32_keygen.c" "$target/gt32_decap.c" \
	"$target/gt32_kem_api.c" "$target/gt32_baseinv_p.c" \
	"$target/gt32_baseinv_prepare.s" "$target/gt32_native_basemul.s" \
	"$target/gt32_permutation_relaxed.s" "$target/gt32_global_physical.s" \
	"$target/gt32_inverse_tail.s" "$target/gt_baseinv_native.c"
cp "$official/kem.c" "$target/tile4_official_kem.inc"
cp "$root/src/tile4_official_keypair_only.c" "$target/gt32_official_ops.c"
cp "$root/src/tile4_supercop_encap_min_api.c" "$target/gt32_kem_api.c"

python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_tile4_core.s" \
	gt32_tile4_frontend_wide_raw_asm
python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_forward_bm_soa.s" \
	gt32_tile4_attr_forward_all_bm_soa_asm
python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_tile4_basemul.s" \
	gt32_tile4_basemul_general_soa_soa_to_soa_asm
python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_q24_codec.s" \
	gt32_q24_decode_soa_body_cage gt32_q24_decode_soa_asm \
	gt32_q24_encode_soa_lazy10788_asm \
	gt32_q24_encode_soa_encap_hr_h1_asm

cat > "$target/CLEAN-MANIFEST.txt" <<'EOF'
implementation=avx2-gt-encap-min
keypair=Official main
encap=same CleanGT Q24 SoA decode; N5-to-M; B3 general; H1 high-range Q24
decap=Official main
variable=remove Keypair-only and Decap-only GT code/data
EOF
find "$target" -maxdepth 1 -type f -print0 | sort -z | xargs -0 sha256sum \
	> "$target/SHA256SUMS"
printf '%s\n' "$target"

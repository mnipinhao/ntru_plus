#!/bin/sh
set -eu

supercop=${SUPERCOP:-/home/nuc/supercop-20260627}
name=${1:-avx2-gt-decap-min}
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
official=$supercop/crypto_kem/ntruplus768/avx2
target=$supercop/crypto_kem/ntruplus768/$name

"$root/tools/export_supercop_global_inverse.sh" "$target"
rm -f "$target/gt32_keygen.c" "$target/gt32_encap.c" "$target/gt32_kem_api.c"
cp "$official/kem.c" "$target/tile4_official_kem.inc"
cp "$root/src/tile4_official_keypair_only.c" "$target/gt32_keygen.c"
cp "$root/src/tile4_official_enc_only.c" "$target/gt32_encap.c"
cp "$root/src/tile4_supercop_decap_clean_api.c" "$target/gt32_kem_api.c"

# Unused GT experimental families. Official NTT/BaseInv/BM/pack stay because
# the control Keypair and Encap intentionally remain byte-for-byte Official.
rm -f "$target/gt32_baseinv_prepare.s" "$target/gt32_native_basemul.s" \
	"$target/gt32_permutation_relaxed.s" "$target/gt32_baseinv_p.c" \
	"$target/gt_baseinv_native.c"

python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_tile4_core.s" \
	gt32_tile4_frontend_wide_raw_asm
python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_forward_bm_soa.s" \
	gt32_tile4_attr_forward_all_bm_soa_asm
python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_tile4_basemul.s" \
	gt32_tile4_basemul_scale_soa_soa_to_m_private_asm \
	gt32_tile4_basemul_general_soa_soa_to_soa_asm
python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_global_physical.s" \
	gt32_global_inverse_core_asm
python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_inverse_tail.s" \
	gt32_tile4_inverse_tail_t9_isolated_private_asm
python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_q24_codec.s" \
	gt32_q24_decode_soa_body_cage gt32_q24_decode3_soa_asm \
	gt32_q24_encode_soa_asm gt32_q24_encode_soa_lazy10788_asm

cat > "$target/CLEAN-MANIFEST.txt" <<'EOF'
implementation=avx2-gt-decap-min
keypair=Official main
encap=Official main
decap=Q24 Decode3; B3-to-M; global inverse; T9; centered/lazy Q24 packs
benchmark_compiler=O3 + function/data sections + linker section GC
purpose=isolate the fastest GT Decap from unrelated GT Keypair/Encap geometry
EOF
find "$target" -maxdepth 1 -type f -print0 | sort -z | xargs -0 sha256sum \
	> "$target/SHA256SUMS"
printf '%s\n' "$target"

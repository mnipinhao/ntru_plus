#!/bin/sh
set -eu

supercop=${SUPERCOP:-/home/nuc/supercop-20260627}
name=${1:-avx2-gt-fastest-clean}
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
target=$supercop/crypto_kem/ntruplus768/$name

"$root/tools/export_supercop_global_inverse.sh" "$target"

# Keypair: typed P-J1 BaseInv -> finalizer-free F0xJ1 BM -> SP1 Q24.
mv "$target/gt32_keygen.c" "$target/tile4_keygen_candidate.inc"
cp "$root/src/tile4_keygen_candidate_p_j1.c" "$target/gt32_keygen.c"
cp "$root/src/tile4_baseinv_p_j1_soa_flat.c" "$target/gt32_baseinv_p_j1.c"
cp "$root/src/tile4_baseinv_p_j1_batch_asm.S" "$target/gt32_baseinv_p_j1_batch.s"

# These assembly implementations are not reachable from the selected clean
# Keypair/Encap/Decap call graph.  The clean benchmark compiler additionally
# uses section GC so unused C helpers and per-function Q24 sections disappear
# from the linked image as well.
rm -f \
	"$target/baseinv.s" \
	"$target/basemul.s" \
	"$target/invntt.s" \
	"$target/ntt.s" \
	"$target/pack.s" \
	"$target/gt32_baseinv_prepare.s"

# The original experiment assembly files are deliberately multi-variant.
# Prune their concrete function emissions so the clean source folder, not
# merely the linker, contains only the selected production call graph.
python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_tile4_core.s" \
	gt32_tile4_frontend_wide_raw_asm
python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_forward_bm_soa.s" \
	gt32_tile4_attr_forward_all_bm_soa_asm
python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_tile4_basemul.s" \
	gt32_tile4_basemul_scale_soa_soa_to_m_private_asm \
	gt32_tile4_basemul_general_soa_soa_to_soa_asm
python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_global_physical.s" \
	gt32_global_inverse_core_asm
python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_permutation_relaxed.s" \
	gt32_tile4_attr_forward_all_baseinv_p_l3_asm
python3 "$root/tools/prune_supercop_clean_asm.py" "$target/gt32_native_basemul.s" \
	gt_basemul_native_f0_j1_e0_asm_avx2

cat > "$target/CLEAN-MANIFEST.txt" <<'EOF'
implementation=avx2-gt-fastest-clean
keypair=P-J1 BaseInv; F0xJ1 finalizer-free native BM; SP1 Q24 pack
encap=Q24 SoA decode; N5-to-M; B3 general; H1 high-range Q24 pack
decap=Q24 Decode3; B3-to-M; global inverse; T9; centered/lazy Q24 packs
benchmark_compiler=O3 + function/data sections + linker section GC
purpose=remove unreachable experimental code from the linked benchmark image
EOF

find "$target" -maxdepth 1 -type f -print0 | sort -z | xargs -0 sha256sum \
	> "$target/SHA256SUMS"
printf '%s\n' "$target"

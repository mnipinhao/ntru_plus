#!/bin/sh
set -eu

supercop=${SUPERCOP:-/home/nuc/supercop-20260627}
name=${1:-avx2-gt-hotclosure-g0-unpruned}
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
target=$supercop/crypto_kem/ntruplus768/$name

"$root/tools/export_supercop_global_inverse.sh" "$target"

# Match the selected CleanGT operation semantics exactly.  Unlike
# install_supercop_fastest_clean.sh, deliberately retain every unselected
# multi-variant assembly emission so G0 and Gc isolate physical closure.
mv "$target/gt32_keygen.c" "$target/tile4_keygen_candidate.inc"
cp "$root/src/tile4_keygen_candidate_p_j1.c" "$target/gt32_keygen.c"
cp "$root/src/tile4_baseinv_p_j1_soa_flat.c" "$target/gt32_baseinv_p_j1.c"
cp "$root/src/tile4_baseinv_p_j1_batch_asm.S" \
	"$target/gt32_baseinv_p_j1_batch.s"

cat > "$target/CLEAN-MANIFEST.txt" <<EOF
implementation=$name
semantic_peer=avx2-gt-hotclosure-gc-pruned
keypair=P-J1 BaseInv; F0xJ1 finalizer-free native BM; SP1 Q24 pack
encap=Q24 SoA decode; N5-to-M; B3 general; H1 high-range Q24 pack
decap=Q24 Decode3; B3-to-M; global inverse; T9; centered/lazy Q24 packs
benchmark_compiler=O3 + function/data sections + linker section GC
purpose=G0 control retaining unreachable multi-variant assembly emissions
EOF

find "$target" -maxdepth 1 -type f -print0 | sort -z | xargs -0 sha256sum \
	> "$target/SHA256SUMS"
printf '%s\n' "$target"

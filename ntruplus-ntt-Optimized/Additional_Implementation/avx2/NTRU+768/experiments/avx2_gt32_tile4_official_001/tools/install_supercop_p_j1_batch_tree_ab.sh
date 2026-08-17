#!/bin/sh
set -eu

supercop=${SUPERCOP:-/home/nuc/supercop-20260627}
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

install_one()
{
	name=$1
	select=$2
	target=$supercop/crypto_kem/ntruplus768/$name

	"$root/tools/export_supercop_global_inverse.sh" "$target"
	mv "$target/gt32_keygen.c" "$target/tile4_keygen_candidate.inc"
	cp "$root/src/tile4_keygen_candidate_p_j1_batch_fixed.c" \
		"$target/gt32_keygen.c"
	cp "$root/src/tile4_baseinv_p_j1_soa_flat.c" \
		"$target/gt32_baseinv_p_j1.c"
	cp "$root/src/tile4_baseinv_p_j1_soa_flat_control.c" \
		"$target/gt32_baseinv_p_j1_control.c"
	cp "$root/src/tile4_baseinv_p_j1_batch_asm.S" \
		"$target/gt32_baseinv_p_j1_batch.s"
	printf '#define GT32_P_J1_BATCH_TREE_SELECT %s\n' "$select" > \
		"$target/gt32_p_j1_batch_select.h"
	printf '%s\n' "$target"
}

install_one avx2-gt-p-j1-batch-tree-control 0
install_one avx2-gt-p-j1-batch-tree-candidate 1

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
	cp "$root/src/tile4_keygen_candidate_p_j1_fixed.c" "$target/gt32_keygen.c"
	cp "$root/src/tile4_baseinv_p_j1_soa_flat.c" "$target/gt32_baseinv_p_j1.c"
	cp "$root/src/tile4_baseinv_p_j1_batch_asm.S" "$target/gt32_baseinv_p_j1_batch.s"
	printf '#define GT32_FIXED_P_J1_SELECT %s\n' "$select" > \
		"$target/gt32_fixed_p_j1_select.h"
	printf '%s\n' "$target"
}

install_one avx2-gt-global-inverse-p-j1-fixed-control 0
install_one avx2-gt-global-inverse-p-j1-fixed-candidate 1

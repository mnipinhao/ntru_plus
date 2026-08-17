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
	mv "$target/gt32_encap.c" "$target/tile4_kem_encap_candidate.inc"
	cp "$root/src/tile4_kem_encap_four_poly_select.c" "$target/gt32_encap.c"
	printf '#define GT32_ENCAP_FOUR_POLY_SELECT %s\n' "$select" > \
		"$target/gt32_encap_four_poly_select.h"
	printf '%s\n' "$target"
}

install_one avx2-gt-encap-four-poly-control 0
install_one avx2-gt-encap-four-poly-candidate 1

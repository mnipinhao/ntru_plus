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
	cp "$root/src/tile4_supercop_native_rcheck_api.c" "$target/gt32_kem_api.c"
	printf '#define GT32_NATIVE_RCHECK_SELECT %s\n' "$select" > \
		"$target/gt32_native_rcheck_select.h"
	printf '%s\n' "$target"
}

install_one avx2-gt-native-rcheck-control 0
install_one avx2-gt-native-rcheck-candidate 1

alt=$supercop/crypto_kem/ntruplus768/avx2-gt-native-rcheck-placement-alt
"$root/tools/export_supercop_global_inverse.sh" "$alt"
cp "$root/src/tile4_supercop_native_rcheck_api.c" "$alt/gt32_kem_api.c"
printf '#define GT32_NATIVE_RCHECK_SELECT 0\n' > \
	"$alt/gt32_native_rcheck_select.h"
printf '#define GT32_NATIVE_RCHECK_ALIGN 4096\n' > \
	"$alt/gt32_native_rcheck_placement.h"
printf '%s\n' "$alt"

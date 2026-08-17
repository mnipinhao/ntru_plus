#!/bin/sh
set -eu

supercop=${SUPERCOP:-/home/nuc/supercop-20260627}
name=${1:-avx2-gt-fastest-clean-prepared-p0}
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
target=$supercop/crypto_kem/ntruplus768/$name

"$root/tools/install_supercop_fastest_clean_native_rcheck.sh" "$name"
cp "$root/src/tile4_kem_prepared_p0.c" "$target/gt32_prepared_p0.c"
cp "$root/src/tile4_kem_prepared_p0.h" "$target/tile4_kem_prepared_p0.h"
cp "$root/src/tile4_kem_prepared_p0_control.c" "$target/gt32_prepared_p0_control.c"
cp "$root/src/tile4_kem_prepared_p0_control.h" "$target/tile4_kem_prepared_p0_control.h"
cp "$root/src/tile4_prepared_fixed_b3.c" "$target/tile4_prepared_fixed_b3.c"
cp "$root/src/tile4_prepared_fixed_b3.h" "$target/tile4_prepared_fixed_b3.h"
cp "$root/src/tile4_prepared_fixed_b3_asm.S" "$target/tile4_prepared_fixed_b3_asm.S"
cp "$root/generated/tile4_prepared_fixed_b3_lambda.h" \
	"$target/tile4_prepared_fixed_b3_lambda.h"
printf '%s\n' "$target"

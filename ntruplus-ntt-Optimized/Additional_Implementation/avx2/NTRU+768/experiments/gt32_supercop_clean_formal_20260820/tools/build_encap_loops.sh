#!/bin/sh
set -eu

SUPERCOP=${SUPERCOP:-/home/nuc/supercop-20260627}
EXP=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
INCLUDE1=$SUPERCOP/include
INCLUDE2=$SUPERCOP/bench/nucpromtlhcubinucai1ummsb209/include/amd64
INCLUDE3=$SUPERCOP/bench/nucpromtlhcubinucai1ummsb209/work/compile

build_one() {
	name=$1
	output=$2
	directory=$SUPERCOP/crypto_kem/ntruplus768/$name
	# shellcheck disable=SC2086
	gcc -DSUPERCOP -march=native -mtune=native -O3 -fwrapv -fPIE -pie \
		-ffunction-sections -fdata-sections -Wl,--gc-sections \
		-I"$directory" -I"$INCLUDE1" -I"$INCLUDE2" -I"$INCLUDE3" \
		-o "$output" "$EXP/tools/encap_loop.c" \
		$directory/*.c $directory/*.s
}

build_one avx2 "$EXP/build/official-encap-loop"
build_one avx2-gt32-clean-20260820 "$EXP/build/gt-clean-encap-loop"

#!/bin/sh
set -eu
EXP=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SUPER=/home/nuc/supercop-20260627
BENCH=$SUPER/bench/nucpromtlhcubinucai1ummsb209
WORK=$BENCH/work/compile
OUT=$EXP/build/exact
mkdir -p "$OUT"

build_one() {
  name=$1; output=$2; impl=$SUPER/crypto_kem/ntruplus768/$name
  gcc -DSUPERCOP -DCOMPILER='"gcc-supercop-045-exact"' -DLOOPS=3 \
    -march=native -mtune=native -O3 -fwrapv -fPIC -fPIE -pie \
    -ffunction-sections -fdata-sections -Wl,--gc-sections \
    -I"$impl" -I"$SUPER/include" -I"$BENCH/include" -I"$BENCH/include/amd64" \
    -I"$BENCH/include/nontimecop/amd64" -I"$WORK" \
    -o "$output" "$WORK/measure-anything.c" "$WORK/measure.c" \
    "$impl"/*.c "$impl"/*.s \
    "$BENCH/lib/amd64/libfastrandombytes.a" \
    "$BENCH/lib/amd64/libkernelrandombytes.a" \
    "$BENCH/lib/nontimecop/amd64/libcpucycles.a" \
    "$BENCH/lib/amd64/libsupercop.a"
}

build_one avx2 "$OUT/official"
build_one avx2-gt32-clean-20260820 "$OUT/gt-clean"
build_one avx2-gt32-clean-decap-b3p-045 "$OUT/gt-private"
sha256sum "$OUT/official" "$OUT/gt-clean" "$OUT/gt-private" > "$EXP/generated/exact_sha256.txt"

#!/bin/sh
set -eu
EXP=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SUPER=/home/nuc/supercop-20260627
GT=$SUPER/crypto_kem/ntruplus768/avx2-gt32-clean-20260820
HOST=$SUPER/bench/nucpromtlhcubinucai1ummsb209
CFLAGS="-O3 -march=native -mtune=native -fwrapv -fno-omit-frame-pointer -ffunction-sections -fdata-sections -Wall -Wextra -Wpedantic"
COMMON="$EXP/src/working_set_057.c $GT/consts.c $GT/fips202.c $GT/symmetric.c $GT/poly.c $GT/baseinv.c"
mkdir -p "$EXP/build"
gcc $CFLAGS -Wl,--gc-sections -I"$GT" -I"$EXP/src" \
  -I"$SUPER/include" -I"$HOST/include/nontimecop/amd64" \
  -o "$EXP/build/bench_057" "$EXP/bench/bench_057.c" $COMMON \
  "$GT"/*.s "$HOST/lib/nontimecop/amd64/libcpucycles.a"
gcc $CFLAGS -Wl,--gc-sections -I"$GT" -I"$EXP/src" \
  -I"$SUPER/include" -I"$HOST/include/nontimecop/amd64" \
  -o "$EXP/build/test_057" "$EXP/tests/test_057.c" \
  "$EXP/src/working_set_057.c" "$GT/encap.c" "$GT/consts.c" \
  "$GT/fips202.c" "$GT/symmetric.c" "$GT/poly.c" "$GT/baseinv.c" \
  "$GT"/*.s "$HOST/lib/nontimecop/amd64/libcpucycles.a"
gcc $CFLAGS -Wl,--gc-sections -I"$GT" -I"$EXP/src" \
  -I"$SUPER/include" -I"$HOST/include/nontimecop/amd64" \
  -o "$EXP/build/pmu_057" "$EXP/bench/pmu_057.c" $COMMON "$GT"/*.s

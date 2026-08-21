#!/bin/sh
set -eu
EXP=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SUPER=/home/nuc/supercop-20260627
GT=$SUPER/crypto_kem/ntruplus768/avx2-gt32-clean-20260820
HOST=$SUPER/bench/nucpromtlhcubinucai1ummsb209
mkdir -p "$EXP/build"
CFLAGS="-O3 -march=native -mtune=native -fwrapv -fno-omit-frame-pointer -ffunction-sections -fdata-sections -Wall -Wextra -Wpedantic"
gcc $CFLAGS -Wl,--gc-sections -I"$GT" -I"$EXP/src" \
  -I"$SUPER/include" -I"$HOST/include/nontimecop/amd64" \
  -o "$EXP/build/bench_056" \
  "$EXP/bench/bench_056.c" "$EXP/src/geometry_056.c" \
  "$GT/consts.c" "$GT/fips202.c" "$GT/symmetric.c" "$GT/poly.c" "$GT/baseinv.c" \
  "$GT"/*.s "$HOST/lib/nontimecop/amd64/libcpucycles.a"

gcc $CFLAGS -Wl,--gc-sections -I"$GT" -I"$EXP/src" \
  -I"$SUPER/include" -I"$HOST/include/nontimecop/amd64" \
  -o "$EXP/build/test_056" \
  "$EXP/tests/test_056.c" "$EXP/src/geometry_056.c" "$GT/encap.c" \
  "$GT/consts.c" "$GT/fips202.c" "$GT/symmetric.c" "$GT/poly.c" "$GT/baseinv.c" \
  "$GT"/*.s "$HOST/lib/nontimecop/amd64/libcpucycles.a"

gcc $CFLAGS -Wl,--gc-sections -I"$GT" -I"$EXP/src" \
  -I"$SUPER/include" -I"$HOST/include/nontimecop/amd64" \
  -o "$EXP/build/pmu_056" \
  "$EXP/bench/pmu_056.c" "$EXP/src/geometry_056.c" \
  "$GT/consts.c" "$GT/fips202.c" "$GT/symmetric.c" "$GT/poly.c" "$GT/baseinv.c" \
  "$GT"/*.s "$HOST/lib/nontimecop/amd64/libcpucycles.a"

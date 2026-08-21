#!/bin/sh
set -eu
EXP=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SUPER=/home/nuc/supercop-20260627
OFF=$SUPER/crypto_kem/ntruplus768/avx2
GT=$SUPER/crypto_kem/ntruplus768/avx2-gt32-clean-20260820
HOST=$SUPER/bench/nucpromtlhcubinucai1ummsb209/include/amd64
mkdir -p "$EXP/build"
CFLAGS="-O3 -march=native -mtune=native -fwrapv -fno-omit-frame-pointer -ffunction-sections -fdata-sections"

gcc $CFLAGS -x assembler-with-cpp -Dpoly_tobytes=off_poly_tobytes \
  -c "$OFF/pack.s" -o "$EXP/build/off_pack.o"

gcc $CFLAGS -Wl,--gc-sections -I"$GT" -I"$SUPER/include" -I"$HOST" \
  -o "$EXP/build/serializer_054" \
  "$EXP/bench/serializer_054.c" \
  "$GT/consts.c" "$GT/fips202.c" "$GT/symmetric.c" "$GT/poly.c" "$GT/baseinv.c" \
  "$GT"/*.s "$EXP/build/off_pack.o"

nm -n "$EXP/build/serializer_054" | grep -E \
  ' (off_poly_tobytes|poly_frombytes|ntruplus768_pack_m_(lazy10788|highrange12699)_avx2)$'


#!/bin/sh
set -eu
EXP=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SUPER=/home/nuc/supercop-20260627
OFF=$SUPER/crypto_kem/ntruplus768/avx2
GT=$SUPER/crypto_kem/ntruplus768/avx2-gt32-clean-20260820
HOST=$SUPER/bench/nucpromtlhcubinucai1ummsb209/include/amd64
mkdir -p "$EXP/build"
CFLAGS="-O3 -march=native -mtune=native -fwrapv -fno-omit-frame-pointer -ffunction-sections -fdata-sections"

gcc $CFLAGS -x assembler-with-cpp -Dpoly_ntt=off_poly_ntt \
    -c "$OFF/ntt.s" -o "$EXP/build/off_ntt.o"
gcc $CFLAGS -x assembler-with-cpp -Dpoly_tobytes=off_poly_tobytes \
    -c "$OFF/pack.s" -o "$EXP/build/off_pack.o"

gcc $CFLAGS -Wl,--gc-sections -I"$GT" -I"$SUPER/include" -I"$HOST" \
    -o "$EXP/build/hash_handoff_052" \
    "$EXP/bench/hash_handoff_052.c" \
    "$GT/consts.c" "$GT/fips202.c" "$GT/symmetric.c" "$GT/poly.c" "$GT/baseinv.c" \
    "$GT"/*.s "$EXP/build/off_ntt.o" "$EXP/build/off_pack.o"

nm -n "$EXP/build/hash_handoff_052" | grep -E ' (hash_g|off_poly_ntt|off_poly_tobytes)$'


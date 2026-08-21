#!/bin/sh
set -eu
EXP=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SUPER=/home/nuc/supercop-20260627
OFF=$SUPER/crypto_kem/ntruplus768/avx2
GT=$SUPER/crypto_kem/ntruplus768/avx2-gt32-clean-20260820
RSP=$SUPER/import/ntruplus-20260723/KAT/NTRU+768/PQCkemKAT_2336.rsp
HOST=$SUPER/bench/nucpromtlhcubinucai1ummsb209/include/amd64
mkdir -p "$EXP/build" "$EXP/generated"
python3 "$EXP/tools/gen_vector.py" --rsp "$RSP" --output "$EXP/generated/vector_048.h"
CFLAGS="-O3 -march=native -mtune=native -fwrapv -fno-omit-frame-pointer -ffunction-sections -fdata-sections -Wl,--gc-sections"
gcc $CFLAGS -I"$OFF" -I"$EXP/generated" -I"$SUPER/include" -I"$HOST" -o "$EXP/build/official" \
 "$EXP/bench/context_048.c" "$OFF/consts.c" "$OFF/fips202.c" "$OFF/symmetric.c" "$OFF/poly.c" "$OFF"/*.s
gcc $CFLAGS -DGT_IMPL -I"$GT" -I"$EXP/generated" -I"$SUPER/include" -I"$HOST" -o "$EXP/build/gt" \
 "$EXP/bench/context_048.c" "$GT/consts.c" "$GT/fips202.c" "$GT/symmetric.c" "$GT/poly.c" "$GT/baseinv.c" "$GT"/*.s

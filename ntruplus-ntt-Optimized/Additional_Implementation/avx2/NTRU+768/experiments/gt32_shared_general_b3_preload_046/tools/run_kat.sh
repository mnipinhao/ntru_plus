#!/bin/sh
set -eu
IMPL=$1
OUT=$2
case "$OUT" in
  /*) ;;
  *) OUT="$(pwd)/$OUT" ;;
esac
SUPERCOP=/home/nuc/supercop-20260627
KAT=$SUPERCOP/import/ntruplus-20260723/Reference_Implementation/NTRU+768/kat
CANONICAL=$SUPERCOP/import/ntruplus-20260723/KAT/NTRU+768
HOST_INCLUDE=$SUPERCOP/bench/nucpromtlhcubinucai1ummsb209/include/amd64
SHIMS=/home/nuc/src/ntru-plus-avx2-gt-rewrite-official-001/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_gt32_tile4_official_001/tools/kat_shims
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT HUP INT TERM
mkdir -p "$OUT"
gcc -mavx2 -mbmi2 -mpopcnt -maes -march=native -mtune=native -O3 \
  -fomit-frame-pointer -ffunction-sections -fdata-sections -Wl,--gc-sections \
  -I"$SHIMS" -I"$IMPL" -I"$HOST_INCLUDE" -Wa,-I,"$IMPL" \
  -o "$TMP/PQCgenKAT_kem" "$KAT/PQCgenKAT_kem.c" "$KAT/aes.c" "$KAT/rng.c" \
  "$SHIMS/crypto_declassify.c" "$IMPL/consts.c" "$IMPL/fips202.c" \
  "$IMPL/symmetric.c" "$IMPL/poly.c" "$IMPL/baseinv.c" "$IMPL/decap.c" \
  "$IMPL/encap.c" "$IMPL/keygen.c" "$IMPL/kem.c" "$IMPL"/*.s
cd "$TMP"; ./PQCgenKAT_kem
cmp PQCkemKAT_2336.req "$CANONICAL/PQCkemKAT_2336.req"
cmp PQCkemKAT_2336.rsp "$CANONICAL/PQCkemKAT_2336.rsp"
sha256sum PQCkemKAT_2336.req PQCkemKAT_2336.rsp > "$OUT/sha256.txt"
printf 'vectors=100\nrequest_byte_exact=pass\nresponse_byte_exact=pass\n' > "$OUT/result.txt"

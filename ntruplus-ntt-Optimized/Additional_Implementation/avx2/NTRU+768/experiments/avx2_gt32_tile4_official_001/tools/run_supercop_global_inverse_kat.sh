#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SUPERCOP=${SUPERCOP:-/home/nuc/supercop-20260627}
IMPL=${IMPL:-$SUPERCOP/crypto_kem/ntruplus768/avx2-gt-global-inverse}
KAT=${KAT:-$SUPERCOP/import/ntruplus-20260723/Reference_Implementation/NTRU+768/kat}
CANONICAL=${CANONICAL:-$SUPERCOP/import/ntruplus-20260723/KAT/NTRU+768}
HOST_INCLUDE=${HOST_INCLUDE:-$SUPERCOP/bench/nucpromtlhcubinucai1ummsb209/include/amd64}
CC=${CC:-gcc}
OUT=${OUT:-$ROOT/results/kat-supercop-global-inverse-20260812}
case "$OUT" in
  /*) ;;
  *) OUT="$ROOT/$OUT" ;;
esac
BUILD=$(mktemp -d)
trap 'rm -rf "$BUILD"' EXIT HUP INT TERM

mkdir -p "$OUT"

cd "$IMPL"
"$CC" \
  -Wall -Wextra -Wpedantic -Wno-unused-result \
	-mavx2 -mbmi2 -mpopcnt -maes -march=native -mtune=native \
	-O3 -fomit-frame-pointer -ffunction-sections -fdata-sections \
	-Wl,--gc-sections \
  -I"$ROOT/tools/kat_shims" -I"$IMPL" -I"$HOST_INCLUDE" \
  -Wa,-I,"$IMPL" \
  -o "$BUILD/PQCgenKAT_kem" \
  "$KAT/PQCgenKAT_kem.c" "$KAT/aes.c" "$KAT/rng.c" \
  "$ROOT/tools/kat_shims/crypto_declassify.c" \
  "$IMPL/consts.c" "$IMPL/fips202.c" "$IMPL/symmetric.c" \
  "$IMPL/poly.c" "$IMPL/gt32_baseinv_p.c" \
  ${GT32_EXTRA_BASEINV_SOURCE:+"$GT32_EXTRA_BASEINV_SOURCE"} \
  ${GT32_EXTRA_BASEINV_SOURCES:-} \
  "$IMPL/gt32_decap.c" "$IMPL/gt32_encap.c" \
  "$IMPL/gt32_keygen.c" "$IMPL/gt32_kem_api.c" \
  "$IMPL"/*.s

cd "$BUILD"
./PQCgenKAT_kem

cmp PQCkemKAT_2336.req "$CANONICAL/PQCkemKAT_2336.req"
cmp PQCkemKAT_2336.rsp "$CANONICAL/PQCkemKAT_2336.rsp"

sha256sum PQCkemKAT_2336.req > "$OUT/sha256.txt"
sha256sum PQCkemKAT_2336.rsp >> "$OUT/sha256.txt"
wc -c PQCkemKAT_2336.req PQCkemKAT_2336.rsp > "$OUT/sizes.txt"
cp PQCkemKAT_2336.rsp "$OUT/PQCkemKAT_2336.rsp"

{
  printf 'implementation=crypto_kem/ntruplus768/%s\n' "$(basename "$IMPL")"
  printf '%s\n' 'vectors=100'
  printf '%s\n' 'fields=seed,pk,sk,ct,ss'
  printf '%s\n' 'request_byte_exact=pass'
  printf '%s\n' 'response_byte_exact=pass'
  printf 'compiler=%s\n' "$CC"
  "$CC" --version | sed -n '1p'
} > "$OUT/result.txt"

printf 'GT32 %s KAT: PASS (100/100, canonical req/rsp byte-exact)\n' "$(basename "$IMPL")"
cat "$OUT/sha256.txt"

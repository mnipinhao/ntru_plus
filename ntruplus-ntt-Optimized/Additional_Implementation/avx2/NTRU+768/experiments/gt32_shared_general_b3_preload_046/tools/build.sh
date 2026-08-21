#!/bin/sh
set -eu
EXP=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
ROOT=$(CDPATH= cd -- "$EXP/../.." && pwd)
BASE=/home/nuc/supercop-20260627/crypto_kem/ntruplus768/avx2-gt32-clean-20260820
SUPER=/home/nuc/supercop-20260627
BENCH=$SUPER/bench/nucpromtlhcubinucai1ummsb209
WORK=$BENCH/work/compile
BUILD=$EXP/build
GEN=$EXP/generated
mkdir -p "$BUILD" "$GEN"

python3 "$EXP/../gt32_decap_load_to_compute_044/tools/generate_variants.py" \
  --root "$ROOT" \
  --decode-candidate "$BASE/pack.s" \
  --output "$GEN"

for profile in A G; do
  impl="$BUILD/impl-$profile"
  rm -rf "$impl"
  cp -a "$BASE" "$impl"
  cp "$GEN/basemul-$profile.s" "$impl/basemul.s"
  gcc -DSUPERCOP -DCOMPILER='"gcc-supercop-046"' -DLOOPS=3 \
    -march=native -mtune=native -O3 -fwrapv -fPIC -fPIE -pie \
    -ffunction-sections -fdata-sections -Wl,--gc-sections \
    -I"$impl" -I"$SUPER/include" -I"$BENCH/include" \
    -I"$BENCH/include/amd64" -I"$BENCH/include/nontimecop/amd64" -I"$WORK" \
    -o "$BUILD/measure-$profile" "$WORK/measure-anything.c" "$WORK/measure.c" \
    "$impl"/*.c "$impl"/*.s \
    "$BENCH/lib/amd64/libfastrandombytes.a" \
    "$BENCH/lib/amd64/libkernelrandombytes.a" \
    "$BENCH/lib/nontimecop/amd64/libcpucycles.a" \
    "$BENCH/lib/amd64/libsupercop.a"
done

python3 "$EXP/tools/audit.py" --control "$BUILD/measure-A" \
  --candidate "$BUILD/measure-G" --output "$GEN/geometry.json"

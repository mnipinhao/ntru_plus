#!/bin/bash
# Build the code-size, executed-code and cold-start binaries for GT and the
# official NO_CE build (main's, offm<set>).  Linux (the Pi 5).
#
# usage: build.sh OFFICIAL OUT
#   OFFICIAL  the directory bench/official/setup.sh assembled
#   OUT       directory for the binaries, created
# PRODUCTION (environment) overrides the packages measured, by default this
# repository's production/Additional_Implementation/aarch64.
#
#   cold_<impl><set>    fully cold operations (cold.c, icache_thrash.S, PMU cycles)
#   fp_<impl><set>      one operation, for callgrind (footprint.c)
#   sz_<impl><set>      the three entry points linked with gc-sections (size_main.c)
#   szstub_<impl><set>  the same program against empty entry points
set -euo pipefail
OFF=$(cd "${1:?usage: build.sh OFFICIAL OUT}" && pwd); OUT=${2:?usage: build.sh OFFICIAL OUT}
H=$(cd "$(dirname "$0")" && pwd); P=$H/../perop
G=$(cd "${PRODUCTION:-$H/../../../production/Additional_Implementation/aarch64}" && pwd)
CC=${CC:-cc}
GC="-ffunction-sections -fdata-sections -Wl,--gc-sections"
RNG=$P/det_randombytes.c
mkdir -p "$OUT"
for s in 768 864 1152; do
  V=$($P/package_sources.sh $G/NTRU+$s)
  GS=$(echo "$V" | sed -n 1p); GF="$(echo "$V" | sed -n 2p) -D_DEFAULT_SOURCE -w -I$G/NTRU+$s"
  d=$OFF/offm$s
  OS="$d/kem.c $d/symmetric.c $d/poly.c $d/add.s $d/ntt.s $d/base.s $d/crepmod3.s $d/pack.s $d/cbd.s $d/fips202.c"
  OF="-O3 -fomit-frame-pointer -w -I$OFF/shim -I$d"
  for impl in gt off; do
    if [ $impl = gt ]; then SRC=$GS; FL=$GF; else SRC=$OS; FL=$OF; fi
    $CC $FL -I$H -o "$OUT/cold_$impl$s" $H/cold.c $H/icache_thrash.S $H/perf_counter.c $RNG $SRC
    $CC $FL -I$H -o "$OUT/fp_$impl$s" $H/footprint.c $RNG $SRC
    $CC $FL -I$H $GC -o "$OUT/sz_$impl$s" $H/size_main.c $RNG $SRC
    $CC $FL -I$H $GC -DSTUB -o "$OUT/szstub_$impl$s" $H/size_main.c $RNG
  done
done
ls "$OUT" | tr '\n' ' '; echo

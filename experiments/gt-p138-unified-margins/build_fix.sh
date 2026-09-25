#!/bin/bash
# P138: Official with the two sponge fixes (upstream_fix/), against Official as shipped.
#   off<set>_cefix    upstream's default build (CE sponge + CE f1600) with the fixed CE/fips202.c   [M2]
#   off<set>_nocefix  SUPERCOP's Official with the fixed load64                                      [M2, A76]
# usage: build_fix.sh B m2|pi [MAIN]   (MAIN: perop5.c / perop5_pi.c, or outhash.c for the check)
set -e
B=${1:?}; M=${2:?}; CC=${CC:-cc}; H=$(cd $(dirname $0) && pwd)
MAIN=${3:-$([ $M = m2 ] && echo perop5.c || echo perop5_pi.c)}
OUT=$B/bin; [ $MAIN = outhash.c ] && OUT=$B/hchk; mkdir -p $OUT
COMMON="-Wno-unused-result -w -I$B/shim -I$B"
for s in 768 864 1152; do
  d=$B/off$s
  OFFSRC="$d/kem.c $d/symmetric.c $d/poly.c $d/add.s $d/ntt.s $d/base.s $d/crepmod3.s $d/pack.s $d/cbd.s"
  $CC -O3 -fomit-frame-pointer $COMMON -I$d -o $OUT/off${s}_nocefix $B/$MAIN $B/rb2.c $OFFSRC $H/upstream_fix/SUPERCOP_fips202.c
  if [ $M = m2 ]; then
    $CC -O3 -fomit-frame-pointer $COMMON -DSUPPORTS_SHAKE256_ASM -I$B/ce -I$d -march=armv8.2-a+crypto+sha3 \
        -o $OUT/off${s}_cefix $B/$MAIN $B/rb2.c $OFFSRC $H/upstream_fix/CE_fips202.c $B/ce/f1600.S
  fi
done
ls $OUT

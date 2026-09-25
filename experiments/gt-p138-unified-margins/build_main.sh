#!/bin/bash
# P138: Official exactly as GitHub main (3991b2a) has it, in SUPERCOP's leaf form.  Through SUPERCOP's own
# ntruplus-supercop-update.sh, main differs from the SUPERCOP 20260831 leaves only in crepmod3.s.
#   offm<set>_noce   the SUPERCOP leaf with main's crepmod3.s (= main's NO_CE build)            [M2, A76]
#   offm<set>_ce     the same with main's CE/fips202.c and CE/f1600.S (main's default build)   [M2]
# usage: build_main.sh B m2|pi [MAIN]
set -e
B=${1:?}; M=${2:?}; CC=${CC:-cc}; H=$(cd $(dirname $0) && pwd)
MAIN=${3:-$([ $M = m2 ] && echo perop5.c || echo perop5_pi.c)}
OUT=$B/bin; [ $MAIN = outhash.c ] && OUT=$B/hchk; mkdir -p $OUT
COMMON="-Wno-unused-result -w -I$B/shim -I$B"
for s in 768 864 1152; do
  d=$B/offm$s
  OFFSRC="$d/kem.c $d/symmetric.c $d/poly.c $d/add.s $d/ntt.s $d/base.s $d/crepmod3.s $d/pack.s $d/cbd.s"
  $CC -O3 -fomit-frame-pointer $COMMON -I$d -o $OUT/offm${s}_noce $B/$MAIN $B/rb2.c $OFFSRC $d/fips202.c
  if [ $M = m2 ]; then
    $CC -O3 -fomit-frame-pointer $COMMON -DSUPPORTS_SHAKE256_ASM -I$B/cemain -I$d -march=armv8.2-a+crypto+sha3 \
        -o $OUT/offm${s}_ce $B/$MAIN $B/rb2.c $OFFSRC $B/cemain/fips202.c $B/cemain/f1600.S
  fi
done
ls $OUT | grep offm

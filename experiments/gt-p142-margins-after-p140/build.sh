#!/bin/bash
# P142: every build of the comparison against GitHub main 3991b2a, one machine.
#   offm<s>_noce   main's NO_CE build (SUPERCOP's leaf with main's crepmod3.s)          [M2, A76]
#   offm<s>_ce     main's default build: CE/fips202.c + CE/f1600.S                       [M2]
#   offm<s>_gtk    main's CE sponge calling GT's permutation (v84a on M2, scalar on A76; the
#                  A76 build defines NTRUPLUS_FORCE_SHA3 only to get past the sponge's #error)
#   gt<s>_offhash  GT's arithmetic and KEM flow with that same sponge and permutation (glue.c)
#   gt<s>          the production tree, its Makefile's sources and CFLAGS
# usage: build.sh B G m2|pi [MAIN]   (B: P138's build dir with offm<s>/, cemain/, ce_gt/, gtk_scalar/, shim/)
set -e
B=${1:?}; G=${2:?}; M=${3:?}; CC=${CC:-cc}; H=$(cd $(dirname $0) && pwd)
MAIN=${4:-$([ $M = m2 ] && echo perop5.c || echo perop5_pi.c)}; OUT=$B/p142bin; [ $MAIN = outhash.c ] && OUT=$B/p142chk; mkdir -p $OUT
if [ $M = m2 ]; then SF="-march=armv8.2-a+crypto+sha3"; PERM="$B/ce_gt/f1600.S $B/ce_gt/gtk_v84a.S"
else SF="-DNTRUPLUS_FORCE_SHA3 -D__ARM_FEATURE_CRYPTO"; PERM="$B/gtk_scalar/f1600.S $B/gtk_scalar/gtk.S"; fi
COMMON="-Wno-unused-result -w -I$B/shim -I$H"
T=$(mktemp -d)
for s in 768 864 1152; do
  d=$B/offm$s
  OFFSRC="$d/kem.c $d/symmetric.c $d/poly.c $d/add.s $d/ntt.s $d/base.s $d/crepmod3.s $d/pack.s $d/cbd.s"
  $CC -O3 -fomit-frame-pointer $COMMON -I$d -o $OUT/offm${s}_noce $H/$MAIN $H/rb2.c $OFFSRC $d/fips202.c
  [ $M = m2 ] && $CC -O3 -fomit-frame-pointer $COMMON -DSUPPORTS_SHAKE256_ASM -I$B/cemain -I$d $SF \
      -o $OUT/offm${s}_ce $H/$MAIN $H/rb2.c $OFFSRC $B/cemain/fips202.c $B/cemain/f1600.S
  $CC -O3 -fomit-frame-pointer $COMMON -DSUPPORTS_SHAKE256_ASM -I$B/cemain -I$d $SF \
      -o $OUT/offm${s}_gtk $H/$MAIN $H/rb2.c $OFFSRC $B/cemain/fips202.c $PERM
  V=$($H/gtsrc.sh $G/NTRU+$s); GF="$(echo "$V" | sed -n 2p) -D_DEFAULT_SOURCE"
  $CC $GF $COMMON -I$G/NTRU+$s -o $OUT/gt$s $H/$MAIN $H/rb2.c $(echo "$V" | sed -n 1p)
  GS=""; for f in $(echo "$V" | sed -n 1p); do case $(basename $f) in symmetric.c|fips202.c|hash_fixed.c|keccakf1600*.S) ;; *) GS="$GS $f";; esac; done
  $CC -O3 -fomit-frame-pointer -w -DSUPPORTS_SHAKE256_ASM $SF -I$B/shim -I$B/cemain -I$d -c $d/symmetric.c -o $T/osym$s.o
  $CC -O3 -fomit-frame-pointer -w -DSUPPORTS_SHAKE256_ASM $SF -I$B/shim -I$B/cemain -I$d -c $B/cemain/fips202.c -o $T/ofips$s.o
  $CC $GF -I$G/NTRU+$s -c $H/glue.c -o $T/glue$s.o
  $CC $GF $COMMON -I$G/NTRU+$s -o $OUT/gt${s}_offhash $H/$MAIN $H/rb2.c $GS $T/osym$s.o $T/ofips$s.o $T/glue$s.o $PERM
done
rm -rf $T
ls $OUT | tr '\n' ' '

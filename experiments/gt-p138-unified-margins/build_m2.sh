#!/bin/bash
# P138, M2: every binary of the three-set comparison in one session (P129's build_m2.sh plus NTRU+768).
#   off<set>_noce  SUPERCOP's ntruplus<set>/aarch64 (portable Keccak)
#   off<set>_ce    + upstream's CryptoExtension permutation (AAPCS64-fixed copy)
#   off<set>_gtk   Official's CE sponge + GT's FEAT_SHA3 permutation (permutation held equal)
#   gt<set>        the production tree, its Makefile's sources and CFLAGS
set -e
B=${1:?}; G=${2:?}; CC=${CC:-cc}; H=$(cd $(dirname $0) && pwd)
mkdir -p $B/bin
COMMON="-Wno-unused-result -I$B/shim -I$B"
for s in 768 864 1152; do
  d=$B/off$s
  OFFSRC="$d/kem.c $d/symmetric.c $d/poly.c $d/add.s $d/ntt.s $d/base.s $d/crepmod3.s $d/pack.s $d/cbd.s"
  $CC -O3 -fomit-frame-pointer $COMMON -I$d -o $B/bin/off${s}_noce $B/perop5.c $B/rb2.c $OFFSRC $d/fips202.c
  $CC -O3 -fomit-frame-pointer $COMMON -DSUPPORTS_SHAKE256_ASM -I$B/ce -I$d -march=armv8.2-a+crypto+sha3 \
      -o $B/bin/off${s}_ce $B/perop5.c $B/rb2.c $OFFSRC $B/ce/fips202.c $B/ce/f1600.S
  $CC -O3 -fomit-frame-pointer $COMMON -DSUPPORTS_SHAKE256_ASM -I$B/ce_gt -I$d -march=armv8.2-a+crypto+sha3 \
      -o $B/bin/off${s}_gtk $B/perop5.c $B/rb2.c $OFFSRC $B/ce_gt/fips202.c $B/ce_gt/f1600.S $B/ce_gt/gtk_v84a.S
  V=$($H/gtsrc.sh $G/NTRU+$s)
  $CC $(echo "$V" | sed -n 2p) $COMMON -I$G/NTRU+$s -o $B/bin/gt$s $B/perop5.c $B/rb2.c $(echo "$V" | sed -n 1p)
done
ls $B/bin

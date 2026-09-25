#!/bin/bash
# P138, Cortex-A76: every binary of the three-set comparison in one session (P129's build_pi.sh plus NTRU+768).
#   off<set>_noce  SUPERCOP's ntruplus<set>/aarch64 (portable Keccak; no FEAT_SHA3 here)
#   off<set>_gtks  Official's sponge + GT's scalar permutation (permutation held equal).
#                  -D__ARM_FEATURE_CRYPTO only selects the sponge's f1600 call.
#   gt<set>        the production tree, its Makefile's sources and CFLAGS
set -e
B=${1:?}; G=${2:?}; CC=${CC:-gcc}; H=$(cd $(dirname $0) && pwd)
mkdir -p $B/bin
COMMON="-Wno-unused-result -I$B/shim -I$B"
for s in 768 864 1152; do
  d=$B/off$s
  OFFSRC="$d/kem.c $d/symmetric.c $d/poly.c $d/add.s $d/ntt.s $d/base.s $d/crepmod3.s $d/pack.s $d/cbd.s"
  $CC -O3 -fomit-frame-pointer $COMMON -I$d -o $B/bin/off${s}_noce $B/perop5_pi.c $B/rb2.c $OFFSRC $d/fips202.c
  $CC -O3 -fomit-frame-pointer $COMMON -DSUPPORTS_SHAKE256_ASM -D__ARM_FEATURE_CRYPTO -I$B/gtk_scalar -I$d \
      -o $B/bin/off${s}_gtks $B/perop5_pi.c $B/rb2.c $OFFSRC $B/gtk_scalar/fips202.c $B/gtk_scalar/f1600.S $B/gtk_scalar/gtk.S
  V=$($H/gtsrc.sh $G/NTRU+$s)
  $CC $(echo "$V" | sed -n 2p) -D_DEFAULT_SOURCE $COMMON -I$G/NTRU+$s -o $B/bin/gt$s $B/perop5_pi.c $B/rb2.c $(echo "$V" | sed -n 1p)
done
ls $B/bin

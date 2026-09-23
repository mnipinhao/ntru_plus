#!/bin/bash
# P129, Cortex-A76: every binary of the 864/1152 comparison in one session.
#   off<set>_noce  SUPERCOP's ntruplus<set>/aarch64 (portable Keccak; no FEAT_SHA3 here)
#   off<set>_gtks  Official's sponge + GT's scalar permutation (hash held equal).
#                  -D__ARM_FEATURE_CRYPTO only selects the sponge's f1600 call.
#   gt<set>        the production tree with its own Makefile CFLAGS
set -e
B=${1:?}; G=${2:?}; CC=${CC:-gcc}
mkdir -p $B/bin
COMMON="-Wno-unused-result -I$B/shim -I$B"
for s in 864 1152; do
  d=$B/off$s
  OFFSRC="$d/kem.c $d/symmetric.c $d/poly.c $d/add.s $d/ntt.s $d/base.s $d/crepmod3.s $d/pack.s $d/cbd.s"
  $CC -O3 -fomit-frame-pointer $COMMON -I$d -o $B/bin/off${s}_noce $B/perop5_pi.c $B/rb2.c $OFFSRC $d/fips202.c
  $CC -O3 -fomit-frame-pointer $COMMON -DSUPPORTS_SHAKE256_ASM -D__ARM_FEATURE_CRYPTO -I$B/gtk_scalar -I$d \
      -o $B/bin/off${s}_gtks $B/perop5_pi.c $B/rb2.c $OFFSRC $B/gtk_scalar/fips202.c $B/gtk_scalar/f1600.S $B/gtk_scalar/gtk.S
done
gtsrc () { ls $G/NTRU+$1/*.c $G/NTRU+$1/*.S 2>/dev/null | grep -v '/randombytes\.c$'; }
$CC -O3 $COMMON -I$G/NTRU+864 -o $B/bin/gt864 $B/perop5_pi.c $B/rb2.c $(gtsrc 864)
$CC -O3 -std=c11 -D_DEFAULT_SOURCE -DNTRUPLUS1152_ASM_BASEMUL_RINV \
    -DNTRUPLUS1152_ASM_BASEINV_NUM -DNTRUPLUS1152_ASM_BASEINV_FINISH \
    $COMMON -I$G/NTRU+1152 -o $B/bin/gt1152 $B/perop5_pi.c $B/rb2.c $(gtsrc 1152)
ls $B/bin

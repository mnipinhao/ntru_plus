#!/bin/zsh
# P129, M2: every binary of the 864/1152 comparison in one session.
#   off<set>_noce  SUPERCOP's ntruplus<set>/aarch64 (portable Keccak)
#   off<set>_ce    + upstream's CryptoExtension permutation (AAPCS64-fixed copy)
#   off<set>_gtk   Official's CE sponge + GT's FEAT_SHA3 permutation (hash held equal)
#   gt<set>        the production tree with its own Makefile CFLAGS
set -e
B=${1:?}; G=${2:?}; CC=${CC:-cc}
mkdir -p $B/bin
COMMON=(-Wno-unused-result -I$B/shim -I$B)
for s in 864 1152; do
  d=$B/off$s
  OFFSRC=($d/kem.c $d/symmetric.c $d/poly.c $d/add.s $d/ntt.s $d/base.s $d/crepmod3.s $d/pack.s $d/cbd.s)
  $CC -O3 -fomit-frame-pointer $COMMON[@] -I$d -o $B/bin/off${s}_noce $B/perop5.c $B/rb2.c $OFFSRC[@] $d/fips202.c
  $CC -O3 -fomit-frame-pointer $COMMON[@] -DSUPPORTS_SHAKE256_ASM -I$B/ce -I$d -march=armv8.2-a+crypto+sha3 \
      -o $B/bin/off${s}_ce $B/perop5.c $B/rb2.c $OFFSRC[@] $B/ce/fips202.c $B/ce/f1600.S
  $CC -O3 -fomit-frame-pointer $COMMON[@] -DSUPPORTS_SHAKE256_ASM -I$B/ce_gt -I$d -march=armv8.2-a+crypto+sha3 \
      -o $B/bin/off${s}_gtk $B/perop5.c $B/rb2.c $OFFSRC[@] $B/ce_gt/fips202.c $B/ce_gt/f1600.S $B/ce_gt/gtk_v84a.S
done
gtsrc () { ls $G/NTRU+$1/*.c $G/NTRU+$1/*.S 2>/dev/null | grep -v '/randombytes\.c$'; }
$CC -O3 $COMMON[@] -I$G/NTRU+864 -o $B/bin/gt864 $B/perop5.c $B/rb2.c $(gtsrc 864)
$CC -O3 -std=c11 -D_DEFAULT_SOURCE -DNTRUPLUS1152_ASM_BASEMUL_RINV \
    -DNTRUPLUS1152_ASM_BASEINV_NUM -DNTRUPLUS1152_ASM_BASEINV_FINISH \
    $COMMON[@] -I$G/NTRU+1152 -o $B/bin/gt1152 $B/perop5.c $B/rb2.c $(gtsrc 1152)
ls $B/bin

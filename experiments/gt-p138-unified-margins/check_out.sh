#!/bin/bash
# P138: output check for every build of the comparison (P129's check_out.sh plus NTRU+768): the same
# seeded key pair, ciphertext and shared secret from every Official variant and GT.
# usage: check_out.sh B GT_DIR [CC] [MARCH]   (MARCH empty: skip the CE variants, i.e. on the Pi)
set -e
B=$1; G=$2; CC=${3:-cc}; MARCH=${4-"-march=armv8.2-a+crypto+sha3"}; H=$(cd $(dirname $0) && pwd)
for s in 768 864 1152; do
  d=$B/off$s; OFF="$d/kem.c $d/symmetric.c $d/poly.c $d/add.s $d/ntt.s $d/base.s $d/crepmod3.s $d/pack.s $d/cbd.s"
  $CC -O2 -w -I$B/shim -I$B -I$d -o $B/h_noce$s $B/outhash.c $B/rb2.c $OFF $d/fips202.c
  if [ -n "$MARCH" ]; then
    $CC -O2 -w -I$B/shim -I$B -DSUPPORTS_SHAKE256_ASM -I$B/ce -I$d $MARCH -o $B/h_ce$s $B/outhash.c $B/rb2.c $OFF $B/ce/fips202.c $B/ce/f1600.S
    $CC -O2 -w -I$B/shim -I$B -DSUPPORTS_SHAKE256_ASM -I$B/ce_gt -I$d $MARCH -o $B/h_gtk$s $B/outhash.c $B/rb2.c $OFF $B/ce_gt/fips202.c $B/ce_gt/f1600.S $B/ce_gt/gtk_v84a.S
  else
    $CC -O2 -w -I$B/shim -I$B -DSUPPORTS_SHAKE256_ASM -D__ARM_FEATURE_CRYPTO -I$B/gtk_scalar -I$d -o $B/h_gtks$s $B/outhash.c $B/rb2.c $OFF $B/gtk_scalar/fips202.c $B/gtk_scalar/f1600.S $B/gtk_scalar/gtk.S
  fi
  V=$($H/gtsrc.sh $G/NTRU+$s)
  $CC $(echo "$V" | sed -n 2p) -D_DEFAULT_SOURCE -w -I$B/shim -I$B -I$G/NTRU+$s -o $B/h_gt$s $B/outhash.c $B/rb2.c $(echo "$V" | sed -n 1p)
done
for s in 768 864 1152; do for v in noce ce gtk gtks gt; do [ -x $B/h_$v$s ] && $B/h_$v$s $v$s; done; done

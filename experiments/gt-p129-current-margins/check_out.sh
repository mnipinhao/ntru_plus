#!/bin/bash
# Output check for the comparison's builds: the same seeded key pair and ciphertext
# must come out of every Official variant and GT.  perop5's selftest cannot see a
# broken hash -- upstream's CE sponge leaves the permutation EMPTY unless
# __ARM_FEATURE_CRYPTO is defined, and encaps/decaps still agree.
# usage: check_out.sh B GT_DIR [CC] [MARCH]   (MARCH empty: skip the CE variants)
set -e
B=$1; G=$2; CC=${3:-cc}; MARCH=${4-"-march=armv8.2-a+crypto+sha3"}
for s in 864 1152; do
  d=$B/off$s; OFF="$d/kem.c $d/symmetric.c $d/poly.c $d/add.s $d/ntt.s $d/base.s $d/crepmod3.s $d/pack.s $d/cbd.s"
  $CC -O2 -w -I$B/shim -I$B -I$d -o $B/h_noce$s $B/outhash.c $B/rb2.c $OFF $d/fips202.c
  if [ -n "$MARCH" ]; then
    $CC -O2 -w -I$B/shim -I$B -DSUPPORTS_SHAKE256_ASM -I$B/ce -I$d $MARCH -o $B/h_ce$s $B/outhash.c $B/rb2.c $OFF $B/ce/fips202.c $B/ce/f1600.S
    $CC -O2 -w -I$B/shim -I$B -DSUPPORTS_SHAKE256_ASM -I$B/ce_gt -I$d $MARCH -o $B/h_gtk$s $B/outhash.c $B/rb2.c $OFF $B/ce_gt/fips202.c $B/ce_gt/f1600.S $B/ce_gt/gtk_v84a.S
  fi
  [ -d $B/gtk_scalar ] && $CC -O2 -w -I$B/shim -I$B -DSUPPORTS_SHAKE256_ASM -D__ARM_FEATURE_CRYPTO -I$B/gtk_scalar -I$d -o $B/h_gtks$s $B/outhash.c $B/rb2.c $OFF $B/gtk_scalar/fips202.c $B/gtk_scalar/f1600.S $B/gtk_scalar/gtk.S
done
$CC -O2 -w -I$B/shim -I$B -I$G/NTRU+864 -o $B/h_gt864 $B/outhash.c $B/rb2.c $(ls $G/NTRU+864/*.c $G/NTRU+864/*.S | grep -v randombytes.c)
$CC -O2 -w -std=c11 -D_DEFAULT_SOURCE -DNTRUPLUS1152_ASM_BASEMUL_RINV -DNTRUPLUS1152_ASM_BASEINV_NUM -DNTRUPLUS1152_ASM_BASEINV_FINISH \
    -I$B/shim -I$B -I$G/NTRU+1152 -o $B/h_gt1152 $B/outhash.c $B/rb2.c $(ls $G/NTRU+1152/*.c $G/NTRU+1152/*.S | grep -v randombytes.c)
for s in 864 1152; do for v in noce ce gtk gtks gt; do [ -x $B/h_$v$s ] && $B/h_$v$s $v$s; done; done

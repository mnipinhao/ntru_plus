#!/bin/bash
# P138 part 2: GT's arithmetic and KEM flow with Official's hash layer, the permutation still GT's.
#   gt<set>_offhash   GT sources without symmetric.c / fips202.c / hash_fixed.c / keccakf1600*.S,
#                     plus Official's symmetric.c (compiled against Official's headers) and the
#                     permutation-equal sponge of the off<set>_gtk (M2) / off<set>_gtks (A76) build.
# off<set>_gtk(s) -> gt<set>_offhash: same hash layer, so the difference is arithmetic + KEM glue;
# gt<set>_offhash -> gt<set>: same arithmetic, so the difference is GT's hash layer (sponge, fixed-length
# hashes, fused hash_g) alone.
# usage: build_offhash.sh B G m2|pi [MAIN]   (MAIN defaults to perop5.c / perop5_pi.c; outhash.c for the check)
set -e
B=${1:?}; G=${2:?}; M=${3:?}; CC=${CC:-cc}; H=$(cd $(dirname $0) && pwd)
if [ $M = m2 ]; then SP="$B/ce_gt/fips202.c $B/ce_gt/f1600.S $B/ce_gt/gtk_v84a.S"; SI=$B/ce_gt; SF="-march=armv8.2-a+crypto+sha3"; MAIN=${4:-perop5.c}
else SP="$B/gtk_scalar/fips202.c $B/gtk_scalar/f1600.S $B/gtk_scalar/gtk.S"; SI=$B/gtk_scalar; SF="-D__ARM_FEATURE_CRYPTO"; MAIN=${4:-perop5_pi.c}; fi
OUT=$B/bin; [ $MAIN = outhash.c ] && OUT=$B/hchk; mkdir -p $OUT
T=$(mktemp -d)
for s in 768 864 1152; do
  d=$B/off$s
  $CC -O3 -fomit-frame-pointer -Wno-unused-result -DSUPPORTS_SHAKE256_ASM $SF -I$B/shim -I$SI -I$d -c $d/symmetric.c -o $T/osym$s.o
  $CC -O3 -fomit-frame-pointer -Wno-unused-result -DSUPPORTS_SHAKE256_ASM $SF -I$B/shim -I$SI -I$d -c $SP 
  mkdir -p $T/sp$s; mv *.o $T/sp$s/ 2>/dev/null || true
  V=$($H/gtsrc.sh $G/NTRU+$s)
  GS=""; for f in $(echo "$V" | sed -n 1p); do case $(basename $f) in symmetric.c|fips202.c|hash_fixed.c|keccakf1600.S|keccakf1600_v84a.S) ;; *) GS="$GS $f";; esac; done
  GL=""; [ $s != 768 ] && { $CC $(echo "$V" | sed -n 2p) -I$G/NTRU+$s -c $H/offhash_glue.c -o $T/glue$s.o; GL=$T/glue$s.o; }
  $CC $(echo "$V" | sed -n 2p) -D_DEFAULT_SOURCE -Wno-unused-result -I$B/shim -I$B -I$G/NTRU+$s -o $OUT/gt${s}_offhash \
      $B/$MAIN $B/rb2.c $GS $T/osym$s.o $T/sp$s/*.o $GL
done
rm -rf $T
ls $OUT

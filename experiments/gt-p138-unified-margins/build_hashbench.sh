#!/bin/bash
# usage: [CC=cc] [PERF_C=perf_counter.c] build_hashbench.sh B G SET m2|pi OUT
set -e
B=$1; G=$2; s=$3; M=$4; O=$5; CC=${CC:-cc}; H=$(cd $(dirname $0) && pwd); T=$(mktemp -d)
if [ $M = m2 ]; then SP="$B/ce_gt/fips202.c"; SA="$B/ce_gt/f1600.S"; SI=$B/ce_gt; SF="-march=armv8.2-a+crypto+sha3"
else SP="$B/gtk_scalar/fips202.c"; SA="$B/gtk_scalar/f1600.S"; SI=$B/gtk_scalar; SF="-D__ARM_FEATURE_CRYPTO"; fi
d=$B/off$s
$CC -O3 -fomit-frame-pointer -w -DSUPPORTS_SHAKE256_ASM $SF -include $H/orename.h -I$B/shim -I$SI -I$d -c $d/symmetric.c -o $T/os.o
$CC -O3 -fomit-frame-pointer -w -DSUPPORTS_SHAKE256_ASM $SF -include $H/orename.h -I$B/shim -I$SI -I$d -c $SP -o $T/of.o
$CC -O3 -c $SA -o $T/oa.o
V=$($H/gtsrc.sh $G/NTRU+$s)
$CC $(echo "$V" | sed -n 2p) -D_DEFAULT_SOURCE -w -I$G/NTRU+$s -o $O $H/hashbench.c ${PERF_C:-} $(echo "$V" | sed -n 1p) $B/rb2.c $T/*.o
rm -rf $T

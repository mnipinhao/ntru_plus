#!/bin/bash
# usage: [CC=cc] [PERF_C=perf_counter.c] build.sh MLKEM_NATIVE_DIR GT_NTRU768_TREE OUT m2|pi
set -e
M=$1/mlkem; G=$2; O=$3; T=$4; CC=${CC:-cc}; H=$(cd $(dirname $0) && pwd); D=$(mktemp -d)
if [ $T = m2 ]; then MA="-march=armv8.4-a+sha3"; L="x1_scalar:x1_scalar x4_v8a_scalar_hybrid:x4_v8a_scalar x1_v84a:x1_v84a x2_v84a:x2_v84a x4_v8a_v84a_scalar_hybrid:x4_v8a_v84a_scalar"
else MA=""; L="x1_scalar:x1_scalar x4_v8a_scalar_hybrid:x4_v8a_scalar"; fi
for p in $L; do f=${p%%:*}; h=${p#*:}
  $CC -c $MA -I$M -I$M/src -DMLK_CONFIG_PARAMETER_SET=768 -DMLK_CONFIG_USE_NATIVE_BACKEND_FIPS202 \
      -DMLK_CONFIG_FIPS202_BACKEND_FILE="\"fips202/native/aarch64/$h.h\"" $M/src/fips202/native/aarch64/src/keccak_f1600_${f}_aarch64_asm.S -o $D/$f.o
done
$CC -O2 $MA -I$H -o $O $H/kbench.c ${PERF_C:-} $D/*.o $G/keccakf1600.S $G/keccakf1600_v84a.S
rm -rf $D

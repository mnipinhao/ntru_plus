#!/bin/bash
# usage: [CC=cc] [PERF_C=perf_counter.c] build_hashattr.sh B G SET m2|pi OUT
# GT's fips202.c (shake256_prefixed) and permutation files from the tree; f1600 -> GT's permutation.
set -e
B=$1; G=$2; s=$3; M=$4; O=$5; CC=${CC:-cc}; H=$(cd $(dirname $0) && pwd)
if [ $M = m2 ]; then AD=$B/ce_gt/f1600.S; else AD=$B/gtk_scalar/f1600.S; fi
V=$($H/gtsrc.sh $G/NTRU+$s)
$CC $(echo "$V" | sed -n 2p) -D_DEFAULT_SOURCE -DSET=$s ${XF:-} -w -I$G/NTRU+$s -o $O $H/hashattr.c ${PERF_C:-} \
    $G/NTRU+$s/fips202.c $G/NTRU+$s/keccakf1600.S $G/NTRU+$s/keccakf1600_v84a.S $AD

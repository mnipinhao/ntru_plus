#!/bin/bash
# usage: [CC=cc] [PERF_C=perf_counter.c] build.sh NTRU+768_TREE MAIN.c OUT [extra sources...]
set -e
P=$1; M=$2; O=$3; shift 3; CC=${CC:-cc}
SRC="kem.c symmetric.c fips202.c keygen.c tables.c ntt.S decap_ntt.S decap_invntt.S base.S pack.S cbd.S add.S keccakf1600.S keccakf1600_v84a.S kem_api.S randombytes.c"
SS=""; for s in $SRC; do [ -f $P/$s ] && SS="$SS $P/$s"; done
$CC -O3 -fomit-frame-pointer -std=c99 -I$P -I. -o $O $M ${PERF_C:-} "$@" $SS

#!/bin/bash
# usage: [CC=cc] [PERF_C=perf_counter.c] build.sh NTRU+1152_TREE OFFICIAL1152_DIR MAIN.c OUT
# The production pack.c with the tree's CFLAGS, the candidate, and Official's
# pack.s with its poly_frombytes renamed o_poly_frombytes.
set -e
G=$1; OD=$2; M=$3; O=$4; CC=${CC:-cc}; T=$(mktemp -d); H=$(cd $(dirname $0) && pwd)
FL=$(printf 'v:\n\t@echo $(CFLAGS)\n' | make -s -C $G -f Makefile -f - v)
perl -pe 's/\b(_?)(poly_frombytes)\b/${1}o_$2/g' $OD/pack.s > $T/o_pack.S
$CC $FL -I$G -I$H -o $O $H/$M $H/frombytes_tbl2.c $H/frombytes_tbl2_asm.S $G/pack.c $T/o_pack.S ${PERF_C:-}
rm -rf $T

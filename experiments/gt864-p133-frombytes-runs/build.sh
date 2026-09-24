#!/bin/bash
# usage: [CC=cc] [PERF_C=perf_counter.c] build.sh NTRU+864_TREE MAIN.c OUT
set -e
G=$1; M=$2; O=$3; CC=${CC:-cc}
SRC="unpack.c api_glue.c pack.c ntt.S ntt9.S ntt_top.S ntt_tail.S base.c inverse.S baseinv_finish.S baseinv_inverse.S baseinv_num.S baseinv_prefix.S baseinv_recover.S basemul_rinv.S inverse9.S inverse16_paired.S inverse_tail_direct.S inverse_route.S add.S cbd.S support_abi.S"
SS=""; for s in $SRC; do SS="$SS $G/$s"; done
$CC -O3 -std=c11 -D_DEFAULT_SOURCE -I$G -I. -o $O $M frombytes_runs.c ${PERF_C:-} $SS

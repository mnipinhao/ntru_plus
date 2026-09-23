#!/bin/sh
# usage: [MAIN=pair.c] [PERF_C=perf_counter.c] [CC=cc] bench.sh NTRU+864_TREE OUT [extra cc flags]
set -e
G=$1; O=$2; shift 2; CC=${CC:-cc}
S="symmetric.c fips202.c ntt_api.c base.c add.S crepmod3.S cbd.S ntt.S ntt9.S ntt_top.S unpack.c unpack_api.c kem.c ntt_tail.S pack.c inverse_api.c inverse.S baseinv_num.S baseinv_prefix.S baseinv_inverse.S baseinv_recover.S baseinv_finish.S inverse16_paired.S inverse_tail_direct.S inverse_route.S crepmod3_raw.S basemul_rinv.S inverse9.S support_abi.S hash_fixed.c keccakf1600.S keccakf1600_v84a.S"
SS=""; for s in $S; do SS="$SS $G/$s"; done
$CC -O3 -std=c11 -D_DEFAULT_SOURCE "$@" -I$G -I. -o $O ${MAIN:-pair.c} detrand.c ${PERF_C:-} $SS

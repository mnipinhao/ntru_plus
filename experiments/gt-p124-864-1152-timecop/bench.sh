#!/bin/sh
# usage: [MAIN=driver.c] [PERF_C=perf_counter.c] bench.sh GT_TREE OUT [extra cc flags] -- KEM bench (bench_min.c, deterministic randombytes)
set -e
G=$1; O=$2; shift 2; CC=${CC:-cc}
case $G in *864*) S="symmetric.c fips202.c ntt_api.c base.c add.S crepmod3.S cbd.S ntt.S ntt9.S ntt_top.S unpack.c unpack_api.c kem.c ntt_tail.S pack.c inverse_api.c inverse.S baseinv_num.S baseinv_prefix.S baseinv_inverse.S baseinv_recover.S baseinv_finish.S inverse16_paired.S inverse_tail_direct.S inverse_route.S crepmod3_raw.S basemul_rinv.S inverse9.S support_abi.S hash_fixed.c keccakf1600.S keccakf1600_v84a.S"; X="";;
  *) S="kem.c symmetric.c fips202.c hash_fixed.c base.c inverse.c pack.c support.c api_glue.c rebase.S keccakf1600.S keccakf1600_v84a.S basemul_rinv.S baseinv_num.S baseinv_finish.S ntt.S inverse16_tail.S ntt_top.S ntt_tail.S ntt9.S inverse_ntt.S inverse9.S inverse16.S crepmod3_raw.S"; X="-DNTRUPLUS1152_ASM_BASEMUL_RINV -DNTRUPLUS1152_ASM_BASEINV_NUM -DNTRUPLUS1152_ASM_BASEINV_FINISH";;
esac
SS=""; for s in $S; do SS="$SS $G/$s"; done
$CC -O3 -std=c11 -D_DEFAULT_SOURCE $X "$@" -I$G -I. -o $O ${MAIN:-bench_min.c} detrand.c ${PERF_C:-} $SS

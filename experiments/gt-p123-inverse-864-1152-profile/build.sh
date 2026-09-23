#!/bin/sh
# usage: [MAIN=driver.c] build.sh GT_TREE OFFICIAL_DIR OUT [extra cc flags]
# GT: every source its Makefile builds (kem.c included, no main).  Official: only
# ntt.s + crepmod3.s from SUPERCOP 20260831, global symbols renamed o_*.
set -e
G=$1; OD=$2; O=$3; shift 3; CC=${CC:-cc}; T=$(mktemp -d)
for f in ntt crepmod3; do
  perl -pe 's/\b(_?)(poly_ntt|poly_invntt_scale|poly_crepmod3)\b/${1}o_$2/g' $OD/$f.s > $T/o_$f.S
done
case $G in *864*) S="symmetric.c fips202.c ntt_api.c base.c add.S crepmod3.S cbd.S ntt.S ntt9.S ntt_top.S unpack.c unpack_api.c kem.c ntt_tail.S pack.c inverse_api.c inverse.S baseinv_num.S baseinv_prefix.S baseinv_inverse.S baseinv_recover.S baseinv_finish.S inverse16_paired.S inverse_tail_direct.S inverse_route.S crepmod3_raw.S basemul_rinv.S inverse9.S support_abi.S hash_fixed.c keccakf1600.S keccakf1600_v84a.S randombytes.c"; X="";;
  *) S="kem.c symmetric.c fips202.c hash_fixed.c base.c inverse.c pack.c support.c api_glue.c rebase.S keccakf1600.S keccakf1600_v84a.S basemul_rinv.S baseinv_num.S baseinv_finish.S ntt.S inverse16_tail.S ntt_top.S ntt_tail.S ntt9.S inverse_ntt.S inverse9.S inverse16.S crepmod3_raw.S randombytes.c"; X="-DNTRUPLUS1152_ASM_BASEMUL_RINV -DNTRUPLUS1152_ASM_BASEINV_NUM -DNTRUPLUS1152_ASM_BASEINV_FINISH";;
esac
SS=""; for s in $S; do SS="$SS $G/$s"; done
$CC -O3 -std=c11 -D_DEFAULT_SOURCE $X "$@" -I$G -o $O ${MAIN:-bench_inv.c} $SS $T/o_ntt.S $T/o_crepmod3.S
rm -rf $T

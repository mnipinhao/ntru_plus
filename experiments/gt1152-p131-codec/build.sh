#!/bin/sh
# usage: [PERF_C=perf_counter.c] [CC=cc] build.sh GT_TREE OFFICIAL_DIR OUT
# GT sources and flags come from the tree (864: its object list; 1152: its Makefile).
set -e
G=$1; OD=$2; O=$3; CC=${CC:-cc}; T=$(mktemp -d)
SYMS='poly_tobytes|poly_frombytes|poly_cbd1|poly_sotp_encode|poly_sotp_decode|poly_ntt|poly_invntt_scale|poly_baseinv_1|poly_basemul_scale|poly_basemul_add|poly_basemul|poly_sub|poly_triple|poly_crepmod3'
for f in add base cbd crepmod3 ntt pack; do perl -pe "s/\\b(_?)($SYMS)\\b/\${1}o_\$2/g" $OD/$f.s > $T/o_$f.S; done
$CC -O3 -std=c11 -D_DEFAULT_SOURCE -include rename.h -I$OD -c $OD/poly.c -o $T/o_poly.o
case $G in
*864*) S="symmetric.c fips202.c ntt_api.c base.c add.S crepmod3.S cbd.S ntt.S ntt9.S ntt_top.S unpack.c unpack_api.c kem.c ntt_tail.S pack.c inverse_api.c inverse.S baseinv_num.S baseinv_prefix.S baseinv_inverse.S baseinv_recover.S baseinv_finish.S inverse16_paired.S inverse_tail_direct.S inverse_route.S crepmod3_raw.S basemul_rinv.S inverse9.S support_abi.S hash_fixed.c keccakf1600.S keccakf1600_v84a.S"; FL="-O3 -std=c11 -D_DEFAULT_SOURCE";;
*) V=$(printf 'v:\n\t@echo $(C_SRC) $(ASM_SRC)\n\t@echo $(CFLAGS)\n' | make -s -C $G -f Makefile -f - v); S=$(echo "$V" | sed -n 1p); FL=$(echo "$V" | sed -n 2p);;
esac
SS=""; for s in $S; do SS="$SS $G/$s"; done
$CC $FL ${EXTRA:-} -I$G -I. -o $O ${MAIN:-comp2.c} detrand.c ${PERF_C:-} $SS $T/o_*.S $T/o_poly.o
rm -rf $T

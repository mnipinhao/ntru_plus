#!/bin/bash
# P136: component benches against SUPERCOP 20260831's Official, on the current trees.
# usage: [PERF_C=perf_counter.c] [CC=cc] build.sh GT_TREE MAIN.c OUT
# GT sources and CFLAGS come from the tree's Makefile (864: KEM_OBJECTS; 1152: C_SRC/ASM_SRC).
set -e
G=$1; M=$2; O=$3; CC=${CC:-cc}; T=$(mktemp -d); H=$(cd $(dirname $0) && pwd)
case $G in *864*) OD=$H/official864;; *) OD=$H/official1152;; esac
SYMS='poly_tobytes|poly_frombytes|poly_cbd1|poly_sotp_encode|poly_sotp_decode|poly_ntt|poly_invntt_scale|poly_baseinv_1|poly_basemul_scale|poly_basemul_add|poly_basemul|poly_sub|poly_triple|poly_crepmod3'
for f in add base cbd crepmod3 ntt pack; do perl -pe "s/\\b(_?)($SYMS)\\b/\${1}o_\$2/g" $OD/$f.s > $T/o_$f.S; done
$CC -O3 -std=c11 -D_DEFAULT_SOURCE -include $H/rename.h -I$OD -c $OD/poly.c -o $T/o_poly.o
case $G in
*864*) V=$(printf 'v:\n\t@echo $(KEM_OBJECTS)\n\t@echo $(CFLAGS)\n' | make -s -C $G -f Makefile -f - BUILD_DIR=@ v)
       S=""; for o in $(echo "$V" | sed -n 1p); do b=${o#@/}; b=${b%.o}; [ -f $G/$b.c ] && S="$S $b.c" || S="$S $b.S"; done;;
*)     V=$(printf 'v:\n\t@echo $(C_SRC) $(ASM_SRC)\n\t@echo $(CFLAGS)\n' | make -s -C $G -f Makefile -f - v); S=$(echo "$V" | sed -n 1p);;
esac
FL=$(echo "$V" | sed -n 2p)
SS=""; for s in $S; do [ $s = randombytes.c ] || SS="$SS $G/$s"; done
$CC $FL -I$G -I$H -o $O $M $H/detrand.c ${PERF_C:-} $SS $T/o_*.S $T/o_poly.o
rm -rf $T

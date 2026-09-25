#!/bin/bash
# usage: [MAIN=file.c] [PERF_C=perf_counter.c] [CC=cc] build768.sh NTRU+768_TREE OUT  (P139 build768.sh; MAIN defaults to mix768.c)
# GT: the tree's Makefile sources and CFLAGS (kem.c included, for the key pair and ciphertext);
# Official: SUPERCOP 20260831's ntruplus768/aarch64 poly.c + asm with every poly_* renamed o_*.
set -e
G=$1; O=$2; CC=${CC:-cc}; H=$(cd $(dirname $0) && pwd); OD=$H/official768; T=$(mktemp -d)
SYMS='poly_tobytes|poly_frombytes|poly_cbd1|poly_sotp_encode|poly_sotp_decode|poly_ntt|poly_invntt_scale|poly_baseinv_1|poly_basemul_scale|poly_basemul_add|poly_basemul|poly_sub|poly_triple|poly_crepmod3'
for f in add base cbd crepmod3 ntt pack; do perl -pe "s/\\b(_?)($SYMS)\\b/\${1}o_\$2/g" $OD/$f.s > $T/o_$f.S; done
$CC -O3 -std=c11 -D_DEFAULT_SOURCE -w -include $H/rename.h -I$OD -I$H/../gt-p138-unified-margins/shim_none -c $OD/poly.c -o $T/o_poly.o
V=$(printf 'v:\n\t@echo $(KEM_SOURCES)\n\t@echo $(CFLAGS)\n' | make -s -C $G -f Makefile -f - v)
SS=""; for s in $(echo "$V" | sed -n 1p); do SS="$SS $G/$s"; done
$CC $(echo "$V" | sed -n 2p) -D_DEFAULT_SOURCE -w -I$G -o $O ${MAIN:-$H/mix768.c} $H/abi_wrap.S $H/detrand.c ${PERF_C:-} $SS $T/o_*.S $T/o_poly.o
rm -rf $T

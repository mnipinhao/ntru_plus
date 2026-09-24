#!/bin/bash
# usage: [CC=cc] [HARNESS=perop5.c] kem_ab.sh NTRU+1152_TREE P129_DIR OUTDIR
# gt1152_base: the tree as shipped.  gt1152_tbl2: api_glue.c's poly_frombytes
# calls frombytes_tbl2_asm (frombytes_tbl2_asm.S added), nothing else changed.
# Both with the tree's Makefile CFLAGS (the -DNTRUPLUS1152_ASM_* kernels).
set -e
G=$1; H=$2; O=$3; CC=${CC:-cc}; HN=${HARNESS:-perop5.c}; D=$(cd $(dirname $0) && pwd)
mkdir -p $O/v
V=$(printf 'v:\n\t@echo $(C_SRC) $(ASM_SRC)\n\t@echo $(CFLAGS)\n' | make -s -C $G -f Makefile -f - v)
S=$(echo "$V" | sed -n 1p); FL=$(echo "$V" | sed -n 2p)
SS=""; VS=""; for s in $S; do [ $s = randombytes.c ] && continue; SS="$SS $G/$s"; [ $s = api_glue.c ] && VS="$VS $O/v/api_glue.c" || VS="$VS $G/$s"; done
perl -pe 's/return frombytes_asm\(r->coeffs, a\);/return frombytes_tbl2_asm(r->coeffs, a);/; $_ = "int frombytes_tbl2_asm(int16_t *, const uint8_t *);\n" . $_ if /^int poly_frombytes\(/' $G/api_glue.c > $O/v/api_glue.c
grep -q "return frombytes_tbl2_asm" $O/v/api_glue.c
$CC $FL -Wno-unused-result -I$G -I$H -o $O/gt1152_base $H/$HN $H/rb2.c $SS
$CC $FL -Wno-unused-result -I$G -I$H -o $O/gt1152_tbl2 $H/$HN $H/rb2.c $VS $D/frombytes_tbl2_asm.S

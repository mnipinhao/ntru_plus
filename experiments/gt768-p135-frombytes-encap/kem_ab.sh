#!/bin/bash
# usage: [CC=cc] [HARNESS=perop5.c] kem_ab.sh NTRU+768_TREE P129_DIR OUTDIR
# gt768_base: the tree as shipped.  gt768_pairs: kem.c's poly_frombytes_encap
# call replaced by frombytes_encap_pairs, nothing else changed.
set -e
P=$1; H=$2; O=$3; CC=${CC:-cc}; HN=${HARNESS:-perop5.c}
SRC="kem.c symmetric.c fips202.c keygen.c tables.c ntt.S decap_ntt.S decap_invntt.S base.S pack.S cbd.S add.S keccakf1600.S keccakf1600_v84a.S kem_api.S"
mkdir -p $O/v
SS=""; VS=""; for s in $SRC; do [ -f $P/$s ] || continue; SS="$SS $P/$s"; [ $s = kem.c ] && VS="$VS $O/v/kem.c" || VS="$VS $P/$s"; done
perl -pe 's/poly_frombytes_encap\(&h, pk\)/frombytes_encap_pairs(h.coeffs, pk)/; $_ .= "int frombytes_encap_pairs(int16_t out[768], const uint8_t in[1152]);\n" if /#include "encap.h"/' $P/kem.c > $O/v/kem.c
grep -q frombytes_encap_pairs $O/v/kem.c
F="-O3 -fomit-frame-pointer -std=c99 -D_DEFAULT_SOURCE -Wno-unused-result -I$P -I$H"
$CC $F -o $O/gt768_base $H/$HN $H/rb2.c $SS
$CC $F -I. -o $O/gt768_pairs $H/$HN $H/rb2.c $VS frombytes_encap_pairs.c

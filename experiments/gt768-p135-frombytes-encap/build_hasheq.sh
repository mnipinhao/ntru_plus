#!/bin/bash
# P135: P120's three builds for NTRU+768 trees at their current source list.
# usage: [CC=cc] build_hasheq.sh P120_DIR OUTDIR MAIN.c RANDOM.c NAME=TREE...   [extra flags in CFLAGS_X]
#   A_official   Official 768 as SUPERCOP ships it (C Keccak)
#   B_<NAME>     the GT tree from its Makefile source list
#   C_<NAME>     the same with Official's fips202.c + symmetric.c in place of GT's hash layer
set -e
H=$1; O=$2; M=$3; RB=$4; shift 4; CC=${CC:-cc}; mkdir -p $O
F="-O3 -fomit-frame-pointer -D_DEFAULT_SOURCE $CFLAGS_X"
d=$H/official
$CC $F -Wno-unused-result -I$H/shim -I$d -o $O/A_official $M $RB $d/kem.c $d/poly.c $d/add.s $d/ntt.s $d/base.s $d/crepmod3.s $d/pack.s $d/cbd.s $d/symmetric.c $d/fips202.c
for nt in "$@"; do
  n=${nt%%=*}; G=${nt#*=}
  src=$(make -s -C $G -f Makefile -f - export_sources <<<$'export_sources:\n\t@echo $(KEM_SOURCES)')
  SS=""; ARITH=""
  for s in $src; do SS="$SS $G/$s"; case $s in symmetric.c|fips202.c|keccakf1600*.S) ;; *) ARITH="$ARITH $G/$s";; esac; done
  $CC $F -I$G -I. -o $O/B_$n $M $RB $SS
  $CC $F "-DNTRUPLUS_INTERNAL=__attribute__((visibility(\"hidden\")))" -I$H/offhash -I$G -I$H/shim -I. -o $O/C_$n $M $RB $ARITH $H/offhash/symmetric.c $H/offhash/fips202.c
done
ls $O

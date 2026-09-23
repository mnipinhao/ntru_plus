#!/bin/sh
# usage: build3.sh GT_TREE OUTDIR MAIN.c RANDOM.c [extra cc flags]   -> OUTDIR/{A_official,B_gt,C_gt_offhash}
G=$1; O=$2; M=$3; RB=$4; shift 4; CC=${CC:-cc}; mkdir -p $O
F="-O3 -fomit-frame-pointer $*"
OFF="official/kem.c official/poly.c official/add.s official/ntt.s official/base.s official/crepmod3.s official/pack.s official/cbd.s"
$CC $F -Wno-unused-result -Ishim -Iofficial -o $O/A_official $M $RB $OFF official/symmetric.c official/fips202.c
GTA="$G/kem.c $G/keygen.c $G/keygen_lambda.c $G/basemul_lambda.c $G/ntt.S $G/base.S $G/pack.S $G/cbd.S $G/crepmod3.S $G/kem_api.S $G/add.S"
$CC $F -I$G -I. -o $O/B_gt $M $RB $GTA $G/symmetric.c $G/fips202.c $G/keccakf1600.S $G/keccakf1600_v84a.S
# C: Official's whole hash layer; its headers come first so GT's kem.c sees Official's symmetric.h/fips202.h too
$CC $F "-DNTRUPLUS_INTERNAL=__attribute__((visibility(\"hidden\")))" -Ioffhash -I$G -Ishim -I. -o $O/C_gt_offhash $M $RB $GTA offhash/symmetric.c offhash/fips202.c

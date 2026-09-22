#!/bin/sh
# usage: build_kem3.sh TREE OUT [extra cc args]   (KEM_SOURCES of the tree's Makefile)
T=$1; O=$2; shift 2
cc -O3 -fomit-frame-pointer -I"$T" -I. "$@" bench_kem3.c "$T/kem.c" "$T/symmetric.c" "$T/fips202.c" "$T/keygen.c" "$T/keygen_lambda.c" "$T/basemul_lambda.c" \
  "$T/ntt.S" "$T/base.S" "$T/pack.S" "$T/cbd.S" "$T/crepmod3.S" "$T/kem_api.S" "$T/add.S" "$T/keccakf1600.S" "$T/keccakf1600_v84a.S" "$T/randombytes.c" -o "$O"

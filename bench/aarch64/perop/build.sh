#!/bin/bash
# Build every binary of the per-operation comparison on this machine.
#
# usage: build.sh OFFICIAL m2|pi OUT [perop.c|outhash.c]
#   OFFICIAL  the directory bench/official/setup.sh assembled
#   m2|pi     Apple M2 Pro (FEAT_SHA3) or Raspberry Pi 5 (Cortex-A76, no FEAT_SHA3)
#   OUT       directory for the binaries, created
#   main      perop.c times the operations (default); outhash.c prints their output
# PRODUCTION (environment) overrides the packages measured, by default this
# repository's production/Additional_Implementation/aarch64.
#
# For each set <s>:
#   offm<s>_noce   main's NO_CE build                                       [M2, A76]
#   offm<s>_ce     main's default build: CE/fips202.c + CE/f1600.S            [M2]
#   offm<s>_gtk    main's CE sponge calling GT's permutation, FEAT_SHA3 on M2
#                  and scalar on the A76 (there NTRUPLUS_FORCE_SHA3 only gets
#                  past the sponge's #error)                                 [M2, A76]
#   gt<s>_offhash  GT's arithmetic and KEM flow with that same sponge and
#                  permutation (offhash_glue.c)                              [M2, A76]
#   gt<s>          the production package, its Makefile's sources and CFLAGS [M2, A76]
set -euo pipefail
OFF=$(cd "${1:?usage: build.sh OFFICIAL m2|pi OUT [main]}" && pwd); M=${2:?}; OUT=${3:?}; MAIN=${4:-perop.c}
H=$(cd "$(dirname "$0")" && pwd)
G=$(cd "${PRODUCTION:-$H/../../../production/Additional_Implementation/aarch64}" && pwd)
CC=${CC:-cc}
case $M in
  m2) SF="-march=armv8.2-a+crypto+sha3"; ADAPTER=$H/f1600_v84a.S; PERMUTATION=keccakf1600_v84a.S;;
  pi) SF="-DNTRUPLUS_FORCE_SHA3 -D__ARM_FEATURE_CRYPTO"; ADAPTER=$H/f1600_scalar.S; PERMUTATION=keccakf1600.S;;
  *) echo "build.sh: the machine is m2 or pi" >&2; exit 1;;
esac
mkdir -p "$OUT"
COMMON="-Wno-unused-result -w -I$OFF/shim -I$H"
RNG=$H/det_randombytes.c
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
for s in 768 864 1152; do
  d=$OFF/offm$s
  OFFSRC="$d/kem.c $d/symmetric.c $d/poly.c $d/add.s $d/ntt.s $d/base.s $d/crepmod3.s $d/pack.s $d/cbd.s"
  PERM="$ADAPTER $G/NTRU+$s/$PERMUTATION"
  $CC -O3 -fomit-frame-pointer $COMMON -I$d -o "$OUT/offm${s}_noce" $H/$MAIN $RNG $OFFSRC $d/fips202.c
  if [ $M = m2 ]; then
    $CC -O3 -fomit-frame-pointer $COMMON -DSUPPORTS_SHAKE256_ASM -I$OFF/cemain -I$d $SF \
        -o "$OUT/offm${s}_ce" $H/$MAIN $RNG $OFFSRC $OFF/cemain/fips202.c $OFF/cemain/f1600.S
  fi
  $CC -O3 -fomit-frame-pointer $COMMON -DSUPPORTS_SHAKE256_ASM -I$OFF/cemain -I$d $SF \
      -o "$OUT/offm${s}_gtk" $H/$MAIN $RNG $OFFSRC $OFF/cemain/fips202.c $PERM
  V=$($H/package_sources.sh $G/NTRU+$s); GF="$(echo "$V" | sed -n 2p) -D_DEFAULT_SOURCE"
  $CC $GF $COMMON -I$G/NTRU+$s -o "$OUT/gt$s" $H/$MAIN $RNG $(echo "$V" | sed -n 1p)
  GS=""
  for f in $(echo "$V" | sed -n 1p); do
    case $(basename $f) in symmetric.c|fips202.c|hash_fixed.c|keccakf1600*.S) ;; *) GS="$GS $f";; esac
  done
  $CC -O3 -fomit-frame-pointer -w -DSUPPORTS_SHAKE256_ASM $SF -I$OFF/shim -I$OFF/cemain -I$d -c $d/symmetric.c -o $T/osym$s.o
  $CC -O3 -fomit-frame-pointer -w -DSUPPORTS_SHAKE256_ASM $SF -I$OFF/shim -I$OFF/cemain -I$d -c $OFF/cemain/fips202.c -o $T/ofips$s.o
  $CC $GF -I$G/NTRU+$s -c $H/offhash_glue.c -o $T/glue$s.o
  $CC $GF $COMMON -I$G/NTRU+$s -o "$OUT/gt${s}_offhash" $H/$MAIN $RNG $GS $T/osym$s.o $T/ofips$s.o $T/glue$s.o $PERM
done
ls "$OUT" | tr '\n' ' '; echo

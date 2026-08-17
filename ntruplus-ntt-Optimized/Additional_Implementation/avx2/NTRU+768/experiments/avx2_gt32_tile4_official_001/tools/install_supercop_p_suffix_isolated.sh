#!/bin/sh
set -eu

supercop=${SUPERCOP:-/home/nuc/supercop-20260627}
name=${1:-avx2-gt-global-inverse-p-suffix-isolated}
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
source=${2:-$root/src/tile4_p_suffix_isolated_asm.S}
baseline=$supercop/crypto_kem/ntruplus768/avx2-gt-global-inverse
target=$supercop/crypto_kem/ntruplus768/$name
stage=$(mktemp -d /tmp/gt32-p-suffix-isolated.XXXXXX)
trap 'rm -rf "$stage"' EXIT HUP INT TERM

cp -a "$baseline"/. "$stage"/
mv "$stage/gt32_keygen.c" "$stage/tile4_keygen_candidate.inc"
cp "$root/src/tile4_keygen_candidate_p_suffix_clean.c" "$stage/gt32_keygen.c"
cp "$source" "$stage/zz_gt32_keypair_psuffix.s"
mkdir -p "$target"
cp -a "$stage"/. "$target"/
printf '%s\n' "$target"

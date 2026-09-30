#!/bin/bash
# Assemble the official implementation that every tool under bench/aarch64/
# compares against: github.com/ntruplus/ntruplus main at 3991b2a, in SUPERCOP
# 20260831's leaf form.
#
# usage: setup.sh OUT SUPERCOP [NTRUPLUS]
#   OUT       output directory, created
#   SUPERCOP  a SUPERCOP 20260831 tree, or any directory that holds its
#             crypto_kem/ntruplus{768,864,1152}/aarch64 leaves
#   NTRUPLUS  a checkout of github.com/ntruplus/ntruplus at 3991b2a; cloned
#             into OUT/src/ntruplus when omitted
#
# Every input file is checked against inputs.sha256 before anything is built.
#
#   OUT/off<set>/   SUPERCOP's leaf, unmodified
#   OUT/offm<set>/  the leaf with main's crepmod3.s.  That is the only file in
#                   which main's NO_CE build differs from the leaf.
#   OUT/cemain/     main's CE sponge and permutation (NTRU+768/CE/), main's
#                   default build on FEAT_SHA3 cores
#   OUT/shim/       SUPERCOP's crypto_*.h and a randombytes.h, for building a
#                   leaf outside SUPERCOP
#   OUT/IDENTITY    the inputs' commit and the SHA-256 of every assembled file
set -euo pipefail
COMMIT=3991b2ae08d6f0008d37e41b8aceaaab27b4ec89
OUT=${1:?usage: setup.sh OUT SUPERCOP [NTRUPLUS]}
SC=${2:?usage: setup.sh OUT SUPERCOP [NTRUPLUS]}
H=$(cd "$(dirname "$0")" && pwd)
sha() { if command -v sha256sum > /dev/null; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d' ' -f1; }

mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)
if [ $# -ge 3 ]; then
  NP=$(cd "$3" && pwd)
else
  NP=$OUT/src/ntruplus
  [ -d "$NP/.git" ] || git clone --quiet https://github.com/ntruplus/ntruplus.git "$NP"
  git -C "$NP" checkout --quiet "$COMMIT"
fi
if [ -d "$NP/.git" ] && [ "$(git -C "$NP" rev-parse HEAD)" != "$COMMIT" ]; then
  echo "setup.sh: $NP is not at $COMMIT" >&2; exit 1
fi

bad=0
while read -r want path; do
  case $want in ''|'#'*) continue;; esac
  case $path in
    supercop/*) f=$SC/${path#supercop/};;
    ntruplus/*) f=$NP/${path#ntruplus/};;
    *) echo "setup.sh: bad inputs.sha256 line: $path" >&2; exit 1;;
  esac
  if [ ! -f "$f" ]; then echo "missing: $f" >&2; bad=1
  elif [ "$(sha "$f")" != "$want" ]; then echo "SHA-256 mismatch: $f" >&2; bad=1; fi
done < "$H/inputs.sha256"
[ $bad = 0 ] || { echo "setup.sh: inputs do not match inputs.sha256" >&2; exit 1; }

for s in 768 864 1152; do
  rm -rf "$OUT/off$s" "$OUT/offm$s"
  cp -R "$SC/crypto_kem/ntruplus$s/aarch64" "$OUT/off$s"
  cp -R "$SC/crypto_kem/ntruplus$s/aarch64" "$OUT/offm$s"
  cp "$NP/Additional_Implementation/aarch64/NTRU+$s/asm/crepmod3.s" "$OUT/offm$s/crepmod3.s"
done
rm -rf "$OUT/cemain" "$OUT/shim"
mkdir -p "$OUT/cemain"
cp "$NP"/Additional_Implementation/aarch64/NTRU+768/CE/{f1600.S,fips202.c,fips202.h} "$OUT/cemain/"
cp -R "$H/shim" "$OUT/shim"

{
  echo "github.com/ntruplus/ntruplus $COMMIT, SUPERCOP 20260831"
  (cd "$OUT" && find off768 off864 off1152 offm768 offm864 offm1152 cemain shim -type f | LC_ALL=C sort |
     while read -r f; do echo "$(sha "$f")  $f"; done)
} > "$OUT/IDENTITY"
echo "official builds assembled in $OUT ($(($(wc -l < "$OUT/IDENTITY") - 1)) files)"

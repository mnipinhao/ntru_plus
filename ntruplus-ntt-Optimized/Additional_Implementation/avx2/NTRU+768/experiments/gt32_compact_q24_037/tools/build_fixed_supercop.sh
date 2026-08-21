#!/bin/sh
set -eu

if [ "$#" -ne 2 ]; then
  echo "usage: $0 IMPLEMENTATION_NAME OUTPUT_ELF" >&2
  exit 2
fi

SUPERCOP=${SUPERCOP:-/home/nuc/supercop-20260627}
IMPLEMENTATION=$1
OUTPUT=$2
IMPL_ROOT="$SUPERCOP/crypto_kem/ntruplus768"
TARGET="$IMPL_ROOT/$IMPLEMENTATION"
PROFILE="$(CDPATH= cd -- "$(dirname -- "$0")/../generated/037r" && pwd)/supercop_compiler_c"
OKC_PROFILE="$(CDPATH= cd -- "$(dirname -- "$0")/../generated/037r" && pwd)/supercop_okc_amd64"
OKC="$SUPERCOP/bench/nucpromtlhcubinucai1ummsb209/bin/okc-amd64"

if [ ! -d "$TARGET" ]; then
  echo "missing implementation: $TARGET" >&2
  exit 1
fi
if [ -e "$OUTPUT" ]; then
  echo "refusing to overwrite: $OUTPUT" >&2
  exit 1
fi

STASH=$(mktemp -d /tmp/gt037r-supercop.XXXXXX)
restore() {
  if [ -f "$STASH/compiler-c" ]; then
    cp "$STASH/compiler-c" "$SUPERCOP/okcompilers/c"
  fi
  if [ -f "$STASH/okc-amd64" ]; then
    cp "$STASH/okc-amd64" "$OKC"
  fi
  for directory in "$STASH"/implementations/*; do
    if [ -d "$directory" ]; then
      mv "$directory" "$IMPL_ROOT/"
    fi
  done
}
trap restore EXIT HUP INT TERM

mkdir "$STASH/implementations"
cp "$SUPERCOP/okcompilers/c" "$STASH/compiler-c"
cp "$PROFILE" "$SUPERCOP/okcompilers/c"
cp "$OKC" "$STASH/okc-amd64"
cp "$OKC_PROFILE" "$OKC"
chmod +x "$OKC"

for directory in "$IMPL_ROOT"/*; do
  if [ -d "$directory" ] && [ "$directory" != "$TARGET" ]; then
    mv "$directory" "$STASH/implementations/"
  fi
done

(
  cd "$SUPERCOP"
  ./do-part crypto_kem ntruplus768
)

MEASURE="$SUPERCOP/bench/nucpromtlhcubinucai1ummsb209/work/compile/measure"
if [ ! -x "$MEASURE" ]; then
  echo "SUPERCOP did not leave an executable measure ELF" >&2
  exit 1
fi
mkdir -p "$(dirname -- "$OUTPUT")"
cp "$MEASURE" "$OUTPUT"

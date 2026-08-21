#!/bin/sh
set -eu
EXP=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SUPER=/home/nuc/supercop-20260627
GT=$SUPER/crypto_kem/ntruplus768/avx2-gt32-clean-20260820
HOST=$SUPER/bench/nucpromtlhcubinucai1ummsb209/include/amd64
mkdir -p "$EXP/build" "$EXP/generated"
CFLAGS="-O3 -march=native -mtune=native -fno-stack-protector -fno-toplevel-reorder -fno-asynchronous-unwind-tables -fno-unwind-tables -fno-builtin-memcpy -fno-tree-loop-distribute-patterns"
gcc $CFLAGS -c "$EXP/src/templates.c" -o "$EXP/build/templates.o"
objcopy --dump-section .text.hash_template="$EXP/build/hash.bin" "$EXP/build/templates.o"
objcopy --dump-section .text.shake_template="$EXP/build/shake.bin" "$EXP/build/templates.o"
if readelf -r "$EXP/build/templates.o" | grep -E '\.text\.(hash|shake)_template' >/dev/null; then
  echo "template contains relocations" >&2; readelf -r "$EXP/build/templates.o" >&2; exit 1
fi
python3 "$EXP/tools/bin2h.py" --hash "$EXP/build/hash.bin" --shake "$EXP/build/shake.bin" --output "$EXP/generated/templates.h"
gcc -O3 -march=native -mtune=native -I"$GT" -I"$EXP/generated" -I"$SUPER/include" -I"$HOST" \
  -o "$EXP/build/address_053" "$EXP/bench/address_053.c" "$GT/KeccakP-1600-AVX2.s"
objdump -d "$EXP/build/templates.o" > "$EXP/build/templates.disasm"

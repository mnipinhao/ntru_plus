#!/bin/bash
# P132: hash of the code and constant bytes of a KEM-only program linked from a
# tree -- identical before and after a step means the step changed no code.
# usage: codehash.sh AARCH64_DIR SET OUTDIR   (SET = 864 | 1152)
set -e
A=$1; n=$2; O=$3; mkdir -p $O
H=$(cd "$(dirname "$0")" && pwd)
if [ $n = 864 ]; then
  SRC=$(sed -n '/^KEM_OBJECTS/,/^$/p' $A/NTRU+864/Makefile | grep -oE '[a-z0-9_]+\.o' | sed 's/\.o$//' | while read b; do ls $A/NTRU+864/$b.c $A/NTRU+864/$b.S 2>/dev/null || true; done)
  FL="-O3 -std=c11 -D_DEFAULT_SOURCE"
else
  V=$(printf 'v:\n\t@echo $(C_SRC) $(ASM_SRC)\n\t@echo $(CFLAGS)\n' | make -s -C $A/NTRU+1152 -f Makefile -f - v)
  SRC=$(for f in $(echo "$V" | sed -n 1p); do echo $A/NTRU+1152/$f; done); FL=$(echo "$V" | sed -n 2p)
fi
rm -f $O/kem$n
cc $FL -I$A/NTRU+$n -o $O/kem$n $H/kem_main.c $SRC $A/NTRU+$n/randombytes.c 2>&1 | grep -v warning >&2 || true
[ -x $O/kem$n ] || { echo BUILD-FAILED; exit 1; }
for sec in __text __const __data; do
  objdump -s -j $sec $O/kem$n 2>/dev/null | grep -E '^ [0-9a-f]+ ' | cut -c1-44
done | shasum -a 256 | cut -c1-16

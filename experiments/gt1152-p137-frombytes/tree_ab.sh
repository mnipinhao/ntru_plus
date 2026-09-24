#!/bin/bash
# usage: [CC=cc] [HARNESS=perop5.c] tree_ab.sh BEFORE_TREE AFTER_TREE P129_DIR OUTDIR
# Both NTRU+1152 trees from their own Makefile source lists and CFLAGS.
set -e
A=$1; B=$2; H=$3; O=$4; CC=${CC:-cc}; HN=${HARNESS:-perop5.c}; mkdir -p $O
for t in before:$A after:$B; do
  n=${t%%:*}; d=${t#*:}
  V=$(printf 'v:\n\t@echo $(C_SRC) $(ASM_SRC)\n\t@echo $(CFLAGS)\n' | make -s -C $d -f Makefile -f - v)
  SS=""; for s in $(echo "$V" | sed -n 1p); do [ $s = randombytes.c ] || SS="$SS $d/$s"; done
  $CC $(echo "$V" | sed -n 2p) -Wno-unused-result -I$d -I$H -o $O/gt1152_$n $H/$HN $H/rb2.c $SS
done

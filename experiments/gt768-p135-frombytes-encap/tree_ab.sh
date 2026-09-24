#!/bin/bash
# usage: [CC=cc] [HARNESS=perop5.c] tree_ab.sh BEFORE_TREE AFTER_TREE P129_DIR OUTDIR
# Both NTRU+768 trees built from their own Makefile source lists and CFLAGS.
set -e
A=$1; B=$2; H=$3; O=$4; CC=${CC:-cc}; HN=${HARNESS:-perop5.c}; mkdir -p $O
for t in before:$A after:$B; do
  n=${t%%:*}; d=${t#*:}
  src=$(make -s -C $d -f Makefile -f - export_sources <<<$'export_sources:\n\t@echo $(KEM_SOURCES)')
  SS=""; for s in $src; do SS="$SS $d/$s"; done
  $CC -O3 -fomit-frame-pointer -std=c99 -D_DEFAULT_SOURCE -Wno-unused-result -I$d -I$H -o $O/gt768_$n $H/$HN $H/rb2.c $SS
done

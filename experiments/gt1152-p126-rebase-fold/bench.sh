#!/bin/sh
# usage: [MAIN=bench_min.c] [PERF_C=perf_counter.c] [CC=cc] bench.sh NTRU+1152_TREE OUT [extra cc flags]
# Sources and -D flags come from the tree's own Makefile.
set -e
G=$1; O=$2; shift 2; CC=${CC:-cc}
V=$(printf 'v:\n\t@echo $(C_SRC) $(ASM_SRC)\n\t@echo $(CFLAGS)\n' | make -s -C $G -f Makefile -f - v)
SRC=$(echo "$V" | sed -n 1p); FL=$(echo "$V" | sed -n 2p)
SS=""; for s in $SRC; do SS="$SS $G/$s"; done
$CC $FL "$@" -I$G -I. -o $O ${MAIN:-bench_min.c} detrand.c ${PERF_C:-} $SS

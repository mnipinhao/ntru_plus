#!/bin/bash
# usage: run_main.sh BINDIR N [PREFIX] -- Official from SUPERCOP 20260831 and from GitHub main, and GT, round robin
D=$1; N=$2; P=${3:-}
for r in $(seq 1 $N); do
  for s in 768 864 1152; do for b in off${s}_noce offm${s}_noce off${s}_ce offm${s}_ce gt$s; do
    [ -x $D/$b ] && $P $D/$b $b
  done; done
done

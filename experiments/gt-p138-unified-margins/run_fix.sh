#!/bin/bash
# usage: run_fix.sh BINDIR N [PREFIX] -- Official as shipped and with the sponge fixes, and GT, round robin
D=$1; N=$2; P=${3:-}
for r in $(seq 1 $N); do
  for s in 768 864 1152; do for b in off${s}_noce off${s}_nocefix off${s}_ce off${s}_cefix gt$s; do
    [ -x $D/$b ] && $P $D/$b $b
  done; done
done

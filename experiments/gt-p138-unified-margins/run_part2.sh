#!/bin/bash
# usage: run_part2.sh BINDIR N [PREFIX]  -- the three builds of the hash-layer split, round robin
D=$1; N=$2; P=${3:-}
for r in $(seq 1 $N); do
  for s in 768 864 1152; do for b in off${s}_gtk off${s}_gtks gt${s}_offhash gt$s; do
    [ -x $D/$b ] && $P $D/$b $b
  done; done
done

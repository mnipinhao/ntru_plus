#!/bin/bash
# usage: run_sessions.sh BINDIR N [PREFIX] -- every build once per session, round robin
D=$1; N=$2; P=${3:-}
for r in $(seq 1 $N); do for s in 768 864 1152; do for b in offm${s}_noce offm${s}_ce offm${s}_gtk gt${s}_offhash gt$s; do
  [ -x $D/$b ] && $P $D/$b $b
done; done; done

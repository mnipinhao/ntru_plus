#!/bin/bash
# usage: run_sessions.sh BINDIR N [PREFIX]   -- N sessions, every binary once per session, round robin
D=$1; N=$2; P=${3:-}
for r in $(seq 1 $N); do
  for s in 768 864 1152; do for b in off${s}_noce off${s}_ce off${s}_gtk off${s}_gtks gt$s; do
    [ -x $D/$b ] && $P $D/$b $b
  done; done
done

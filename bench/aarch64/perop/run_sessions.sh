#!/bin/bash
# usage: run_sessions.sh BIN N [PREFIX...]
# N sessions; each runs every build in BIN once, round robin, so drift during
# the run is charged to all of them alike.  PREFIX runs each binary, e.g.
# `taskset -c 3` on the Pi.  One line per run, on stdout.
D=${1:?usage: run_sessions.sh BIN N [PREFIX...]}; N=${2:?}; shift 2
for r in $(seq 1 "$N"); do
  for s in 768 864 1152; do
    for b in offm${s}_noce offm${s}_ce offm${s}_gtk gt${s}_offhash gt$s; do
      if [ -x "$D/$b" ]; then "$@" "$D/$b" "$b"; fi
    done
  done
done

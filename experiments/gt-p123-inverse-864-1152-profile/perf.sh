#!/bin/sh
# usage: perf.sh N  (on the Pi) -> A76 cycle samples per function, GT then Official
set -e; n=$1
MAIN=cg_driver.c CC=gcc ./build.sh gt/NTRU+$n official$n pf$n -no-pie -fno-pie
for m in 3 4; do
  taskset -c 3 perf record -q -e cycles:u -F 20000 -o pf$n.$m.data ./pf$n $m 2>/dev/null
  perf report -i pf$n.$m.data --stdio --sort symbol 2>/dev/null | grep -v '^#' | grep . | head -16
done

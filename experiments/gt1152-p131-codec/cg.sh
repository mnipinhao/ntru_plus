#!/bin/sh
# usage: cg.sh (on the Pi, in ~/p131) -> dynamic instruction mix per codec function, per call
set -e
MAIN=cg_comp.c CC=gcc EXTRA="-no-pie -fno-pie" ./build.sh gt/NTRU+1152 official1152 cgc
for m in none g_tob g_tobs o_tob g_from o_from g_bmr o_bms; do
  valgrind --tool=callgrind --dump-instr=yes --compress-pos=no --compress-strings=no --callgrind-out-file=cg.$m.out ./cgc $m 2>/dev/null || true
done
for m in g_tob g_tobs o_tob g_from o_from g_bmr o_bms; do python3 mix.py cgc cg.none.out cg.$m.out | sed -n '1p;3,4p'; done

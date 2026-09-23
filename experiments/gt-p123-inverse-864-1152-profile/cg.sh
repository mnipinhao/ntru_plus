#!/bin/sh
# usage: cg.sh N   (on the Pi, in ~/p123) -> dynamic instruction mix of both inverses
set -e; n=$1
MAIN=cg_driver.c CC=gcc ./build.sh gt/NTRU+$n official$n cg$n -no-pie -fno-pie
for m in 0 1 2; do
  valgrind --tool=callgrind --dump-instr=yes --compress-pos=no --compress-strings=no \
    --callgrind-out-file=cg$n.$m.out ./cg$n $m 2>/dev/null
done
python3 mix.py cg$n cg$n.0.out cg$n.1.out cg$n.2.out

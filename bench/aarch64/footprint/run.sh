#!/bin/bash
# usage: run.sh BIN [PAIRS] [CORE]
# Prints, for GT and the official build of each set:
#   size       the linked KEM text: the program minus the same program with empty entry points
#   footprint  the distinct instruction bytes callgrind sees inside each entry point
#   cold       PAIRS (default 12) process pairs per set on CORE (default 3), GT and
#              official alternating which goes first; each prints the medians of 61
#              fully cold runs of each operation
# Needs valgrind, taskset and user-space access to the cycle counter.
set -euo pipefail
X=$(cd "${1:?usage: run.sh BIN [PAIRS] [CORE]}" && pwd); PAIRS=${2:-12}; CORE=${3:-3}
H=$(cd "$(dirname "$0")" && pwd)
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
for s in 768 864 1152; do for i in gt off; do
  a=$(size "$X/sz_$i$s" | awk 'NR==2{print $1}'); b=$(size "$X/szstub_$i$s" | awk 'NR==2{print $1}')
  echo "size $i$s kem_text $((a - b)) (with $a, stub $b)"
done; done
OPS=(crypto_kem_keypair crypto_kem_enc crypto_kem_dec)
for s in 768 864 1152; do for i in gt off; do for op in 0 1 2; do
  valgrind --tool=callgrind --collect-atstart=no --toggle-collect=${OPS[$op]} --dump-instr=yes \
      --dump-line=no --compress-pos=no --compress-strings=no --callgrind-out-file="$T/cg" \
      "$X/fp_$i$s" $op > /dev/null 2>&1
  echo "footprint $i$s op$op $(python3 "$H/footprint.py" "$T/cg")"; rm -f "$T/cg"
done; done; done
for p in $(seq 1 "$PAIRS"); do for s in 768 864 1152; do
  if [ $((p % 2)) = 1 ]; then order="gt off"; else order="off gt"; fi
  for i in $order; do taskset -c "$CORE" "$X/cold_$i$s" $i$s; done
done; done

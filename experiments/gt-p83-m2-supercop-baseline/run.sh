#!/bin/zsh
S="$1"; REPS="${2:-6}"
BINS=(off768_noce off768_ce gt768 off864_noce off864_ce gt864 off1152_noce off1152_ce gt1152)
: > $S/raw.txt
for r in $(seq 1 $REPS); do
  for b in $BINS; do $S/bin/$b $b >> $S/raw.txt 2>&1; done
  echo "rep $r done" >&2
done

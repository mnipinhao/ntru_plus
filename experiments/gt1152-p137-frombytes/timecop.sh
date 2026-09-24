#!/bin/sh
# P137: SUPERCOP TIMECOP (system valgrind) in the P119 staging (TIMECOP cpucycles and valgrind headers set up there);
# the leaf is supercop_run.py's gt-after export, copied in as gt-p137.
# usage (on the Pi): timecop.sh LOOPS LEAF...
LOOPS=$1; shift
B=/home/pi/gt768-p119-supercop/.build; S=$B/supercop; D=$S/crypto_kem/ntruplus1152
for v in "$@"; do
  for n in $(ls $D | grep -v -E '^(checksum|goal)'); do [ -d $D/$n ] && chmod 1755 $D/$n; done
  chmod 755 $D/$v
  (cd $S && env TIMECOP=$LOOPS taskset -c 3 sh ./do-part crypto_kem ntruplus1152 > $B/timecop-$LOOPS-$v.log 2>&1)
  cp $S/bench/pinhao/data $B/timecop-$LOOPS-$v.data
  echo "## $v (TIMECOP=$LOOPS)"
  grep -E " timecop_(pass|fail|error) crypto" $B/timecop-$LOOPS-$v.data | awk '{print "  ", $7, $9}' | sort | uniq -c
  grep " timecop_fail " $B/timecop-$LOOPS-$v.data | grep -oE "at 0x[0-9A-F]+: [^ ]+ \([^)]*\)" | sed -E 's/at 0x[0-9A-F]+: //' | sort | uniq -c | sort -rn | head -5
done

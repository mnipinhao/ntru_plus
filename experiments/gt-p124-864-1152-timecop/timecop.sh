#!/bin/sh
# P124: SUPERCOP TIMECOP (system valgrind) on one NTRU+ set, one implementation at a time.
# usage: timecop.sh N LOOPS IMPL...
N=$1; LOOPS=$2; shift 2
B=/home/pi/gt768-p119-supercop/.build; S=$B/supercop; D=$S/crypto_kem/ntruplus$N
for v in "$@"; do
  for n in $(ls $D | grep -v -E '^(checksum|goal|api|description|designers)'); do [ -d $D/$n ] && chmod 1755 $D/$n; done
  chmod 755 $D/$v
  (cd $S && env TIMECOP=$LOOPS taskset -c 3 sh ./do-part crypto_kem ntruplus$N > $B/timecop-$N-$LOOPS-$v.log 2>&1)
  cp $S/bench/pinhao/data $B/timecop-$N-$LOOPS-$v.data
  echo "## ntruplus$N $v (TIMECOP=$LOOPS)"
  grep -E " timecop_(pass|fail|error) crypto" $B/timecop-$N-$LOOPS-$v.data | awk '{print "  ", $7, $9}' | sort | uniq -c
  grep " timecop_fail " $B/timecop-$N-$LOOPS-$v.data | grep -oE "at 0x[0-9A-F]+: [^ ]+ \([^)]*\)" | sed -E 's/at 0x[0-9A-F]+: //' | sort | uniq -c | sort -rn | head -5
done

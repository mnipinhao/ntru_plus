#!/bin/sh
# P120: SUPERCOP TIMECOP (valgrind memcheck) on three NTRU+768 leaves, one at a time,
# in the P119 staging.  valgrind is user-space (~/vg/bin wrapper, no system install).
set -e
export PATH=$HOME/vg/bin:$PATH
B=/home/pi/gt768-p119-supercop/.build; S=$B/supercop; D=$S/crypto_kem/ntruplus768
for v in official-g gt-noann gt-after-d; do
  for n in official gt-before gt-after gt-after-d gt-noann official-g; do chmod 1755 $D/$n; done
  chmod 755 $D/$v
  echo "=== $v $(date)"
  (cd $S && env TIMECOP=1 taskset -c 3 sh ./do-part crypto_kem ntruplus768 > $B/timecop-$v.log 2>&1) || echo "do-part exit $?"
  cp $S/bench/pinhao/data $B/timecop-$v.data
  grep -E " timecop_(pass|fail|error) " $B/timecop-$v.data | awk '{print $6,$7,$8,$9,$10,$11,$12}' | sort | uniq -c
done
echo "=== done $(date)"

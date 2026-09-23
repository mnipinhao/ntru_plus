#!/bin/sh
# P120: SUPERCOP TIMECOP with the system valgrind (valgrind + matching libc6-dbg installed via apt).
# usage: timecop_system.sh LOOPS LEAF...   (leaves staged under the P119 SUPERCOP staging)
LOOPS=$1; shift
B=/home/pi/gt768-p119-supercop/.build; S=$B/supercop; D=$S/crypto_kem/ntruplus768
echo "valgrind: $(command -v valgrind) $(valgrind --version)"
for v in "$@"; do
  for n in $(ls $D | grep -v -E '^(checksum|goal)'); do chmod 1755 $D/$n; done
  chmod 755 $D/$v
  (cd $S && env TIMECOP=$LOOPS taskset -c 3 sh ./do-part crypto_kem ntruplus768 > $B/timecop-sys-$LOOPS-$v.log 2>&1)
  cp $S/bench/pinhao/data $B/timecop-sys-$LOOPS-$v.data
  echo "## $v (TIMECOP=$LOOPS)"
  grep -E " timecop_(pass|fail|error) crypto" $B/timecop-sys-$LOOPS-$v.data | awk '{print "  ", $7, $9}' | sort | uniq -c
  grep " timecop_fail " $B/timecop-sys-$LOOPS-$v.data | grep -oE "at 0x[0-9A-F]+: [^ ]+ \([^)]*\)" | sed -E 's/at 0x[0-9A-F]+: //; s/gt768_[a-z0-9]+_[a-z]+_//; s/crypto_kem_ntruplus768_[a-z_]+_constbranchindex_//' | sort | uniq -c | sort -rn | head -4
done

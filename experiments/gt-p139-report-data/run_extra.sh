#!/bin/bash
# P139 (Pi): linked size, executed footprint (callgrind), and 12 alternating cold pairs per set on core 3.
X=${1:?}; H=$(cd $(dirname $0) && pwd)
for s in 768 864 1152; do for i in gt off; do
  a=$(size $X/sz_$i$s | awk 'NR==2{print $1}'); b=$(size $X/szstub_$i$s | awk 'NR==2{print $1}')
  echo "size $i$s kem_text $((a - b)) (with $a, stub $b)"
done; done
OPS=(crypto_kem_keypair crypto_kem_enc crypto_kem_dec)
for s in 768 864 1152; do for i in gt off; do for op in 0 1 2; do
  valgrind --tool=callgrind --collect-atstart=no --toggle-collect=${OPS[$op]} --dump-instr=yes --dump-line=no \
      --compress-pos=no --compress-strings=no --callgrind-out-file=/tmp/cg.$$ $X/fp_$i$s $op >/dev/null 2>&1
  echo "footprint $i$s op$op $(python3 $H/footprint.py /tmp/cg.$$)"; rm -f /tmp/cg.$$
done; done; done
for p in $(seq 1 12); do for s in 768 864 1152; do
  if [ $((p % 2)) = 1 ]; then o="gt off"; else o="off gt"; fi
  for i in $o; do taskset -c 3 $X/cold_$i$s $i$s; done
done; done
echo EXTRA-DONE

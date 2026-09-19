#!/bin/sh
# Install the scheduled kernels, prove they still match production, then measure.
set -e
S=/private/tmp/claude-501/-Users-chenpinhao-ntruplus/a827c50f-9c4e-40e1-b926-99dea89f0d8e/scratchpad
G=/Users/chenpinhao/ntruplus/experiments/gt864-p60-fused-terminal
D=$S/inv864_P60s
rm -rf $D && cp -R $S/inv864_P60 $D
for k in fused_bank0 fused_bank1 fused_bank2; do
  if [ -f $G/$k.sched.S ]; then cp $G/$k.sched.S $D/$k.S; echo "  installed $k.sched.S";
  else echo "  $k NOT scheduled, keeping the unscheduled version"; fi
done
cd $S
SRC=""; for f in $D/*.c; do case $(basename $f) in kem.c|randombytes.c) ;; *) SRC="$SRC $f";; esac; done
cc -O3 -mcpu=apple-m1 -I$D dumpinv.c $SRC $D/*.S -o dump_p60s
./dump_p60s out_p60s.bin P60s
if cmp -s out_prod.bin out_p60s.bin; then echo "  CORRECTNESS: byte-identical to production"
else echo "  CORRECTNESS: MISMATCH — not measuring"; exit 1; fi
cc -O3 -mcpu=apple-m1 '-DLABEL="P60-sched"' -Ic_gt864 -I$D ibm.c $SRC $D/*.S -o bin_p60s
echo "=== M2 Pro ==="
./bin_gt864; ./bin_p29; ./bin_p60; ./bin_p60s; ./bin_off864
tar czf /tmp/p60s.tgz --no-xattrs -h -C $S inv864_P60s
scp -q /tmp/p60s.tgz pi@100.99.191.9:/tmp/
ssh -o BatchMode=yes pi@100.99.191.9 'cd ~/inv-cmp && tar xzf /tmp/p60s.tgz -C .
D=$PWD/inv864_P60s; SRC=""
for f in $D/*.c; do case $(basename $f) in kem.c|randombytes.c) ;; *) SRC="$SRC $f";; esac; done
gcc -O3 -march=native -D_GNU_SOURCE -DLABEL=\"P60-sched\" -Ic_gt864 -I$D ib.c $SRC $D/*.S -o bin_p60s 2>/dev/null
echo "=== Pi 5 A76 ==="
echo "--- cycles ---";       for b in gt864 p29 p60 p60s off864; do taskset -c 3 ./bin_$b; done
echo "--- instructions ---"; for b in gt864 p29 p60 p60s off864; do taskset -c 3 ./bin_$b i; done'

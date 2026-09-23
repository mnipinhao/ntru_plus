#!/bin/sh
# P124: stage NTRU+864/1152 in the P119 SUPERCOP staging and export GT leaves.
# usage (on the Pi): stage.sh SRC_ROOT   -- SRC_ROOT/{before,after}/NTRU+{864,1152}
set -e
SRC=$1; B=/home/pi/gt768-p119-supercop/.build; S=$B/supercop; P=/home/pi/supercop-20260831
for n in 864 1152; do
  D=$S/crypto_kem/ntruplus$n
  [ -d $D ] || cp -r $P/crypto_kem/ntruplus$n $D
  for v in before after; do
    rm -rf $D/gt-$v
    python3 $SRC/$v/NTRU+$n/scripts/export_supercop.py $D/gt-$v
  done
  ls $D
done

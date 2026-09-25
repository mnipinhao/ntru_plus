#!/bin/bash
# P139 (Pi): cold-start, footprint and size binaries for GT and Official (GitHub main's NO_CE build).
# usage: build_extra.sh B TREES OUT   (B: P138's build dir with offm<set>/ and shim/; TREES: NTRU+<set>/)
set -e
B=$1; G=$2; O=$3; CC=${CC:-gcc}; H=$(cd $(dirname $0) && pwd); mkdir -p $O
GC="-ffunction-sections -fdata-sections -Wl,--gc-sections"
for s in 768 864 1152; do
  V=$($H/gtsrc.sh $G/NTRU+$s); GS=$(echo "$V" | sed -n 1p); GF="$(echo "$V" | sed -n 2p) -D_DEFAULT_SOURCE -w -I$G/NTRU+$s"
  d=$B/offm$s; OS="$d/kem.c $d/symmetric.c $d/poly.c $d/add.s $d/ntt.s $d/base.s $d/crepmod3.s $d/pack.s $d/cbd.s $d/fips202.c"
  OF="-O3 -fomit-frame-pointer -w -I$B/shim -I$B -I$d"
  for impl in gt off; do
    if [ $impl = gt ]; then SRC=$GS; FL=$GF; else SRC=$OS; FL=$OF; fi
    $CC $FL -I$H -o $O/cold_$impl$s $H/cold.c $H/icache_thrash.S $H/perf_counter.c $H/rb2.c $SRC
    $CC $FL -I$H -o $O/fp_$impl$s $H/footprint.c $H/rb2.c $SRC
    $CC $FL -I$H $GC -o $O/sz_$impl$s $H/size_main.c $H/rb2.c $SRC
    $CC $FL -I$H $GC -DSTUB -o $O/szstub_$impl$s $H/size_main.c $H/rb2.c
  done
done
ls $O | tr '\n' ' '

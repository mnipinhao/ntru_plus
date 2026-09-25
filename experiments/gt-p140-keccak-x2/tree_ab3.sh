#!/bin/bash
# usage: [CC=cc] [HARNESS=perop5.c] tree_ab3.sh BEFORE_AARCH64 AFTER_AARCH64 P129_DIR OUTDIR -- all three sets, each tree from its Makefile
set -e
A=$1; B=$2; H=$3; O=$4; CC=${CC:-cc}; HN=${HARNESS:-perop5.c}; G=$(cd $(dirname $0) && pwd)/../gt-p138-unified-margins/gtsrc.sh; mkdir -p $O
for s in 768 864 1152; do for t in before:$A after:$B; do n=${t%%:*}; d=${t#*:}/NTRU+$s
  V=$($G $d); $CC $(echo "$V" | sed -n 2p) -D_DEFAULT_SOURCE -Wno-unused-result -w -I$d -I$H -o $O/${n}$s $H/$HN $H/rb2.c $(echo "$V" | sed -n 1p)
done; done

#!/bin/sh
# P125: range proof of the linked 864/1152 decapsulation inverse (M2, clang).
# usage: prove.sh [GT_AARCH64_DIR]
set -e
A=${1:-../../ntruplus-GT-Production/Additional_Implementation/aarch64}
T=$(mktemp -d)
./build.sh $A/NTRU+864 $T/ri864 && python3 range_interp2.py $T/ri864 poly_invntt_ternary 864 2497 | grep -v '_q[0-9]*_start\|tail_direct_[0-9]'
./build.sh $A/NTRU+1152 $T/ri1152 && python3 range_interp2.py $T/ri1152 poly_invntt_ternary 1152 2458
rm -rf $T

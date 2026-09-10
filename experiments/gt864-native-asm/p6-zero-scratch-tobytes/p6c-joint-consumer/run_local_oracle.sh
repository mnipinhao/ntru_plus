#!/bin/sh
set -eu

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tmpdir=$(mktemp -d /tmp/gt864-p6c.XXXXXX)
trap 'rm -rf "$tmpdir"' EXIT HUP INT TERM

awk '/^\.global gt864_p6c_pack_a/{emit=1} emit{print} /gt864_p6c_pack_a_slothy_end:/{print "    ret"; exit}' \
    "$here/candidate.pack-a.alloc.S" > "$tmpdir/pack.S"
awk '/^\.global gt864_p6c_row0/{emit=1} emit{print} /gt864_p6c_row0_slothy_end:/{print "    ret"; exit}' \
    "$here/candidate.row0.alloc.S" > "$tmpdir/row.S"

clang -O2 -arch arm64 -c "$tmpdir/pack.S" -o "$tmpdir/pack.o"
clang -O2 -arch arm64 -c "$tmpdir/row.S" -o "$tmpdir/row.o"
clang -O2 -arch arm64 "$here/test_candidate.c" "$here/oracle_wrapper.S" \
    "$tmpdir/pack.o" "$tmpdir/row.o" -o "$tmpdir/test_candidate"
"$tmpdir/test_candidate"

#!/bin/sh
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$here/../../../.." && pwd)
src="$root/ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
tmpdir=$(mktemp -d /tmp/gt864-p6d3.XXXXXX)
trap 'rm -rf "$tmpdir"' EXIT HUP INT TERM

clang -O2 -arch arm64 -c "$here/p6d3-full.alloc.S" -o "$tmpdir/candidate.o"
clang -O2 -arch arm64 -c "$src/gt864_tobytes_public.S" -o "$tmpdir/public.o"
clang -O2 -arch arm64 -c "$src/gt864_tobytes_full_core.S" -o "$tmpdir/full.o"
clang -O2 -arch arm64 -c "$src/gt864_tobytes_small_core.S" -o "$tmpdir/small.o"
clang -O2 -arch arm64 -c "$src/gt864_pair_merge_full.S" -o "$tmpdir/merge-full.o"
clang -O2 -arch arm64 -c "$src/gt864_pair_merge_small.S" -o "$tmpdir/merge-small.o"
clang -O2 -arch arm64 "$here/test_d3.c" "$tmpdir"/*.o -o "$tmpdir/test"
"$tmpdir/test"

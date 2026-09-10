#!/bin/sh
set -eu

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$here/../../../.." && pwd)
tmpdir=$(mktemp -d /tmp/gt864-p6d.XXXXXX)
trap 'rm -rf "$tmpdir"' EXIT HUP INT TERM

python3 "$here/generate_oracle_asm.py"
clang -O2 -arch arm64 -c "$here/oracle.generated.S" -o "$tmpdir/oracle.o"
clang -O2 -arch arm64 -c "$root/ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/gt864_tobytes_full_core.S" -o "$tmpdir/reference.o"
clang -O2 -arch arm64 "$here/test_producer.c" "$tmpdir/oracle.o" "$tmpdir/reference.o" -o "$tmpdir/test_producer"
"$tmpdir/test_producer"

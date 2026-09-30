#!/bin/bash
# Output check: every build of a set must give the same seeded key pair,
# ciphertext and shared secret.  perop.c's self-test cannot see a broken hash,
# because encapsulation and decapsulation would still agree.
# usage: check.sh OFFICIAL m2|pi OUT
set -euo pipefail
H=$(cd "$(dirname "$0")" && pwd)
OUT=${3:?usage: check.sh OFFICIAL m2|pi OUT}
"$H/build.sh" "$1" "$2" "$OUT" outhash.c > /dev/null
fail=0
for s in 768 864 1152; do
  lines=$(for b in offm${s}_noce offm${s}_ce offm${s}_gtk gt${s}_offhash gt$s; do
            if [ -x "$OUT/$b" ]; then "$OUT/$b" "$b"; fi; done)
  echo "$lines"
  if [ "$(echo "$lines" | awk '{print $3, $5, $7}' | sort -u | wc -l)" -eq 1 ]; then
    echo "NTRU+$s: $(echo "$lines" | wc -l | tr -d ' ') builds agree"
  else
    echo "NTRU+$s: OUTPUTS DIFFER"; fail=1
  fi
done
exit $fail

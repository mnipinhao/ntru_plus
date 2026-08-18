#!/bin/sh
set -eu

supercop=${SUPERCOP:-/home/nuc/supercop-20260627}
name=${1:-avx2-gt-hotcompact-c0}
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
target=$supercop/crypto_kem/ntruplus768/$name

"$root/tools/install_supercop_fastest_clean.sh" "$name"

# Phase B is deliberately byte-for-byte execution preserving: remove only the
# post-ret placement cage from the selected production lazy serializer.
python3 - "$target/gt32_q24_codec.s" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text()
needle = " .org .Lq24_lazy_cage_begin + 5120, 0x90\n"
if text.count(needle) != 1:
    raise SystemExit(f"expected one production lazy cage, found {text.count(needle)}")
path.write_text(text.replace(needle, "", 1))
PY

cat >> "$target/CLEAN-MANIFEST.txt" <<EOF
compaction=C0 removes only post-ret lazy10788 Q24 serializer cage
executed_instructions=unchanged
EOF

find "$target" -maxdepth 1 -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum \
	> "$target/SHA256SUMS"
printf '%s\n' "$target"

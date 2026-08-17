#!/bin/sh
set -eu

supercop=${SUPERCOP:-/home/nuc/supercop-20260627}
name=${1:-avx2-gt-fastest-clean-native-rcheck}
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
target=$supercop/crypto_kem/ntruplus768/$name

# The clean installer selects P-J1/finalizer-free/SP1 Keypair and prunes the
# multi-variant assembly sources.  The current export API selects the promoted
# native-domain final verification Decap.
"$root/tools/install_supercop_fastest_clean.sh" "$name"

cat > "$target/CLEAN-MANIFEST.txt" <<'EOF'
implementation=avx2-gt-fastest-clean-native-rcheck
keypair=P-J1 BaseInv; F0xJ1 finalizer-free native BM; SP1 Q24 pack
encap=Q24 SoA decode; N5-to-M; B3 general; H1 high-range Q24 pack
decap=Q24 Decode3; B3-to-M; global inverse; native-domain final verification
benchmark_compiler=O3 + function/data sections + linker section GC
purpose=fastest qualified clean composite with native-rcheck
EOF

find "$target" -maxdepth 1 -type f ! -name SHA256SUMS -print0 |
	sort -z | xargs -0 sha256sum > "$target/SHA256SUMS"
printf '%s\n' "$target"

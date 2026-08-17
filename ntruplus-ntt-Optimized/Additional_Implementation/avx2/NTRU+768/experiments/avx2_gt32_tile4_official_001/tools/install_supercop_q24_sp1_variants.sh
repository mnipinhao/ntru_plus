#!/bin/sh
set -eu

supercop=/home/nuc/supercop-20260627
tool_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
symbol=gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm
old_symbol=gt32_q24_encode_p_soa_halfscatter_lazy10788_asm
stage=$(mktemp -d /tmp/gt32-q24-sp1-supercop.XXXXXX)
trap 'rm -rf "$stage"' EXIT HUP INT TERM

"$tool_root/export_supercop_global_inverse.sh" "$stage/base" >/dev/null

# Select SP1 only in the exported keygen implementation.  Decapsulation and
# encapsulation remain byte-for-byte identical to the production GT control.
sed -i "s/$old_symbol/$symbol/g" "$stage/base/gt32_keygen.c"
sed -i "/void $old_symbol(/i void $symbol(uint8_t *out, const int16_t *in);" \
	"$stage/base/tile4.h"

count=$(grep -c "$symbol" "$stage/base/gt32_keygen.c")
if [ "$count" -ne 3 ]; then
	echo "expected three SP1 keygen calls, found $count" >&2
	exit 100
fi

for front in 0 32 64 96; do
	back=$((96 - front))
	name=avx2-gt-global-inverse-q24-sp1-pad$front
	target=$supercop/crypto_kem/ntruplus768/$name
	if [ -e "$target" ]; then
		echo "refusing to overwrite existing variant: $target" >&2
		exit 100
	fi
	cp -a "$stage/base" "$target"

	# The SP1 function has its own ELF text section.  Keep that section's total
	# padding constant while moving only the function body inside the cage.
	awk -v symbol="$symbol" -v front="$front" -v back="$back" '
		$0 == "\t.globl " symbol {
			if (front != 0) print "\t.space " front ",0x90"
		}
		{ print }
		$0 == "\t.size " symbol ",.-" symbol {
			if (back != 0) print "\t.space " back ",0x90"
		}
	' "$target/gt32_q24_codec.s" > "$target/gt32_q24_codec.s.new"
	mv "$target/gt32_q24_codec.s.new" "$target/gt32_q24_codec.s"

	grep -q "$symbol(" "$target/gt32_keygen.c" || {
		echo "SP1 call selection missing in $target" >&2
		exit 100
	}
	{
		echo "candidate=q24_tf1_sp1_keygen"
		echo "placement_cage_bytes=96"
		echo "sp1_front_padding_bytes=$front"
		echo "sp1_back_padding_bytes=$back"
		echo "production_selector_modified=no"
	} > "$target/PLACEMENT.txt"
	echo "$target"
done

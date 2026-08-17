#!/bin/sh
set -eu

supercop=/home/nuc/supercop-20260627
tool_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
old_symbol=gt32_q24_encode_p_soa_halfscatter_lazy10788_asm
tf1_symbol=gt32_q24_encode_p_soa_halfscatter_tf1_lazy10788_asm
sp1_symbol=gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm
cage_bytes=5120
stage=$(mktemp -d /tmp/gt32-q24-fixed-supercop.XXXXXX)
trap 'rm -rf "$stage"' EXIT HUP INT TERM

"$tool_root/export_supercop_global_inverse.sh" "$stage/base" >/dev/null

for symbol in "$tf1_symbol" "$sp1_symbol"; do
	begin=".L${symbol}_fixed_cage_begin"
	awk -v symbol="$symbol" -v begin="$begin" -v cage="$cage_bytes" '
		$0 == symbol ":" { print; print begin ":"; next }
		$0 == "\t.size " symbol ",.-" symbol {
			print "\t.org " begin " + " cage ",0x90"
		}
		{ print }
	' "$stage/base/gt32_q24_codec.s" > "$stage/base/gt32_q24_codec.s.new"
	mv "$stage/base/gt32_q24_codec.s.new" "$stage/base/gt32_q24_codec.s"
	done

sed -i "/void $old_symbol(/i void $tf1_symbol(uint8_t *out, const int16_t *in);\nvoid $sp1_symbol(uint8_t *out, const int16_t *in);" \
	"$stage/base/tile4.h"

for variant in tf1 sp1; do
	case "$variant" in
		tf1) symbol=$tf1_symbol ;;
		sp1) symbol=$sp1_symbol ;;
	esac
	name=avx2-gt-global-inverse-q24-$variant-fixed
	target=$supercop/crypto_kem/ntruplus768/$name
	if [ -e "$target" ]; then
		echo "refusing to overwrite existing variant: $target" >&2
		exit 100
	fi
	cp -a "$stage/base" "$target"
	sed -i "s/$old_symbol/$symbol/g" "$target/gt32_keygen.c"
	count=$(grep -c "$symbol" "$target/gt32_keygen.c")
	if [ "$count" -ne 3 ]; then
		echo "expected three $variant keygen calls, found $count" >&2
		exit 100
	fi
	{
		echo "candidate=q24_${variant}_fixed_geometry"
		echo "tf1_section_cage_bytes=$cage_bytes"
		echo "sp1_section_cage_bytes=$cage_bytes"
		echo "only_expected_source_delta=gt32_keygen_call_target"
		echo "production_selector_modified=no"
	} > "$target/GEOMETRY.txt"
	echo "$target"
done

diff -u \
	"$supercop/crypto_kem/ntruplus768/avx2-gt-global-inverse-q24-tf1-fixed/gt32_q24_codec.s" \
	"$supercop/crypto_kem/ntruplus768/avx2-gt-global-inverse-q24-sp1-fixed/gt32_q24_codec.s"

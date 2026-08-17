#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
	echo "usage: $0 OUTPUT_DIRECTORY" >&2
	exit 100
fi

output=$1
case "$output" in
	""|/|/home|/home/nuc|/home/nuc/src)
		echo "refusing unsafe output directory: $output" >&2
		exit 100
		;;
esac

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
official=/home/nuc/supercop-20260627/crypto_kem/ntruplus768/avx2
gtn="$root/../gt_ntt"
stage=$(mktemp -d /tmp/gt32-supercop-export.XXXXXX)
trap 'rm -rf "$stage"' EXIT HUP INT TERM

cp -a "$official"/. "$stage"/
rm "$stage/kem.c"

cp "$root/src/tile4.h" "$stage/"
cp "$root/src/tile4_kem_candidate.h" "$stage/"
cp "$root/src/gt32_native_rcheck_placement.h" "$stage/"
cp "$root/src/tile4_kem_encap_candidate.h" "$stage/"
cp "$root/src/tile4_keygen_candidate.h" "$stage/"
cp "$root/src/tile4_kem_decap_global_minimal.c" "$stage/gt32_decap.c"
cp "$root/src/tile4_kem_encap_candidate.c" "$stage/gt32_encap.c"
cp "$root/src/tile4_keygen_candidate.c" "$stage/gt32_keygen.c"
cp "$root/src/tile4_supercop_api.c" "$stage/gt32_kem_api.c"
cp "$root/src/tile4_baseinv_p_soa_flat.c" "$stage/gt32_baseinv_p.c"

cp "$gtn/gt_basemul_soa.h" "$stage/"
cp "$gtn/gt_basemul_soa_tables.inc" "$stage/"
cp "$gtn/gt_ntt_avx2.h" "$stage/"
cp "$gtn/gt_baseinv_native.h" "$stage/"
cp "$gtn/gt_baseinv_native.c" "$stage/"
cp "$gtn/gt_forward_lazy_bounds.h" "$stage/"
cp "$root/generated/tile4_baseinv_p_tables.inc" "$stage/"
mkdir -p "$stage/generated"
cp "$root/generated/tile4_inverse_tail_constants.inc" "$stage/generated/"

preprocess_asm()
{
	source=$1
	target=$2
	shift 2
	cc -E -P -x assembler-with-cpp "$@" -o "$stage/$target" "$source"
}

preprocess_asm "$root/src/tile4_asm.S" gt32_tile4_core.s
preprocess_asm "$root/src/tile4_basemul_asm.S" gt32_tile4_basemul.s
preprocess_asm "$root/src/tile4_q24_codec_asm.S" gt32_q24_codec.s
preprocess_asm "$root/src/tile4_forward_bm_soa_attribution_asm.S" \
	gt32_forward_bm_soa.s
preprocess_asm "$root/src/tile4_inverse_tail_asm.S" gt32_inverse_tail.s \
	-DTILE4_ISOLATED=1
preprocess_asm "$root/src/tile4_global_physical_asm.S" \
	gt32_global_physical.s
preprocess_asm "$root/src/tile4_permutation_relaxed_asm.S" \
	gt32_permutation_relaxed.s
preprocess_asm "$gtn/gt_baseinv_native_prepare_asm.S" \
	gt32_baseinv_prepare.s
preprocess_asm "$gtn/gt_basemul_layout_asm.S" gt32_native_basemul.s

mkdir -p "$output"
cp -a "$stage"/. "$output"/
echo "$output"

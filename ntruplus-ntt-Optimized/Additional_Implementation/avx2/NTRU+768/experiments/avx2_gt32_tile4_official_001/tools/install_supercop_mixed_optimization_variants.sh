#!/bin/sh
set -eu

supercop=/home/nuc/supercop-20260627
source_dir=$supercop/crypto_kem/ntruplus768/avx2-gt-global-inverse

if [ ! -d "$source_dir" ]; then
	echo "missing source implementation: $source_dir" >&2
	exit 100
fi

install_variant()
{
	name=$1
	optimization=$2
	shift 2
	target=$supercop/crypto_kem/ntruplus768/$name
	if [ -e "$target" ]; then
		echo "refusing to overwrite existing variant: $target" >&2
		exit 100
	fi
	cp -a "$source_dir" "$target"
	for source in "$@"; do
		sed -i "1i #pragma GCC optimize (\"$optimization\")" "$target/$source"
	done
	{
		printf 'variant=%s\n' "$name"
		printf 'local_optimization=%s\n' "$optimization"
		printf 'translation_units=%s\n' "$*"
	} > "$target/MIXED_OPTIMIZATION.txt"
}

install_variant avx2-gt-global-inverse-encap-o2 O2 gt32_encap.c
install_variant avx2-gt-global-inverse-decap-o2 O2 gt32_decap.c
install_variant avx2-gt-global-inverse-keygen-o2 O2 \
	gt32_keygen.c gt32_baseinv_p.c gt_baseinv_native.c
install_variant avx2-gt-global-inverse-api-o2 O2 gt32_kem_api.c
install_variant avx2-gt-global-inverse-allhot-o2 O2 \
	gt32_encap.c gt32_decap.c gt32_keygen.c gt32_baseinv_p.c \
	gt_baseinv_native.c gt32_kem_api.c
install_variant avx2-gt-global-inverse-allhot-o3 O3 \
	gt32_encap.c gt32_decap.c gt32_keygen.c gt32_baseinv_p.c \
	gt_baseinv_native.c gt32_kem_api.c

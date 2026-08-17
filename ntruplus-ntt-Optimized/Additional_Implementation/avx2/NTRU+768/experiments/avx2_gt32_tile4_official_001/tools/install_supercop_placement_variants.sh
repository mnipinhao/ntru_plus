#!/bin/sh
set -eu

supercop=/home/nuc/supercop-20260627
source_dir=$supercop/crypto_kem/ntruplus768/avx2-gt-global-inverse

if [ ! -d "$source_dir" ]; then
	echo "missing source implementation: $source_dir" >&2
	exit 100
fi

for padding in 32 64 96; do
	target=$supercop/crypto_kem/ntruplus768/avx2-gt-global-inverse-pad$padding
	if [ -e "$target" ]; then
		echo "refusing to overwrite existing variant: $target" >&2
		exit 100
	fi
	cp -a "$source_dir" "$target"
	sed -i "1a .space $padding,0x90" "$target/gt32_global_physical.s"
	printf '%s\n' "placement_variant=global_physical_front_pad_$padding" > "$target/PLACEMENT.txt"
	diff -u "$source_dir/gt32_global_physical.s" "$target/gt32_global_physical.s" || true
done

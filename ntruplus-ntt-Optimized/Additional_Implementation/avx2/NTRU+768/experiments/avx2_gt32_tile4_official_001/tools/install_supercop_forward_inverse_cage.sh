#!/bin/sh
set -eu

supercop=/home/nuc/supercop-20260627
source_dir=$supercop/crypto_kem/ntruplus768/avx2-gt-global-inverse

install_variant()
{
	forward_front=$1
	inverse_front=$2
	forward_back=$((32 - forward_front))
	inverse_back=$((32 - inverse_front))
	name=avx2-gt-global-inverse-cage-f${forward_front}-i${inverse_front}
	target=$supercop/crypto_kem/ntruplus768/$name
	assembly=$target/gt32_global_physical.s
	if [ -e "$target" ]; then
		echo "refusing to overwrite existing variant: $target" >&2
		exit 100
	fi
	cp -a "$source_dir" "$target"
	sed -i "1a .space $forward_front,0x90" "$assembly"
	sed -i "/^\.size gt32_global_forward_core_asm/a .space $forward_back,0x90\n.space $inverse_front,0x90" "$assembly"
	sed -i "/^\.size gt32_global_inverse_core_asm/a .space $inverse_back,0x90" "$assembly"
	{
		printf 'forward_front_pad=%s\n' "$forward_front"
		printf 'forward_back_pad=%s\n' "$forward_back"
		printf 'inverse_front_pad=%s\n' "$inverse_front"
		printf 'inverse_back_pad=%s\n' "$inverse_back"
		printf 'total_cage_bytes=64\n'
	} > "$target/PLACEMENT_CAGE.txt"
}

install_variant 0 0
install_variant 32 0
install_variant 0 32
install_variant 32 32

#!/bin/sh
set -eu

blocks=${1:-2}
tool_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

case "$blocks" in
	''|*[!0-9]*|0) echo "BLOCKS must be a positive integer" >&2; exit 100 ;;
esac

block=1
while [ "$block" -le "$blocks" ]; do
	for implementation in \
		avx2-gt-global-inverse \
		avx2-gt-global-inverse-p-suffix-iso-pad0 \
		avx2-gt-global-inverse-p-suffix-iso-pad64 \
		avx2-gt-global-inverse-p-suffix-iso-pad128 \
		avx2-gt-global-inverse-p-suffix-iso-pad256 \
		avx2-gt-global-inverse-p-suffix-iso-pad256 \
		avx2-gt-global-inverse-p-suffix-iso-pad128 \
		avx2-gt-global-inverse-p-suffix-iso-pad64 \
		avx2-gt-global-inverse-p-suffix-iso-pad0 \
		avx2-gt-global-inverse
	do
		"$tool_root/run_supercop_cross_flags.sh" "$implementation" O3 1
	done
	block=$((block + 1))
done

#!/bin/sh
set -eu

blocks=${1:-4}
tool_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

case "$blocks" in
	''|*[!0-9]*|0) echo "BLOCKS must be a positive integer" >&2; exit 100 ;;
esac

block=1
while [ "$block" -le "$blocks" ]; do
	for implementation in \
		avx2-gt-global-inverse-p-j1-fixed-control \
		avx2-gt-global-inverse-p-j1-fixed-candidate \
		avx2-gt-global-inverse-p-j1-fixed-candidate \
		avx2-gt-global-inverse-p-j1-fixed-control
	do
		"$tool_root/run_supercop_cross_flags.sh" "$implementation" O3 1
	done
	block=$((block + 1))
done

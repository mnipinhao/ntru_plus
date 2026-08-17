#!/bin/sh
set -eu

blocks=${1:-4}
tool_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

case "$blocks" in
	''|*[!0-9]*|0) echo "BLOCKS must be a positive integer" >&2; exit 100 ;;
esac

block=1
while [ "$block" -le "$blocks" ]; do
	# Symmetric operation order controls temperature and monotonic drift.
	for implementation in \
		avx2 \
		avx2-gt-global-inverse \
		avx2-gt-global-inverse-p-suffix \
		avx2-gt-global-inverse-p-suffix \
		avx2-gt-global-inverse \
		avx2
	do
		"$tool_root/run_supercop_cross_flags.sh" "$implementation" O3 1
	done
	block=$((block + 1))
done

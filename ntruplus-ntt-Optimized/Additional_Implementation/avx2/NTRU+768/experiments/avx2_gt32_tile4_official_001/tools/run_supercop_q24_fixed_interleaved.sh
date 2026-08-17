#!/bin/sh
set -eu

blocks=${1:-4}
tool_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

case "$blocks" in
	''|*[!0-9]*|0) echo "BLOCKS must be a positive integer" >&2; exit 100 ;;
esac

for optimization in O2 O3; do
	block=1
	while [ "$block" -le "$blocks" ]; do
		# ABBA controls monotonic temperature/frequency drift inside each block.
		for variant in tf1 sp1 sp1 tf1; do
			"$tool_root/run_supercop_cross_flags.sh" \
				"avx2-gt-global-inverse-q24-$variant-fixed" \
				"$optimization" 1
		done
		block=$((block + 1))
	done
done

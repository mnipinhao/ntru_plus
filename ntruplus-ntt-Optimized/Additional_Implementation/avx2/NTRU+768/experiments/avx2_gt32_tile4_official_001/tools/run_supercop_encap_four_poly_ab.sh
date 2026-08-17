#!/bin/sh
set -eu

blocks=${1:-8}
tool_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

case "$blocks" in
	''|*[!0-9]*|0) echo "BLOCKS must be positive" >&2; exit 100 ;;
esac

block=1
while [ "$block" -le "$blocks" ]; do
	if [ $((block % 2)) -eq 1 ]; then
		sequence="control candidate candidate control"
	else
		sequence="candidate control control candidate"
	fi
	for variant in $sequence; do
		"$tool_root/run_supercop_cross_flags.sh" \
			"avx2-gt-encap-four-poly-$variant" O3GC 1
	done
	block=$((block + 1))
done

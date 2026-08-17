#!/bin/sh
set -eu

blocks=${1:-4}
tool_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

case "$blocks" in
	''|*[!0-9]*|0) echo "BLOCKS must be positive" >&2; exit 100 ;;
esac

block=1
while [ "$block" -le "$blocks" ]; do
	if [ $((block % 2)) -eq 1 ]; then
		sequence="official candidate candidate official"
	else
		sequence="candidate official official candidate"
	fi
	for variant in $sequence; do
		if [ "$variant" = official ]; then implementation=avx2
		else implementation=avx2-gt-p-j1-batch-tree-candidate
		fi
		"$tool_root/run_supercop_cross_flags.sh" "$implementation" O3GC 1
	done
	block=$((block + 1))
done

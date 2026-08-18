#!/bin/sh
set -eu

blocks=${1:-4}
case "$blocks" in
	''|*[!0-9]*|0) echo "BLOCKS must be a positive integer" >&2; exit 100 ;;
esac

tool_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
experiment_root=$(CDPATH= cd -- "$tool_root/.." && pwd)
stamp=$(date +%Y%m%d-%H%M%S)
log="$experiment_root/results/hotclosure-supercop-matrix-$stamp.log"

run_one()
{
	implementation=$1
	echo "HOTCLOSURE block=$block implementation=$implementation" | tee -a "$log"
	start_lines=$(wc -l < "$log")
	"$tool_root/run_supercop_cross_flags.sh" "$implementation" O3GC 1 >> "$log" 2>&1
	sed -n "$((start_lines + 1)),\$p" "$log" | grep -E '^(Benchmark complete:|do_part_exit_code=|elapsed_seconds=)' || true
}

block=1
while [ "$block" -le "$blocks" ]; do
	# Palindromic order controls slow drift without changing any ELF in place.
	run_one avx2
	run_one avx2-gt-hotclosure-g0-unpruned
	run_one avx2-gt-hotclosure-gc-pruned
	run_one avx2-gt-hotclosure-gc-pruned
	run_one avx2-gt-hotclosure-g0-unpruned
	run_one avx2
	block=$((block + 1))
done

echo "$log"

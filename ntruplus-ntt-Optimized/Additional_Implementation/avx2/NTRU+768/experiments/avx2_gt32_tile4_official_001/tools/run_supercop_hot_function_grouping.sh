#!/bin/sh
set -eu

blocks=${1:-4}
case "$blocks" in ''|*[!0-9]*|0) echo "BLOCKS must be positive" >&2; exit 100 ;; esac
tool_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
experiment_root=$(CDPATH= cd -- "$tool_root/.." && pwd)
stamp=$(date +%Y%m%d-%H%M%S)
log="$experiment_root/results/hotgroup-supercop-matrix-$stamp.log"

run_one()
{
	label=$1 implementation=$2 mode=$3
	echo "HOTGROUP block=$block label=$label implementation=$implementation mode=$mode" | tee -a "$log"
	start_lines=$(wc -l < "$log")
	"$tool_root/run_supercop_cross_flags.sh" "$implementation" "$mode" 1 >> "$log" 2>&1
	sed -n "$((start_lines + 1)),\$p" "$log" | grep -E '^(Benchmark complete:|do_part_exit_code=|elapsed_seconds=)' || true
}

block=1
while [ "$block" -le "$blocks" ]; do
	run_one H0 avx2-gt-hotclosure-gc-pruned O3GC
	run_one H1 avx2-gt-hotgroup-h1-firstuse HOT-H1
	run_one H2 avx2-gt-hotgroup-h2-weighted HOT-H2
	run_one H2 avx2-gt-hotgroup-h2-weighted HOT-H2
	run_one H1 avx2-gt-hotgroup-h1-firstuse HOT-H1
	run_one H0 avx2-gt-hotclosure-gc-pruned O3GC
	block=$((block + 1))
done
echo "$log"

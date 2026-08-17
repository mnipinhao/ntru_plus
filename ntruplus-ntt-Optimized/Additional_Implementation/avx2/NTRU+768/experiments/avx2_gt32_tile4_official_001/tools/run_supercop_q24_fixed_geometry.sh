#!/bin/sh
set -eu

repeats=${1:-2}
tool_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$tool_root/.." && pwd)
supercop=/home/nuc/supercop-20260627
measure=$supercop/bench/nucpromtlhcubinucai1ummsb209/work/compile/measure

case "$repeats" in
	''|*[!0-9]*|0) echo "REPEATS must be a positive integer" >&2; exit 100 ;;
esac

for optimization in O2 O3; do
	for variant in tf1 sp1; do
		implementation=avx2-gt-global-inverse-q24-$variant-fixed
		"$tool_root/run_supercop_cross_flags.sh" \
			"$implementation" "$optimization" "$repeats"
		nm -n "$measure" > \
			"$root/results/supercop-q24-${variant}-fixed-${optimization}.nm"
		readelf -SW "$measure" > \
			"$root/results/supercop-q24-${variant}-fixed-${optimization}.sections"
		objdump -d --no-show-raw-insn "$measure" > \
			"$root/results/supercop-q24-${variant}-fixed-${optimization}.objdump"
	done
done

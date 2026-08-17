#!/bin/sh
set -eu

supercop=${SUPERCOP:-/home/nuc/supercop-20260627}
implementation=${1:-avx2-gt-fastest-clean-prepared-fixed-b3}
output=${2:-results/supercop-prepared-fixed-b3-incremental-measure}
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
measure_source=$supercop/crypto_kem/measure.c
compiled=$supercop/bench/nucpromtlhcubinucai1ummsb209/work/compile/measure
backup=$(mktemp /tmp/supercop-measure-prepared-fixed.XXXXXX)

cp "$measure_source" "$backup"
restore()
{
	cp "$backup" "$measure_source"
	rm -f "$backup"
}
trap restore EXIT HUP INT TERM

cp "$root/tools/supercop_measure_prepared_fixed_b3.c" "$measure_source"
"$root/tools/run_supercop_cross_flags.sh" "$implementation" O3GC 1
cp "$compiled" "$root/$output"
sha256sum "$root/$output"

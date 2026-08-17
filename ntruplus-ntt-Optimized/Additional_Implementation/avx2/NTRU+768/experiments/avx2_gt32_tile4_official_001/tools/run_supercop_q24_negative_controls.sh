#!/bin/sh
set -eu

blocks=${1:-2}
tool_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
supercop=/home/nuc/supercop-20260627
measure_source=$supercop/crypto_kem/measure.c
backup=$(mktemp /tmp/supercop-measure.XXXXXX)
cp "$measure_source" "$backup"
restore()
{
	cp "$backup" "$measure_source"
	rm -f "$backup"
}
trap restore EXIT HUP INT TERM

case "$blocks" in
	''|*[!0-9]*|0) echo "BLOCKS must be a positive integer" >&2; exit 100 ;;
esac

for operation in enc dec; do
	cp "$tool_root/supercop_measure_${operation}_first.c" "$measure_source"
	for optimization in O2 O3; do
		block=1
		while [ "$block" -le "$blocks" ]; do
			for variant in tf1 sp1 sp1 tf1; do
				implementation=avx2-gt-global-inverse-q24-$variant-fixed
				"$tool_root/run_supercop_cross_flags.sh" \
					"avx2-gt-global-inverse-q24-$variant-fixed" \
					"$optimization" 1
				latest=$(find "$supercop/results" -maxdepth 1 -type d \
					-name "ntruplus768-$implementation-*" -printf '%T@ %p\n' |
					sort -nr | sed -n '1s/^[^ ]* //p')
				{
					echo "operation_first=$operation"
					echo "optimization=$optimization"
					echo "variant=$variant"
				} > "$latest/CONTROL_OPERATION.txt"
			done
			block=$((block + 1))
		done
	done
done

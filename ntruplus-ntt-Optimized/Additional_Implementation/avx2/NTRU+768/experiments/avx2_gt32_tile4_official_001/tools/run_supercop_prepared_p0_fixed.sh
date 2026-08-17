#!/bin/sh
set -eu

binary=${1:?usage: run_supercop_prepared_p0_fixed.sh BINARY OUTPUT [LAUNCHES]}
output=${2:?usage: run_supercop_prepared_p0_fixed.sh BINARY OUTPUT [LAUNCHES]}
launches=${3:-16}
cpu=${BENCH_CPU:-1}

test -x "$binary"
mkdir -p "$output"
sha256sum "$binary" > "$output/elf-sha256-before.txt"
{
	echo "timestamp=$(date --iso-8601=seconds)"
	echo "cpu=$cpu"
	echo "cycle_backend=default-perfevent"
	echo "binary=$binary"
} > "$output/environment.txt"

i=1
while [ "$i" -le "$launches" ]; do
	file=$(printf '%s/run-%02d.out' "$output" "$i")
	echo "PREPARED_P0 launch=$i/$launches"
	taskset -c "$cpu" "$binary" > "$file"
	i=$((i + 1))
done
sha256sum "$binary" > "$output/elf-sha256-after.txt"

#!/bin/sh
set -eu

if [ "$#" -lt 3 ] || [ "$#" -gt 4 ]; then
	echo "usage: $0 OFFICIAL_MEASURE GT_MEASURE OUTPUT_DIR [BLOCKS]" >&2
	exit 100
fi

official=$1
gt=$2
output=$3
blocks=${4:-16}
cpu=${BENCH_CPU:-1}

case "$blocks" in
	''|*[!0-9]*|0) echo "BLOCKS must be a positive integer" >&2; exit 100 ;;
esac
test -x "$official"
test -x "$gt"
mkdir -p "$output"

{
	echo "timestamp=$(date --iso-8601=seconds)"
	echo "hostname=$(hostname)"
	echo "kernel=$(uname -sr)"
	echo "cpu=$cpu"
	echo "thread_siblings=$(cat /sys/devices/system/cpu/cpu$cpu/topology/thread_siblings_list 2>/dev/null || echo unavailable)"
	echo "scaling_driver=$(cat /sys/devices/system/cpu/cpu$cpu/cpufreq/scaling_driver 2>/dev/null || echo unavailable)"
	echo "scaling_governor=$(cat /sys/devices/system/cpu/cpu$cpu/cpufreq/scaling_governor 2>/dev/null || echo unavailable)"
	echo "official=$official"
	echo "gt=$gt"
	sha256sum "$official" "$gt"
	size -A "$official" | awk '$1==".text" || $1==".rodata" {print "official_" $1 "=" $2}'
	size -A "$gt" | awk '$1==".text" || $1==".rodata" {print "gt_" $1 "=" $2}'
} > "$output/environment.txt"

run=0
block=1
while [ "$block" -le "$blocks" ]; do
	if [ $((block % 2)) -eq 1 ]; then
		sequence="official gt gt official"
	else
		sequence="gt official official gt"
	fi
	position=1
	for variant in $sequence; do
		run=$((run + 1))
		file=$(printf '%s/run-%03d-block-%02d-pos-%d-%s.out' \
			"$output" "$run" "$block" "$position" "$variant")
		if [ "$variant" = official ]; then binary=$official; else binary=$gt; fi
		printf 'SERIOUS block=%d/%d position=%d variant=%s\n' \
			"$block" "$blocks" "$position" "$variant"
		taskset -c "$cpu" "$binary" > "$file"
		position=$((position + 1))
	done
	block=$((block + 1))
done

sha256sum "$official" "$gt" > "$output/elf-sha256-after.txt"

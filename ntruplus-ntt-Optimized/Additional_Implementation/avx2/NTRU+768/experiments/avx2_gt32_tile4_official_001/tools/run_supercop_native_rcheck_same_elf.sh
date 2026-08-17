#!/bin/sh
set -eu

launches=${1:-8}
implementation=${2:-avx2-gt-native-rcheck-control}
supercop=${SUPERCOP:-/home/nuc/supercop-20260627}
tool_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
measure_source=$supercop/crypto_kem/measure.c
backup=$(mktemp /tmp/supercop-measure-native-rcheck.XXXXXX)
manifest=$tool_root/../results/native-rcheck-same-elf-${implementation}-launches.txt
cp "$measure_source" "$backup"
restore()
{
	cp "$backup" "$measure_source"
	rm -f "$backup"
}
trap restore EXIT HUP INT TERM

case "$launches" in
	''|*[!0-9]*|0) echo "LAUNCHES must be positive" >&2; exit 100 ;;
esac

cp "$tool_root/supercop_measure_native_rcheck_same_elf.c" "$measure_source"
: > "$manifest"
i=1
while [ "$i" -le "$launches" ]; do
	"$tool_root/run_supercop_cross_flags.sh" \
		"$implementation" O3GC 1
	latest=$(find "$supercop/results" -maxdepth 1 -type d \
		-name "ntruplus768-$implementation-*" \
		-printf '%T@ %p\n' | sort -nr | sed -n '1s/^[^ ]* //p')
	printf '%s\n' "$latest" >> "$manifest"
	i=$((i + 1))
done
printf '%s\n' "$manifest"

#!/bin/sh
set -eu

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
	echo "usage: $0 IMPLEMENTATION O2|O3|O3GC|HOT-H1|HOT-H2 [REPEATS]" >&2
	exit 100
fi

implementation=$1
optimization=$2
repeats=${3:-1}
supercop=${SUPERCOP:-/home/nuc/supercop-20260627}
okc=$supercop/bench/nucpromtlhcubinucai1ummsb209/bin/okc-amd64
tool_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

case "$optimization" in
	O2) forced=$tool_root/supercop_okc_o2.sh ;;
	O3) forced=$tool_root/supercop_okc_o3.sh ;;
	O3GC) forced=$tool_root/supercop_okc_o3_gc.sh ;;
	HOT-H1) forced=$tool_root/supercop_okc_o3_gc_hot_h1.sh ;;
	HOT-H2) forced=$tool_root/supercop_okc_o3_gc_hot_h2.sh ;;
	*) echo "unsupported optimization: $optimization" >&2; exit 100 ;;
esac

case "$repeats" in
	''|*[!0-9]*|0) echo "REPEATS must be a positive integer" >&2; exit 100 ;;
esac

backup=$(mktemp /tmp/supercop-okc-amd64.XXXXXX)
cp "$okc" "$backup"
restore()
{
	cp "$backup" "$okc"
	rm -f "$backup"
}
trap restore EXIT HUP INT TERM

cp "$forced" "$okc"
chmod 755 "$okc"

i=1
while [ "$i" -le "$repeats" ]; do
	echo "SUPERCOP_CROSS implementation=$implementation optimization=$optimization repeat=$i/$repeats"
	BENCH_CPU=${BENCH_CPU:-1} "$supercop/run-ntruplus768-avx2.sh" "$implementation"
	i=$((i + 1))
done

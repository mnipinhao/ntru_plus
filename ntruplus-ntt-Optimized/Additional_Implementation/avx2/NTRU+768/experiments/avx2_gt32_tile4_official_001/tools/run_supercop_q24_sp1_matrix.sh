#!/bin/sh
set -eu

repeats=${1:-2}
tool_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

case "$repeats" in
	''|*[!0-9]*|0) echo "REPEATS must be a positive integer" >&2; exit 100 ;;
esac

# Rerun Official in the same session/compiler matrix instead of comparing
# against historical measurements from a different thermal/runtime state.
for optimization in O2 O3; do
	"$tool_root/run_supercop_cross_flags.sh" avx2 "$optimization" "$repeats"
	for front in 0 32 64 96; do
		"$tool_root/run_supercop_cross_flags.sh" \
			"avx2-gt-global-inverse-q24-sp1-pad$front" \
			"$optimization" "$repeats"
	done
done

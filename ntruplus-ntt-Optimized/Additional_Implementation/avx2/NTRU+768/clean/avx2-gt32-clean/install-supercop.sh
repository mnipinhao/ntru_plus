#!/bin/sh
set -eu

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
	echo "usage: $0 SUPERCOP_ROOT [IMPLEMENTATION_NAME]" >&2
	exit 64
fi

supercop_root=$1
implementation=${2:-avx2-gt32-clean}
source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
target_dir=$supercop_root/crypto_kem/ntruplus768/$implementation

if [ ! -d "$supercop_root/crypto_kem/ntruplus768" ]; then
	echo "not a SUPERcop tree: $supercop_root" >&2
	exit 1
fi
if [ -e "$target_dir" ]; then
	echo "refusing to overwrite existing target: $target_dir" >&2
	exit 1
fi

mkdir "$target_dir"
for path in "$source_dir"/*; do
	case $(basename "$path") in
		README.md|SYMBOLS.md|LAYOUTS.md|IMPLEMENTATION.md|BENCHMARK.md|SOURCE-MANIFEST.md|SHA256SUMS|install-supercop.sh)
			continue
			;;
	esac
	cp -R "$path" "$target_dir"/
done

echo "$target_dir"

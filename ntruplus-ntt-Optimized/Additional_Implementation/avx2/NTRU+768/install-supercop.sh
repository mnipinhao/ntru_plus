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
for name in \
	KeccakP-1600-AVX2.s KeccakP-1600-SnP.h \
	Makefile \
	add.s api.h architectures baseinv.c baseinv.h baseinv_impl.inc \
	baseinv_tables.inc basemul.h basemul.s batch_inverse.s cbd.s consts.c \
	consts.h crepmod3.s decap.c encap.c fips202.c fips202.h goal-constbranch \
	goal-constindex internal.h invntt.s kem.c keygen.c ntt.h ntt.s \
	ntt_bounds.h ntt_m.s ntt_p.s pack.s rhash.s params.h poly.c poly.h symmetric.c \
	symmetric.h util.h encap-slot-pad.s e0v-tail.ld QUALIFICATION.md
do
	cp "$source_dir/$name" "$target_dir/$name"
done
mkdir "$target_dir/generated"
cp "$source_dir/generated/tile4_inverse_tail_constants.inc" \
	"$target_dir/generated/tile4_inverse_tail_constants.inc"
mkdir "$target_dir/qualified"
for name in audit-layout.py build-supercop.py encap-control.c encap-e0v.c encap-ql2.c \
	ql2-promotion-results.json
do
	cp "$source_dir/qualified/$name" "$target_dir/qualified/$name"
done

echo "$target_dir"

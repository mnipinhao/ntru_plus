# Third-party comparison checkouts

## NTRU+ Official Main

- Upstream: <https://github.com/ntruplus/ntruplus.git>
- Local path: `third_party/NTRUplus-official-main`
- Revision at import: `0c249d5828b90e8dd5de2c8405323d5ee2a0ce41`
- Imported: 2026-07-30

This ignored source snapshot is the Official Main comparison baseline for the
NTRU+768 AVX2 lane.  It was created with `git archive`, so it intentionally has
no nested Git metadata and cannot drift through an accidental pull.

To restore the exact snapshot after a fresh clone:

```sh
git clone https://github.com/ntruplus/ntruplus.git /tmp/ntruplus-official
git -C /tmp/ntruplus-official checkout \
  0c249d5828b90e8dd5de2c8405323d5ee2a0ce41
git -C /tmp/ntruplus-official archive HEAD | \
  tar -x -C third_party/NTRUplus-official-main
```

The relevant implementation is
`Additional_Implementation/avx2/NTRU+768`.  Keep its in-place Forward and
scaled basemul/inverse contracts distinct from the KPQC Final out-of-place
benchmark API.

## NTTRU

- Upstream: <https://github.com/gregorseiler/NTTRU.git>
- Local path: `third_party/NTTRU`
- Branch at import: `master`
- Revision at import: `65bb4da35944d0ee2ce8462de86e479486904625`
- License: Apache-2.0 for the IBM-authored sources, with the exceptions listed
  in `NTTRU/LICENSE`

The checkout is intentionally ignored by the outer NTRU+ repository and keeps
its own Git metadata. This makes it possible to inspect upstream history or
switch revisions without mixing NTTRU sources into the NTRU+ working tree.

The most relevant comparison lane is `NTTRU/avx2/`. In particular:

- `ntt.s` and `invntt.s`: forward and inverse transforms
- `basemul.s` and `baseinv.s`: NTT-domain multiplication and inversion
- `reduce.s`, `add.s`, `short.s`, and `pack.s`: supporting vector kernels
- `consts.c`: vector constants and transform tables
- `poly.c` and `poly.h`: C wrappers and polynomial interface
- `params.h`: `N = 768`, `Q = 7681`
- `Makefile` and `test/`: build, correctness tests, and cycle benchmarks

To restore the checkout after a fresh clone of this repository:

```sh
git clone https://github.com/gregorseiler/NTTRU.git third_party/NTTRU
git -C third_party/NTTRU checkout 65bb4da35944d0ee2ce8462de86e479486904625
```

To inspect upstream updates without changing the checked-out revision:

```sh
git -C third_party/NTTRU fetch origin
git -C third_party/NTTRU log --oneline HEAD..origin/master
```

The AVX2 lane requires an x86-64 AVX2 host. The current Darwin arm64 host can
be used for source review, but not for executing its AVX2 tests or benchmarks.

See [`../docs/nttru-avx2-comparison-guide.md`](../docs/nttru-avx2-comparison-guide.md)
for the kernel reading order, structural comparison with NTRU+768, and the
recorded x86-64 test result.

The shorter Chinese concept guide is
[`../docs/nttru-avx2-essence-zh.md`](../docs/nttru-avx2-essence-zh.md).

## NTRU Prime truncation

- Upstream: <https://github.com/vector-polymul-ntru-ntrup/NTRU_Prime_truncation.git>
- Paper: <https://eprint.iacr.org/2023/604>
- Local path: `third_party/NTRU_Prime_truncation`
- Branch at import: `main`
- Revision at import: `3eb881fb4aa83a9c424a121acefb1b8d35cf6f93`
- License: CC0-1.0

The checkout is intentionally ignored by the outer NTRU+ repository and keeps
its own Git metadata. It is a source and scheduling reference, not vendored
NTRU+ production code. The most relevant source-reading lane is
`NTRU_Prime_truncation/avx2/avx2_bench/`:

- `__avx2.c`: whole-multiplication pipeline and fused twist/transposes
- `rader17.S`: forward and inverse truncated size-17 Rader transforms
- `radix_3x2.S`: Good–Thomas 3-by-2 transform and twist scheduling
- `basemul.S`: cyclic/negacyclic size-16 convolution kernels
- `basemul_core.inc`, `butterflies.inc`, and `permute.inc`: reusable arithmetic
  and layout macros
- `__avx2_const.c`: pre-expanded Montgomery and twist tables
- `test.c`, `bench_*.c`, and `microbench.c`: upstream correctness and timing
  harnesses

To restore the checkout after a fresh clone of this repository:

```sh
git clone https://github.com/vector-polymul-ntru-ntrup/NTRU_Prime_truncation.git \
  third_party/NTRU_Prime_truncation
git -C third_party/NTRU_Prime_truncation checkout \
  3eb881fb4aa83a9c424a121acefb1b8d35cf6f93
```

At the reviewed revision, `avx2/avx2_bench/Makefile` refers to the defined
variable `COMMON_SOURCEs` as `COMMON_SOURCE`, and its test/benchmark source
lists also omit `ring.c`. Consequently, the documented `make test` and
`make bench` commands fail to link. The upstream checkout remains unmodified;
the complete explicit-source build command and validation evidence are
recorded in the comparison guide.

The AVX2 lane requires an x86-64 AVX2 host. The current Darwin arm64 host is
suitable for source review only.

See
[`../docs/ntru-prime-truncation-avx2-comparison-guide.md`](../docs/ntru-prime-truncation-avx2-comparison-guide.md)
for the full pipeline, structural comparison, reproducible remote validation,
and measurement limitations. The shorter Chinese concept guide is
[`../docs/ntru-prime-truncation-avx2-essence-zh.md`](../docs/ntru-prime-truncation-avx2-essence-zh.md).

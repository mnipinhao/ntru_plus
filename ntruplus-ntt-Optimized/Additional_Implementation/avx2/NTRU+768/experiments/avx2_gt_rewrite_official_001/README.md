# AVX2 GT rewrite against Official Main

Experiment ID: `AVX2-GT-REWRITE-OFFICIAL-001`.

This experiment now contains a complete canonical, byte-exact GT backend and
the evidence needed to decide whether it may replace Official Main.  It does
not currently pass the performance gate, so `BACKEND=official` remains the
default and GT remains opt-in.

Official Main revision `0c249d5828b90e8dd5de2c8405323d5ee2a0ce41`
owns the KEM call graph, public API, `poly` type, in-place transform signatures,
wire formats, scaling, failure behavior, and KAT contract. `ntruplus-KpqC-Final`
is comparison material only and must not define the new API.

The immutable source authority is vendored at:

```text
third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768
```

The tracked GT champion at `../gt_ntt` is a source and benchmark reference. Do
not copy the dirty working tree wholesale. Move kernels into this rewrite only
after their input layout, output layout, scaling, range, aliasing, and consumer
contracts pass a differential test against Official Main.

## Implemented boundaries

- Same-binary Official oracle for forward, basemul/scale, baseinv, inverse,
  serialization, ranges, and supported aliases.
- Generated Official index tree, GT CRT maps, twists, alpha values, schedules,
  scale/range metadata, and hash manifest.
- Scalar B1/B2/C oracle plus int64 schoolbook multiplication in
  `Z_q[x]/(x^768-x^384+1)`.
- AVX2 B1/B2 NTT32 and paired inverse; B1 is selected. C is rejected by its
  register/static-cost gates before AVX2 implementation.
- BM-A direct quartic AVX2 (`vpmaddwd`, signed-int32 reducer), a rejected BM-B
  3q Karatsuba control, AVX2 batch baseinv, mapping-aware serialization, and a
  canonical full-KEM integration.
- Build-time backend selection with the Official public API unchanged and no
  runtime dispatch.

The selected GT layout is backend-private:

```text
batch = ((branch*3+k3)*2+block32)
Q     = 16*block32+lane
word  = 64*batch+16*degree+lane
```

See `contracts/`, `proofs/`, generated `manifest.json`, and `results/` for the
machine-readable contract and gate evidence.

## Reproduce

```sh
make CC=gcc check
make CC=gcc bench-n32
make CC=gcc bench-n32-instructions
make CC=gcc bench-basemul
make CC=gcc bench-basemul-instructions
make CC=gcc bench-kem
make CC=gcc bench-kem-instructions

# Public KEM API, compile-time selection only:
make CC=gcc BACKEND=official selected-kat-run
make CC=gcc BACKEND=gt selected-kat-run
```

`make check` includes the frozen Official contract, generated-file check,
stage/schoolbook/baseinv tests, one-million-vector BM32 test, 8-round
same-binary KEM differential, 100-case byte-exact KAT, release-object audit,
and ASan/UBSan run.

The fused F0/F1 producer and inverse DFT3/preweight/top-CRT/store are AVX2, but
the current compiler-generated cyclic16/NTT32 scheduling still has substantial
fixed row-workspace traffic.  Lazy serialization/add/sub fusion is
intentionally not promoted while this larger boundary remains slower; see the
current numbers in `results/promotion.yml`.

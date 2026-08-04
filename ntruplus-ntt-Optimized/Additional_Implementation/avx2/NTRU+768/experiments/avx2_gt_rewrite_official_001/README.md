# AVX2 GT rewrite against Official Main

Experiment ID: `AVX2-GT-REWRITE-OFFICIAL-001`.

This experiment now contains a complete canonical, byte-exact GT backend and
the evidence needed to decide whether it may replace Official Main. Round 2
decomposed full-caller cost and stopped at the theoretical Amdahl gate: paired
B1 forward/inverse accounts for only 36,778 caller-weighted cycles, while at
least 95,420 cycles must be removed. No Round 2 assembly was started.
`BACKEND=official` therefore remains the default and GT remains opt-in.

Round 3 then closed the complete GT–Official differential. Its authoritative
same-binary baseline is Official 90,611.830 cycles versus GT 186,228.970
cycles. Direct native-layout costs plus one non-nested decapsulation region
reconstruct the 95,617.140-cycle gap to 0.844%; both absolute closures are
also below 5%. The largest coherent scope costs only 53,228.365 cycles even
with an impossible zero floor, so it cannot meet the 70,000-cycle removable
potential gate. The final Round 3 decision is `stop-gt-unsuitable-for-avx2`;
no benchmark-only prototype or integration was authorized.

A subsequent scope-control experiment links the committed
`avx2-gt-ntt-prototype` native keypair kernels into the same Official Main
binary. Its hardened hybrid (native GT keypair, Official encap/decap) is
byte-exact for 100 deterministic triplets and measures `-65 ± 753` paired
cycles versus Official: parity within noise. This does not contradict Round
3, because it bypasses every expensive GT encap/decap boundary. Replacing
only Round 3's keypair with the prototype result would still project about
164.7k cycles. See `results/prototype-branch-comparison.md`.

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
make CC=gcc bench-call-counts
make CC=gcc bench-stages
make CC=gcc bench-stages-pmu
make CC=gcc bench-stages-pmu-summary
make round2-amdahl
make CC=gcc bench-kem
make CC=gcc bench-kem-reversed
make CC=gcc bench-call-counts
make CC=gcc bench-symmetric
make CC=gcc bench-round3-coarse-region
make CC=gcc bench-symmetric-pmu
make round3-attribution
make CC=gcc check-prototype-source-closure
make CC=gcc prototype-keypair-differential
make CC=gcc bench-prototype-compare

# Public KEM API, compile-time selection only:
make CC=gcc BACKEND=official selected-kat-run
make CC=gcc BACKEND=gt selected-kat-run
```

`make check` includes the frozen Official contract, generated-file check,
stage/schoolbook/baseinv tests, one-million-vector BM32 test, 8-round
same-binary KEM differential, 100-case byte-exact KAT, release-object audit,
and ASan/UBSan run.

The fused F0/F1 producer and inverse DFT3/preweight/top-CRT/store are AVX2.
Although compiler-generated cyclic16/NTT32 has substantial fixed workspace
traffic, making that paired boundary infinitely fast still projects about
150,083 cycles per caller triplet. See `proofs/round2-amdahl-gate.md` and
`results/round2-amdahl.json`; a future performance round must use a broader
optimization boundary rather than B1 assembly alone.

Round 3 evidence is in `results/round3-baseline.yml`,
`results/round3-attribution.json`, `results/round3-symmetric-pmu.json`, and
`results/round3-decision.md`. Reversed link order changes the measured gap by
7.267%, so the result is marked frontend-sensitive, but this remains below the
10% attribution-inconclusive threshold.

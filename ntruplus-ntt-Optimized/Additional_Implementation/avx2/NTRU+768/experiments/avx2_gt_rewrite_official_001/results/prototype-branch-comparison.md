# Committed prototype branch comparison

This control compares three materially different scopes in one binary on CPU
1. The prototype source closure is locked to branch revision
`76a0c183f73fb008a808c0c3ebe97af8415ecad5`; no source is read from the dirty
`avx2-gt-ntt-prototype` worktree. Hashes are recorded in
`contracts/prototype-source-closure.json`.

## Correctness

The adapter changes only the obsolete KPQC two-operand `poly_triple` call to
Official Main's in-place signature. The native forward, baseinv, basemul, and
pack kernels are unchanged. One hundred deterministic keypairs and hybrid
KEM triplets matched Official Main byte for byte. The hardened adapter also
applies Official-style secret clearing; a no-clear entry is retained only as
a benchmark control.

## Same-binary result

Measurement: two warmups, 24 balanced-order paired samples, 100 calls per KEM
operation per sample.

| Backend | Keypair | Encap | Decap | Triplet | Paired triplet delta |
|---|---:|---:|---:|---:|---:|
| Official | 38,766.650 | 40,175.380 | 11,959.820 | 91,089.980 | 0 |
| Round 3 canonical full GT | 61,364.410 | 63,520.060 | 62,399.550 | 187,313.260 | +96,598.560 ± 1,038.370 |
| Prototype hardened hybrid | 38,735.570 | 40,019.940 | 12,003.720 | 90,740.690 | -65.030 ± 752.900 |
| Prototype no-clear hybrid | 38,567.500 | 40,049.650 | 11,937.500 | 90,517.590 | -702.510 ± 1,231.700 |

Cycles shown for the first five columns are medians. The paired delta column
is the median and MAD of per-sample differences. The hardened result is
statistically consistent with parity, not evidence of a speedup.

## Why the conclusions differ

The prototype result is a **native GT keypair plus Official encap/decap**. It
keeps the native representation across forward, baseinv, basemul, and pack,
and therefore removes essentially all of the 22.6k-cycle Round 3 keypair gap.
It does not exercise a GT inverse, unpack/frombytes, basemul-scale, ciphertext
add/encode boundary, or decapsulation equality path.

Round 3 instead measures a **complete canonical GT KEM**. Its conclusion is
about the 95.6k full-KEM gap, dominated by encap and decap boundaries that the
prototype hybrid never replaces. Substituting the measured prototype keypair
into the Round 3 full GT while leaving Round 3 encap/decap unchanged projects
approximately 164.7k cycles, still far from Official parity.

Therefore these results are compatible:

- Native GT is demonstrably viable for the coherent keypair pipeline.
- The committed prototype provides no full-native KEM parity evidence.
- Round 3's stop decision remains valid for its frozen canonical full-KEM
  architecture, but must not be generalized to all native GT architectures.

## Next gate

Do not import the dirty worktree wholesale. A future full-native round must
first freeze a committed source closure for one consumer-complete path. The
highest-value path is decapsulation because it accounts for the largest Round
3 gap. That closure must include native unpack, basemul-scale/inverse, and the
equality/serialization boundary; it must be benchmarked as an actual
decapsulation caller, not inferred from isolated inverse kernels.

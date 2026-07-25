# GT-Optimized: Good-Thomas NTRU+768 on AArch64 Neon

This document summarizes the main performance changes in the Good-Thomas
Optimized (GT-Optimized) NTRU+768 AArch64 implementation. It is intended for
reviewers who already understand NTRU+ and want to see where the implementation
differs from KPQC final, why those changes help on Neon, and where the measured
cycle reductions come from.

GT-Optimized keeps the NTRU+768 parameter set, public KEM API, and canonical
public-key, secret-key, and ciphertext encodings unchanged.

This document explains performance and design rationale. The exact production
layout, symbol-pairing, source-closure, and ABI contracts are defined in
[`IMPLEMENTATION.md`](IMPLEMENTATION.md).

## 1. Executive Summary

The primary optimization is a new forward-NTT decomposition built around
Good-Thomas `96 = 3 x 32`. It exposes eight independent length-96 transforms
to the eight 16-bit lanes of Neon vectors and separates each transform into a
3-point dimension and a 32-point dimension without a cross-dimension twiddle
pass.

The resulting forward NTT is approximately 21-25% faster at its production KEM
call sites. Two additional changes improve key generation and decapsulation:

- AArch64 Neon hierarchical batch inversion for key generation.
- A paired pointwise/inverse contract that leaves an `R^-1` factor for the
  inverse final constants to absorb.

Measured on a Raspberry Pi 5 Cortex-A76, with both implementations using
portable `NO_CE` SHAKE:

| Operation | KPQC final | GT-Optimized | Cycle reduction |
|---|---:|---:|---:|
| Key generation | 40,134 | 36,852 | **8.18%** |
| Encapsulation | 39,311 | 37,832 | **3.76%** |
| Decapsulation | 35,179 | 32,741 | **6.93%** |

The full-KEM reductions are smaller than the forward-NTT reduction because
SHAKE, canonical serialization, sampling, and other unchanged work remain in
the complete operation.

## 2. Good-Thomas Forward NTT

### 2.1 Transform shape

GT-Optimized maps the 768-coefficient transform to Neon as follows:

```text
768 coefficients
    -> two 384-coefficient branches
    -> four stride-4 streams per branch
    -> eight length-96 transforms in Neon lanes
    -> Good-Thomas 96 = 3 x 32
    -> 32 groups of eight-way DFT3
    -> three rows of eight-way NTT32
    -> pointwise-native output layout
```

The eight length-96 transforms are independent. At a fixed transform position,
one Neon vector therefore carries one coefficient from each transform:

```text
lane 0..3: four streams from branch 0
lane 4..7: four streams from branch 1
```

The ring-specific top split and twist establish these length-96 transforms.
Good-Thomas then decomposes each transform into coprime dimensions `3` and
`32`.

### 2.2 Why Good-Thomas helps

Because `gcd(3, 32) = 1`, Good-Thomas maps the length-96 index through a
Chinese-remainder permutation. The 3-point and 32-point dimensions do not need
the cross-dimension twiddle multiplication pass required by a mixed-radix
Cooley-Tukey decomposition of the same dimensions.

This does not mean that the complete NTRU+ transform has no twiddle factors.
The ring split still needs its twist, and the DFT3 and NTT32 kernels still use
their own constants. The avoided work is specifically the additional
cross-dimension twiddle layer between the `3` and `32` dimensions.

The decomposition provides four practical implementation advantages:

1. **Eight-way lane parallelism.** Eight scalar transforms execute in parallel
   in the eight 16-bit Neon lanes.
2. **No cross-dimension twiddle pass.** DFT3 output can feed the NTT32 rows
   without an intermediate element-wise twiddle stage.
3. **Repeated row structure.** The three NTT32 rows use the same vector
   arithmetic shape, making bounded scheduling and reuse of kernel structure
   practical.
4. **Consumer-native output.** The final stores produce the block-major layout
   used by the following pointwise kernel instead of restoring KPQC's internal
   NTT-domain order.

The implementation also removes selected scratch store/reload boundaries
between NTT32 stages and schedules bounded arithmetic and modular-reduction
windows for Cortex-A76. These are implementation improvements enabled by the
new transform shape; they are not separate changes to the NTRU+ mathematics.

## 3. Where GT-Optimized Wins

The following measurements use actual production KEM contracts. Combined rows
overlap their component operations and must not be added together.

| KEM path | Measured contract | KPQC final | GT-Optimized | Reduction | Main reason |
|---|---|---:|---:|---:|---|
| Key generation | NTT for `f` | 3,642 | 2,857 | **21.55%** | Good-Thomas and eight-way Neon |
| Key generation | NTT for `g` | 3,639 | 2,867 | **21.21%** | Good-Thomas and eight-way Neon |
| Key generation | Base inversion + following multiplication | 6,693 | 5,708 | **14.72%** | Neon hierarchical batch inversion and retained layout |
| Encapsulation | NTT for `r` | 3,441 | 2,593 | **24.64%** | Good-Thomas and scheduled NTT32 |
| Encapsulation | NTT for `m` | 3,441 | 2,592 | **24.67%** | Good-Thomas and scheduled NTT32 |
| Encapsulation | Multiply-add + ciphertext packing | 3,030 | 2,893 | **4.52%** | Specialized producer-to-packing contract |
| Decapsulation | First multiplication + paired inverse NTT | 6,593 | 5,461 | **17.17%** | Retained `R^-1` and fused inverse constants |
| Decapsulation | NTT for `m1` | 3,441 | 2,593 | **24.64%** | Good-Thomas forward NTT |
| Decapsulation | NTT for `r1` | 3,441 | 2,593 | **24.64%** | Good-Thomas forward NTT |
| Decapsulation | Verify product to canonical bytes | 3,426 | 3,394 | **0.93%** | Compact verification endpoint |

The clearest repeatable improvement is the forward NTT. It is faster in
key generation, encapsulation, and both forward-transform sites in
decapsulation. Key generation and decapsulation then receive separate gains
from their own cross-kernel contracts.

## 4. Key Generation

GT-Optimized keeps the key-generation transform output in a vector-native
coefficient-quartic layout through base inversion, the following pointwise
products, and canonical public-key packing. This avoids converting between
independent kernel layouts at each boundary.

The hierarchical batch-inversion algorithm follows Kim, Cho, and Park,
*Accelerating NTRU+ Key Generation via Hierarchical Batch Inversion*. Their
work provides C and AVX2 implementations. GT-Optimized maps the same method to
AArch64 Neon:

```text
24 denominator vectors
    -> eight groups of three vectors
    -> batch inversion of eight group products
    -> one vector field inversion
    -> hierarchical recovery of all inverses
```

The Neon implementation also uses a 15-multiplication field-inversion addition
chain. The shorter addition chain and hierarchical batching are separate
changes; the complete 14.72% paired improvement must not be attributed only to
the removal of one field multiplication.

## 5. Decapsulation

KPQC final uses its existing Cooley-Tukey forward and Gentleman-Sande inverse
pairing. GT-Optimized uses a Cooley-Tukey inverse that consumes the row order
produced by the Good-Thomas forward path.

The first decapsulation pointwise product deliberately leaves one Montgomery
`R^-1` factor in its output. The inverse final constants absorb that factor
together with inverse normalization, untwist, branch merge, and final scaling.
This avoids a separate factor-correction pass.

For this reason, the meaningful production comparison is:

```text
first decapsulation pointwise product + paired inverse NTT
```

The pair is 17.17% faster than the corresponding KPQC-final path. The generic
standalone `poly_basemul` and `poly_invntt` entrypoints should not be used to
estimate this production-path improvement independently.

## 6. Compatibility and Tradeoffs

GT-Optimized uses a different internal NTT-domain permutation and pointwise
layout from KPQC final. Canonical pack/unpack endpoints absorb that fixed
permutation, so the external byte format remains unchanged.

This approach has two relevant costs:

- Canonical GT serialization performs permutation work in addition to ordinary
  coefficient packing.
- The linked GT-Optimized test binary has approximately 3.63 times the `.text`
  size of KPQC final. Section garbage collection is enabled, and rejected
  experimental variants are not included.

The code-size figure is included as an implementation tradeoff, not as part of
the performance claim. Exact size measurements and component details are in
[`BENCHMARKS.md`](BENCHMARKS.md).

## 7. Measurement and Validation

The public full-KEM benchmark uses:

- Raspberry Pi 5 Cortex-A76 pinned to core 3.
- Linux hardware CPU-cycle counters through `perf_event_open`.
- Debian GCC 14.2.0 with `-O3 -fomit-frame-pointer`.
- Portable `NO_CE` SHAKE for both implementations.
- Balanced `KPQC/GT` and `GT/KPQC` execution order.
- 62 samples per implementation and operation, with 2,000 calls per sample.

The included benchmark and raw samples are under
[`../../benchmark/results/pi5-reference-20260725/`](../../benchmark/results/pi5-reference-20260725/).

Release validation includes:

- 100 full KEM round trips on Linux/AArch64 and macOS/AArch64.
- AAPCS64 callee-saved-register sentinel checks for required public entrypoints.
- Byte-for-byte canonical KAT equality with KPQC final.
- Expected `PQCkemKAT_2336.rsp` SHA-256:
  `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.

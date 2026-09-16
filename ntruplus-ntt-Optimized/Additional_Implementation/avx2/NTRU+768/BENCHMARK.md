# Benchmark record

## Current QL2 production versus Official (139)

The promoted source tree was built directly with SUPERcop's native
`crypto_kem/measure.c`. Each mode used 16 ABBA/BAAB blocks, 32 fresh launches
per implementation, CPU 1, fixed frequency, and 3,072 observations per
operation. Negative delta means GT is faster.

| ASLR | Operation | Official | GT QL2 | GT - Official | Relative | 95% paired-block CI |
|---|---|---:|---:|---:|---:|---:|
| on | Keypair | 21480.32 | 21262.67 | **-217.65** | -1.013% | [-235.21,-190.73] |
| on | Encap | 28113.76 | 28218.59 | **+104.83** | +0.373% | [+54.02,+109.50] |
| on | Decap | 19314.02 | 19247.86 | **-66.16** | -0.343% | [-88.58,-42.69] |
| off | Keypair | 21443.23 | 21263.68 | **-179.55** | -0.837% | [-198.58,-163.23] |
| off | Encap | 28051.12 | 28207.89 | **+156.76** | +0.559% | [+98.87,+170.52] |
| off | Decap | 19262.85 | 19224.85 | **-38.00** | -0.197% | [-53.58,-24.33] |

QL2 substantially narrows the old production Encap gap but does not yet beat
Official. Keypair and Decap remain faster in both ASLR modes. Raw launch data,
ELF hashes, and the parser are retained in experiment 139.

## E0V executable-layout qualification

E0V removes the memory-resident Encap sum polynomial: the existing B3 product
and message M values enter a two-source Q24 routine, which adds them before the
unchanged transpose, reduction, and packing path. Experiments 087 and 091
proved the local and block-caged full-caller mechanisms. Experiment 093 then
qualified the production integration contract.

The geometry-preserving ASLR-on paired block medians were:

| Operation | E0V - control cycles | Bootstrap 95% CI | Favorable blocks |
|---|---:|---:|---:|
| Keypair | -10.375 | [-32.875, +25.75] | 10/16 |
| Encap | **-26.875** | **[-71.75, -8.00]** | **13/16** |
| Decap | +2.750 | [-11.75, +15.50] | 7/16 |

With ASLR disabled the corresponding medians were +13.375, **-42.625**, and
+10.625 cycles; only Encap had a confidence interval excluding zero. Thus the
production expectation is Keypair approximately neutral, Encap faster, and
Decap approximately neutral. The much larger movements in the natural 092
relink are not assigned to E0V.

### Executable layout is an implementation contract

For cycle-scale SIMD optimizations, source-level equivalence is insufficient
when integration moves unrelated hot code by more than the causal credit. This
implementation therefore treats the qualified executable layout as part of
the implementation contract: the Encap caller keeps a 611-byte reservation,
the E0V helper occupies a dedicated page-aligned RX tail, pre-existing hot
text and rodata remain fixed, and a build-time audit rejects drift. Helper size
itself is not frozen; isolation, alignment, security flags, and non-movement of
the existing hot image are the invariant properties.

The production-owned `qualified/build-supercop.py` applies the same link recipe
inside a prepared SUPERcop tree and `qualified/audit-layout.py` emits a map with
symbol geometry, hashes, section flags, and tail alignment.

### 094 frame trim

After E0V promotion, lifetime coloring removed the unused fifth polynomial
slot. A phase-matched three-profile campaign separated address phase from
frame size. `F1-FP` Encap measured -19.375 cycles with ASLR enabled and +4.125
cycles with ASLR disabled; both median-bootstrap confidence intervals crossed
zero widely. The 8128-to-6592-byte frame reduction is therefore selected as a
performance-neutral stack-footprint improvement. No cycle credit is assigned
to it.

## Constant-table-GC fixed-ELF comparison

The independently exported `avx2-gt32-clean-tablegc` implementation was
freshly built next to Official and measured with the same 16-block, 64-launch
fixed-ELF method.  GT `.text` remains 64,343 bytes while `.rodata` falls
from 56,808 to 21,576 bytes.

With ASLR disabled, GT minus Official is:

| Operation | Delta cycles | Relative | Favorable blocks |
|---|---:|---:|---:|
| Keypair | **-345.11** | **-1.606%** | 16/16 |
| Encap | **+102.18** | **+0.365%** | 1/16 |
| Decap | **-219.19** | **-1.134%** | 16/16 |

With ASLR enabled, the deltas are -304.15, +150.65, and -228.81 cycles,
respectively.  Although the ASLR-on medians are more favorable than the
preceding Clean typed image, block dispersion does not consistently improve.
Table GC is therefore retained as image hygiene, but it does not by itself
close whole-image delivery variance.  Full hashes, KAT evidence, statistics,
and raw-run policy are documented in
`experiments/avx2_gt32_tile4_official_001/results/tablegc-formal-20260818/REPORT.md`.

## Fresh formal comparison

The finalized `avx2-clean-typed-v1` directory was compiled alongside Official
Main with GCC 15.2.0 and SUPERcop O3GC flags. The fixed benchmark ELFs were:

| Implementation | ELF SHA-256 | `.text` | `.rodata` |
|---|---|---:|---:|
| Official `avx2` | `c7c1d482a0357fba85d14060196dccd08a616bbf1404ae5a72b24e86df91b217` | 42,007 B | 5,384 B |
| Clean typed | `a3e095ed2800ae5a91fd8d17cd0d93a2c673a1741d75fccd6317c0bfbbb83069` | 64,343 B | 56,808 B |

Each mode used 16 balanced blocks and 64 fresh launches on CPU 1. Odd blocks
were Official/GT/GT/Official and even blocks reversed the order. Each launch
contributed 96 native observations per KEM operation. Negative delta means the
clean implementation is faster.

### Production-like PIE with ASLR enabled

| Operation | Official cycles | Clean cycles | Clean - Official | Relative | Favorable blocks | Bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| Keypair | 21,456.65 | 21,173.91 | **-270.17** | **-1.259%** | 16/16 | [-303.06, -234.73] |
| Encap | 28,033.98 | 28,240.95 | **+207.92** | **+0.742%** | 2/16 | [+167.00, +244.48] |
| Decap | 19,344.52 | 19,144.79 | **-209.63** | **-1.084%** | 16/16 | [-215.85, -193.56] |

Encap contained one +1066-cycle paired-block outlier; its confidence interval
nevertheless remains entirely above zero.

### Same PIE ELFs with ASLR disabled by `setarch -R`

| Operation | Official cycles | Clean cycles | Clean - Official | Relative | Favorable blocks | Bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| Keypair | 21,509.71 | 21,171.57 | **-331.91** | **-1.543%** | 16/16 | [-357.13, -309.17] |
| Encap | 28,032.45 | 28,127.58 | **+110.00** | **+0.392%** | 1/16 | [+64.20, +131.77] |
| Decap | 19,308.30 | 19,094.16 | **-222.43** | **-1.152%** | 16/16 | [-247.75, -198.94] |

The production decision is unchanged: the clean backend wins Keypair and
Decap, but it is not a strict replacement because Official still wins Encap.
Disabling ASLR narrows Encap's delivery variance without changing direction.

Raw launches, fixed ELFs, environment records, and analyzed JSON are under
`experiments/avx2_gt32_tile4_official_001/results/clean-typed-v1-formal-20260818/`.

## Clean-folder validation

The independently installed `avx2-clean-typed` snapshot passed the canonical
100-vector NTRU+768 KAT byte-for-byte on 2026-08-18:

```text
PQCkemKAT_2336.req  36c27b6089b8910733a01fea1136469769b3ca3c35f2b375cfcc592f2112cfaa
PQCkemKAT_2336.rsp  22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8
```

The clean implementation also compiles as independent C/assembly translation
units and relocatably links with only the expected SUPERcop/libc imports:
`randombytes`, `crypto_declassify`, stack checking, and secure clear.

## Required formal method

- SUPERcop implementation directories in one fixed benchmark ELF.
- One pinned physical core.
- Turbo/frequency/runtime state recorded.
- ASLR disabled for the controlled measurement process with `setarch -R`.
- Palindromic Official/GT block order to limit drift.
- Keypair, Encap, and Decap measured from the same binary image.
- Report core cycles as the microarchitecture primary metric and TSC as
  latency corroboration.
- Run KAT, valid differential tests, and malformed/canonicality tests first.

Do not compare isolated numbers from different ELFs or infer a production win
from linker padding.

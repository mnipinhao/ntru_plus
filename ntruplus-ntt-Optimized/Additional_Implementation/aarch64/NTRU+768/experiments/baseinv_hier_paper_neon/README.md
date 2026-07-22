# Paper-Exact Hierarchical Batch Inversion for Neon

## Status

This directory contains a default-off production candidate. The production
default is unchanged. Setting:

```sh
GT_PRODUCTION_USE_PAPER_HIER_K8=1
```

links only paper k8 and selects it for `poly_baseinv_scaled_r()`. Its prepare,
recursive denominator inversion, and finish dispatch are kept in one
translation unit so the compiler can optimize the full path. The k6 and k12
variants remain benchmark-only.

The implementation independently follows Algorithm 15 from *Accelerating
NTRU+ Key Generation via Hierarchical Batch Inversion*.  The external source
repository is used as an algorithm and scheduling reference; its C/AVX2 source
is not copied into this tree.

## Why This Is Different From Current GT

Current production forms eight independent three-vector products, but its
inner `batch_inverse_8_tree_neon()` is a serial length-eight prefix and
recovery chain.  The `TREE` name therefore describes a fixed k=8 decomposition,
not the paper's recursive hierarchy.

The paper-exact variants implemented here are:

```text
k6:  24 -> 6 groups of 4 -> 6 -> 3 -> 1 -> 3 -> 6 -> recover groups
k8:  24 -> 8 groups of 3 -> 8 -> 4 -> 2 -> 1 -> 2 -> 4 -> 8 -> recover groups
k12: 24 -> 12 groups of 2 -> 12 -> 6 -> 3 -> 1 -> 3 -> 6 -> 12 -> recover groups
```

Each node is one `int16x8_t`; the eight lanes are independent Fq elements.
All three variants retain the current scaled-R Montgomery contract and use:

```text
69 vector fqmul
1 gt_fqinv15_asm call
```

The optimization changes the dependency graph, not the arithmetic count.

## Files And Targets

Implementation:

```text
experiments/baseinv_hier_paper_neon/paper_hier_neon.c
```

Isolated denominator, full baseinv, and KPQC-final comparison:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench -B \
  bench_gt_baseinv_paper_hier_neon_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

Same-binary KEM byte differential and keypair PMU:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench -B \
  bench_gt_baseinv_paper_hier_neon_keygen_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

Integrated production-candidate component profile:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench -B \
  bench_gt_kem_component_profile_pmu \
  VARIANT=gt_production_paper_hier_k8 SUDO= CORE=3
```

## Correctness

Pi5, 64 deterministic baseinv inputs per run:

| variant | mod-q mismatches | denominator exact mismatches | full baseinv exact mismatches | h/hinv byte mismatches | zero behavior |
| --- | ---: | ---: | ---: | ---: | --- |
| paper k6 | 0 | 97 | 5 | 0 | pass |
| paper k8 | 0 | 0 | 0 | 0 | pass |
| paper k12 | 0 | 95 | 4 | 0 | pass |

The k6 and k12 multiplication orders can produce different non-canonical
int16 representatives.  They remain equivalent modulo q and produce identical
public-key-domain bytes in this harness.  Paper k8 preserves the current exact
representatives for these inputs.

The same-binary KEM differential passed 1000 deterministic seeds:

```text
keypair return mismatches = 0
pk mismatch seeds         = 0
sk mismatch seeds         = 0
ct mismatch seeds         = 0
enc shared-secret seeds   = 0
dec shared-secret seeds   = 0
```

## Pi5 PMU Results

Pi5, core 3, `NTESTS=31`, `NITERATIONS=5000` for the stage rows:

| row, two operands | cycles | instructions | IPC | delta vs current GT |
| --- | ---: | ---: | ---: | ---: |
| GT quartic prepare | 5678 | 5435 | 0.957 | - |
| KPQC contiguous-Q prepare | 4170 | 5025 | 1.205 | -26.6% |
| denominator current serial-inner | 2073 | 1929 | 0.931 | baseline |
| denominator paper k8 | 1833 | 1885 | 1.028 | -11.6% |
| denominator KPQC flat batch | 2750 | 2285 | 0.831 | +32.7% |
| full current external hier-k8 | 9087 | 8403 | 0.925 | baseline |
| full KPQC final, native contract | 8056 | 8547 | 1.061 | -11.3% |

The KPQC row is a native-contract kernel measurement, not a drop-in GT
replacement. KPQC loses 917 cycles to paper k8 in denominator inversion, but
saves 1508 cycles in prepare. Its `poly_baseinv_1` consumes native contiguous-Q
NTT data and is a hand-scheduled ASM kernel that interleaves two coefficient
groups. GT consumes quartic AoS/block-major data and pays `vld4q_s16` /
`vst4q_s16` in prepare. The prepare/layout contract is the dominant reason the
standalone KPQC baseinv is faster.

A block-local AoS-to-QSoA round trip measured 8776 cycles, but it is not a
valid adapter. Across the diagnostic inputs it produced 97241 inverse mod-q
mismatches and 72922 GT-product mod-q mismatches. The missing mapping includes
global NTT branch/block order and lambda/twiddle correspondence, not only a
four-lane transpose. Therefore 8056 cycles must not be presented as the cost
of a semantically equivalent GT drop-in.

The first paper production adapter called the hierarchy across a translation
unit boundary and showed almost no keypair win. Integrating prepare and the
paper hierarchy in one production-only source recovers the denominator gain:

| production component | current GT | integrated paper k8 | delta |
| --- | ---: | ---: | ---: |
| scaled baseinv x2 | 9085.8 cycles, 8366 instr | 8870.6 cycles, 8360 instr | -215.2 cycles (-2.37%) |
| keypair total | 38513.7 cycles, 83081 instr | 38318.4 cycles, 83075 instr | -195.3 cycles (-0.51%) |

The generated `poly_baseinv_scaled_r` body grows from 2008 to 3044 text bytes
(+1036 bytes). The candidate trades code size for a shorter dependency graph;
it has not been scheduled with Slothy.

The fair three-binary cycle profile is stored in
`aarch64-bench/results/gt_kpqc_paper_hier_k8_integrated_2026-07-19`:

| full KEM | current GT | paper k8 | KPQC final |
| --- | ---: | ---: | ---: |
| keygen | 38298 | 38086 | 39961 |
| encap | 37705 | 37711 | 39050 |
| decap | 33494 | 33474 | 35178 |

Only keygen uses baseinv. The paper keygen win is 212 cycles (0.55%); the
encap/decap deltas are measurement noise. KPQC Final is not faster overall:
current GT is faster by 4.16% in keygen, 3.44% in encap, and 4.79% in decap.

The KEM-path contract also explains why standalone baseinv is misleading:

| keygen component, one chain | current GT | paper k8 | KPQC final |
| --- | ---: | ---: | ---: |
| baseinv | 4515 | 4405 | 4056 |
| matching basemul | 2022 | 2020 | 2641 |
| baseinv + basemul contract | 6534 | 6430 | 6694 |

KPQC wins the isolated baseinv row, but GT wins once the matching scaled-factor
basemul is included.

## Decision

Paper k8 is the preferred candidate:

- fastest denominator and full-baseinv result
- exact representative equality in the current differential inputs
- 1000-seed KEM byte differential pass
- 0.55% keypair-level win in the integrated production build

It is now available through the default-off production gate. It has not been
scheduled with Slothy; the current body is compiler-generated Neon intrinsics.
The next optimization target is the paper-k8 body and the GT prepare/layout
boundary. ASM or Slothy work should use paper k8 as the denominator baseline,
not the old serial-inner tree.

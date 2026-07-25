# GT production A76 kernel and I-cache closeout

Date: 2026-07-23

This report closes the ordered wave:

```text
unused NTT32 closure
-> rminus1 basemul pair pipeline
-> inverse final V0 arithmetic
-> bounded I-cache/link-order experiments
```

Production uses the current source order with section GC enabled. Direct-CQ
keygen remains a separate opt-in profile.

## 1. Unused NTT32 closure

The selected mixed and direct-CQ forward transforms are self-contained. The
standalone `ntt32_batch8_to_blockmajor.n1.opt.S` object was removed from both
full-KEM source lists and retained only through `GT_LEGACY_NTT32_SOURCE` for
legacy/sample tests.

```text
text before: 97959 bytes
text after:  94247 bytes
reduction:    3712 bytes
```

KEM, KAT, layout, and symbol-closure gates pass. This is a code-size closure
change, not an NTT arithmetic speedup.

## 2. Rminus1 basemul pair pipeline

The old loop handled one quartic group at a time. The selected kernel handles
two independent groups per loop and moves the second group's lambda and
operand loads ahead of the first group's final Montgomery fold/store. This
uses load/vector-pipeline overlap while the Cortex-A76 V0 multiply chain is
busy.

The production source is:

```text
asm/gt/basemul/poly_basemul_rminus1.n1.opt.S
```

It keeps the existing raw `R^-1` output contract and preserves AAPCS64
`d8-d15`. The old leaf did not preserve those callee-saved lanes.

Direct paired Pi 5 PMU:

| Variant | Cycles | Instructions | Delta |
|---|---:|---:|---:|
| old arithmetic through ABI-safe wrapper | 2020.02 | 1920 | baseline |
| source-order pair | 2010.01 | 1894 | -10 |
| selected pair schedule | 1912.01 | 1894 | -108 (-5.35%) |

Unique replacement full decapsulation improved by 81 to 115 cycles depending
on AB/BA order. The selected object adds 320 text bytes. Differential, ABI,
KEM, symbol-closure, transform-semantic, and deterministic KAT gates pass.

## 3. Inverse final V0 arithmetic

The active final region already folds normalization, untwist, branch merge,
and the `R^-1` correction into branchfold constants. It also omits the three
intermediate post-DFT3 Barrett reductions.

Dynamic V0 arithmetic remaining in the final region:

| Category | Instructions per inverse |
|---|---:|
| inverse DFT3 multiply | 96 |
| branchfold Montgomery multiply | 576 |
| final Barrett reduction | 576 |
| total | 1248 |

The model in `experiments/invntt_final_v0_arithmetic/` constructs every
inverse-DFT3 output reachable from centered Stage45 values in
`[-1728,1728]^3`. It checks all 192 low/high branchfold outputs and all 65,536
signed 16-bit multipliers for a two-instruction Barrett replacement.

```text
final Barrett deletion safe:       0 / 192 chains
sqrdmulh + mls replacement safe:   0 / 192 chains
ASM candidate emitted:             no
```

The reductions perform real representative correction. Deleting them keeps a
mod-q residue but can change the value by `q`; because `3457 mod 3 = 1`, the
following `poly_crepmod3` can then change. The previously tested quotient-reuse
inverse-plus-crep3 path had the same arithmetic count and was slower in the
production-relevant full path. This line is closed without a new arithmetic
DAG.

## 4. I-cache and link order

Four replacement layouts were measured on Pi 5 core 3 with 61 samples x 2,000
calls:

```text
L0 current
L1 current + function/data sections + --gc-sections
L2 mode-specific source/link order
L3 mode-specific source/link order + section GC
```

First-pass medians:

| Mode | L0 | L1 GC | L2 mode-hot | L3 mode-hot+GC |
|---|---:|---:|---:|---:|
| keygen | 37713 | 37711 | 37720 | 37719 |
| encap | 37604 | 37590 | 37604 | 37582 |
| decap | 32850 | 32825 | 32853 | 32885 |

Section GC reduced text by 14,068 bytes. It also reduced the measured
decapsulation L1I misses from about 10.09 to 3.79 per measured call, but that
did not translate into a stable cycle win. Ten balanced outer AB/BA rounds
gave GC-minus-current paired p50:

| Mode | Paired p50 | Win rate |
|---|---:|---:|
| keygen | +16 cycles | 2/10 |
| encap | -9 cycles | 6/10 |
| decap | +3 cycles | 5/10 |

The cycle result is effectively neutral across the three complete KEM modes,
while the text reduction is large and repeatable. Production therefore adopts
section GC as a deliberate size-first build policy:

- keep the current source order;
- enable `GT_PRODUCTION_USE_SECTION_GC=1` by default;
- retain `GT_PRODUCTION_USE_SECTION_GC=0` only to reproduce the historical
  non-GC baseline;
- leave KPQC final unchanged in comparison builds;
- reject the tested mode-hot order;
- do not add blanket alignment padding.

The A76 diagnosis is that the selected binary was not consistently
frontend-limited. Fewer L1I refills were real, but backend/V0 work still
dominates the arithmetic kernels, and placement changes moved small costs
between KEM modes. The GC promotion is therefore justified by the 14,068-byte
text reduction, not by a claimed cycle speedup.

After making GC the production default, the current exact `kem_enc` build was
remeasured with the same sources and counter configuration:

```text
GC disabled: 95270 text bytes
GC enabled:  81162 text bytes
reduction:   14108 text bytes
```

The 40-byte difference from the first 14,068-byte result comes from the newer
current binary closure/placement. The stable claim is approximately 14.1 KB
less text.

## 5. Current GT versus KPQC final

Pi 5 Cortex-A76, portable `NO_CE`, 31 samples x 2,000 calls:

| Operation | KPQC final | GT production | GT reduction |
|---|---:|---:|---:|
| keygen | 39995 | 37721 | 5.69% |
| encapsulation | 39075 | 37604 | 3.76% |
| decapsulation | 35193 | 32848 | 6.66% |

Selected component results:

| Component | KPQC | GT | GT delta |
|---|---:|---:|---:|
| forward NTT | 3606 | 2861 | -20.66% |
| generic inverse diagnostic | 3969 | 4087 | +2.97% |
| decap rminus1 basemul actual | 2641 | 1912 | -27.60% |
| decap rminus1 inverse actual | 3952 | 3557 | -9.99% |
| decap first basemul+inverse pair | 6594 | 5467 | -17.09% |
| keygen baseinv+basemul contract | 6693 | 5698 | -14.87% |

The complete profiler is:

```text
aarch64-bench/results/gt_production_section_gc_2026-07-23/
```

The remaining measured overhead is concentrated at canonical serialization
boundaries, not in the promoted rminus1 pair or a removable inverse-final
reduction.

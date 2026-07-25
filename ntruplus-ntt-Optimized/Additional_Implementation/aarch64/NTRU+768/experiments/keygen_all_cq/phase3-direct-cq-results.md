# Keygen All-CQ Phase 3: Direct-CQ NTT Endpoint

Date: 2026-07-23

Branch: `codex/aarch64-keygen-all-cq`

Status: correctness, ABI, KEM, and Pi 5 performance gates pass. This is the
selected serious all-CQ experiment candidate; production default is unchanged.

## Contract

Each Stage345 block produces eight complete BPQ Q values, split into two CQ
groups. A CQ group consumes four BPQ Q values and emits four coefficient-major
vectors in the existing production lane order:

```text
P0, P2, P4, P6, P1, P3, P5, P7
```

The exact endpoint is:

```text
Stage345 output Q
  -> proof-backed parking when an output register is overwritten early
  -> 4x8 in-register trn transpose
  -> four fixed-offset CQ stores
```

The active arithmetic, modular reduction, and Stage345 producer schedule are
unchanged. Across 24 CQ groups the generated endpoint uses:

```text
parking moves       9
trn instructions  192
CQ Q stores        96
spills               0
raw Q reloads        0
recomputation        0
```

The feasibility analyzer preserves the 96 audited low-D output sites as
semantic uses and unifies `D/Q/V` aliases to one physical Neon register. All
24 groups pass the no-spill gate.

## Correctness and ABI

Pi 5 results:

```text
1000 differential cases against:
  production poly_ntt
    -> block-major-to-BPQ
    -> existing BPQ-to-CQ contract

direct mismatches     0
in-place mismatches   0
ABI mask              0x0
full KEM count        0
```

The ABI sentinel checks `x19-x28` and the AAPCS64-required low `d8-d15`
halves. The feature-usage and secret-independent static checkers report zero
warnings. The generic Neon pattern checker reports only the inherited modular
multiply patterns and the explicit transpose operations measured here.

## Endpoint PMU

Pi 5 Cortex-A76, core 3 pinned, same binary, Linux grouped `perf_event_open`,
61 samples x 20000 calls:

| Endpoint | Cycles | Instructions | CPI |
|---|---:|---:|---:|
| production raw block-major NTT | 2592.02 | 3701 | 0.7004 |
| production NTT + BPQ + CQ adapters | 3328.97 | 5950 | 0.5595 |
| direct-BPQ NTT + CQ adapter | 2739.32 | 3917 | 0.6993 |
| direct-CQ NTT | 2660.47 | 3722 | 0.7148 |

Direct-CQ removes 78.85 cycles and 195 instructions from the direct-BPQ plus
CQ path. Compared with raw block-major NTT it costs 68.45 cycles and 21
instructions, but already returns the layout consumed by CQ pointwise kernels.

## Keygen Components

Pi 5, portable NO_CE hash, 31 samples x 2000 calls:

| Component | Direct-BPQ all-CQ | Direct-CQ all-CQ | Delta |
|---|---:|---:|---:|
| sample NTT f | 2935 | 2854 | -81 |
| sample NTT g | 2922 | 2866 | -56 |
| baseinv actual | 3946 | 3946 | 0 |
| basemul actual | 1762 | 1762 | 0 |
| baseinv + basemul | 5708 | 5708 | 0 |

The pointwise budget is unchanged. The gain is isolated to the two keygen NTT
terminal-layout paths.

## Full Keygen

Replacement binaries use Linux perf-event cycles, deterministic inputs, core 3
pinning, 61 samples x 2000 keypairs, and 200 warmups. Two balanced-order runs:

| Variant | Run 1 | Run 2 | Midpoint |
|---|---:|---:|---:|
| mixed GT production | 37680 | 37691 | 37685.5 |
| direct-BPQ all-CQ | 36947 | 36950 | 36948.5 |
| direct-CQ all-CQ | 36753 | 36756 | 36754.5 |

Direct-CQ saves approximately:

```text
vs direct-BPQ all-CQ: 194 cycles, 0.53%
vs mixed production:  931 cycles, 2.47%
```

Retired instructions:

| Variant | Instructions |
|---|---:|
| mixed GT production | 86067 |
| direct-BPQ all-CQ | 81942 |
| direct-CQ all-CQ | 81565 |

Direct-CQ retires 377 fewer instructions than direct-BPQ and 4502 fewer than
mixed production.

## Code Size

With identical function/data sections and linker garbage collection:

| Replacement binary | Text bytes |
|---|---:|
| mixed GT production | 89698 |
| direct-BPQ all-CQ | 100561 |
| direct-CQ all-CQ | 101193 |

Direct-CQ is 11495 bytes larger than production. The measured binary still
needs generic `poly_ntt` for encapsulation and decapsulation and adds a complete
keygen-only CQ NTT body. This duplication, not correctness or keygen speed, is
the promotion blocker.

Measured symbols:

```text
poly_ntt                       address 0x77a0, size 0x39b8
gt_experiment_poly_ntt_to_cq  address 0x12600, size 0x3a0c
```

Both are 32-byte aligned; the CQ candidate is 64-byte aligned.

## Decision

Keep direct-CQ as the selected serious all-CQ experiment candidate,
default-off. Do not replace GT production yet.

The next gate is a shared-core/code-size design: keep one Phase123/Stage12 core
and branch only into the generic block-major versus keygen CQ Stage345 endpoint
tail. The gate must preserve the measured direct-CQ cycles while removing most
of the duplicated NTT text.

# Early-CQ Keygen Phase 1 Results

Date: 2026-07-22

Branch: `codex/aarch64-keygen-all-cq`

Status: correctness pass, performance experiment only, not selected for
production.

## Question

Would key generation be faster if both NTT operands entered persistent CQ
layout before base inversion, so baseinv, basemul, and pack could all consume
the same coefficient-major quartic layout?

No complete earlier all-CQ keygen pipeline was found in the repository. The
historical direct-tuple candidates used k-major/AoS memory and transient `ld4`
loads; they did not keep a persistent CQ representation across baseinv and
basemul.

## Candidate

Phase 1 deliberately leaves the shared production NTT unchanged:

```text
poly_ntt block-major
  -> production block-major-to-BPQ
  -> BPQ-to-CQ once
  -> CQ-input hierarchical K=8 baseinv
  -> scaled-R CQ inverse
  -> CQ x CQ basemul
  -> CQ pack
```

This is an adapter baseline. It measures the value and cost of the persistent
CQ contract before changing the NTT final-store epilogue.

CQ lanes follow the production transpose order:

```text
P0, P2, P4, P6, P1, P3, P5, P7
```

The existing `gt_keygen_bpq_lambda8` table is already ordered for these lanes.

## Correctness

Pi 5 differential, 1000 random small-polynomial pairs:

```text
pack_mismatches             = 0
invertibility_mismatches    = 0
product_mismatches          = 0
product_mod_q_mismatches    = 0
mixed_product_max_abs       = 1853
all_cq_product_max_abs      = 1853
ABI sentinel mask           = 0x0
```

The full KEM test also completed with `count: 0`.

The first CQ basemul draft was mathematically correct modulo q but performed
two Montgomery reductions and then added the representatives. Its maximum
absolute output was 3507, outside the CQ pack's expected range, causing 30
packed-byte mismatches. The accepted version matches the production
single-final-reduction shape; both backends then have maximum absolute output
1853 and byte-identical pack results.

## Pi 5 Component Cycles

Cortex-A76, portable NO_CE hash path, core 3 pinned, Linux `perf_event` cycles,
31 samples x 2000 calls, 100 warmups. Values are medians.

| Keygen component | Mixed production | Early CQ | Delta |
|---|---:|---:|---:|
| sample NTT f, including endpoint adapters | 3302 | 3468 | +166 |
| sample NTT g, including endpoint adapters | 3305 | 3465 | +160 |
| baseinv actual | 4044 | 3946 | -98 |
| basemul actual | 1668 | 1762 | +94 |
| baseinv + basemul contract | 5708 | 5708 | 0 |
| public CQ pack | 566 | 568 | +2 |
| secret f pack | 605 | 568 | -37 |
| secret hinv CQ pack | 568 | 568 | 0 |

The sample-NTT delta isolates the extra BPQ-to-CQ conversion after the same
shared `poly_ntt` and block-major-to-BPQ adapter. Its observed cost is about
163 cycles per polynomial.

The direct CQ baseinv saves about 98 cycles, but the compiler-generated CQ x CQ
basemul loses about 94 cycles against the Slothy-scheduled mixed BPQ x CQ ASM.
Consequently, the combined pointwise contract is currently flat.

## Full Keygen

The first full-keygen run was rejected: `bench_kem_runtime.c` had its own mixed
BPQ/CQ wrapper and did not call the candidate functions. The wrapper now gives
`GT_EXPERIMENT_USE_KEYGEN_ALL_CQ` precedence, and symbol audit is required
before accepting results.

Accepted replacement-binary comparison:

- both binaries use `-ffunction-sections -fdata-sections -Wl,--gc-sections`;
- core 3 pinned;
- 61 samples x 2000 deterministic keypairs, 200 warmups;
- balanced order A/B/B/A;
- output checksums are identical.

| Run | Mixed production cycles | Early CQ cycles |
|---|---:|---:|
| first pair | 37739 | 37958 |
| second pair | 37736 | 37957 |
| mean of medians | 37737.5 | 37957.5 |

Early CQ is **220 cycles slower**, or approximately **0.58%**.

## Code Size

With identical linker garbage collection:

| Replacement binary | Text bytes |
|---|---:|
| mixed production | 89561 |
| early CQ | 83233 |

The phase-1 candidate is 6328 text bytes smaller. The candidate uses
compiler-generated direct-CQ baseinv/basemul kernels and removes the mixed
BPQ prepare, BPQ x CQ basemul, and BPQ secret pack from the live source
closure. This is useful code-size evidence, but it does not offset the measured
cycle regression.

## Decision

Do not promote phase 1 to production.

The experiment establishes three facts:

1. A persistent CQ keygen contract is mathematically and ABI safe.
2. Moving the transpose earlier does not by itself reduce the baseinv+basemul
   cycle budget; the current optimized mixed ASM is already strong.
3. The next meaningful gate is an NTT endpoint change. Phase 2 first inserts a
   direct-BPQ checkpoint so the block-major-to-BPQ cost can be measured
   independently from the approximately 163-cycle BPQ-to-CQ conversion.

Phase 2 subsequently showed that block-major-to-BPQ is the larger boundary;
see `phase2-direct-bpq-results.md`.

Phase 2 should remain default-off and compare:

```text
mixed production
vs direct-CQ NTT + current phase-1 CQ kernels
vs direct-CQ NTT + scheduled CQ x CQ basemul
```

The promotion bar remains full-keygen cycles, not isolated conversion or code
size.

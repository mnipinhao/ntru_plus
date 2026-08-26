# NTRU+864 Good-Thomas Neon optimization campaign

Status: planning and contract reconstruction; Production is unchanged.

Repository revision: `c8bdd73c113951b42c75bbc8903e7be3ab7dd548`

## Campaign goals

This campaign has two equal goals:

1. Produce a faster NTRU+864 AArch64 Neon implementation using a proven
   Good-Thomas decomposition where it improves the full KEM.
2. Make every mathematical, representation, implementation, validation, and
   promotion decision understandable and reproducible by the repository owner.

Generated code may be written by tools or AI, but no generated or hand-written
kernel is accepted as an unexplained black box.

## Current source-of-truth

Production remains:

```text
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+864/
```

All campaign work remains default-off below this directory:

```text
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/Experiment/NTRU+864/
```

The frozen comparison implementation is:

```text
ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+864/
```

No experiment may be referenced by Production. Promotion means copying a
reviewed, validated change into Production after a separate audit.

## What the current NTRU+864 arithmetic does

The current ring is

```text
R_q = Z_3457[x] / (x^864 - x^432 + 1).
```

The public `poly` stores 864 signed 16-bit coefficients, or 1,728 bytes. The
reference NTT maps this coefficient representation to 288 cubic base rings:

```text
product_i Z_q[X] / (X^3 - zeta_i).
```

The current transform schedule is:

```text
special ring-specific radix-2 layer
  -> two radix-3 layers (144, 48)
  -> four radix-2 layers (24, 12, 6, 3)
  -> 288 cubic blocks
```

The current forward assembly groups the first three levels in one large pass
and the final four levels in a second pass. `poly_basemul`, `poly_basemul_add`,
and `poly_baseinv` consume the cubic-block representation; `poly_invntt`
reverses it.

The full KEM call counts that matter are:

| Path | Forward NTT | Base inverse | Base multiply/add | Inverse NTT |
| --- | ---: | ---: | ---: | ---: |
| key generation | 2 | 2 | 2 | 0 |
| encapsulation | 2 | 0 | 1 add-product | 0 |
| decapsulation | 2 | 0 | 2 | 1 |

This table is the optimization workload. A faster standalone forward NTT is
not sufficient if it makes base multiplication, inversion, packing, or the
full KEM slower.

## Good-Thomas hypothesis

The current transform has 288 cubic points and

```text
288 = 9 * 32
gcd(9, 32) = 1
3457 - 1 = 3456 = 12 * 288.
```

Therefore the coefficient field contains 288th roots of unity and a 9-by-32
prime-factor/Good-Thomas decomposition is algebraically plausible. A natural
CRT coordinate map starts with:

```text
j -> (j mod 9, j mod 32)
j = 64*row + 225*column mod 288
```

because `32^-1 mod 9 = 2` and `9^-1 mod 32 = 25`.

This is a hypothesis, not yet the implementation contract. Before coding we
must prove how the current ring-specific first layer, cubic block labels,
zeta ordering, forward/inverse scaling, and Montgomery representation map to
the 9-by-32 coordinates. The production zeta table must be derived or checked;
constants from NTRU+768 must not be copied.

The likely data shape is nine rows, each containing 32 cubic blocks:

```text
9 rows * 32 points * 3 int16 coefficients = 864 coefficients.
```

The 32-point Neon experience from NTRU+768 is reusable as engineering
knowledge only. Its constants, twists, layouts, cutoffs, and range claims do
not automatically apply to NTRU+864.

## Phase plan and hard gates

### Phase 0 — Freeze the baseline

Deliverables:

- exact commit, linked source list, compiler, flags, hash backend, host, and
  SUPERCOP revision;
- Production test and KAT results;
- SUPERCOP Q1/median/Q3 for key generation, encapsulation, and decapsulation;
- component attribution for forward NTT, inverse NTT, base multiply/add, and
  base inversion on the same target host;
- binary size and symbol closure.

Gate: no optimization result is reported without a reproducible baseline using
the same host, compiler policy, hash policy, and counter backend.

### Phase 1 — Reconstruct the current contract

We will walk through, annotate, and test:

1. the coefficient-domain ring relation;
2. every forward NTT stage and zeta consumption order;
3. the exact 288-cubic-block output layout;
4. Montgomery and centered-representative conventions;
5. base multiplication, base inversion, and inverse input contracts;
6. every keygen, encap, and decap consumer.

Deliverables:

- current forward operation DAG;
- stage-by-stage C oracle;
- layout/index map with small worked examples;
- current range table;
- annotated assembly reading guide.

Gate: each transform boundary must be explainable in both mathematics and
memory offsets before a GT candidate is created.

### Phase 2 — Prove or reject the 9-by-32 decomposition

Tasks:

1. express the current 288-point transform relation independently of its loop
   schedule;
2. derive forward and inverse CRT maps and their exponent convention;
3. derive 9-point and 32-point roots, twists, and inverse scaling from the
   NTRU+864 source constants;
4. show how each output corresponds to `X^3 - zeta_i`;
5. account for all input/output permutations;
6. prove intermediate bounds and narrowing points;
7. count arithmetic, table loads, vector shuffles, and full memory passes.

Gate: a scalar round trip and full polynomial multiplication must match the
current reference on boundary vectors and randomized vectors. Failure means
the mapping is revised or Good-Thomas is rejected; assembly does not begin.

### Phase 3 — Scalar GT reference and differential harness

Create a deliberately readable, default-off implementation:

```text
coefficient input
  -> explicit GT input map/twist
  -> length-9 transform
  -> length-32 transform
  -> explicit map to the current cubic-block contract
```

The first reference should return the exact current output ordering so the
existing base multiplication, base inversion, and inverse NTT remain unchanged.

Tests:

- CRT map is a permutation of `0..287`;
- basis-vector and impulse tests;
- all-zero, all-one, alternating, maximum centered, and minimum centered inputs;
- stage-level comparison with current reference NTT;
- forward/inverse round trip;
- full polynomial multiplication comparison;
- full KEM and KAT comparison.

Gate: exact equality at the declared representation boundary, not merely
congruence after serialization.

### Phase 4 — First Neon forward candidate

Only after Phase 3 passes, create a platform contract covering:

- 128-bit Neon only; no SVE/SVE2/SME;
- candidate AoS, SoA, or hybrid cubic layout;
- the 9-point radix-3-by-radix-3 kernel;
- the 32-point kernel;
- table layout in consumption order;
- lane widths, widening, reductions, and narrowing;
- stack/scratch use, alignment, aliasing, ABI, live-ins, and live-outs;
- public-only table indices and branch structure.

Start with portable C/intrinsics or readable unscheduled assembly. Scheduling
comes after the instruction DAG is understood. If Slothy is used, preserve its
symbolic input, driver, configuration, tool revision, logs, generated output,
and an instruction-by-instruction explanation of the contracted region.

Gate: candidate remains Experiment-only and must pass the scalar GT oracle,
current NTT differential tests, ABI sentinels, KEM tests, and KAT before timing.

### Phase 5 — Integrate in increasing scope

Integration order:

1. forward NTT component;
2. forward NTT in full keygen/encap/decap callers;
3. pointwise cubic multiply/add using the preserved layout;
4. base inversion;
5. inverse GT transform;
6. optional caller-specific layouts that remove proven conversion passes;
7. full KEM source closure and serialization endpoints.

Each step has a same-binary or otherwise layout-controlled A/B comparison.
No later phase is used to hide a regression introduced by an earlier phase.

### Phase 6 — SUPERCOP measurement

Production and candidate are packaged as distinct implementations of the same
`crypto_kem/ntruplus864` primitive. Record:

- SUPERCOP revision and raw result path;
- host CPU, core policy, OS, compiler, and frequency policy;
- implementation source commit and package provenance;
- Q1, median, and Q3 for keygen, encap, and decap;
- repeated fresh runs and observed baseline noise;
- code size and any cache/PMU attribution used to explain the result.

Promotion thresholds are set only after Phase 0 measures baseline variance.
The full-KEM result, not an isolated kernel number, is authoritative.

### Phase 7 — Promotion audit

Promotion requires all of the following:

- algebra, root, CRT map, scaling, representation, and range proofs reviewed;
- no secret-dependent control flow or memory access introduced;
- stage differential tests, boundary tests, randomized tests, KEM tests, and
  KAT pass;
- AAPCS64/ABI checks pass;
- SUPERCOP shows a reproducible full-path improvement;
- source/object closure proves Production links no Experiment files;
- implementation and reading-guide documentation are complete;
- rejected alternatives and tradeoffs remain recorded.

The promotion is a separate commit. If evidence is inconclusive, the candidate
stays in Experiment without changing Production.

## Required explanation for every code change

Before a change:

1. problem being solved;
2. mathematical contract;
3. input/output representation and range;
4. files and symbols affected;
5. predicted performance mechanism;
6. oracle and failure modes.

After a change:

1. exact diff summary;
2. walkthrough from caller to kernel and back;
3. important instructions or intrinsics and why they are valid;
4. commands run and unedited result summary;
5. what is proven, observed, assumed, or still unknown;
6. keep, refine, reject, or promote decision.

## Black-box prohibitions

- No unexplained generated assembly.
- No copied NTRU+768 constants or layouts without an NTRU+864 derivation.
- No performance claim without exact linked-source and binary provenance.
- No KAT-only correctness claim.
- No microbenchmark-only promotion.
- No combined multi-kernel change before individual attribution.
- No changed reduction schedule without an updated range proof.
- No representation name without an index formula and consumer list.
- No silent Production-default change.

## Immediate next action

The next implementation turn should perform Phase 0 and Phase 1 only: capture
the SUPERCOP-capable baseline and produce a small executable reference that
prints and verifies the current 288 cubic-block index/zeta map. It should not
write a GT Neon kernel yet.

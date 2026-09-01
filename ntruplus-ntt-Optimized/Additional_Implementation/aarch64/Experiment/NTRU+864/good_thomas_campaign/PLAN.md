# NTRU+864 Good-Thomas Neon optimization campaign

Status: local full-KEM SUPERCOP baseline established; Production is unchanged.

Baseline source revision: `5c2e3053b33a32b7d637a74296759cac2103534b`

Baseline record:
`results/supercop_m2pro_baseline_20260826/SUMMARY.md`. This is the same-host
A/B baseline; a target-host baseline is still required before promotion.

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

The exact stock Neon boundary is now frozen by
`experiments/gt_layout_consumer_abi_gate`: it is not leaf-major AoS.  Forward
stores 36 eight-leaf SoA tiles, each laid out as `j0[8], j1[8], j2[8]`.
BaseMul and BaseMulAdd consume the same shape, with one zeta vector lane matched
to each physical leaf.  Groups `0..17` are alpha leaves and `18..35` are beta
leaves; their row/column lane patterns match.  The legacy pattern mixes rows
and columns inside a tile and is therefore an ordering convention, not a
consumer requirement when data, zetas, and inverse mapping move together.

The follow-up M3 experiment
`experiments/gt_transform_domain_tile_abi_search` freezes fixed-row,
eight-column batching as the primary producer ABI: NTT9 runs across nine
registers while eight columns occupy Neon lanes, and each output register can
be stored directly as one BaseMul component vector.  Public `P9` is carried as
register/store order and public `P16` as lane/table order.  Lane-dependent row
rotation remains a conditional extension for the later twist-table study.
Fixed-column row-lane batching remains a secondary no-main-transpose candidate
until its cross-lane NTT9 and row-8 tail cost is measured; arbitrary
column-stream chunking is rejected because nine outputs cross every eight-leaf
BaseMul tile boundary.

The M4 equal-boundary experiment
`experiments/gt_boundary_cost_campaign` now closes that comparison.  All
candidates consume the exact 896-value P8+tail contract and complete the same
weighted, paper-oriented NTT9 before storing 36 BaseMul SoA tiles.  Native
Apple-arm64 diagnostics retain fused fixed-row FR-0: its stabilized median was
383.658 ns versus 1029.133 ns for FC-0.  FC's cheaper isolated bridge does not
offset the cost of running each radix-3 transform with only three useful
lanes.  The best searched lane rotation has identical code shape and only a
potential 32-byte exact table saving; its timing overlaps FR-0, so it remains
conditional rather than changing the ABI.

The fused FR implementation directly transposes each eight-column P8 tile into
NTT9 registers, constructs `s=8` with exact lane loads, and stores SoA without
an 864-value scratch.  This preserves the intended logical two-load/two-store
forward schedule.  The intrinsic code is still an Experiment prototype: its
observed range is not a formal proof, compiler-emitted stack traffic still
needs an assembly register-budget pass, and no BaseMul/inverse/full-KEM or
SUPERCOP claim has been made.

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

Current algebra experiment:

```text
experiments/gt_9x32_root_gate
```

Its local root-topology gate passes. This proves that the exact current cubic
leaf roots form a 9-by-32 grid, but does not yet prove the forward/inverse
factorization, scaling, ranges, or a Neon layout. The next permitted experiment
is direct scalar evaluation/interpolation against this root oracle.

The follow-up `experiments/gt_9x32_scalar_reference` gate also passes. It now
serves as the frozen canonical-mod-q C oracle for direct versus factorized
forward transforms, inverse round trip, cubic-leaf multiplication, and complete
schoolbook quotient-ring multiplication. Its scope is closed; legacy leaf
ordering and Montgomery boundaries must be handled in a new experiment.

That boundary experiment is now complete as
`experiments/gt_9x32_montgomery_reference`. It proves that GT can retain normal
`R^0` coefficients while encoding public roots and inverse factors in
Montgomery form. The row-major GT grid maps to the current cubic-leaf order by
a pure permutation with no rescaling. Forward and basemul match current scalar
representatives exactly; inverse and full products match modulo q, with the
candidate inverse intentionally returning centered representatives.

This Montgomery implementation is the frozen authoritative GT C reference v1.
The canonical scalar implementation remains its independent algebra oracle and
the repository scalar `ntt.c` remains its legacy compatibility oracle. Future
staged or Neon candidates must test against the authoritative GT reference;
they must not modify it to absorb candidate behavior.

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

### Phase 1 — Record only the minimum replacement contract

Good-Thomas is expected to replace the current internal transform schedule, so
we will not document every old butterfly, physical block index, or packed zeta
slot unless it is needed to diagnose a mismatch. We retain only:

1. coefficient-domain input and in-place/aliasing behavior;
2. the mathematical transform/base-ring relation used as the oracle;
3. Montgomery and centered-representative conventions at boundaries;
4. base multiplication, base inversion, inverse, and byte-output contracts;
5. every keygen, encap, and decap consumer.

Deliverables:

- current forward operation DAG;
- operation-level C oracle and full multiplication relation;
- boundary representation and scale table;
- caller/consumer map;
- only the old internal details required by failing differential tests.

Gate: the new GT path must have an independent mathematical oracle and preserve
all externally consumed semantics. Exact equality with the old internal NTT
array is optional if all downstream GT consumers are replaced and the complete
polynomial/KEM relations are verified.

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

The first reference must declare one complete GT representation contract. It
may either adapt back to the current cubic-block ordering for staged reuse, or
replace the forward transform, base multiplication/inversion, and inverse as a
closed GT family. Exact equality with the old internal NTT array is required
only for the compatibility-adapter route.

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
`crypto_kem/ntruplus864repo` primitive. The `repo` suffix prevents collision
with SUPERCOP's different built-in NTRU+864 byte contract. Record:

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

M5B `gt_ntt16_producer_range` closes the conditional producer obligation. For
every input representative in `[-3456,3456]`, the exact top split and twisted
radix-2 NTT16 schedule reaches at most 8874, below M5A's 15752 limit. No extra
Barrett reduction is needed. The intrinsics realization spills its 16-vector
array, so it freezes arithmetic/range but not the final memory schedule.

M5C `gt_fr0_basemul_arithmetic` closes BaseMul/BaseMulAdd. M5D
`gt_fr0_inverse_consumer` now closes the inverse permutation and arithmetic:
FR-0 returns to P8 through inverse NTT9, then a packed alpha/beta inverse NTT16
recombines directly to natural coefficients. It proves the M5C `[-2168,2168]`
input contract, a 19512 maximum lazy halfword magnitude, a 3696 output bound,
and exactly two algorithmic full-buffer load/store passes. M5E
`gt_fr0_inverse_asm_realization` now realizes the exact inverse in three
stackless, branchless arithmetic blocks without coefficient spills or
callee-saved vector registers. M5E-r1 replaces widening Montgomery FQMUL with
paired Algorithm-10 `mul/sqrdmulh/mls` and groups independent operations by
register budget. It retains the two-pass boundary, proves a 6888 final bound,
uses 7,292 code bytes, and is locally 48.8% faster than the M5D intrinsic
combined median-of-medians. The wrapper retains a 48-byte GPR call frame.
M5F `gt_forward_composition_barrett` now closes the forward composition ABI.
It packs each bank's tail NTT16 into two registers, keeps both column blocks
live beside the main NTT16, and proves exactly 864 meaningful loads plus 864
stores in pass 2 with no intermediate NTT16 traffic. M5F-r2
`gt_forward_barrett_reduction_search` records the historical four-product R0
result. M5G `gt_forward_symbolic_dag` changes B3 to the exact two-product
destructive DAG. Its correlation-aware proof covers every Forward
instantiation: NTT16 reaches 9342 and the complete changed DAG reaches 28568
with zero unsafe signed-halfword nodes. It uses 24 NTT9 fixed multiplications
per block and an estimated 22-register NTT9 peak; main NTT16 still sets the
whole-kernel peak at 24. The 15-instruction B3 source uses only Slothy
symbolic registers. Its remote hard gate passes: Slothy 0.2.2 returns an
OPTIMAL 24-cycle N1-proxy schedule using exactly `v0,v24-v31`, with no spill,
stack, memory, GPR, or forbidden-vector instruction.
M5H `gt_forward_ntt9_level1_slothy` then makes all nine active level-1
vectors real dataflow while reserving nine registers for the other column
block. Slothy returns an OPTIMAL 48-cycle N1-proxy schedule using all fifteen
allowed registers `v0-v7,v25-v31`, with zero reserved-register, spill, stack,
memory, branch, or GPR instruction.
The next steps are:

1. Add four eta/eta-inverse products and the three level-2 B3s with
   consumer-driven destructive reuse; no spare support register may be
   assumed after M5H.
2. If that complete NTT9 register gate passes, connect its allocation to the
   NTT16 producer, realize fused Forward, then audit linked closure/code size.
3. Run the full Forward oracle, KEM/KAT, source closure, target-host
   attribution, and SUPERCOP before any Production decision.

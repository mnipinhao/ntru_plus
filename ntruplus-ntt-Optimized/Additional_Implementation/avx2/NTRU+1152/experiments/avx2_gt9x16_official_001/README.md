# NTRU+1152 AVX2 GT9x16 experiment 001

The immutable research baseline is `upstream/supercop-avx2`, imported from the
release pinned in `bench/supercop.lock`. Never edit it. Put handwritten C in
`src/`, assembly in `asm/`, reproducible generator output in `generated/`,
correctness checks in `tests/`, and experiment-specific benchmark adapters in
`bench/`.

Use a disposable campaign produced by `scripts/prepare_supercop.py`; candidate
installation refuses to target a pristine tree. Repository-local measurements
are diagnostic only. See the repository workflow document for formal gates.

## Active milestone

**Checkpoint G1A closes five producer/consumer edge oracles derived from the
four shortlisted views, without adding assembly or replacing unknown cycle
debt/credit with zero. F-R3D D1 remains the measured forward control.**

The checkpoint following that named milestone now also contains the first
correctness-first full-forward path and its diagnostic competitiveness test.

## Full-forward correctness-first path

The path contains:

- a scalar proof/test of `n=16u+81v`, `k=64p+9q` over the 144-point field DFT;
- the free `H -> R` relabel and scalar `Y`/`Z` permutation oracles;
- a 27-`vpblendw` AVX2 `Z` producer;
- a debug materialized-`Y` baseline with nine additional 128-bit half combines;
- source-derived distance-8 tables cross-checked between the current scalar
  NTT and pinned AVX2 expansion, plus a fused shear→stage-8 validation path;
- a bit-exact adapter around the unchanged Official AVX2 small-input top split;
- branch-root pre-twists and a two-layer radix-3 reference NTT9;
- an offline component oracle recording every `branch × GT row × NTT16 lane`
  factor/root and all four positions in Official's packed AVX2 output;
- coefficient-by-coefficient full-forward differential tests after mod-q
  canonicalization;
- randomized signed-16-bit, centered-boundary, alias, canary, sanitizer, and
  generated-code audits.

Run `make check sanitize audit`. `make bench-local-record` produces a pinned
repository-local diagnostic; those cycle numbers are not SUPERCOP evidence.
The compiler currently represents the nine materialization operations as
`vblendps`, which is semantically equivalent to the proposed half selection.

The isolated fused stage-8 differential proves only that consuming `Z[a].low` and
`Z[a-1].high` is equivalent to materializing `Y` before the same Montgomery
butterfly. A correctness-first AVX2 routing baseline for distances 4/2/1 now
matches its scalar source-table oracle, retaining CT output order. It does not
by itself establish a complete transform result. The complete correctness-first
path now matches pinned Official AVX2
`poly_ntt` for its `[-3,4]` small-input contract. NTT16 lanes remain four-bit
reversed and NTT9 rows remain two-trit reversed; the generated oracle performs
the mapping instead of inserting cosmetic permutations.

The paired transform result is deliberately diagnostic. It includes the
explicit gather/pre-twist adapter, eight materialized correctness-first NTT16
islands, scalar NTT9, and scatter to Official's packed layout. It does not
qualify the candidate or justify a SUPERCOP/KEM run.

## Pipeline co-design checkpoint

`STRUCTURE.md` records the linked Official-vs-GT structure audit. `LAYOUT.md`
selects the provisional native terminal ABI spanning forward, BaseMul/BaseInv,
and inverse. `CHECKPOINT-C.md` records the explicit assembly island. C0 is a
zero-frame, call-free port of the verified shear and all NTT16 stages, with a
register-only macro over `ymm0..ymm8`. C1 is correctness-valid but rejected
because its split representation doubles vector Montgomery multiplies. C0 is
selected for the next straight-line NTT9 checkpoint; neither result is
production-qualified.

Checkpoint C2 then tested terminal-coefficient pair packing before starting
NTT9. It halves Montgomery chains, but the complete two-island transform is
46.8% slower because operand compression, row reconstruction, and the initial
shear boundary dominate. C2 is retained as a negative experiment. Checkpoint D
is paused while the physical AVX2 orientation is reassessed.

Checkpoint C3 refines that conclusion. Official-style persistent sum/difference
routing reduces one row-pair from 72.619 to 50.413 cycles and routing from 44
to 18 instructions. Terminal pairing remains viable; C2's per-layer canonical
reconstruction is the rejected choice. The next gate is a complete nine-row
shear→C3 path, still before NTT9.

Checkpoint C4 completes that gate. The natural-input nine-row pair is 17.9%
faster than two C0 islands, has zero intermediate materialization, and leaves
all rows in persistent S/D form. NTT9 work is reopened only for a kernel that
consumes this representation directly.

Checkpoint D adds the pinned Official T0/T3x3/T2x4 stage baseline and a
hand-written D-A NTT9 that directly consumes persistent S/D. D-A is bit-exact
but 27.4% slower than Official's two radix-3 layers. C4 from-Z is 11.0% faster
than Official's four radix-2 layers, while C4 natural is 32.9% slower and
reproduces a 208-cycle orientation tax. The D-B oracle proves that moving NTT9
first turns the shear into `rho^(-vp)` and that this phase can be absorbed into
distance-dependent NTT16 twiddles without extra Montgomery chains. See
`CHECKPOINT-D.md`.

Checkpoint E pauses assembly to close the complete NTT-domain representation
contract. It audits the pinned Official forward/BaseMul/BaseInv/inverse
lifecycle, distinguishes resident `R^0` from inverse-feed `R^-1`, records
BaseInv's 18-vector denominator side state, maps all 1,152 physical terminal
cells, and retains terminal-major, persistent-pair, and inverse-oriented
hybrid ABIs for full-path prototypes. No layout is selected from static costs.
See `CHECKPOINT-E.md` and `LAYOUT.md`.

Checkpoint F-R3A evaluates the paper's scaled radix-3 core without conflating
it with the rotated inter-level schedule. R0/R1/R2 pass a complete linear-basis
oracle; R1/R2 reduce the algebraic NTT9 Montgomery-chain count from 18 to 10,
and R2 reduces distinct inter-level twists from three to two. The factor-four
forward scale closes through BaseMul, BaseInv `den[18]`, keypair ratios, and
the existing inverse normalization multiplication without a standalone scale
pass. No performance result exists until R1/R2 assembly is implemented. See
`CHECKPOINT-F-R3.md`.

Checkpoint F-R3B implements R1 plus memory/cached R2 leaves under the same
persistent-S/D ABI. R1 is 13.0% faster than R0; R2-memory is neutral relative
to R1; R2-cached is another 2.1% faster by eliminating twist memory operands.
All variants pass schedule-exact, modulo-q `4*R0`, alias, canary, sanitizer,
and generated cut-point range gates. R2-cached is selected only for the next
R2-plus-adjusted-NTT16 checkpoint. Checkpoint F-R3C completes that connection,
proves all four radix-2 ranges, and records both the isolated 726-cycle gate
and the stronger contiguous Official-body comparison. See
`CHECKPOINT-F-R3B.md` and `CHECKPOINT-F-R3C.md`.

Checkpoint F-R3D separates direct half-pack/resident-`q` cleanup (D0) from a
physical-adjacent two-row Montgomery pipeline (D1). D1 reaches 421 cycles for
adjusted NTT16 and 683.5 cycles combined, so the aggressive D2 schedule is not
needed. See `CHECKPOINT-F-R3D.md`.

Checkpoint G0 then moves the decision boundary from a universal NTT ABI to
consumer edges. `generated/g0-consumer-graph.json` names the encapsulation,
scaled-multiply/inverse, and BaseInv/inverse paths;
`generated/g0-representation-views.json` applies the `R=(P,Q,B,g,s,O)` schema,
separates measured/generated/hypothesis evidence, rejects standalone full-array
canonicalization, defers the nonlocal `p,-p` row pairing, and shortlists F1,
F3, F4, and F5 for G1. See `CHECKPOINT-G0.md`.

Checkpoint G1A generates exact 1,152-cell permutations and explicit terminal
basis, gauge, scale, absorption-point, runtime-operation, and range contracts
for F1, F3, F4, and the two F5 branches. It also replaces the sequential
F1-then-F5 interpretation with orthogonal G1B/G1C experiments and a
null-preserving edge debt/credit matrix. F3 is a closed cheap-basis family, not
an ASM-selected basis; BaseInv→inverse normalization remains open. See
`CHECKPOINT-G1A.md`.

Checkpoint G1B prices the actual F1 producer tail. F1-B0 costs +60.5 cycles
versus F0, while the fused F1-B1 schedule costs +58.5 cycles and saves 3 cycles
relative to B0. Both are exact over all 1,152 cells at transform scale 4 with
no frame or spills. This is a high producer tax, so F0 remains the control and
F1 consumer credit/net delta remain null. See `CHECKPOINT-G1B.md`.

Checkpoint G1C0 audits the actual Official inverse sink before writing a
prototype. Official BMScale→inverse is already zero-conversion, so a
store-order-only C1 has no baseline credit. BaseInv `den[18]` lifetime and the
scale-1/4 R0 scalar normalization (`142 mod 3457`) are closed, but adjusted
inverse-head component/twiddle/range oracles are still required before C2 ASM.
See `CHECKPOINT-G1C0.md`.

Checkpoint G1C1 closes the adjusted inverse first layer as the inverse of GT's
distance-1 butterfly, rather than copying Official's source-stage order. Its
576 butterflies cover all 1,152 persistent-pair cells, retain Official
factor/root identities, prove the local `2I` inverse relation, preserve the
Montgomery exponent, and fit the BMScale/BaseInv signed-i16 range contracts
without another reduction. This authorizes the inverse distance-1 ASM only;
the linked BMScale-tail+head C2 gate is still closed. See
`CHECKPOINT-G1C1.md`.

Checkpoint G1C2-contract resolves the real BMScale result lifetime. Official's
`c0/c1/c2` are available together, but `c3` arrives 26 instructions later after
`c2`'s register has been reused. A materialized persistent-pair path therefore
needs 12 routing instructions per row plus a c2 temporary seam under the
faithful schedule. The selected prototype instead consumes each live result
directly with the inverse distance-1 head, using no edge loads or BMScale→inverse
materialization. This is an ASM authorization, not a cycle result. See
`CHECKPOINT-G1C2-CONTRACT.md`.

Checkpoint G1C3 implements that linked C2-L leaf. A producer-real differential
is bit-exact for raw BMScale and BMScale plus inverse distance-1 over 1,003
cases and all 1,152 cells. The object has zero edge reloads, calls, branches,
frames, spills, and `vzeroupper`; all 72 stores immediately follow an
eight-instruction direct D1 sequence. The linked audit corrects the provisional
cost to 32 D1 instructions per row and the peak to 16 live YMM, still
spill-free. Cycles remain null pending a paired materialized-control benchmark.
See `CHECKPOINT-G1C3-LINKED.md`.

Checkpoint G1C-M2 audits the complete live BMScale tail and proves that its
intermediates are lane-separable: none already contains the adjacent-q pairing
needed by inverse D1. C2-L matches the scoped eight-instruction-per-vector
head-only bound. Against an exact materialized control it removes 72 raw stores
and 72 edge reloads, measures 588 versus 610 cycles in all nine pinned local
launches, and authorizes a full adjusted-inverse16 split-state experiment. F1's
roughly 117-cycle two-forward debt and F5's 22-cycle credit remain independent
prices; an F0 plus F5 path pays no F1 debt. See `CHECKPOINT-G1C-M2.md`.

Checkpoint G1C-M3A fixes the full inverse experiment as C0/C1/C2, so C1-C0
prices the linked head in a full caller and C2-C1 prices persistent inverse
state. It derives D1/D2/D4/D8 from the current physical-q order. The first
independent BMScale range envelope fails signed-i16 at D2 sum (±55,296), so
lazy C2 assembly is not yet authorized: the next gate must bound actual
producer-correlated register states without inserting a convenience reduction.
See `CHECKPOINT-G1C-M3A.md`.

Checkpoint G1C-M3B traces D2 provenance and runs 10,003 deterministic cases
through real F1-B1 production and exact BMScale/inverse semantics. D2 and D4
show no corpus overflow, but remain proof-open. Current-orientation D8 has 187
unsafe sums and 11 unsafe differences; the first concrete sum is -36,284.
Zero-repair C2 is therefore rejected, while full reduction is not authorized.
M3C now searches D8 orientation and minimum one-sided/selective repair. See
`CHECKPOINT-G1C-M3B.md`.

Checkpoint G1C-M3C0 exhausts all 256 local output-swap masks at each of the
three inverse16 boundaries. Factor-partition-preserving masks and all-L/R-edge
masks are disjoint, including every zero-route `q -> q xor c` relabel. Sign
gauges cannot repair the permanent D8 counterexample, and a root-power gauge on
its all-L path would require new arithmetic. M3C0 therefore closes without a
zero-cost candidate; M3C1 is skipped and M3C2 minimum repair is next. See
`CHECKPOINT-G1C-M3C0.md`.

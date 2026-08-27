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

Checkpoint G1C-M3C2 evaluates none/left/right/both repair at all 576 D8 nodes
on the fixed real-producer corpus. Only 37 nodes fail without repair, all at
pair 0, and every one accepts either one-sided repair. The scalar minimum is
37 reductions; an adjacent-row half-vector set cover projects this to 22
abstract vector repair chains and 30 routes, versus 37 selective full-vector
chains or 72 full-D4 control chains. Exact producer-domain safety remains open,
so no ASM or timing is authorized. See `CHECKPOINT-G1C-M3C2.md`.

Checkpoint G1C-M3C2-P proves that the corpus-selected one-sided cover is not
safe under the general signed-i16 D4 register contract: its exact bound is
34,496. Both operands at all 576 D8 nodes are required conditionally, yielding
the 72-vector M3C3 control. Two full-array AVX2 reducers pass exhaustive i16
correctness and static gates. Paired local pricing is 165 cycles for signed
Barrett versus 93 for Montgomery-by-identity, with Montgomery winning 9/9
launches. This is isolated control pricing; D2/D4 proof remains open. See
`CHECKPOINT-G1C-M3C2P-M3C3.md`.

The subsequent full-path proof rejects placing that selected identity repair
only at the D4 tail: under the declared independent BMScale lane contract, D2
can already require `[-55296,55296]`. It also proves a safe replacement:
Montgomery-by-identity on the D1 large/sum stream preserves the Montgomery
scale and bounds every later D2/D4/D8 pre-Montgomery operation by 17,377.
Therefore D4-tail fusion and full M3 timing remain forbidden; see
`CHECKPOINT-G1C-M3-FULL-PATH-PROOF.md`.

Checkpoint G1C-M3C4 implements the safe repaired full path. C0/C1/C2 measure
1136/1108/1099 cycles; the linked edge contributes -28 cycles and persistent
D2/D4/D8 contributes another -9.5 cycles, both in 9/9 launches. C2 retains one
post-D1 boundary and removes 288 later boundary memory instructions. See
`CHECKPOINT-G1C-M3C4.md`.

The post-price HWA-A0 audit confirms that terminal-major
`V[b,row,j][lane]=A[b,P[row],Q[lane],j]` is Hwa-style coefficient-plane SIMD,
but also records that the M3 harness obtains it from F1-B1, not the faster F0
persistent S/D producer. No separate Hwa candidate is forked. The next gate is
the direct C2 inverse16-to-inverse-NTT9 consumer map; see
`CHECKPOINT-HWA-A0.md`.

Checkpoint G1C-ITAIL-MAP proves that C2's final lanes are natural inverse16
time coordinates, not residual S/D state, with 2,304 linear-basis component
checks. The current paper p order is already the inverse-NTT9 radix-3 grouping,
so 72 strided YMM loads consume the existing stores without a repack or lane
route. The shared map also gives a 54-vector `d=3` NTRU+864 topology projection,
while leaving its range and repair policy unclaimed. The next probe is a
correctness-first reference inverse NTT9 on this direct-load boundary; see
`CHECKPOINT-G1C-ITAIL-MAP.md`.

Checkpoint G1C-ITAIL-REF implements that two-layer inverse paper-R2 reference.
It passes an independent inverse-DFT matrix oracle on 1,003 arbitrary transform
cases, 257 real C2 producer cases, canonical-control equivalence, alias, range,
canary, and sanitizers. In the complete C2-to-reference-inverse9 region, direct
B is 26,555.5 cycles versus canonical A at 27,218.5, a -667.5-cycle win in all
9 launches. Absolute cycles are scalar-reference diagnostics; the result only
prices representation debt. A straight-line AVX2 two-radix3 B baseline is now
authorized; see `CHECKPOINT-G1C-ITAIL-REF.md`.

Checkpoint G1C-ITAIL-ASM-B0 implements that baseline directly over physical P.
It passes the full reference gate, uses the expected 80 Montgomery chains for
all eight inverse9 bodies, peaks at 15 YMM with zero spill/routing, and measures
490 cycles for the pure body. In the complete C2-store boundary, optimized B is
1532 cycles versus optimized vector-canonical A at 1548, a -16-cycle win in all
9 launches. Reduction and centered-output debt, rather than arithmetic-chain
inflation, is now the next target; see `CHECKPOINT-G1C-ITAIL-ASM-B0.md`.

Checkpoint G1C-ITAIL-B1P exhausts all 729 cyclic orientations within the
current physical B ABI, two-radix3 family, and scale/output contract.  It
proves that Forward R2's apparent paper rotation retains no residual phase:
`D_F` and therefore `D_F^2` are identity.  BMScale, inverse-interstage, and
residual top-split gauge placement cannot beat B0's four nontrivial
inter-stage chains, 10 total Montgomery chains, two constants, and zero
permutation.  This is not a global inverse9 lower bound; R2 has internalized
the phase convention by the observed boundary rather than made orientation
irrelevant.  Three arithmetic ties proceed to exact B1R range/normalization
analysis; no B1 assembly is authorized yet.  See
`CHECKPOINT-G1C-ITAIL-B1P.md`.

Checkpoint G1C-ITAIL-B1R exhausts all input and inter-stage reduction policies
for the three B1P ties.  The B0 `rho^(+/-1)` orientation has the best i16
margin.  Its unique minimum inter-stage Barrett set is `{0,3,6}`, proving the
existing reductions on wires 1 and 2 are removable while all input and final
normalization steps remain required.  The narrow B1 ASM deletion is now
authorized; see `CHECKPOINT-G1C-ITAIL-B1R.md`.

Checkpoint G1C-ITAIL-ASM-B1 implements exactly that deletion. It removes 48
linked instructions over the eight inverse9 bodies while retaining all 80
Montgomery chains and the 15-YMM spill-free leaf. A pinned SUPERCOP-derived
serious run measures B1 at StQ2 890.0000 cycles versus B0 at 902.7917; the
per-launch delta is negative in 9/9 launches with median -12.9792 cycles. B1
is selected as the materialized inverse9 control, but is not KEM- or
production-qualified. See `CHECKPOINT-G1C-ITAIL-ASM-B1.md`.

Checkpoint G1C-ITAIL-D0 proves a register-live D8-to-B1 wavefront at 14/16 YMM
and implements the exact same arithmetic DAG as the materialized control. M1
removes 72 D8 stores and 72 B1 reloads, but its immediate-triad schedule costs
StQ2 2007.6944 versus M0 at 1642.3241: +365.3704 cycles, losing all 9 serious
launches. The schedule is rejected; one late-layer1 M2 attribution control is
the final boundary-fusion gate. See `CHECKPOINT-G1C-ITAIL-D0.md`.

Checkpoint G1C-ITAIL-D0-M2 retains all nine D8 outputs before executing B1's
original layer order. Exact proof and object audit remain at 14/16 YMM, remove
the same 144 boundary memory instructions as M1, and preserve the arithmetic
DAG. In the balanced SUPERCOP-derived serious run M2 is 1789.2855 cycles,
faster than M1 by a per-launch median 215.1528 cycles but slower than M0 by
152.9722 cycles in all 9 launches. This closes the current D8-to-inverse9
fusion class. The next gate is F0 persistent forward to consumer-native
BaseMul, followed by one integrated `2F+B+I` island. See
`CHECKPOINT-G1C-ITAIL-D0-M2.md`.

Checkpoint F0-MA-MAP moves to the actual pinned encapsulation caller. It proves
that the boundary is `F0(r) + F0(m) + resident h -> MulAdd -> poly_tobytes`,
not a `2F+B+I` path, and that encapsulation contains no inverse transform. The
72-vector F0 map is a complete 1,152-cell semantic/physical/Official
bijection, including the paper-adjusted final-row order `8,2,5`. MA0--MA3 are
symbolically exact and remain alive; no assembly or benchmark is authorized
until resident-`h`, range, register, inverse-four, and serializer schedules are
proved. See `CHECKPOINT-F0-MA-MAP.md`.

Checkpoint F0-MA-SCHED proves the nine exact two-tile Official `h`/serializer
chunks, role-aware inverse-four placement, signed-i16 schedules, and spill-free
MA1/MA3 liveness. MA2 and MA3 share a 432-route external geometry, but MA3 has
13 versus 19 Montgomery chains per tile at peak 15 YMM; MA1 remains the direct
F0-native research prototype at peak 14 YMM. MA1 and MA3 ASM are authorized in
that order with mandatory 32-byte entry/constant alignment audit. No assembly
or performance result exists yet. See `CHECKPOINT-F0-MA-SCHED.md`.

Checkpoint F0-MA1-ASM0 implements the fixed B0/P0 correctness island. It
passes 1,003 exact random/boundary cases and the range, scale, non-alias,
canary, sanitizer, ABI, and 32-byte linked-alignment gates. The exact one-tile
ledger is 28 Montgomery chains after making the common four-chain resident-`h`
R-lift explicit. The former 792-route value is now correctly labeled semantic
route slots; this object executes 48 R2 routing instructions. No timing was
run. The next gate is the nine-serializer-chunk caller-shaped ASM1; see
`CHECKPOINT-F0-MA1-ASM0.md`.

Checkpoint F0-MA1-ASM1 expands that island to the complete nine-chunk
serializer-facing caller. C1's two-tile interleaving beats sequential C0 by a
median 273.0625 cycles in all nine serious SUPERCOP-derived launches, despite
216 extra correctness-first moves. The complete byte-exact MA0 control still
beats selected C1 by a median 1039.4167 cycles in all nine launches. MA1 is
therefore frozen as the weighted-schoolbook architecture control; MA3 is the
next implementation. These are derived primitive results, not native KEM or
production evidence. See `CHECKPOINT-F0-MA1-ASM1.md`.

Checkpoint F0-MA3 implements the low-rank EE/OO/TT challenger as an exact
21-chain single-tile proof kernel and a 378-chain full nine-chunk caller. The
full path retains C1-style two-tile ILP, has no canonical intermediate ABI,
and passes byte-exact, range, sanitizer, constant-time ABI, and 32-byte
alignment gates. An exhaustive final-range proof removes the redundant
post-`inv4` center, deleting 720 expanded instructions. Despite that, the
pinned SUPERCOP-derived serious result is MA3 4689.2870 versus MA0 2817.3750
cycles; MA3 loses all 9 launches by a median +1868.6042 cycles. MA3 is frozen
as attribution evidence and the MA2 coefficient-plane geometry is reopened.
See `CHECKPOINT-F0-MA3.md`.

Checkpoint F0-MA2 implements the Hwa-style coefficient-plane hypothesis as a
real complete nine-chunk AVX2 MulAdd-to-serializer path. It streams raw F0 and
resident-h planes through 19-chain quartic schoolbook arithmetic, uses only
semantic-plane scratch, omits a proved-redundant final Barrett pass, and never
reconstructs an Official-vector intermediate. ASM0, CHUNK0, and the complete
path pass 1,003 byte-exact random/boundary cases; the full 4,681-instruction
leaf peaks at 14 YMM with no calls, branches, spills, stack use, or
`vzeroupper`, and preserves 32-byte entry/constant alignment. The pinned
SUPERCOP-derived serious run measures MA2 at 2072.1435 cycles versus MA0 at
2826.4907, winning 9/9 launches with a median -753.8333-cycle delta. MA2 is
selected for real encapsulation caller integration, but is not yet native-KEM
or production qualified. See `CHECKPOINT-F0-MA2.md`.

Checkpoint F0-MA2-KEM integrates MA2 into the real pinned encapsulation caller.
It preserves actual public-key decoding, hashing, sampling, both forward NTTs,
input residency, stack allocation, error behavior, and secure clears. Until a
direct coefficient-domain F0 producer exists, two explicit scale-four
Official-to-F0 adapters are included and priced. The candidate passes all 100
canonical KAT vectors, but native SUPERCOP encapsulation regresses from
43061.6157 to 44373.6944 cycles. Normal/reversed link-order and ASLR on/off
fixed-ELF campaigns all put the 95% CI entirely above zero. This complete
caller is frozen as a performance rejection; MA2 can reopen only after the
adapters are removed by producer integration. See `CHECKPOINT-F0-MA2-KEM.md`.

Checkpoint F0-PROD0 now provides a complete coefficient-domain-to-MA2-F0
producer without forming Official NTT output or calling the Official-to-F0
adapter.  It preserves physical P/Q, scale four, and the exact per-cell range
contract; 2,304 signed impulses, 1,003 random KEM-small inputs, alias, canary,
and sanitizer gates pass.  The correctness-first O3 object still reserves
3,872 stack bytes and executes eight scalar GT adapters plus four R2+D1 calls,
so it is not a performance candidate.  F0-PROD1-MA2 must remove that producer
debt before the four-way caller attribution. See `CHECKPOINT-F0-PROD0.md`.

Checkpoint F0-PROD1-SCHED turns that producer into a mechanically checked
assembly plan without changing top-split or R2/D1 arithmetic. Thirty-six
direct split-load maps form two streams apiece, and the R2 first layer uses all
72 final-F0 vector slots as transient storage before in-place R2/D1 overwrite.
Only the 2,304-byte split array remains; scalar adapter and pair staging are
absent from the planned boundary. Generated label-routing, range-subset,
register-liveness, stack, and 32-byte alignment gates authorize only the P1-H
producer assembly checkpoint. KEM benchmarking remains blocked until that
assembly passes differential and linked-shape audits. See
`CHECKPOINT-F0-PROD1-SCHED.md`.

Checkpoint F0-PROD1-ASM implements the authorized P1-H helper-shaped producer.
It is raw-representative exact to PROD0 and canonicalized exact to Official
times four over the full impulse/random/boundary suite, including alias,
canary, generated ranges, and sanitizer. The wrapper retains only the
2,304-byte split in a 2,336-byte frame; its four dynamic AVX2 helper calls have
no helper frame, spill, nested call, or `vzeroupper`. Exact attribution records
576 direct-formation routing instructions per complete forward. This closes
the machine-geometry correctness question but does not yet claim speed. Only a
producer-only paired comparison is authorized next. See
`CHECKPOINT-F0-PROD1-ASM.md`.

Checkpoint F0-PROD1-PRICE compares that producer with the exact legacy
`poly_ntt -> scale4/F0 adapter` contract in the same SUPERCOP-derived measure
ELF. P1-H is slower in all 9 serious launches: the per-launch median regression
is +158.7083 cycles for one forward and +259.1875 cycles for two back-to-back
forwards. Diagnostic counters show approximately 110 fewer instructions and
65 fewer stores, but 168 additional retired loads per forward. The generic F0
producer boundary is therefore rejected for MA2 caller integration. The next
gate is only a movement-graph study for an `F0-PROD2-MA2` specialized epilogue;
top-split fusion and routing micro-superoptimization remain unauthorized. See
`CHECKPOINT-F0-PROD1-PRICE.md`.

Checkpoint F0-PROD2-MA2-MAP removes the generic-F0 boundary from the design,
not the memory boundary. Its 1,152-cell oracle maps every D1 lane to the exact
MA2 serializer chunk, tile, coefficient plane, and q lane. Store-address-only
P2-A is impossible because a D1 vector contains two coefficient halves. P2-B
is selected: four local `vperm2i128` operations per tile form MA2-native planes
and overwrite the same terminal-pair slots, preserving the 2,304-byte backing
with no extra temporary. Against the actual MA2 assembly this removes 72
duplicated loads per forward operand, or 144 for encapsulation's two operands;
the plane permutations move to the producer rather than disappear. Only a
materialized P2-B ASM0 differential is authorized next; KEM, resident-`h`,
top-split fusion, and chunk-oriented P2-C remain blocked. See
`CHECKPOINT-F0-PROD2-MA2-MAP.md`.

Checkpoint F0-PROD2-MA2-ASM0 implements only the selected materialized P2-B
redeposit. The generated assembly preserves P1-H formation, R2, D1 arithmetic,
traversal, reductions, and scale; its linked D1 ledger adds only the expected
72 dynamic `vperm2i128` plane formations per forward. Raw 2,304-byte plane
output is exact over 2,304 signed impulses and 1,003 random/boundary/alias
cases, while 257 complete MA2 consumer cases produce byte-identical
ciphertexts. All eighteen static backing slots satisfy last-read-before-write,
so the existing 2,304-byte backing is reused without another temporary. The
next authorized gate is only P1-H-plus-projection versus direct-P2-B boundary
pricing; KEM and encapsulation integration remain blocked. See
`CHECKPOINT-F0-PROD2-MA2-ASM0.md`.

Checkpoint F0-PROD2-MA2-PRICE measures the exact materialized MA2-plane
boundary without executing MA2 arithmetic. P2-B beats P1-H-plus-projection in
all 9 serious launches: the paired per-launch median is -20.0000 cycles for
one producer and -115.1458 cycles for two back-to-back producers. The full
linked ledger shows that cross-lane work is relocated, not removed:
`vperm2i128` delta is zero, while each operand removes 144 aligned reloads and
72 extra plane stores. Consumer-native final materialization is therefore
validated as a machine-level architecture, but this remains a SUPERCOP-derived
boundary result rather than a KEM claim. Only the unchanged-MA2 consumer
island is authorized next. See `CHECKPOINT-F0-PROD2-MA2-PRICE.md`.

Checkpoint F0-PROD2-MA2-CONSUMER appends the exact same resident-`h` projection,
MA2 arithmetic, inverse-four, and serializer symbol to control and candidate.
P2-B remains faster in all 9 serious launches, with pooled StQ2 5191.8750
versus 5318.4097 and paired median -126.5000 cycles. This is close to the
standalone boundary's -115.1458-cycle magnitude rather than a substantial
downstream amplification. Consumer-native materialization remains validated,
but current P1-H/P2-B is not advanced to native KEM against the earlier
approximately 1,312-cycle encapsulation deficit. The next gate is only an
Official-like faster-producer-to-MA2 mapping study (`F0-PROD3-MA2-MAP`), not
permutation micro-optimization. See `CHECKPOINT-F0-PROD2-MA2-CONSUMER.md`.

Checkpoint GT9X16-PROD3-AOS-BRANCH0 implements one complete in-place branch
from the unchanged top-split AoS state to the exact P2-B/MA2 plane ABI. The
1,152-byte raw differential passes the complete impulse, random-small,
unaligned in-place, and canary suite. The linked leaf has 72 data loads, 72
stores, 148 Montgomery chains, 36 Barrett vectors, zero spill, and a 16-YMM
peak. It also corrects the earlier C1 static ledger: 24 routes reach
AoS-physical-q coefficient planes, while exact MA2 packed lanes require eight
additional routes per tile. The real count is therefore 288 per branch and
576 per full forward, leaving a static 360-route credit versus G0/P2-B's 936.
No benchmark was run. Only the second-branch/full-producer correctness gate is
next. See `CHECKPOINT-GT9X16-PROD3-AOS-BRANCH0.md`.

Checkpoint GT9X16-PROD3-AOS-FULL expands the proven machine shape to both
branches and passes a raw exact 2,304-byte differential against all four
G0/P2-B pair paths, including full impulse, random-small, unaligned in-place,
immutability, canary, and sanitizer gates. The linked apples-to-apples audit
confirms 144 loads, 144 stores, and 576 routes versus G0/P2-B's 288 loads, 216
stores, and 936 routes, with identical 296 Montgomery chains and 72 Barrett
vectors. The tradeoff is 78 more constant-memory operands and 8,826 more
symbol text bytes. No benchmark was run; only SUPERCOP-derived serious
producer-boundary pricing is authorized next. See
`CHECKPOINT-GT9X16-PROD3-AOS-FULL.md`.

Checkpoint GT9X16-PROD3-AOS-PRICE prices the complete coefficient-to-exact-MA2
boundary with the pinned SUPERCOP compiler/build/timing machinery. A
nine-process ASLR-on selection chooses reversed archive placement by absolute
2x candidate time; the serious headline then measures persistent AoS at
2946.5231 versus G0/P2-B at 3377.8935 pooled StQ2. The candidate wins all nine
launches with a paired median delta of -429.1250 cycles and bootstrap 95% CI
[-432.1458,-425.1875]. Normal/reversed and ASLR on/off controls all preserve
the direction. This validates the producer architecture at the materialized
boundary, but remains SUPERCOP-derived rather than native-KEM evidence. Only
the unchanged-MA2 consumer island is authorized next. See
`CHECKPOINT-GT9X16-PROD3-AOS-PRICE.md`.

Checkpoint GT9X16-PROD3-AOS-CONSUMER appends the identical resident-`h`, native
MA2, inverse-four, and serializer tail to both producer variants. Persistent
AoS measures 4765.0602 versus G0/P2-B at 5192.9537 pooled StQ2; it wins all
nine headline launches with a paired median delta of -432.0000 cycles and 95%
CI [-436.1875,-421.9583]. Normal/reversed placement and ASLR on/off all agree.
The preceding producer-only median was -429.1250, so the credit survives the
complete ciphertext consumer boundary rather than being consumed by the
larger frontend footprint. This reauthorizes complete encapsulation KAT and
native SUPERCOP `enc_cycles`, but is not itself a native-KEM result. See
`CHECKPOINT-GT9X16-PROD3-AOS-CONSUMER.md`.

Checkpoint GT9X16-PROD3-ENCAP integrates persistent AoS into the real caller
without changing its semantics.  Correctness and the 100-case KAT are exact,
but the caller reveals a missing island edge: `r` must also be serialized in
Official NTT order for `hash_g` before SOTP creates `m`.  The candidate uses an
exact inverse projection and scale-removal bridge for that second output.
Native SUPERCOP measures `enc_cycles` at 44557.9769 versus Official 43059.2778,
a +1498.6991-cycle (+3.48%) regression.  Fixed-common O3GC paired replay is
also slower by +1892.85 to +2125.25 cycles across normal/reversed placement
and ASLR on/off, with every confidence interval above zero.  No production
promotion is allowed.  The next checkpoint isolates the coefficient-`r`
dual-output/hash fanout; PROD3, MA2, twist, top split, and code organization
remain frozen.  See `CHECKPOINT-GT9X16-PROD3-ENCAP.md`.

Checkpoint GT9X16-PROD3-ENCAP-R-HASH-FANOUT-ATTRIBUTION uses four same-ELF
variants to separate producer cost from the incremental hash consumer.  Under
the selected normal-placement ASLR-on serious replay, Official hash fanout
costs +305.8021 cycles while current PROD3 recovery costs +835.3333, producing
a **+529.5313-cycle excess fanout tax** with 9/9 positive launches and 95% CI
[+525.8021,+533.7500].  C0 is also +181.8750 cycles slower than Official O0,
so complete dual output is +712.8333 cycles.  Normal/reversed placement and
ASLR on/off agree.  Hash recovery is therefore a significant but incomplete
explanation of native regression.  The next checkpoint is only an exact
MA2-plane-to-12-bit-byte mapping/range/movement proof; direct serializer ASM
is not yet authorized.  See `CHECKPOINT-GT9X16-PROD3-HASH-FANOUT.md`.

Checkpoint GT9X16-PROD3-MA2-HASH-DIRECT-MAP removes the Official coefficient
array from the target contract and maps every MA2 plane lane directly to its
Official coefficient and exact 12-bit byte ownership. The later pinned
physical-to-serialized pack probe corrects the initial locality assumption:
zero of 576 true serializer pairs reside within one MA2 vector. The exhaustive scale
proof covers all 41,505 integers in `[-20751,20753]`: inv4 Montgomery produces
`[-1998,1998]`, after which sign-add-q is bit-exact with Official's Barrett plus
sign canonicalization and yields `[0,3456]`. H1 is the first schedule target:
it removes 416 current intermediate reloads and 216 stores without a full
coefficient temporary. All initial H2 locality and route counts are withdrawn;
a corrected H2 design remains open.
Serializer ASM and benchmarking are still unauthorized. See
`CHECKPOINT-GT9X16-PROD3-MA2-HASH-DIRECT-MAP.md`.

Checkpoint GT9X16-PROD3-MA2-HASH-DIRECT-SCHEDULE turns the byte map into one
fully lowerable H1 schedule. Its initial H2 24/48/96-byte candidates were later
withdrawn after the pinned pack-layout probe.
H1 uses 272 data loads, 27 separately accounted constant loads, 804 routing
plus packing instructions, 54 byte stores, no coefficient temporary, and a
spill-free 16-YMM peak. Only H1 ASM0 was authorized; H2 remained deferred and
its old `1086` figure is not evidence. See
`CHECKPOINT-GT9X16-PROD3-MA2-HASH-DIRECT-SCHEDULE.md`.

Checkpoint GT9X16-PROD3-MA2-HASH-H1-ASM0 implements the complete 2,304-byte
MA2-plane to 1,728-byte serializer as one aligned, straight-line AVX2 leaf.
Raw byte tests cover every signed plane impulse, the full uniform proved range,
random full-range states, and actual coefficient-domain PROD3 callers. The
linked 1,662-instruction ledger matches all scheduled classes exactly and has
zero stack/spill/call/branch/`vzeroupper`. The external-byte gate also exposed
that the old H2 schedule confused Official physical NTT positions with the
post-`pack.s` serialized order. A pinned basis probe corrects the map; H1 is
unchanged, while all prior H2-24/48/96 counts are withdrawn. No benchmark was
run. See `CHECKPOINT-GT9X16-PROD3-MA2-HASH-H1-ASM0.md`.

Checkpoint GT9X16-PROD3-MA2-HASH-H1-PRICE prices only the materialized
scale-four MA2-plane to exact 1,728-byte boundary. Direct H1 measures 768.3310
cycles versus current H0 recovery at 1083.1238 pooled StQ2 under the selected
reversed-placement ASLR-on setting. The per-launch median delta is -314.6458
cycles with 95% CI [-317.9583,-311.9271], and H1 wins 9/9 launches under all
four normal/reversed and ASLR on/off controls. H1 is therefore selected for a
frozen-caller integration check, but the result is SUPERCOP-derived rather
than native-KEM evidence and is not large enough by itself to close the prior
encapsulation deficit. H2 remains withdrawn. See
`CHECKPOINT-GT9X16-PROD3-MA2-HASH-H1-PRICE.md`.

Checkpoint GT9X16-PROD3-H1-INTEGRATION replaces only the old `r` hash-recovery
bridge in the real research caller with the selected direct H1 serializer.
The caller retains two PROD3 forwards, unchanged `hash_g`/SOTP ordering,
resident `h`, native MA2, allocation, and secure clears. The newly installed
flat candidate passes all 100 frozen NTRU+1152 KAT vectors byte-for-byte; the
response SHA-256 remains `2ddfc810...9464c3`. Native performance is
intentionally not rerun. H1 is now the research Encap baseline, and the next
checkpoint is map-only joint Q-order co-design. See
`CHECKPOINT-GT9X16-PROD3-H1-INTEGRATION.md`.

Checkpoint GT9X16-PROD3-MA2-QORDER-CO-DESIGN searches all 384 four-bit index
permutations plus XOR orientations without changing arithmetic. The 33 Pareto
orders collapse to two movement profiles. Current frozen MA2 Q remains
Pareto-optimal: 32 current-like orientations retain 144 producer routes, 128
resident-`h` source-half groups, 336 H1 coefficient routes, and 272 H1 data
loads. The sole different point is C1 natural Q: it removes all 144 final
producer routes but raises the `h` ownership count by 16 groups and H1 by 24
routes plus 16 loads. H1's 324 pack-transpose routes do not change. All 576
serialized pairs cross MA2 vectors for every candidate, so Q-order cannot
revive the invalidated H2-96 design. Natural Q is retained only for an exact
schedule-lowering checkpoint; no ASM, timing, or native KEM is authorized.
See `CHECKPOINT-GT9X16-PROD3-MA2-QORDER-CO-DESIGN.md`.

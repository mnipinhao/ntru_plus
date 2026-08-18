# NTRU+768 GT32-TILE4 five-layer experiment

This directory is a new research branch from the frozen `experiments/gt_ntt`
result.  It does not modify the frozen GT32 or the current GT16 experiment.

## Fixed layout

```text
tile = 2*k3 + branch
vector = Q/4
lane = 4*(Q%4) + quartic_degree
word = 128*tile + 16*vector + lane
```

Each 256-byte tile is one `(k3, branch)` and contains four scalar NTT32s.
The assembly loads exactly eight data YMM registers and keeps them resident
through all five layers.

Forward executes CT distances `16,8,4,2,1`; the identity distance-16 layer is
raw and range-proved, while the remaining layers use Montgomery factors.
Inverse executes DIT distances
`1,2,4,8,16`.  Cross-register layers expose four parallel Montgomery chains;
the final/initial local layers use 128-bit-half and quartic-qword shuffles.
There is no stack frame, scratch traffic, runtime exponent lookup, or data
spill in either kernel.

The frontend intrinsic and leaf assembly consume coefficient-order input and
directly write TILE4 in Q pairs.  Each pair is split, twisted, transformed by
DFT3, regrouped by branch, and stored to its final tile.  The assembly uses a
fixed 16-iteration public loop, generated source offsets/twist streams, no
stack, and no old row01/row2 layout.  The full-forward candidate uses one
aligned 1536-byte semantic scratch, so its public boundary supports `out == in`.

The `*_all_asm` entries process all six tiles and support exact `out == in`
aliasing because each tile is fully loaded before any tile store.  They are
still an experimental backend boundary: the frontend is currently intrinsics,
and quartic basemul/inverse tail have not yet been changed to consume TILE4.

## Generated truth

`tools/generate_tile4.py` emits compact execution-order assembly constants, a
complete 768-word mapping CSV, and a hash manifest.  The mapping records all
three DFT3 input sources for both low/high top halves, `(k3,branch,n32,c)`,
TILE4 word, physical Q, logical bit-reversed `k32`, terminal exponent/lambda,
and inverse source word.

It also exhaustively bounds every fixed-factor Montgomery product over the
incoming interval and composes those bounds through the butterfly DAG.  For
the centered `[-1728,1728]` input contract, the conservative maximum through
forward plus unnormalized inverse is 30175, below signed-int16 32767.

## Checks

```sh
make CC=gcc check
make CC=gcc sanitize
make CC=gcc audit
```

The differential test covers zero, impulse, alternating maximum bounds,
`[-3,4]`, random centered inputs, exact C-vs-assembly forward/inverse, modular
round-trip, and in-place aliasing.  Full forward is also compared modulo q with
the frozen parent's independent `ntt_gt_rowbitrevlayout()` after an explicit
row-bitrev-to-TILE4 coordinate conversion.  The audit rejects stack-relative
operands in the five-layer assembly kernels.

## Directional short benchmark

A same-binary 20-sample run with 2,000 calls per sample is recorded in
`results/tile4-forward-directional-short.json`.  It is intentionally not a
promotion benchmark.  Frozen GT32 measured 469.029 TSC and the complete TILE4
forward measured 603.078 TSC, a 28.580% regression.  Decomposition measured
236.974 for direct frontend and 352.339 for the serial five-layer core.

That result is retained as the pre-T1 checkpoint.  The follow-up T1--T4/T5
experiment is recorded in `results/tile4-forward-t1-t5-short.json` and changes
the directional conclusion.  Pair-packed local layers remove duplicated
Montgomery lanes, raw `-722` replaces the small-input top split, generated
fixed displacements remove the source offset dependency, and one combined leaf
runs frontend plus core with a single `vzeroupper`.

In the latest same-binary short run, pair packing reduced the core from 339.709
to 230.601 TSC.  Raw and then fixed-displacement frontend reduced 227.088 to
191.499 and 180.976 TSC.  The complete candidate measured 443.030 versus frozen
GT32 at 462.615 TSC, directionally 4.233% faster.  Matching the frontend's
16-byte stores in the core measured 443.030 versus 448.973 for wide loads; this
small result is not treated as settled.  These are 2,000-call directional
samples, not promotion data, so basemul integration remains gated on an
explicit serious benchmark.

## Official three-way directional comparison

`make CC=gcc bench-official-short` links unmodified Official `poly_ntt`, frozen
GT32, and TILE4 N5 into the same binary.  The 2,000-call result recorded in
`results/tile4-forward-vs-official-short.json` measured 453.125 TSC for
Official, 466.502 for frozen GT32, and 395.195 for N5.  N5 was directionally
12.785% faster than Official and 15.286% faster than frozen GT32.

This is a kernel comparison, not a caller result.  Official is in-place while
the two GT entries are out-of-place; no input copy is charged.  The Official
timed loop repeatedly transforms its aligned work buffer after one valid
small-input call.  Its assembly has fixed control flow and data-independent
latency, but a promotion decision still requires the explicit serious
benchmark and consumer integration.

## Gate A formal forward result

The formal warm-L1 gate uses 100,000 calls per sample, 20 AB/BA samples per
process, and five independent process launches.  Median-of-launch-medians is
452.801 TSC for Official, 462.515 for frozen GT32, and 383.430 for the selected
64-byte-aligned N5.  N5 is 15.320% faster than Official and provides 69.371 TSC
per forward, or a 138.742 TSC `B+I` budget for a `2F+B+I` chain.  In-place alias
measured 394.313 TSC.

A synthetic 64-KiB L1 eviction before every individually timed call measured
506.900 for Official and 511.027 for aligned N5, making N5 0.814% slower.  The
forward promotion claim is therefore limited to the normal warm caller path;
it is not a claim that TILE4 wins from cold cache.  Full launch data and the
machine governor metadata are in `results/tile4-forward-gate-a-formal.json`.

## Gate B inverse core I1

The first inverse optimization replaces eight duplicated raw-qword butterflies
with four pair-packed butterflies and replaces eight duplicated local-half
Montgomery chains with four pair-packed chains using inverse execution-order
tables.  It leaves the remaining three cross-register stages unchanged.

I1 is bit-exact with the scalar inverse and I0 over the full test set.  The
2,000-call short benchmark measured 228.541 TSC versus 275.387 for I0, saving
46.846 TSC or 17.011%.  This is only the TILE4 inverse NTT32 core; it excludes
inverse DFT3, untwist, normalization, top merge, and coefficient-order stores,
so it is not yet an Official `Delta I` measurement.

## N5 contiguous qword frontend

`gt32_tile4_frontend_wide_raw_asm()` implements the quartic-native N5 shape.
Each of eight groups loads six contiguous YMM vectors, performs the raw top
split before permutation, uses immediate `vpblendd` to select whole quartic
qwords, consumes generator-owned branch/n3 twist streams, runs two DFT3s, and
writes six complete 32-byte TILE4 vectors.  It has no offset table, scalar
indexed loads, word-plane transpose, or mask registers.

The same-binary short result is recorded in
`results/tile4-forward-n5-short.json`.  The wide frontend measured 145.300 TSC
versus 177.774 for fixed-displacement gather.  The combined N5 plus pair-packed
core measured 396.165 versus frozen GT32 at 469.036 TSC, directionally 15.536%
faster.  The raw entry remains explicitly limited to coefficient inputs in
`[-3,4]`; this is not yet a promotion benchmark or a general mod-q entry.

## Native TILE4 scale contract and basemul B2

The generated scale contract labels every boundary by the exponent in the
stored representation `x*R^e mod q`.  Forward is `e=0 -> e=0`; native quartic
basemul is `e=0 x e=0 -> e=-1`; inverse preserves `e=-1`; and its final fused
normalization must carry `e=2` to return coefficient output at `e=0`.  Lambda
is generated in physical TILE4 Q order as `lambda*R` (`e=1`).  An independent
int64 schoolbook test converts the basemul result with one Montgomery `R^2`
operation and checks every coefficient against the ordinary quartic product.

B0 is the scalar alias-safe oracle.  The first intrinsic B1 is retained as a
negative control: disassembly shows stack spills and its broadcast mapping
duplicates arithmetic lanes.  B2 instead uses a self-inverse 12-unpack
register network to transform four TILE4 vectors into four full coefficient
planes, applies the zero-spill quartic Montgomery schedule, and transforms the
result back to TILE4.  Its first version requires distinct output and inputs.

The 2,000-call, 20-sample directional result is recorded in
`results/tile4-basemul-b2-short.json`: Official measured 339.593 TSC, frozen
GT32 `e=-1` measured 307.822, B1 measured 1502.951, and B2 measured 434.952.
B2 is 95.359 TSC slower than Official, leaving 43.383 TSC of the formal
138.742-TSC two-forward consumer budget for the inverse delta.  B2 temporarily
stores four coefficient planes in its destination block before the inverse
transpose.  The next experiment therefore fuses those planes directly into
inverse stage 1, removing four stores, four reloads, and the inverse transpose
rather than trying to schedule the rejected broadcast B1.

## Split Gate C and Gate D contracts

The ordinary and decapsulation-only basemul paths are now separate symbols.
`gt32_tile4_basemul_general_b2_asm` fuses the Montgomery `R^2` finalizer and
returns the common TILE4 AoS ABI at `e=0`; it is the only B2 variant eligible
for later `add`, `sub`, or `tobytes` callers.  In the directional short run it
measured 444.477 TSC versus Official at 331.988.  The arithmetic contract is
correct, but Gate C remains open until the real keygen/encap/verification
consumer chains are measured.

`gt32_tile4_basemul_scale_soa_private_asm` is restricted to the decapsulation
`basemul_scale -> invntt_scale` island.  It stops before the B2 output
inverse-transpose, returns private coefficient planes at `e=-1`, and measured
390.957 TSC versus 434.435 for the AoS scale result, saving 43.478 TSC.  Its
layout and sole legal consumer are generated into `tile4_scale_contract.json`.
The direct-layout scalar `gt32_tile4_inverse_soa_private_ref` is exact with the
TILE4 inverse after benchmark-excluded conversion and is the oracle for I2.
The next D2a step is an assembly inverse NTT32 that consumes these planes; no
claim is made by adding its cost to an incompatible Frozen inverse layout.

## Gate D2a I2 hard stop

The executable D0 baseline is B2 AoS plus I1 AoS, not the incompatible sum of
B2-S and I1.  In the current short paired run D0 measured 660.577 TSC.  The
I2 hard gate was therefore fixed at 272.019 TSC from the earlier producer
measurement; 228.541 TSC was the strong gate.

Two exact private-layout I2 implementations were measured.  The serial
coefficient implementation measured 468.802 TSC.  The intended eight-data-YMM
version removes the coefficient loop, shares stage constants, and measured
361.092 TSC, but still exceeds the hard gate.  The executable B2-S plus
parallel-I2 pipeline measured 757.904 TSC, regressing 97.327 TSC from D0.

The private Q permutation makes the first two inverse stages pair-pack well,
but maps the next two Montgomery stages to lane-wise shuffle butterflies;
their arithmetic/shuffle DAG is materially larger than I1's fully occupied
cross-register chains.  Generator-derived range propagation ends at absolute
bound 12150, all exact tests pass, and neither assembly symbol spills.  This
is therefore a performance hard stop rather than a correctness, scale, range,
or ABI failure.  D2b tail work is not started; Gate C remains independent.

## AoS inverse tail

The active AoS path now has a complete inverse consumer.  Generator-owned
branch matrices fold inverse twist, top reconstruction, the full `1/96`
normalization, and the `R^2` factor that converts `e=-1` input to `e=0`.
Assembly processes six TILE4 vectors per group, performs two IDFT3s and two
self-inverse qword `GT_BLEND3` networks, then writes A/B/C directly in
coefficient order.  It uses fixed public control flow and no stack operands.

Final stores are exact centered-canonical.  The proved range chain is
`12150 -> 2359` at the I1 checkpoint, at most `7077` after IDFT3, at most
`3812` before final correction, and `[-1728,1728]` at the ABI.  Exact
scalar/intrinsic/assembly differential and 1000 round trips pass, together
with ASan/UBSan and the spill audit.

The 2,000-call short run measured 425.444 TSC for the intrinsic tail and
370.502 for zero-spill assembly.  I1 plus tail measured 608.893; B2 plus the
complete inverse measured 1048.044.  A separate same-binary consumer run
measured 796.826 for Official, 1297.028 for frozen GT32, and 1127.645 for
TILE4.  TILE4 is directionally 13.060% faster than frozen, but 41.516% slower
than Official.  A roughly 7--8% shift across the two link compositions is
recorded as code-placement sensitivity; neither short result is a promotion
benchmark.  See `results/tile4-aos-inverse-tail-short.json` and
`results/tile4-consumer-vs-official-short.json`.

## Private inverse-tail DAG reduction

Four separately callable assembly controls isolate the remaining tail DAG.
T1 changes only final canonical correction to a bounded private representative;
T2 changes only IDFT3 from four Montgomery products to one; T3 additionally
centers only `r1+r2`; and T4 uses two normalized untwists plus one correction
product instead of the four-entry branch matrix.  The combined champion is a
decapsulation-only entry and is not a replacement for the canonical inverse.

All canonical variants are exact with the scalar oracle.  Relaxed variants are
mod-q equal, stay within absolute bound 1818, and are bit-exact after the
Official reference `crepmod3` formula over 1000 test cases.  Generator range
metadata proves raw pair sum/difference at 24300, one-Mont IDFT3 output at
26354, and all int16 add/sub operations safe.

The same 2,000-call binary measured canonical baseline 368.808 TSC, T1
309.890, T2 352.894, T3 298.990, T3 plus relaxed output 228.909, canonical T4
309.927, and the combined private champion 214.183.  Matrix3 therefore saves
14.726 TSC under the private contract but regresses 10.937 TSC in the
canonical path.  The selected champion is 41.926% faster than the canonical
baseline tail.

A same-binary end-to-end target charges both backends two identical 1536-byte
input copies, then measures two forwards, basemul-scale, and inverse.  Its
output is checked mod q and after `crepmod3` before timing.  Official measured
1709.562 TSC and TILE4 private measured 1728.023, a remaining 18.461 TSC or
1.080% regression.  This is short directional evidence, not a formal parity
claim; the next gate must control placement and use the real decapsulation
caller.  See `results/tile4-private-tail-dag-short.json`.

## Private tail microarchitecture and crepmod3 boundary

T5 specializes the prologue, keeps `w/w_qinv` resident, overlaps center and
Montgomery chains, and writes IDFT3 outputs in place.  T6 schedules both
branches together; T7 batches six untwists, three corrections, and six final
centers; T8 removes half of the blend-result moves.  All pass the complete
mod-q and `crepmod3` differential suite.

T5--T9 remain within roughly one TSC and reorder between short launches.  One
run measured T5 214.130, T6 215.344, T7 213.401, T8 213.796, and isolated T9
214.651 TSC.  There is no defensible speed winner.  T9 is selected because it
exports only the production body: its function is 5578 bytes and its object
including constants is 16714 bytes, versus 63058 bytes for the ablation
object.

T10 directly reduces the proved raw matrix output (absolute bound 4810) to
ternary coefficients.  It is correct but not faster: standalone T8 plus
Official `crepmod3` measured 331.465 TSC versus 338.487 fused.  In the final
short full-chain composition, Official `2F+B+I+crepmod3` measured 1831.771,
isolated T9 plus Official `crepmod3` 1867.057, and T10 1868.883.  T9 remains
35.285 TSC or 1.926% behind Official.  T10 is a negative control; the next
meaningful step is the real fixed-placement decapsulation caller, not more
tail scheduling.  See `results/tile4-private-tail-microarch-short.json`.

## C3-only lazy basemul promotion statistics

The selected private chain is now frozen as N5 forward, c0--c2 raw/c3
centered-late basemul, I1, T9, and the Official `crepmod3`.  The c3-only
checkpoint is not a general basemul ABI: it is valid only for generated N5
output bounds and the immediate private inverse consumer.  The leaf does not
perform runtime range or alias checks.

The serious same-binary gate uses 100,000 calls per sample, 20 ABBA/BAAB
paired samples per launch, and five independent launches.  In the primary
link order, the complete chain without `crepmod3` measured 1697.028 versus
1691.794 TSC ticks (paired ratio 0.997310; TILE4 won 5/5 launches).  Including
`crepmod3` measured 1815.907 versus 1812.632 (ratio 0.996652; 5/5).  The
reversed-link corroboration measured ratios 0.993528 (4/5) and 0.996412
(4/5), respectively.  Basemul alone remains 49.3% slower and basemul plus
inverse remains 16.6% slower; the end-to-end win comes from the two N5
forwards, not from a hidden consumer win.

Core PMU measurements use one million calls, three repetitions, and separate
non-multiplexed event groups.  On the full chain TILE4 retired about 11.3%
fewer instructions and used about 0.9% fewer core cycles.  With `crepmod3`, it
retired about 10.4% fewer instructions while core cycles were effectively at
parity.  TILE4 has substantially more L1 load traffic and backend-bound slots;
those remain the consumer-side risk for real caller integration.

These results promote the arithmetic chain to an integration candidate, not
the backend to production.  Full deterministic private decapsulation,
byte-exact KEM/KAT behavior, and caller-native adversarial range tests remain
required.  Raw samples, PMU scaling data, and both binaries' hashes, sections,
symbol addresses, and reported sizes were collected from the minimal
`--gc-sections` comparison binaries and recorded in
`results/tile4-promotion-serious.json`,
`results/tile4-promotion-serious-reversed.json`,
`results/tile4-promotion-pmu.json`, and
`results/tile4-promotion-symbols.json`.

## P1 single-use decoded operand island

The generator now owns a bijective mapping from each serialized 12-bit
component through Official `(branch,block,coefficient)` order into both TILE4
AoS and the private BM SoA `(group,plane,lane)` order.  Correctness-first
unpackers preserve full-input processing and Official noncanonical rejection;
tests cover canonical values, `q` rejection, both layouts, and exact mixed-BM
output.  The mixed `SoA e=0 x AoS e=0 -> c0--c2 raw/c3 centered AoS e=-1`
assembly skips one complete input transpose without changing arithmetic.

In the 2,000-call ABBA/BAAB short gate, the existing AoS BM measured 404.256
TSC and the mixed BM 347.937, a 13.6% reduction with 39/40 paired wins.  With
the same correctness-first Official-unpack-plus-layout bridge on both paths,
the complete `frombytes(f)+BM+I1+T9` path improved from 2164.626 to 2109.203
TSC, or 2.6% by paired median with 39/40 wins.  AoS and private-SoA bridge
costs themselves are effectively equal, so the BM transpose saving survives
the consumer chain.

The absolute boundary still rejects this implementation for integration:
bare Official AVX2 `frombytes` measured 94.208 TSC, while Official unpack plus
the scalar AoS bridge measured 1318.491.  P0 proves serialized slots first
pass through Official's 128-word lane permutation and then a global
Good--Thomas permutation, so the next P1 gate needs a generated AVX2 fixed
schedule rather than scalar mapped stores.  P2 (`hinv` private SoA through
SoA-output BM and specialized `tobytes`) remains deferred until that boundary
is competitive.  See
`generated/tile4_serialized_mapping.json` and
`results/tile4-mixed-frombytes-short.json`.

## P1-V vectorized decoder gate

V1 now reuses the Official six-chunk AVX2 12-bit unpack and invalid-mask
arithmetic, but replaces Official stores with generator-owned fixed qword
destinations in TILE4 AoS order.  It never materializes Official component
layout and preserves full-input noncanonical rejection.  Canonical mapping and
malformed-input tests pass exactly.

The current V2 symbol is deliberately named a control: it runs V1 and then
transposes twelve 128-byte blocks into the private BM SoA layout.  Its selected
transpose processes two blocks concurrently through all three unpack levels.
This is faster than the serial block schedule, but it still creates the AoS
store/reload boundary and therefore is not the requested direct private-SoA
decoder.

The 2,000-call ABBA/BAAB measurements place V1 roughly 50 TSC ticks above bare
Official unpack.  V2's extra transpose remains approximately the same size as,
and in the representative same-run paired comparison slightly larger than,
the mixed basemul saving.  The complete caller alternates between a very small
win and loss; its paired delta is below its MAD, so the short gate is
inconclusive rather than a promotion result.

Three controls were rejected.  Wide stores for the 36 single-chunk AoS vectors
reduced the later transpose differential but made the absolute decoder slower;
memory-source first-level transpose increased load uops; and duplicating the
unpack body to remove one internal call did not repay its code-size cost.  P1
integration remains stopped until a generated shuffle network writes private
SoA directly from unpack registers, or proves that this permutation cannot fit
under the same-run mixed-BM saving.  The selected short samples are in
`results/tile4-mixed-frombytes-short.json`.

### Direct private-SoA static network gate

The generator now expands the most plausible direct network class before any
assembly is written.  It symbolically applies the same four-vector transpose
used by the BM, maps every target private-SoA lane back to an unpacked source
lane, and finds the minimum number of source-half selections in a network made
from `vperm2i128`, zeroing `vpshufb`, and `vpor`.  Masks are shared across the
four coefficient planes; dynamic operations are not.

This class fails decisively.  The global mod-3 Good--Thomas permutation makes
each coefficient plane lose the qword locality that makes V1 cheap.  The exact
plan needs 72 distinct masks applied four times: 288 `vpshufb`, 288 cross-half
`vperm2i128`, 192 accumulator ORs, 48 memory-merge ORs, 96 wide stores, and 144
source-transpose shuffles.  Its 1056 estimated layout instructions exceed the
selected AoS-materialization control's 480 by 576 instructions.

No assembly is emitted for this rejected class.  This is not a proof that
every conceivable AVX2 direct decoder is impossible; it is a proof-backed
stop for the suggested `permute halves -> pshufb -> blend` shape.  A continuing
V2 attempt must preserve quartic qword SIMD utilization across the mod-3
permutation, or co-design a different private consumer ABI.  Repeating this
coefficient-plane network in hand assembly is not justified.  The full lane
routes and static accounting are recorded in
`generated/tile4_frombytes_direct_soa_plan.json`.

## A1 wide direct-AoS basemul gate

The direct-AoS `vpmaddwd` proposal is mathematically valid.  A1 constructs the
four qword-local `D0..D3` vectors, forms four signed 32-bit dot products, uses
two `vphaddd` operations, applies one 32-bit Montgomery reduction per output,
and packs directly back to TILE4 AoS.  The output is uniformly `e=-1`; it does
not use the champion's c0--c2 raw/c3-only center contract.

Generator bounds prove a maximum `vpmaddwd` pair magnitude of 232761888, a
four-term sum of 465523776, and an `x-m*q` numerator of 692078271.  All fit
signed int32.  Montgomery32 output is bounded by 10561, and every subsequent
I1 int16 butterfly remains safe through a worst terminal bound of 28594.
Tests pass mod q, the R-exponent oracle, in-place alias, I1, T9, and `crepmod3`
over 1000 cases.

Performance rejects the implementation direction.  In the selected 2,000-call
short run, A1 measured 529.311 TSC versus 397.222 for c3center-late; BM plus I1
measured 758.155 versus 628.798.  Disassembly shows no spill and already
hoists all shuffle masks and reducer constants.  A hand version can clearly
remove roughly two of 34 loop instructions by using precomputed lambda-qinv,
but would need about 25% fewer cycles to reach the champion.  That gap is too
large for scheduling alone, so A2 assembly is rejected under the bounded
stop-loss.  See `generated/tile4_wide_aos_range.json` and
`results/tile4-wide-a1-short.json`.

## Basemul cost attribution

N5 forward and the private I1 plus T9 inverse are frozen while this gate
decomposes B3 in a benchmark-only object.  The object exports independent
AoS/SoA transpose leaves, a true SoA-by-SoA arithmetic core, a c3-only repair
leaf, and no production KEM symbols.  Exact checks establish that the
transpose is self-inverse and that the raw, c3-repaired, and reconstructed B3
boundaries match the existing implementation bit for bit.

In the expanded 2,000-call, 20-sample same-binary run, the empty call measured 2.527
TSC.  After correcting repeated call overhead, two input transposes cost
87.526, the production c3 arithmetic cost 262.853, and the output transpose
cost 42.514 TSC.  Their reconstructed sum is 395.419 versus 397.302 for the
fused B3 leaf, a residual of 1.883 TSC or less than 0.5%.  The attribution
therefore closes for this warm-L1 microbenchmark.

The important comparison is arithmetic-only.  Official
`poly_basemul_scale` in its native layout measured 265.972 TSC including the
same call overhead, while TILE4's c3 production arithmetic measured 265.380;
TILE4 is 0.592 TSC faster in this run.  Raw TILE4 arithmetic was 257.372 and
the c3 range policy adds 8.008 TSC inside the arithmetic leaf.  In contrast,
input plus output layout costs 130.040 TSC.  This accounts almost exactly for
the complete B3 disadvantage of 131.331 TSC relative to Official.

The result selects the layout case, not the arithmetic case: the current
single-accumulator schoolbook schedule is already at Official arithmetic
parity.  Further qinv-hoist, issue-order, or Karatsuba work is not the next
gate.  A continuing design must remove at least one complete transpose at a
real producer or consumer boundary without introducing another global
permutation.  The raw samples, MADs, contracts, and corrected reconstruction
are in `results/tile4-basemul-attribution-short.json`.

### BM planes to local I1 fusion

The first layout follow-up tests the highest-priority local fusion without
changing the public or production ABI.  For each 16-quartic block, the final
four qword unpacks of the plane-to-AoS transpose are algebraically cancelled
with the first four unpacks of I1's raw stage 0.  The benchmark-only producer
then executes the pair-packed Montgomery stage 1 before storing a post-stage1
AoS boundary; a second leaf finishes the three cross-register I1 stages.
This removes eight shuffle instructions and four AoS store/reload pairs per
block, and its final I1 output matches the champion exactly.

The static reduction does not survive as a cycle win.  The champion B3 plus
I1 measured 627.490 TSC and the fused path 629.901.  The paired fused-minus-
champion delta was +1.958 TSC with MAD 4.067, and the fused path won only 7 of
20 samples.  Its producer and cross-stage remainder measured 517.088 and
118.534 TSC respectively.  A compact single-body control using rotating
constant pointers was worse at approximately 647 TSC.

The candidate therefore fails both the 628-TSC parity and 610-TSC continuation
gates.  It remains a useful negative result: deleting shuffle and a memory
boundary is insufficient when the resulting coupled DAG and code shape lose
the same amount elsewhere.  No production kernel calls these symbols.  A
future Direct-AoS attempt must be the materially different A2-F DAG that also
eliminates unnecessary 32-bit finalization and the standalone pack boundary;
this local SoA fusion should not be extended further.

### Forward terminal to private BM planes

The input-side follow-up keeps the N5 frontend and the first four NTT32 stages
unchanged.  Instead of reconstructing each final stage-5 pair as TILE4 AoS,
the benchmark-only core retains pair-packed sums and differences and maps
them directly into the four private BM coefficient planes.  A generated
`vpshufb`, dword-unpack, and qword-unpack network needs 12 shuffles per
16-quartic block, versus four stage-5 reconstruction shuffles plus the normal
12-shuffle transpose.  The composition therefore deletes four real shuffles
per block rather than merely moving the transpose.

The new representation is exact: converting its output back to AoS matches
N5 bit for bit, its SoA-input BM matches B3 exactly, and the complete
`2F + BM + I1` output is exact.  In the T9-linked corroboration binary, a
private-SoA forward costs 32.513 TSC more than the matched AoS forward, while
the SoA-input arithmetic plus one output redeposit saves 93.944 TSC in BM.
The local chain measures 1465.548 versus 1441.599 TSC, a paired saving of
23.243 TSC with MAD 3.535 and 20/20 wins.

Adding the unchanged T9 tail preserves and enlarges the directional result:
`2F + BM + I1 + T9` measures 1713.992 versus 1678.389 TSC.  The paired saving
is 39.050 TSC with MAD 8.504 and 20/20 wins.  This remains a short kernel-chain
gate rather than a real decapsulation caller result, but T9 is no longer the
blocker.

This is a conditional pass.  It clears the 20-TSC complete-chain gate but
misses the original 5--8 TSC per-forward budget by a wide margin.  The result
is therefore evidence for a caller-private representation island, not a new
general forward ABI.  It remains benchmark-only until the saving survives
the real private caller boundaries; no 100,000-iteration benchmark is justified
yet.  See `results/tile4-forward-bm-redeposit-short.json`.

### A2-F common bilinear DAG feasibility

The generator now expands every post-I1-stage1 quartic coefficient into its
source leaf, `a_i*b_j`, lambda, sign, inverse-twiddle, and Montgomery-scale
terms.  The minimal two-leaf A2-F1 proof succeeds: the worst raw `U+/-V` is
931047552, its REDC numerator is 1157602047, and narrowing is bounded by
17664.  All remain within signed int32 and int16 respectively.

The four-leaf A2-F2 candidate fails before assembly.  The nontrivial ordinary
inverse twiddle is 708, so directly evaluating the weighted raw expression is
bounded by 660112714368, far outside int32.  Folding the twiddle into dynamic
B operands is safe, but its two B pre-twiddle Montgomery chains merely replace
the two original stage-1 twiddle chains: the reduction count stays six per
four leaves.  A one-pass allocation also needs all 16 YMM before reserving a
shuffle mask or reducer constant; splitting c01/c23 avoids spills only by
rebuilding the A1 D-vectors.

Consequently no A2-F assembly is emitted.  This is the requested aggressive
gate applying its stop rule: the safe factorization removes neither reduction
chains nor enough representation work to recover A1.  A future reopening
needs a factorization that shares a dynamic pre-twiddle across multiple
reductions, or a wider SIMD integer domain.  Full expressions and bounds are
recorded in `generated/tile4_a2f_dag.json`.

### Caller-private polymul gate

The representation island is now enclosed in a real benchmark-only entry
whose public boundary is two ordinary small coefficient polynomials and one
ordinary ternary result after `crepmod3`.  Both the AoS baseline and private-
SoA candidate receive the same 7680-byte caller-owned scratch object.  The
scratch is 64-byte aligned in the primary contract, function boundaries are
preserved, and the dead frontend buffer is reused for the candidate's single
SoA-to-AoS redeposit.  No private layout escapes the entry.

The entry is exact over 64 deterministic random trials for distinct output,
`out==a`, `out==b`, and squaring.  The selected short primary run measured
1739.234 versus 1710.821 TSC: a paired saving of 29.548 TSC with MAD 4.818 and
20/20 wins.  Across 32/64-byte scratch placement and normal/reversed link
order, every configuration remained positive at 20.906--29.548 TSC, with
77/80 aggregate wins.  This cleared the short continuation gate.

The subsequent 100000-iteration run remained directionally positive in all
four configurations at 23.824--29.278 TSC and 75/80 aggregate wins.  However,
the primary 64-byte configuration measured a 25.327-TSC saving with only
17/20 wins and paired MAD 20.341.  It therefore fails the predeclared primary
stability gate and is classified
`inconclusive-serious-primary-win-rate-fail`.  PMU work, production selection,
and public ABI changes remain stopped.  The short and serious matrices are in
`results/tile4-private-caller-short.json` and
`results/tile4-private-caller-serious.json`.

### Asymmetric AA / SA / SS caller gate

The caller harness now also measures a one-sided private layout without
changing its public coefficient-polynomial boundary.  `AA` uses two ordinary
N5 AoS forwards and B3, `SA` uses one private-SoA forward plus one ordinary
AoS forward and the mixed SoA/AoS BM, and `SS` is the previous two-private-
forward candidate.  All paths share I1, T9, `crepmod3`, scratch size, alias
cases, and sample ordering.

The 2,000-iteration four-placement short gate measured a primary AA median of
1741.132 TSC.  SA measured 1714.463 TSC and saved 27.290 TSC with 17/20
primary wins; across 32/64-byte scratch alignment and normal/reversed link
order it saved 22.026--27.290 TSC with 75/80 wins.  SS saved only 14.705 TSC
in the primary placement with 14/20 wins, although all corroboration medians
remained positive.  SA is therefore the selected representation candidate,
but its primary win rate calls for a recheck rather than a serious benchmark.
The generated record is `results/tile4-private-caller-aa-sa-ss-short.json`,
and the actual KEM operand provenance is recorded in
`docs/basemul-callsite-provenance.md`.

### Encapsulation general-scale asymmetric gate

`gt32_tile4_basemul_general_soa_aos_to_aos_asm` is a benchmark-only Gate C
variant for the real `encap.c` producer topology.  It accepts the private-SoA
forward result for `r` and the ordinary AoS decode of `h`, then transposes the
four raw product planes and issues four parallel `Mont(R^2)` chains.  Its
output is the ordinary TILE4 AoS `e=0` boundary, so the existing add and
serialization consumers need no scale-repair pass.

The scoped benchmark includes `frombytes(h) + NTT(r) + BM + add(m)` and checks
64 deterministic cases exactly.  In the recorded 2,000-iteration normal and
reversed-link short runs the asymmetric path remained positive with 19/20
wins in both binaries, but saved only 13.513 and 16.405 TSC.  This proves that
the scale debt can be fused without erasing the representation benefit, while
leaving too little margin for serious or production promotion.  `tobytes` is
an excluded identical suffix because both paths already meet the same AoS
`e=0` boundary.  See `results/tile4-encap-mixed-general-short.json`.

### One-sided pair-AoSoA(2) static gate

The generator now evaluates all three coefficient pair partitions for the
`decap.m1` topology: one bytes operand is decoded to the pair layout, the
other remains AoS, and the BM must return AoS for I1.  It counts the complete
decoder network, the BM-input conversion, and the minimum output redeposit.

Inside the existing coefficient-plane transpose plus half-select/vpshufb
network class, all partitions need 912 decoder instructions.  Even granting
a hypothetical pair-native BM zero input-conversion cost, `01|23` needs 48
output shuffles and has an optimistic layout debt of 960 instructions, 576
above the 384-instruction V1-AoS-plus-BM-transpose baseline.  `02|13` and
`03|12` each need 96 output shuffles and are 624 instructions above baseline.
The pair decoder improves on the rejected 1056-instruction full-SoA decoder,
but cannot reach the end-to-end gate, so no pair arithmetic or assembly is
emitted.  See `generated/tile4_pair_aosoa_gate.json`.

### BaseMul contract matrix and deferred-c3 gate

The generated scale contract now treats BaseMul as a two-dimensional family,
not a universal symbol.  AoS/AoS and private-SoA/AoS inputs each have a scale
variant returning `e=-1` for `inverse_scale`, and a general variant returning
`e=0` for add/sub/Encodeq.  The selected production path remains AoS/AoS;
mixed symbols stay caller-scoped candidates.  The four legal contracts and
their consumers are recorded in `generated/tile4_scale_contract.json`.

The final c3-range question is also closed.  A fully raw c3 reaches absolute
bound 28040 after the raw inverse length-2 stage, which is still int16-safe.
The first reducing Montgomery stage is length 4, but it reduces only each
butterfly's high arm; a permanent low-arm path such as physical Q=0 cannot
have its normalization absorbed there.  The fully raw conservative chain
first becomes unsafe at length 16 and needs the previously tested selective
checkpoint after length 8.  That checkpoint was exact but slower than the
selected c3-at-BM-boundary path, so the approximately 8-TSC c3 center remains.
The mechanical conclusion is in
`generated/tile4_raw_aos_inverse_range.json` under
`c3_deferred_center_gate`.

### Encap Encodeq/G boundary closure

Algorithm 12 serializes `rhat` and hashes those bytes before the mixed BM, so
the private-SoA forward result must also support byte-exact, non-destructive
Encodeq.  The currently executable control transposes private SoA back to AoS
and then uses the identical AoS encoder.  Its measured 42.514-TSC transpose
penalty exceeds the complete arithmetic-side mixed-path saving of 13.513 to
16.405 TSC, yielding a projected regression of 26.109 to 29.001 TSC before
the common encoder/hash suffix.

The AoS-bridge Encap path is therefore stopped.  A genuinely direct private-
SoA Encodeq remains logically possible, but must cost less than 13.513 TSC
above the AoS encoder, retain `rhat` for BM, and avoid intermediate AoS.  No
such network is currently implemented; the analogous natural direct-SoA
decoder's 1056 versus 480 instruction result is a warning, not a reverse-
encoder proof.  See `results/tile4-encap-encodeq-boundary.json`.

### Destructive four-way stage-5 schedule

The first post-caller ASM experiment keeps stage 4, the private plane mapping,
BM, I1, and T9 unchanged.  Its benchmark-only `FR_MONT_QWORD_PACKED4` extracts
all four high and low qword pairs first, reuses the four dead odd data vectors
as Montgomery temporaries, and issues four independent chains by operation
class.  This removes four register moves per tile, or 24 per polynomial, and
requires no spill.

The output is exact at both the private-forward boundary and through
`2F+BM+I1+T9`, but the shorter static schedule is slower.  Forward core rises
from 264.788 to 279.794 TSC, a paired regression of 14.886 TSC with 0/20 wins.
The complete chain rises from 1597.999 to 1632.942 TSC, a regression of 33.645
TSC with 0/20 wins.  Batching all unpack and multiply classes lengthens the
live ranges and produces a less favorable execution schedule than the older
two-pair groups, despite deleting moves.

This fails both predeclared gates, so stage-5 instruction-order tuning stops.
The S5x4 symbol remains benchmark-only and is not used as the starting point
for the stage-4/stage-5 combined-layout experiment.  Results are in
`results/tile4-s5-schedule-short.json`.

### Stage-4 to stage-5 to planes layout gate

The generator symbolically tracks every 16-bit lane from stage-4 S/D state,
through standard reconstruct or direct qword unpack, and through the complete
12-shuffle private-plane network.  Direct consumption changes stage-5 qword
order from `[0,1,2,3]` to `[0,2,1,3]`.  After plane conversion, every
coefficient plane has the same lane permutation:

```text
[0,8,2,10,4,12,6,14,1,9,3,11,5,13,7,15]
```

This is a swap of physical lane-index bits 0 and 3.  It moves eight of sixteen
lanes across the 128-bit AVX2 boundary.  Reordered stage-5 tables can preserve
the arithmetic, and reordered lambda tables can preserve each quartic
modulus, but `vpshufb`, the existing dword/qword unpack topology, and whole-
plane store order cannot cross that boundary.  Twiddle constants alone also
cannot change the inverse butterfly incidence graph.

The candidate deletes eight stage-4 reconstruct shuffles per tile, but a
standard downstream consumer needs at least one cross-lane repair for each of
the eight output plane vectors.  The proved best net shuffle saving is
therefore zero, and no solution exists within the current 12-shuffle plane
network.  Assembly is not emitted.  Reopening this idea requires a separately
generated inverse topology whose native leaf order already swaps bits 0 and
3; that is a new forward-plus-inverse private ABI experiment rather than a
forward-tail constant rewrite.  See `generated/tile4_s45_layout_gate.json`.

### Permutation-native inverse and T9 gate

The reopened generator gate carries the stage-4-eliding permutation through
Basemul and a mechanically conjugated inverse instead of repairing it at the
Forward boundary.  In private coefficient-plane coordinates the permutation
is `[0,8,2,10,4,12,6,14,1,9,3,11,5,13,7,15]`.  Translating through the actual
private-plane Q order shows that it swaps semantic Q bits 1 and 2.  The
generated inverse graph therefore exchanges the length-4 cross-half topology
with the length-8 cross-vector topology while preserving all 80 butterflies,
49 non-identity fixed-factor butterflies, and 16 vector Montgomery chains per
tile.  Its 13-YMM peak also matches I1.  The Forward and inverse
algebraic gates pass without an explicit repair pass.

The first hard T9 gate does not pass.  T9 addresses a vector by
`group=Q/4` and a qword within it by `qlane=Q%4`.  Under the permutation,
physical group bit 0 becomes logical qlane bit 1 and physical qlane bit 1
becomes logical group bit 0.  Thus each physical YMM contains the two
128-bit halves of two different logical output groups.  Constants can absorb
all factors, but load addresses, whole-YMM store order, and the existing
within-group `BLEND3` cannot move a half between adjacent groups.

Keeping T9 full-width requires at least 48 cross-lane repairs: six streams,
four adjacent group pairs, and two reconstructed logical vectors per pair.
An XMM-only alternative avoids an explicit permute only by doubling vector
arithmetic, reductions, and stores.  Consequently the required zero-extra-
shuffle T9 absorption is false and no assembly is emitted.  This stop is
specifically the zero-cost T9 gate, not an algebraic rejection of the
conjugated inverse.  The 48-repair lower bound is still smaller than the 96
shuffles removed from two Forwards, but benchmarking that relaxed design
requires a separately approved end-to-end gate.  The complete edge graph and
proof are in `generated/tile4_permutation_native_gate.json`.

### Relaxed permutation-native cost gate

The relaxed gate implements the stage-4-eliding Forward-P terminal and a
materialized 48-`vperm2i128` P-to-standard T9 repair control.  Sixty-four
deterministic random trials pass the Forward-P mapping, exact repair, and
repair-plus-T9 differential.  Disassembly confirms that the Forward loop
drops from 16 to 8 static `vperm2i128` instructions, hence 48 dynamic
instructions per Forward and 96 for the two-Forward caller shape.

Real execution does not convert that static deletion into the anticipated
8--12 TSC.  One Forward saves 3.402 TSC (MAD 0.274, 19/20 wins); two Forwards
save 5.956 TSC (MAD 1.536, 20/20 wins).  The materialized repair control adds
18.362 TSC over T9 (MAD 1.787, 0/20 wins), although that number includes the
temporary repaired-buffer stores and reloads.

The predeclared continuation condition was
`S_forward_P > C_T9_repair + 8 TSC`.  It fails even under the impossible
optimistic assumption `C_T9_repair=0`, because 5.956 is below the required
8-TSC margin.  R1 fused T9, R2 half-width T9, and Inverse-P assembly are
therefore not emitted.  This is a cost stop for the current bit-1/bit-2 Q
permutation on this AVX2 core; the generator feasibility result for Inverse-P
remains valid.  Results are in `results/tile4-permutation-relaxed-short.json`.

The lower-risk streaming-B control also passes 64 exact random trials but is
decisively slower: Forward-B plus BM regresses by 208.650 TSC, and the result
remains 213.664 TSC slower through I1 and T9, both with 0/20 wins.  Its split-
half scratch traffic and serialized BM schedule cost much more than the
eliminated B-plane materialization.  See
`results/tile4-streaming-b-short.json`.

### Joint terminal-layout family gate

The reopened gate no longer fixes the stage-4 pairing or the leaf
permutation.  For one 16-quartic BM block the generator enumerates all three
perfect pairings of the four pre-stage-4 vectors, both orientations of both
pairs, and all 24 free post-stage-5 register assignments: 288 combinations.
Twenty-four combinations produce coefficient-homogeneous planes and a
well-formed standard-AoS redeposit.  The optimum is the already known
P-domain pairing, not a new zero-debt permutation.  It removes stage-4
reconstructs, needs no Forward repair or additional Montgomery chain, but
requires four `vperm2i128` repairs per BM output block.

Including two Forward terminals and the mandatory BM output back to standard
AoS, the selected P layout costs 56 static shuffle instructions per block,
versus 68 for canonical AoS and 60 for the existing standard private-SoA
control.  Thus it passes the static gate by exactly one 12-shuffle layer
relative to canonical AoS, but only by four shuffles relative to the current
private-SoA implementation.  At this gate, coefficient-pair `01|23`,
`02|13`, `03|12`, and native-stage-5-packed layouts remain only optimistic
layout floors; the follow-up arithmetic gate below resolves them.

The selected benchmark-only BM consumes P-domain planes using generator-
permuted lambda streams and performs the four output half repairs directly in
registers before standard AoS stores.  It passes exact P mapping and BM output
differentials over 64 random small-input cases.  In the 2,000-call short gate,
`two terminals + BM` saves 19.852 TSC versus canonical AoS (17/20 wins, delta
MAD 4.462) but only 2.299 TSC versus standard private SoA (13/20 wins, delta
MAD 3.648).  The predeclared continuation gate was at least 20 TSC.  The
candidate therefore stops before caller integration and no serious benchmark
is run.  See `generated/tile4_terminal_layout_family_gate.json` and
`results/tile4-terminal-layout-short.json`.

### Pair/native-stage-5 BaseMul arithmetic gate

The follow-up gate leaves the saturated four-plane schoolbook design space and
derives exact quartic multiplication DAGs for `01|23`, `02|13`, `03|12`, and
native stage-5 qwords.  Both useful factorizations are mechanically expanded
and asserted equal to schoolbook multiplication modulo `x^4-lambda`.
`02|13` is the natural quadratic tower, but needs 13 fully occupied vector
Montgomery chains per 16 quartics.  The existing split-quartic `01|23` K2
algebra is better: its ninth variable product and three lambda products occupy
the four qword slots of the final chain, for 12 chains.  This is seven fewer
than the 19-chain flat schoolbook schedule and needs no coefficient-plane
materialization.

That arithmetic improvement does not pass the AVX2 execution-shape gate.  The
N5 input bound is 10788; the four-coefficient Karatsuba sum therefore requires
a proved input checkpoint, reducing it to 2179 before pair sums.  Its raw c3
bound is 18173, so a second native-qword checkpoint is required before inverse
length 2.  Across one 16-quartic block those checkpoints cost 36 vector
instructions.  The minimum concrete dense-qword operand construction costs 32
`vpshufb` plus 16 adds, while the 12 generic Montgomery chains cost 60 more
instructions.  These three unavoidable classes already total 144 compute
instructions; the eight input loads and four output stores bring the candidate
to 156 before any Karatsuba recombination, lane routing, loop control, or
register moves.

The complete disassembled B3 loop is itself 156 instructions per 16 quartics.
Thus the native candidate has no static room for its required algebra, even
under an optimistic zero-cost routing assumption.  The one-block assembly gate
is rejected before implementation.  This does not negate the 12-chain algebra;
it says that AVX2 qword construction and the proof-required range checkpoints
cost more than the coefficient-plane boundary they replace.  Reopening this
direction requires a producer that emits the two Karatsuba operand vectors
directly with the required range, or a wider SIMD/register domain.  See
`generated/tile4_pair_native_bm_gate.json`.

### Forward-terminal Karatsuba-basis co-design gate

The producer-side reopen condition was tested without writing assembly.  The
generator enumerates all 40 nonzero sign-normalized rows in
`{-1,0,1}^4`, all 72,780 rank-four bases made from those rows, and retains
the 979 bases from which every split-`01|23` K2 operand can be synthesized
with integral unit coefficients.  Its deliberately optimistic instruction
lower bound ignores mixed-sign lane repair, register moves, loads, and stores.
Even under that model, the selected basis is the existing monomial basis up to
lane order: terminal formation costs zero and the two dense K2 operand vectors
still require lower bounds of three instructions each.  The best non-monomial
basis adds a three-instruction terminal transform while leaving the same six-
instruction operand synthesis lower bound.

The reason is structural rather than a missed shuffle.  S4 and S5 have shape
`M_Q tensor I_degree4`: their butterflies combine component/Q coordinates,
whereas the K2 forms combine quartic-degree coordinates.  A degree-basis change
therefore commutes with S4/S5 but is not formed by their existing add/sub
edges.  In addition, each terminal butterfly computes
`low +/- Mont(high,twiddle)`.  Its only reducer precedes the final two adds, so
it cannot center both independent terminal outputs.  The proved S5 bound stays
10788 rather than becoming the 2179 BM-entry bound.  Changing a twiddle cannot
absorb a lambda-scaled degree basis either, because the low arm bypasses that
factor.

Carrying all eight redundant K2 forms through S4/S5 would double the fully
occupied vector state and Montgomery work; forming them after S5 preserves the
existing operand-construction and checkpoint costs.  A compact nonstandard
basis can pass through inverse stages 0/1 without an immediate permutation,
but it does not remove Karatsuba recombination.  A second exhaustive compact-
output search starts from the twelve post-Montgomery L01 product slots.  Among
289 ternary bases with unit product-source coefficients and an integral unit
repair, the best non-monomial output `[c2,c1,c1+c3,c0]` reduces an optimistic
scalar add/sub sparsity lower bound from 16 to 14 and its longest dependency
proxy from 8 to 6.  It still compresses twelve streams to four and introduces
a three-instruction eventual monomial-repair lower bound; qword routing and
mixed-sign repair are not included in those optimistic numbers.  Carrying all
twelve streams through inverse would instead triple its vector work.

Thus the output basis offers only a two-operation sparsity proxy, while input
formation and the mandatory post-add checkpoint remain unchanged.  There is
no proved dynamic work reduction from which to establish the required
20-TSC-equivalent margin, so the gate emits neither assembly nor a benchmark.
The scoped stop is
`stop-compact-terminal-basis-no-new-mechanism`; it can be reopened only if a
producer emits redundant K2 forms without doubling transform work, or if a
terminal operation after the last add/sub supplies the required reduction.
See `generated/tile4_terminal_karatsuba_basis_gate.json`.

### Terminal CT/GS/twisted range-schedule gate

The terminal range gate exhausts every exact two-layer S4/S5 network made from
one-chain CT or GS butterflies, independent input/output branch swaps, and
arbitrary nonzero factors in `F_q`.  Each Q group has 4,096 structural
assignments; candidate matrices must equal the current canonical pre-S4 to
post-S5 matrix exactly, without an untracked input or output scale.  The search
finds 544 exact and int16-safe factorizations across all eight groups while
keeping the current 32 S4/S5 Montgomery chains.

The available reduction relocation is much smaller than the optimistic 50%
case.  Only the identity-twiddle group `Q=0..3` admits any GS placement.  Its
best exact schedule leaves two outputs at bounds 1778 and 1747, but the other
two remain at 22524 and 10469.  Every other group requires an all-CT shape and
keeps all four outputs above the 2179 K2 bound.  In aggregate only 2 of 32
leaves avoid an explicit checkpoint; all eight physical TILE4 vectors still
contain at least one unreduced qword.  Therefore a whole-vector checkpoint is
removed from zero vectors, despite no increase in Montgomery count.

This stops the exact-boundary schedule before assembly.  A twisted schedule
with a changed boundary scale is not silently counted as equivalent: it must
first prove that BM and inverse absorb that scale/layout with a net consumer
saving.  See `generated/tile4_terminal_range_schedule_gate.json`.

### High-range and asymmetric BaseMul gate

This gate corrects an important contract ambiguity.  The production B3
schoolbook kernel already accepts symmetric N5 bounds `10788 x 10788` directly;
it has no BM-input checkpoint.  Exhausting every low-word residue of the signed
Montgomery formula gives the safe enclosing product interval
`[-3504,3504]`, one tighter than the previous 3505 bound.  Current B3's raw
quartic coefficient bounds are `[5503,8915,12328,14016]`, all int16-safe; only
c3 is centered for the private I1 consumer.  The 2179 requirement belongs to
the 12-chain L01/K2 pair-and-total operand DAG, not to BaseMul generally.

For L01/K2, the interval model proves a maximum safe input-bound product of
31,340,543.  Pure int16 symmetric formation reaches at most 5598.  With one
operand at 10788, the other may be at most 2905; the existing centered bound
2179 is therefore sufficient.  The asymmetric `10788 x 2179` arithmetic has
final bounds `[4063,9258,11207,28467]`, but the high operand's total sum is
43152, so its `S.sum` formation and Montgomery product need a selective i32
path.  Symmetric `10788 x 10788` additionally produces a c3/r1 bound of 79481
and needs a wide recombination plus final modular reduction.

Selective widening still fails the static execution-shape gate.  Starting
from the already proved 216-instruction native-L01 compute floor, removing
half the input checkpoint and charging only the minimum extra cost of one
16-lane i32 Montgomery chain leaves an optimistic asymmetric floor of 211.
Removing the full input checkpoint and adding the minimum wide chain plus c3
reducer leaves a symmetric floor of 206.  Both already exceed the complete B3
loop's 156 instructions by 55 and 50 respectively, while excluding widening,
horizontal sums, qword routing, register moves, memory, and loop control.
Moving lambda to individual wrapped terms also doubles the three lambda chains
without removing a boundary; pairwise reductions add chains to arithmetic
that is already at Official parity.

No high-range ASM or benchmark is emitted.  Reopening selective widening now
requires it to remove a complete operand-construction or output-routing
network in addition to the checkpoints.  See
`generated/tile4_high_range_bm_gate.json`.

### Terminal transpose-cut L1/L2 gate

The corrected high-range contract makes the two B3 input transposes the next
clean representation target.  This gate keeps the quartic monomial basis,
the 19-chain B3 schoolbook arithmetic, private c3 center, standard AoS output,
I1, and T9 unchanged.  It cuts the existing Forward-to-plane network after
its lane-local word permutation (`L1`) or after its dword-unpack layer (`L2`).
The generator composes the producer prefix with the exact B3 suffix; moving a
shuffle across the store/load boundary is never counted as deleted work.

For each of L0/L1/L2/L3 it covers all 24 register orders, 16 independent
128-bit half orders, and 24 coefficient-label permutations, or 36,864
physical assignments per layout.  Register renames, whole-vector store
placement, factor/lambda table order, and coefficient relabeling preserve the
number of coefficient labels resident in a vector.  L1 retains four labels
per vector and therefore requires the D+Q suffix; L2 retains two and requires
Q; only full L3 is directly coefficient-homogeneous for the unchanged B3
plane ABI.  Neither L1 nor L2 introduces a cross-half repair, Montgomery
chain, range checkpoint, spill, or output-side change.

Per 16-quartic block, the exact producer-plus-B3-input shuffle costs are 28
for canonical L0 and 24 for each of L1, L2, and L3.  Consequently AA/LA/LL
cost 68/64/60 layout shuffles including the unchanged output transpose.
L1/L2 genuinely delete one four-shuffle layer versus an AoS operand, but have
no new static advantage over the existing private full-SoA path.  Benchmark-
only assembly was nevertheless emitted to test whether moving the last layers
between producer and consumer changes the critical path.

All L1/L2 mixed and two-specialized-operand paths pass exact output checks on
the deterministic case and 64 random small-input cases.  In the 2,000-call
post-frontend terminal+B3 gate, L2/L2 saved 49.083 TSC versus AA (19/20 wins,
delta MAD 2.730) and 21.174 TSC versus the existing SA path (18/20 wins,
delta MAD 10.212).  This narrowly passed the local 20-TSC continuation gate.

The full private caller includes both frontends, two terminal cores, B3, I1,
T9, and `crepmod3`, with 32/64-byte scratch placement and normal/reversed link
order.  L2/L2 saves 34.186--46.477 TSC versus AA with 75/80 wins.  Relative to
the already selected asymmetric SA path, however, it saves only
7.540--19.645 TSC with 69/80 wins; the primary placement is 18.361 TSC with
16/20 wins.  It therefore fails the predeclared incremental 20-TSC stability
gate and stops as a benchmark-only local optimum.  No 100,000-iteration run
or production integration is performed.  See
`generated/tile4_terminal_transpose_cut_gate.json`,
`results/tile4-terminal-transpose-cut-short.json`, and
`results/tile4-private-caller-transpose-cut-short.json`.

### Asymmetric SoA/L2 transpose-cut continuation

The symmetric stop does not imply that both operands should use the same
layout.  The follow-up combines the already selected private-SoA producer on
one side with L2 on the other.  `SoA x L2` enters B3 with zero plus four Q
unpacks; `L2 x SoA` is retained as an orientation control because B3 hoists
qinv products only for its A-side registers.  Both candidates keep the same
schoolbook products, 19 Montgomery chains, ranges, c3 center, AoS output, I1,
and T9.  Static producer-plus-consumer accounting is 60 layout shuffles per
block for either orientation, four below SA and tied with L2/L2/full-SoA.

Both orientations pass deterministic and 64-random exact differentials for
the terminal+B3 boundary and for the complete coefficient-polymul caller,
including distinct output, `out==a`, `out==b`, and squaring.  Short local
launches put `SoA x L2` 18.264--21.928 TSC ahead of SA and consistently ahead
of the reverse orientation, but the 20-TSC continuation signal is close to
the noise boundary.

The authoritative caller gate therefore uses two 2,000-iteration launches,
each with 32/64-byte scratch placement and normal/reversed link order.  Across
the resulting 160 paired samples, `SoA x L2` saves 35.403--44.157 TSC versus
AA with 150/160 wins.  Relative to the selected SA path it saves
12.861--21.050 TSC with 144/160 wins.  `L2 x SoA` saves 37.158--41.378 TSC
versus AA with 153/160 wins, but only 12.781--18.499 TSC versus SA.  The
orientation effect is real but neither candidate meets the rule that every
placement save at least 20 TSC over SA.

`SoA x L2` is retained as the worst-case-margin asymmetric transpose-cut
champion, not promoted over SA.  No serious benchmark, public/release symbol,
or production selector change is made.  See
`results/tile4-terminal-transpose-cut-asymmetric-short.json` and
`results/tile4-private-caller-transpose-cut-asymmetric-short.json`.

## Official serialized-leaf correction and first KEM slice

The first real decapsulation integration exposed a semantic hole that the
standalone unpack tests could not detect.  The old serialized mapping treated
an Official `pack.S` internal word as if it were an AoS
`(branch,block,coefficient)` word.  It is instead a coefficient-transposed
unpack position.  In addition, a TILE4 leaf must be selected through the
Official `index[192]` tree and then mapped from logical `k32` to physical
`Q=bitreverse5(k32)`.  The previous tests proved only that the old unpack and
its inverse permutation were self-consistent.

The generator now reconstructs the Official tree and asserts the complete
mapping

```text
serialized slot -> Official leaf/degree
                -> GT (branch,k3,logical-k32)
                -> TILE4 physical Q and AoS word.
```

A direct differential using the same four small-input polynomials now proves
`Official NTT -> poly_tobytes -> TILE4 frombytes` congruent word-for-word to
N5.  Until a new shuffle network is synthesized from this corrected mapping,
the AVX2 unpack keeps fixed control flow but redeposits explicit 16-bit lanes.
Consequently the earlier P1-V decoder timing and direct-SoA/pair decoder gates
are invalidated as performance evidence; the Forward, BaseMul, inverse, and
private-caller arithmetic results are unaffected.

The opt-in `crypto_kem_dec_gt32_candidate` now implements the complete
Official decapsulation DAG with the private `BM e=-1 -> I1 -> T9` first
product and the general `BM e=0 -> Encodeq` recovered-r product.  Eight
deterministic valid rounds, 56 malformed/failure cases, the recovered message
coefficients, recovered-r bytes, return code, and shared secret all match the
frozen Official Main exactly.  The existing 1,000-trial TILE4 regression and
ASan/UBSan suite also pass.  This is a correctness checkpoint only: keypair
and encapsulation remain pending, the semantic decoder is not yet
performance-qualified, no serious benchmark was run, and Official remains the
public selector.

### Correct-semantic Decodeq layout search

The corrected source graph is now used directly rather than routing through
an assumed Official internal word order.  For every serialized lane the
generator records its Official leaf and degree, maps that leaf to
`(branch,k3,k32)`, applies physical `Q=bitreverse5(k32)`, and searches exact
AVX2 half/lane routes to six targets: AoS, L2, coefficient SoA, and the three
quartic pair layouts.  Load-address selection, whole-vector destination
placement, and constant relabeling are free in the cost model; only real
cross-half/lane instructions and stores are charged.

The best exact known networks, excluding the common six AVX2 unpack groups,
cost 1152 instructions for AoS, 512 for L2, 288 for SoA, and 408 for each pair
layout.  The SoA route consists of 96 `vperm2i128`, 96 `vpshufb`, 48 `vpor`,
and 48 stores, uses 20 distinct masks, and is emitted as a fixed-control
benchmark/private symbol.  One hundred canonical and malformed decoder cases
plus the 1,000-trial BaseMul regression prove its words and rejection result
exactly match the corrected semantic map.

The 2,000-iteration short gate gives the following medians in TSC ticks:

| Scope | Official | corrected AoS | corrected SoA |
| --- | ---: | ---: | ---: |
| Decodeq only | 176.509 | 767.019 | 327.283 |

Direct SoA therefore saves a paired median 446.504 TSC versus the current
correctness-first AoS decoder with 20/20 wins.  For
`2 x Decodeq -> BaseMul_scale -> I1 -> T9 -> crepmod3`, AA is 3289.064,
the real-decapsulation orientation `c(AoS) x f(SoA)` is 2758.329, and
isolated SS is 2233.788.  SS is not the real caller winner: decapsulation
must preserve `c` in AoS for the later `c-m` edge.  Charging the necessary
third decode raises SS to 2985.441, so the selected caller contract is SA.
It saves a paired median 527.905 TSC versus AA with 20/20 wins.

Only `f` was switched to corrected semantic SoA in the opt-in KEM candidate;
`c` and `hinv` remain AoS.  The full eight-round/56-failure byte-exact gate,
the 1,000-trial regression, and ASan/UBSan still pass.  A same-binary valid
decapsulation short test is nevertheless negative: Official is 12064.122
TSC and the GT32 candidate is 16854.764 TSC, a paired 4692.295 TSC regression
with 0/20 GT wins.  Thus the decoder-layout gate passes locally and is
correctly integrated, but backend promotion remains blocked by the remaining
decapsulation DAG.  No 100,000-iteration serious benchmark was run.

Artifacts are `generated/tile4_correct_semantic_decoder_gate.json`,
`generated/tile4_frombytes_semantic_soa_routes.inc`,
`results/tile4-correct-semantic-decoder-short.json`, and
`results/tile4-kem-decap-candidate-short.json`.

### Decapsulation differential closure and SoA-domain Encodeq

The full-decapsulation attribution corrects an earlier inference from the
composite decoder-plus-first-product benchmark.  The first native
`BaseMul_scale -> inverse -> crepmod3` region is not 528 TSC faster than
Official when measured directly: it is about 18.526 TSC slower in the final
SoA-domain candidate.  The original saving belonged primarily to replacing
the correctness-first decoder.  Before the encoder rewrite, the dominant
cost was the scalar GT-to-byte boundary: recovered-r `tobytes` and the final
Forward-plus-`tobytes` together contributed roughly 3.46k TSC of differential
cost.

The corrected semantic map is now searched in the reverse direction for
AoS, L2, coefficient SoA, and all three pair layouts.  The target is the 48
coefficient-transposed vectors consumed by the unchanged Official `pack.s`;
canonicalization and 12-bit packing stay in Official code.  In the fixed
load/half-select/zeroing-shuffle/OR network class, the materialized route
costs are 1536 instructions for AoS, 656 for L2, 384 for SoA, and 608 for
each pair layout.  The SoA champion has exactly two routes per output vector
and is emitted as a fixed-address, spill-free AVX2 bridge.

The new private decapsulation island keeps `c`, `f`, `mhat`, and `hinv` in
correct-semantic coefficient SoA.  It uses SS `BaseMul_scale`, a private-SoA
Forward for `m`, an in-layout subtraction, and SS general BaseMul with SoA
e=0 output.  Both recovered-r and the final randomness check route through
the generated bridge and then the unchanged Official `poly_tobytes`.  Its
scratch liveness is reduced from eight to five polynomials; this reduction
is correctness-neutral but did not produce measurable short-run speedup.

The 2,000-iteration, 20-sample valid-decapsulation short gate is:

| Candidate | Median TSC | Delta vs Official |
| --- | ---: | ---: |
| Official | 12021.366 | -- |
| previous GT SA | 16808.825 | +4726.889 |
| GT persistent SoA + direct Encodeq | 12661.119 | +586.767 |

The new candidate saves 4119.494 TSC versus SA with 20/20 wins and remains
byte-exact for eight valid rounds and 56 malformed/failure cases.  This is a
major integration pass but not promotion: it is still about 4.9% slower than
Official in this short gate, and no 100,000-iteration benchmark was run.

Direct native-cost attribution explains 318.747 of a contemporaneous
586.562 TSC full gap.  The measured phase deltas are +152.257 for decoding
`c/f`, +74.424 for decoding `hinv`, +18.526 for the first product/inverse,
-56.393 for Forward(m), -0.140 for subtraction, -13.239 for general BaseMul,
+99.773 for recovered-r Encodeq, and +43.540 for final Forward-plus-Encodeq.
The remaining approximately 268 TSC is context/glue/cache/code-placement
sensitive; the 45.7% closure error is explicitly inconclusive for fine-grain
optimization attribution.  The next defensible targets are the corrected
semantic SoA decoder and the two direct Encodeq routes, with caller-region
measurement before any further kernel rewrite.

Artifacts are `generated/tile4_correct_semantic_encodeq_gate.json`,
`generated/tile4_soa_to_official_routes.inc`,
`results/tile4-decap-phase-attribution-short.json`, and
`results/tile4-kem-decap-candidate-short.json`.

### Decodeq/glue/Encodeq boundary reduction gate

All full-caller comparisons in this gate use the median of paired deltas;
subtracting the two standalone medians is not treated as an authoritative
delta.  No 100,000-iteration serious run was made.

The first decoder experiment shares the low mask, malformed-input
accumulator, and AVX/SSE transition across the three corrected-semantic SoA
decodes used by decapsulation.  It remains byte-exact, but a direct
same-binary control saves only 1.712 TSC with 3.210 TSC MAD and 13/20 wins.
The boundary is therefore retained for its simpler caller contract, not as a
performance result.  A single corrected-semantic SoA decode is still about
77.083 TSC slower than Official; the cost is in the common 12-bit unpack plus
the exact 96 `vperm2i128`, 96 `vpshufb`, and 48 `vpor` semantic route.  A
future decoder continuation must jointly synthesize unpack and semantic lane
placement rather than merely merge calls.

The small glue ladder also stops cleanly.  Unnecessary zero initialization of
four stack byte buffers was removed because all bytes are defined before use,
but its latest same-binary control is inconclusive (-54.581 TSC with 129.269
TSC MAD).  Specializing the generic KEM core to turn two indirect dispatches
into direct calls is worse and placement-sensitive; the final control is
206.890 TSC slower with only 4/20 wins.  The selected candidate therefore
keeps the smaller generic core and does not proceed to a monolithic wrapper.

Encodeq E1 has a real acceleration mechanism.  Two Official pack-input
vectors share the same selected SoA source halves and differ only in their
`vpshufb` masks.  The generator now hoists those loads and half selections,
reducing the materialized bridge from 384 to 288 instructions.  The grouped
bridge saves 34.468 TSC per Encodeq call with 0.500 TSC MAD and 20/20 wins,
while preserving the unchanged Official canonical reduction and 12-bit pack.
It is the selected KEM candidate path.

E2 directly generates each eight-vector Official pack batch in registers and
copies the Official reduction/packing DAG, eliminating 48 bridge stores and
48 pack reloads.  It is correct but saves only 2.986 TSC locally, while its
unrolled symbol is 5,160 bytes.  A full short run regressed to a paired
+560.060 TSC gap.  E2 is therefore build-only research evidence and is
excluded from the normal candidate binary.

With the E1 bridge and generic core selected, the latest 2,000-iteration,
20-sample short gate is:

| Candidate | Median TSC | Paired delta vs Official |
| --- | ---: | ---: |
| Official | 12044.095 | -- |
| GT32 persistent SoA + grouped Encodeq | 12389.215 | +326.944 |

The remaining short gap is about 2.71%, with 77.908 TSC paired MAD and only
1/20 GT wins, so it does not meet the at-most-2% serious-benchmark gate.
Updated phase reconstruction explains 233.088 of 326.944 TSC; its 28.7%
closure error is much smaller than the previous 45.7% but is still not a
fine-grained closure.  Decodeq contributes +228.989 TSC and is now the only
large repeated kernel debt.  Arithmetic remains near parity or favorable,
and further Encodeq materialization removal has been stopped by E2.

Artifacts are `results/tile4-correct-semantic-decoder-short.json`,
`results/tile4-kem-decap-candidate-short.json`,
`results/tile4-kem-decap-candidate-e2-direct-pack-short.json`, and
`results/tile4-decap-phase-attribution-short.json`.

### GT32-POLY-LAYOUT-ABI-001 global placement screen

The optimization boundary is now the complete polynomial subsystem rather
than an isolated decoder or NTT kernel.  SHAKE, randombytes, KEM control flow,
verification, shared-secret selection, and generic protocol semantics remain
fixed.  The first global ABI layer keeps coefficient planes, B3 schoolbook
arithmetic, Montgomery policy, and the NTT32 arithmetic DAG fixed, and changes
only the quartic leaf assignment to group/vector/lane positions.

The generator exhausts all 120 permutations of the five logical-k32 bit axes
and all 32 XOR masks.  The 720 `(branch,k3)` tile permutations are collapsed
because they are exactly whole-vector destination and constant-table
relabelings.  Thus 3,840 enumerated representatives cover 2,764,800 physical
ABIs.  Corrected Official leaf semantics are used throughout.  Every candidate
is charged for grouped Decodeq routes, Forward terminal placement, the inverse
entry, unchanged lane-wise SoA BaseMul compatibility, grouped Encodeq routes,
register/source pressure, and the real keygen/encap/decap multiplicities.

The current private-SoA map is `bits-21430-xor-00`: physical bits low-to-high
select logical-k32 bits `[2,1,4,3,0]`.  Its layout-variable instruction model
is 2016 for decap, 1440 for encap, and 1440 for keygen.  Six zero-terminal-debt
axis classes tie these totals; none improves any caller over the current map.

The unconstrained static minimum, `bits-12403-xor-00`, reduces Decodeq from
288 to 216 and Encodeq from 288 to 264 instructions, but moves logical bit 3
into the group coordinate.  It therefore mixes both current Forward groups in
all 48 vectors and incurs a 48-instruction terminal/inverse repair lower bound,
with possible materialization beyond that floor.  Its modeled deltas are -120
instructions for decap, -24 for encap, and **+24 for keygen**.  It is not a
global ABI candidate and no assembly is emitted.

This is a first-layer hard stop, not a claim that every custom polynomial ABI
is exhausted.  Pure bit-affine leaf placement has no zero-terminal-debt global
improvement and cannot support the 10% decapsulation goal.  Reopening requires
a second-layer mechanism: hybrid SoA/qword storage, a quartic degree-lane
change, a different scale domain, or direct CBD/SOTP deposition.  Full static
accounting and the Pareto front are in
`generated/tile4_poly_layout_abi_gate.json`.

### GT32-POLY-ABI-002-003 topology and typed-terminal closure

The second ABI gate tests the two mechanisms left open by ABI-001 without
repeating the universal affine-placement screen.  It promotes each physical
Q placement to a semantic coordinate system, conjugates the complete
32-point transform as `P * NTT32 * P^-1`, and regenerates physical-order
forward/inverse edges, execution-order twiddles, quartic lambda streams, and
T9 source routes.  Exact 32-by-32 matrices prove the forward DFT, inverse
round trip (`I * F = 32`), and all 192 CRT leaves; all four quartic degrees
give 768 exhaustive semantic basis cases per candidate.

For the six best unconstrained wire placements, topology-native Forward and
inverse preserve the current 16 Montgomery vector chains per tile, require at
most 15 YMM registers, and have no spill.  The best caller model is 1800
layout-variable instructions for decap, 1320 for encap, and 1368 for keygen,
so all three numeric caller thresholds pass.  T9 still needs 48 cross-half
repairs, however, versus the gate of at most 24.  The exact routes can be
fused into T9 loads and do not require a standalone materialization pass, but
their instruction count alone stops Phase A before assembly.

Phase B fixes `W=bits-12403-xor-00` and `M=bits-21430-xor-00`.  Every W/M
target is one exact `vperm2i128` from at most two source vectors, so SUB and
specialized B3 operand loads can absorb alignment without a global W/M pass.
This is exactly four added shuffles per 16-quartic block and passes the local
operator gate.  The caller-weighted decap cost is nevertheless 1848, only 168
instructions below current M and short of the required 192; encap does not
regress.  No mixed-operator assembly is emitted.

Phase C enumerates 17 heterogeneous 128-bit-half packet topologies: three H2
pairings, six `1+1+2` partitions, and eight oriented `1+3` partitions.  For
each I and P endpoint it independently exhausts all 24 within-16 Q bit orders
for each degree plane, or 5,640,192 layouts per endpoint.  Uniform layouts,
the old bit1/bit2 P layout, pair-basis/K2 variants, and XOR reruns remain
excluded.  The best I is a `1+1+2` packet requiring 24 instructions and saves
120 versus the current inverse transition.  The best P uses the analogous
wire order and needs 48 formation plus 228 fused route/store instructions to
produce the unchanged 48-vector Official `pack.s` input, saving 12 per P
transition.  The weighted decap saving is therefore 144, below the required
192.  It adds no Montgomery chain/checkpoint, spills no registers, and its
estimated reusable P symbol is 1380 bytes, but the savings gate still stops
assembly.

All representation changes are leaf/degree permutations, so the generated
scale proof preserves Forward `e=0`, BMscale/I `e=-1`, BMgeneral/P `e=0`, and
the final inverse `e=0`, together with the existing range bounds and c3
centering policy.  Because no phase passed its static assembly gate, no new
production symbol or benchmark was produced; the 20-TSC/18-of-20 cycle gate
was not invoked.  The unchanged implementation still passes the 1,000-trial
mapping/Forward/BaseMul/inverse/alias/round-trip suite and the existing eight
valid plus 56 malformed/failure KEM byte-exact cases.  Reopen only with a
T9-native mapping at or below 24 repairs,
a W/M operator that beats four shuffles per block and reaches 192 weighted
decap savings, a typed P route that lifts the combined saving above 192, or a
genuinely new degree/scale/terminal algebra mechanism.

Run `make poly-abi-v2` to regenerate:

- `generated/poly_abi_v2_candidates.json`
- `generated/poly_abi_v2_callgraph_cost.json`
- `generated/poly_abi_v2_topology_proofs.json`
- `generated/poly_abi_v2_packet_routes.json`

### GT32-TRANSPOSE-REDEPOSIT-001

This gate keeps the current semantic leaf placement, private coefficient-SoA
B3 representation, Montgomery scale/range contract, and NTT32 arithmetic DAG.
It asks whether the final transpose can be paid by destination addresses or
by a different register network, rather than opening another polynomial ABI
search.

The exact chunk-purity proof closes the small-store variants before assembly.
Normal TILE4 AoS and raw Stage-5 pair-packed data are destination-pure only at
2-byte granularity.  L1 first becomes pure at 4 bytes.  L2 first becomes pure
at 8 bytes, but therefore needs 16 stores per 16-quartic block, plus extraction
and four-YMM consumer reconstruction; it exceeds the eight-store qword gate.
Only the completed L3 private SoA planes are address-only at 32 bytes.  There
is no eligible 16-byte T2 candidate.

The exact four-vector search finds two alternative 12-instruction networks:

```text
Stage5 packed: 4 vpshufb  + 4 vshufps + 4 vshufps
normal AoS:    4 vpunpckw + 4 vshufps + 4 vshufps
```

Both are bit-exact, depth three, use no extra mask, add no Montgomery chain,
and spill no register.  They replace the current second and third unpack
layers, but do not reduce instruction count.  Accordingly both were emitted
only as T1 port/dependency-shape probes.  A partial next-block T3 is rejected
statically: B3 keeps four A planes, four A-qinv planes, four B planes, one
accumulator, two temporaries, and q live (all 16 YMM); even the smallest next
terminal fragment raises the proved peak to 18 and requires a spill or
scratch boundary.  The old streaming-B experiment is not repeated.

The short benchmark uses 2,000 calls per sample, 20 paired AB/BA samples, two
warm-ups, CPU 1, 32- and 64-byte scratch alignment, and both T1-before-T0 and
T0-before-T1 symbol placement.  Each configuration first runs 1,000 random
bit-exact terminal and full polynomial-slice trials.  Representative paired
T1-minus-T0 medians are:

| Placement / alignment | AoS transpose + BM | two AoS transposes + BM | Forward + BM | 2 Forward + BM | decap polynomial slice |
| --- | ---: | ---: | ---: | ---: | ---: |
| normal / 64 | +0.901 | +0.655 | +0.873 | -2.126 | +3.096 |
| normal / 32 | -0.063 | +0.415 | -0.406 | -1.145 | +1.116 |
| reversed / 64 | -0.075 | +0.016 | -1.923 | -1.785 | +0.180 |
| reversed / 32 | -0.142 | +0.035 | +1.536 | -1.725 | -4.335 |

Neither T1 reaches the 10-TSC one-producer or 15-TSC two-producer threshold,
and neither approaches 18/20 stable wins across alignments and placements.
This is a hard stop for the current port-shape substitution: fewer independent
materialization boundaries are not available, and an equal-count VSHUFPS DAG
does not survive the B3 consumer boundary.  No PMU, 100k serious benchmark,
or production integration is run.

Artifacts:

- `generated/tile4_transpose_redeposit_gate.json`
- `results/tile4-transpose-redeposit-short.json`

Reopen only if a 16-byte-pure cut needs at most eight stores with lower total
producer/consumer uops, a B3 schedule frees at least two YMM without
recomputation, or a genuinely new terminal-consumer DAG is found that is not
equivalent to the rejected streaming-B schedule.

### GT32-AOS-DOT-REDC16-001

This bounded experiment reopens only A1's final reduction.  The TILE4 AoS
layout, D0--D3 `vpmaddwd` dot products, lambda semantics, `e=0 x e=0 -> e=-1`
scale, and I1/T9/`crepmod3` consumers are unchanged.  R0 is the compiler's
two-`vpmulld` Montgomery32 finalizer.  R1 forms
`m = low16(x*qinv)` with `vpmullw`, obtains the high half of `m*q` with a
16-bit multiply, subtracts it from `x>>16`, and packs the valid even words
directly into AoS output.

The generator exhausts all 65,536 low words.  Unsigned R1-U is bit-exact to
R0.  Signed R1-S differs from R0 by exactly zero or `q`, hence is mod-q exact.
Exact interval propagation gives BM coefficient bounds
`[6188,7645,9103,10560]` for R1-U and `[4460,5917,7374,8831]` for R1-S.
After all five I1 layers the worst bounds are 28,592 and 24,913 respectively,
so both stay within signed int16 without a new checkpoint.  The assembly uses
15 YMM registers, no stack, spill, scratch, secret-dependent address, or
`vpmulld`; D and pack masks plus q/qinv remain resident, and the two REDC16
chains are interleaved.

Both normal and reversed-link-order binaries pass 1,000 boundary/random
trials.  R1-U intrinsic and assembly are bit-exact to R0, R1-S intrinsic and
assembly are bit-exact to each other, both alias directions pass, and I1,
T9, canonical mod-q output, and `crepmod3` remain exact at their contracts.
ASan/UBSan and the unchanged 1,000-trial global GT32 suite also pass.

The authoritative short run uses 2,000 calls, 20 paired AB/BA samples, two
warm-ups, CPU 1, and no 100k serious run:

| Placement | R1-U BM | saving vs A1 | wins | paired vs B3 | BM+I1 paired vs B3 | BM+I1+T9+crepmod3 paired vs B3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| normal | 400.062 TSC | 114.282 | 20/20 | -47.073 | -50.421 | -52.443 |
| reversed | 408.543 TSC | 126.558 | 20/20 | -50.607 | -52.097 | -65.903 |

R1-U therefore clears the 70-TSC/18-of-20 continuation gate, the 450-TSC
family gate, and the 430-TSC Forward-terminal extension gate in both
placements.  It does not clear the historical standalone target of 397.222
TSC, but its A1-paired BM+I1 medians are 625.478 and 625.032 TSC, so both
placements clear the historical 628.798 composite target.  R1-S also clears
that target, but is not selected over bit-exact R1-U without a serious result.
Both variants beat same-binary B3 and B3+I1 by roughly 47--52 TSC.

The authorized serious run uses 100,000 calls for each of the same 20 paired
samples, again with normal and reversed placement.  GCC is 15.2.0 and CPU 1
was pinned under the `powersave` governor.  Its R1-U results are:

| Placement | R1-U BM | saving vs A1 | wins | paired vs B3 | BM+I1 | BM+I1 paired vs B3 | full private consumer paired vs B3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| normal | 400.235 TSC | 115.553 | 20/20 | -49.410 | 627.474 | -51.746 | -51.119 |
| reversed | 397.526 TSC | 132.488 | 19/20 | -51.363 | 625.590 | -52.250 | -52.003 |

The serious result preserves the short-run conclusion.  Standalone R1-U does
not beat the historical 397.222 target in both placements, but BM+I1 is below
628.798 in both.  It also beats same-binary B3, B3+I1, and the complete
I1/T9/`crepmod3` private consumer with 20/20 wins in both placements for all
three paired B3 comparisons.  R1-S also passes, but R1-U remains selected
because its output representative is bit-exact to R0.

The decision is now
`pass-serious-R1-U-AoS-scale-BM-primitive-qualified-not-KEM-selected`.
R1-U remains a benchmark-only symbol: the serious run qualifies the primitive
when its operands are already TILE4 AoS, but does not prove that a KEM caller
can produce those operands cheaply.  The public and production selectors are
unchanged.  The next gate must therefore include the real Decodeq or Forward
producer.  Reopen the rejected R0 path only with a different reduction
primitive; do not return to generic 32-bit Montgomery scheduling.

Artifacts:

- `generated/tile4_aos_dot_redc16_gate.json`
- `generated/tile4_aos_dot_redc16_constants.inc`
- `results/tile4-aos-dot-redc16-short.json`
- `results/tile4-aos-dot-redc16-serious.json`

#### Official Main core-cycle comparison

The promoted short candidate was also compared directly with the frozen
Official Main objects in the same binary using hardware
`cpu_core/cycles`.  Each backend/gate uses one million calls, three repeats,
alternating backend order, CPU 1, and normal plus reversed link placement.
The event ran at 99--100%, so it was not materially multiplexed.  These are
actual PMU core cycles, not TSC ticks.

| Placement | Gate | Official Main cycles | GT32 R1-U cycles | GT minus Official | GT delta |
| --- | --- | ---: | ---: | ---: | ---: |
| normal | BaseMul | 428.097 | 633.525 | +205.428 | +47.986% |
| normal | BaseMul + inverse | 1180.210 | 1359.787 | +179.577 | +15.216% |
| normal | 2 Forward + BM + inverse | 2735.261 | 2748.537 | +13.276 | +0.485% |
| normal | full + `crepmod3` | 2935.420 | 2946.896 | +11.475 | +0.391% |
| reversed | BaseMul | 429.432 | 639.036 | +209.604 | +48.810% |
| reversed | BaseMul + inverse | 1175.882 | 1361.063 | +185.181 | +15.748% |
| reversed | 2 Forward + BM + inverse | 2733.270 | 2749.234 | +15.964 | +0.584% |
| reversed | full + `crepmod3` | 2923.494 | 2933.744 | +10.251 | +0.351% |

Subtracting the separately measured medians gives useful, but non-paired,
phase attribution.  In normal placement the inverse portion recovers about
25.851 cycles and the two Forward/copy portion recovers about 166.301 cycles;
these offset most, but not all, of the 205.428-cycle BaseMul debt.  Reversed
placement gives the same shape: inverse saves about 24.423 and the two
Forward/copy portion saves about 169.217 cycles against a 209.604-cycle
BaseMul debt.  The remaining complete-chain loss is therefore 13--16 core
cycles, approximately 0.5%.

The core-cycle decision is
`GT32-R1U-full-polymul-not-stably-faster-than-Official-Main`.  This does not
invalidate the R1-U promotion over the previous GT B3 implementation; it says
that the current complete GT polynomial chain is still fractionally behind
Official Main in actual core cycles.  It is not a full keygen/encap/decap KEM
comparison because R1-U has not yet been integrated into those callers.

Artifact: `results/tile4-aos-dot-redc16-official-cycles.json`.

### GT32-AOS-DOT-REDC16-CALLSITE-001

This short gate tests R1-U at the actual first decapsulation product rather
than treating its AoS inputs as free.  The control uses the current combined
three-input corrected-semantic decoder to keep `c`, `f`, and `hinv` in the
persistent private SoA ABI, then runs the SoA x SoA scale-B3, I1, T9, and
`crepmod3`.  The candidate uses a benchmark-only combined decoder that emits
`c/f` in TILE4 AoS for R1-U while keeping `hinv` bit-exact in private SoA for
the later general product.  Both share one rejection accumulator, one mask
setup, and one AVX/SSE transition; no three-call decoder penalty is hidden in
the candidate.

Both link placements pass 1,000 valid end-to-end first-product trials, exact
`hinv` persistence, and malformed canonicality checks in each of the three
serialized inputs.  The 2,000-call, 20-sample ABBA/BAAB short result is:

| Placement | Region | SoA control | R1-U candidate | candidate - control | wins |
| --- | --- | ---: | ---: | ---: | ---: |
| normal | combined three-input decoder | 513.810 | 1185.922 | +669.707 | 0/20 |
| normal | BM + I1 + T9 + `crepmod3` | 873.891 | 967.400 | +94.297 | 0/20 |
| normal | full first-product state | 1382.305 | 2140.739 | +750.740 | 0/20 |
| reversed | combined three-input decoder | 519.346 | 1178.496 | +658.576 | 0/20 |
| reversed | BM + I1 + T9 + `crepmod3` | 874.156 | 969.502 | +95.085 | 0/20 |
| reversed | full first-product state | 1381.540 | 2139.066 | +750.360 | 0/20 |

The result is a hard callsite stop.  R1-U's approximately 51-TSC serious win
over AoS B3 does not transfer to the persistent-SoA decapsulation primitive:
the native SoA x SoA scale-B3 consumer is itself about 94--95 TSC faster than
R1-U's AoS chain, and the corrected-semantic AoS deposit adds another
659--670 TSC.  The primary full state loses about 750 TSC with 0/20 wins in
both placements, far beyond the serious continuation threshold.  No 100k or
production integration is run.

Decision: `stop-R1-U-decap-integration-decoder-debt`.  This does not demote
R1-U as an AoS-input primitive; it fixes its dispatch domain.  R1-U may be
reused only where both operands are already TILE4 AoS (notably a Forward-native
synthetic/caller gate), or when a new wide corrected-semantic AoS decoder
removes the scalar `vpextrw` deposit debt.  The current persistent-SoA decap
island remains selected.

Artifact: `results/tile4-aos-dot-redc16-callsite-short.json`.

The same binary also runs the separate native-provenance control requested by
the dispatch model:

```text
2 x coefficient-order Forward -> TILE4 AoS
-> B3 or R1-U -> I1 -> T9 -> crepmod3
```

Here R1-U does transfer its primitive advantage.  Normal placement improves
from 1826.271 to 1771.566 TSC (paired -55.154, MAD 1.954, 20/20 wins), and
reversed placement improves from 1832.403 to 1777.707 TSC (paired -52.350,
MAD 2.351, 20/20 wins).  This is
`short-pass-Forward-native-R1-U-await-serious`: it confirms that dispatch by
operand provenance is the correct model, but it is not yet a 100k result and
does not authorize terminal-register fusion.

The authorized Forward-native serious closure uses 100,000 complete chain
calls in each of 20 ABBA/BAAB paired samples and the same two link placements:

| Placement | B3 control | R1-U | paired delta | paired MAD | wins |
| --- | ---: | ---: | ---: | ---: | ---: |
| normal | 1836.089 | 1776.666 | -60.664 | 7.835 | 20/20 |
| reversed | 1841.238 | 1779.022 | -58.503 | 7.248 | 20/20 |

Both placements clear the 40-TSC, 18/20-win, and MAD-below-saving gates.  The
decision is
`pass-serious-Forward-native-R1-U-specialized-chain-qualified`.  The same
implementation is now exposed internally through the typed alias
`gt32_tile4_basemul_scale_ff_aos_r1u_asm`, where `ff` means both operands are
the e=0 TILE4 AoS outputs of GT32 Forward.  The alias is not a generic
BaseMul selector and no current NTRU+ KEM callsite is changed.  Decodeq/SoA
integration remains hard-stopped, and terminal-register fusion remains a
separate future experiment.

Artifact:
`results/tile4-aos-dot-redc16-forward-native-serious.json`.

### GT32-ENCAP-MIXED-AOS-SOA-BM-001

This generator-only gate evaluates the new provenance orientation rather than
rerunning the old encapsulation experiment.  The old gate used decoded
`h_AoS` with Forward-produced `r_SoA`; this candidate keeps corrected-semantic
decoded `h` in private SoA and keeps Forward-produced `r/m` in TILE4 AoS.  Its
desired arithmetic edge is `h_SoA x r_AoS -> c_AoS` at general `e=0` scale.

The arithmetic is legal, but the complete encapsulation DAG has two mandatory
wire boundaries which the isolated mixed-BM description omits:

```text
Forward(r) -> Encodeq(rhat) -> G
BMgeneral(hhat,rhat) + Forward(m) -> Encodeq(chat)
```

Under the corrected semantic mapping, private SoA is pack-native and TILE4
AoS is not.  The existing exact fixed-network proof needs 1,536 route
instructions per AoS polynomial, versus 288 for the grouped materialized SoA
route or 240 for direct SoA-to-pack routing.  Thus two AoS Encodeq boundaries
add at least 2,496 instructions relative to the conservative grouped-SoA
control.  Even granting the candidate three complete 12-shuffle layers over
all twelve 16-quartic blocks (an intentionally generous 432-instruction
credit), the optimistic result is still a 2,064-instruction regression.

The existing `gt32_tile4_basemul_general_soa_aos_to_aos_asm` does not supply a
new mechanism: it transposes the AoS operand inside B3 and returns the same
wire-hostile AoS output.  Consequently this experiment stops before new ASM
or cycle benchmarking with
`static-hard-stop-before-assembly-AoS-wire-boundary-debt`.

This does not reject mixed-source general multiplication.  It narrows the
viable typed target to a dual-use/packet representation: `rhat` must remain
pack-native for its first Encodeq while feeding the mixed BM, and the BM plus
`mhat` output must land directly in private SoA or Official pack-input `P`.
Reopen only with that producer/consumer mechanism, or with a new AoS direct
encoder that removes at least 1,032 route instructions per encoded polynomial.

Artifact: `generated/tile4_encap_mixed_aos_soa_gate.json`.

### GT32-KEYGEN-FJ1-P0-001 — Phase A

The first key-generation typed-representation gate proves that BaseInv can
produce `J1`, an inverse in TILE4 AoS with Montgomery exponent `e=1`, without
an extra scale pass.  With Forward input `F0` at `e=0`, the existing quartic
formula has numerator `e=-2` and determinant `e=-3`.  The standard batch
inverse returns the determinant inverse at `e=3`, so its final recovery gives
an `e=0` inverse.  Replacing only the field-inversion addition chain's final
fixed factor,

```text
Mont(prefinal, R^-1) -> Mont(prefinal, ordinary 1)
```

shifts every recovered determinant inverse from `e=3` to `e=4`; the backward
batch-recovery loop preserves that extra `R`, and final BaseInv recovery lands
at `J1 e=1`.  The instruction count and control/address trace are unchanged.
Consequently the R1-U finalizer has the desired general-product scale directly:
`F0 e=0 x J1 e=1 -> P0 e=0`, since `0+1-1=0`.

The generator checks all 192 physical leaves with all 81 quartics over
coefficients `{-1,0,1}` (15,552 leaf/quartic cases), exhaustively checks the
field-inversion final-factor identity for all 3,456 nonzero field elements,
and checks 64 fixed-shape batch inversions plus targeted zero positions.  The
zero detection, whole-output zero mask, alias requirements, and keygen retry
semantics remain unchanged.  Conservative range accounting gives a maximum
BaseInv add/sub bound of 12,337, below signed int16, and a worst F0 x J1
four-term dot accumulator of 76,594,800, below signed int32.

Phase A therefore passes with
`phase-A-pass-J1-zero-pass-continue-to-FJ-P0-route-synthesis`.  This is not yet
an assembly or performance result: the TILE4 AoS BaseInv schedule and the
route from R1-U's degree-separated REDC16 intermediates into the 48-vector
Official `pack.S` input still need synthesis.  A candidate may not materialize
ordinary TILE4 AoS and then pay the known complete AoS-to-P route.

The Phase-B packet precheck also fixes the physical granularity of that next
search.  Every `(R1 source vector, coefficient)` group sends its four values
to two P0 targets, and every P0 vector draws from eight R1 source vectors.
However, each TILE4 tile maps exactly to one contiguous eight-vector pack
batch (in batch order `0,5,2,4,1,3`).  Therefore a single-loop epilogue cannot
deposit a contiguous P fragment; the smallest coherent producer is an entire
eight-source tile.  The known constructive routing shapes are 240
instructions for ideal degree packets, 384 if eight AoS results could stay
live, and 480 with an eight-vector tile scratch, versus 1,536 for the forbidden
full materialized AoS route.  Current R1-U peaks at 15 YMM and cannot retain
eight outputs, so Phase B remains an assembly-scheduling gate rather than an
automatic pass.

Artifact: `generated/tile4_keygen_fj1_p0_gate.json`.

### GT32-KEYGEN-FJ1-P0-ASM-001 — bounded probe

Phase B emitted two benchmark-only, noalias leaves that compute the complete
typed edge `F0 AoS e=0 x J1 AoS e=1 -> P0 e=0` without materializing an
intermediate AoS product polynomial.  S0 redeposits two-word fragments after
each R1-U source vector.  S1 retains four source vectors, performs one
register-resident 4x4 transpose, and writes four half-tile degree packets.
Generator simulation proves every one of the 768 word routes; 1,000 runtime
boundary/random trials are bit-exact to R1-U plus the semantic reference map
and to the unchanged Official pack output.  Both leaves are spill-free and do
not contain `vpmulld`; text sizes are 384 bytes (S0) and 1,085 bytes (S1).

The same-binary 2,000-iteration short gate measured the complete
`F0 x J1 -> P0 -> Official pack` edge:

| placement | control | S0 | S0-control | S1 | S1-control |
| --- | ---: | ---: | ---: | ---: | ---: |
| normal | 628.661 | 773.589 | +145.540 | 661.877 | +34.892 |
| reversed | 629.109 | 776.078 | +146.488 | 663.619 | +33.947 |

S0 and S1 both won 0/20 samples in both placements.  Excluding the unchanged
pack does not reverse the result: route-only S0 is slower by 130.907/134.488
TSC and route-only S1 by 32.344/32.955 TSC.  The result is therefore a hard
stop for the family that forms complete AoS quartics and then converts or
materializes P0.  Standalone BaseInv J1 assembly is paused because this family
does not supply a profitable consumer.  This result does not by itself reject
a consumer-native path starting directly at the post-REDC `c01/c23` packets.
No production selector or KEM callsite was changed.

Artifacts: `generated/tile4_keygen_fj1_p0_routes.inc` and
`results/tile4-keygen-fj1-p0-asm-short.json`.

### GT32-R1U-PACKET-PACK-GATE-001

The follow-up static gate starts at R1-U's two post-REDC packets and forbids
the three operations that made S1 misleadingly broad: compacting each source
to a complete AoS quartic, running the full four-vector transpose, and
materializing the 48-vector P0 polynomial.  The generated mapping proves that
each `c01` or `c23` packet contains eight useful words for four P targets and
that four R1 sources provide exactly one half of all eight vectors in a pack
batch.

A constructive four-source packet route costs 24 instructions per half: eight
lane-local packet shuffles and two eight-instruction 4x4 dword transpose
networks.  It can stream each half without P0, but AVX2 then loses the
full-width pack's free second 128-bit lane.  Even an optimistic half-pack floor
is 76 instructions: 48 canonicalization/sign-fix operations, 16 operations to
form 12-bit pairs, at least six byte compactions, and six stores.  Across six
tiles the best known boundary-free schedule is therefore 1,200 instructions,
versus 1,284 for the complete measured S1 edge shape: only 84 instructions of
static credit against the observed requirement to recover about 34 TSC.

Keeping the first eight P halves live does not close the gap: they leave seven
registers for the split R1 computation but only one free register, while each
second-half source produces two packets that must survive until a four-source
transpose.  The alternatives are a forbidden P-half scratch, S0-like
source-serial insertion, or recomputing the shared R1 prefix.  Consequently no
third ASM is emitted.

The decision is narrowly
`static-stop-before-third-ASM-no-credible-34-TSC-margin`.  It closes the known
half-stream schedule, not every possible packet-native mechanism.  Reopen if
REDC and 12-bit packing are replaced by one DAG that forms both halves without
eight persistent targets, recomputation, or materialization.  The larger
keygen reopen remains BaseInv denominator/adjugate quotient finish directly to
pack-native output; Forward(f) dual F0/pack output and wider SIMD remain valid
alternatives.

Artifact: `generated/tile4_r1u_packet_pack_gate.json`.

### GT32-BM-SOA-DOT-REDC16-001

The first kernel-first experiment ports R1-U's exact-int32 dot-product and
unsigned high-word REDC16 to the persistent private SoA representation.  It
keeps the existing physical-Q order and computes `SoA e=0 x SoA e=0 -> SoA
e=-1`; no AoS input transpose, `vpmulld`, stack, or vector spill is present.
The implementation precomputes `lambda*B1..B3`, forms the six reusable B pair
patterns, executes two `vpmaddwd` products per coefficient and half, and
reduces each completed int32 accumulator once.

Correctness passes 1,000 zero, maximum-bound, alternating, and random trials
against the existing private-SoA arithmetic, current I1 input, I1 core, and T9
tail modulo q.  The short 2,000-iteration gate is nevertheless a decisive
regression:

| placement | region | control | dot/REDC16 | delta | wins |
| --- | --- | ---: | ---: | ---: | ---: |
| normal | arithmetic | 257.931 | 350.798 | +92.905 | 0/20 |
| reversed | arithmetic | 257.395 | 341.183 | +83.766 | 0/20 |
| normal | BM+I1+T9 | 751.926 | 847.415 | +96.160 | 1/20 |
| reversed | BM+I1+T9 | 751.966 | 847.388 | +94.144 | 0/20 |

The static shape explains why the AoS R1-U result does not transfer to SoA.
The new symbol contains 178 instructions versus 123 for the existing raw SoA
arithmetic control.  Sixteen leaves require separate low/high dword chains for
every coefficient, followed by even-word compaction and lane-order repair.
Thus reducing the mathematical Montgomery-chain count increases the actual
AVX2 instruction DAG and critical path.  This private kernel is hard-stopped;
the general e=0 finalizer is not implemented.

Artifacts: `src/tile4_bm_soa_dot_redc16_asm.S` and
`results/tile4-bm-soa-dot-redc16-short.json`.

### GT32-INV-RADIX4-01-ASM-001

The inverse follow-up treated the first raw qword butterfly and the following
fixed-factor half butterfly as one radix-4 region.  R4A was stopped before a
new symbol because its exact expansion has the same add/sub, shuffle, and
Montgomery DAG as the current paired inverse.  R4B uses the actual stage-1
constant pattern: half of the qwords are Montgomery identity (`-147 = R mod
q`).  It compacts identity qwords from two pairs, runs one full-width
Montgomery chain for their nonidentity partners, and redeposits both pairs.

The benchmark-only assembly passes 1,000 inverse-core, `out == in` alias, and
inverse-plus-T9 mod-q trials and uses no stack, spill, or `vpmulld`.  It does not pass the cycle
gate:

| placement | region | control | R4B | paired delta | wins |
| --- | --- | ---: | ---: | ---: | ---: |
| normal | inverse core | 225.133 | 238.549 | +13.648 | 1/20 |
| reversed | inverse core | 224.037 | 238.311 | +14.389 | 0/20 |
| normal | inverse + T9 | 457.166 | 466.676 | +12.365 | 5/20 |
| reversed | inverse + T9 | 452.655 | 466.445 | +13.465 | 1/20 |

The core and full consumer region are consistently about 12--14 TSC slower.  The
identity specialization replaces multiply-port work with a longer compaction
and redeposit dependency path; saving four static instructions and twelve
symbol bytes is not useful on this core.  The inverse radix-4 family is
hard-stopped.  Artifact: `results/tile4-inv-radix4-short.json`.

### GT32-FWD-RADIX4-45-ASM-001

The strict one-tile static gate expands current forward stages 4 and 5 as one
radix-4 transform.  Under the frozen terminal ABI it still needs four
independent stage-4 and four independent stage-5 fixed-factor arms: eight
full-width Montgomery chains in total.  No shared nontrivial factor removes a
chain, and the partial identity qwords require the same compaction/redeposit
shape rejected by inverse R4B.  Because neither a chain nor a complete local
shuffle network disappears, no forward assembly is emitted.  Reopen only for
a six-or-fewer-chain derivation, a proven complete shuffle-network removal, or
a consumer that accepts the unreconstructed radix-4 packets.  Artifact:
`generated/tile4_fwd_radix4_45_gate.json`.

### GT32-FWD-IDENTITY-LAZY-001

The remaining whole-vector identity experiment was evaluated separately from
the rejected mixed-lane inverse specialization.  The generator propagates a
bound for every physical vector through all five stages.  Raw S2 identity
arms are int16-safe but raise the terminal BM input bound from 10788 to 12447;
raw S2+S3 reaches 17608.  Both are rejected before assembly.  Replacing only
the two S2 identity chains with `center10` preserves the exact e=0 scale and
the existing 10788 terminal contract, so F3 was emitted as a benchmark-only
variant.  It removes two vector multiplies per tile without adding shuffles.

F3 passes 1,000 Forward, `out == in`, and `2F -> R1-U -> I1 -> T9` mod-q
trials.  The short paired result is positive but below the continuation gate:

| placement | region | control | F3 | paired delta | wins |
| --- | --- | ---: | ---: | ---: | ---: |
| normal | NTT32 core | 231.145 | 228.424 | -3.764 | 16/20 |
| reversed | NTT32 core | 230.942 | 227.262 | -3.597 | 19/20 |
| normal | full Forward | 403.789 | 402.452 | -1.793 | 14/20 |
| reversed | full Forward | 403.095 | 400.586 | -2.065 | 18/20 |
| normal | two Forward | 809.003 | 802.088 | -8.246 | 20/20 |
| reversed | two Forward | 808.119 | 800.665 | -7.494 | 20/20 |
| normal | full synthetic chain | 1665.269 | 1653.048 | -10.662 | 19/20 |
| reversed | full synthetic chain | 1658.118 | 1652.577 | -6.441 | 17/20 |

One full Forward saves only 1.8--2.1 TSC, below the required 5 TSC and with
one placement below 18/20 wins.  F3 is therefore frozen as a valid research
variant but hard-stopped for serious benchmarking and production selection.
Artifacts: `generated/tile4_forward_identity_lazy_gate.json` and
`results/tile4-forward-identity-lazy-short.json`.

### GT32-FIXED-MUL-PRIMITIVE-001

The final fixed-factor gate exhaustively synthesizes Q15 Barrett constants for
every Forward and inverse twiddle at its proven input bound.  Barrett is exact
mod q and can produce tighter representatives, but its AVX2 DAG remains
`vpmulhrsw + vpmullw + vpmullw + vpsubw`: three vector multiplies and the same
two-multiply dependency depth as current Montgomery.  Signed Plantard's
constant form relies on a packed 16x32 high-product shape that AVX2 does not
provide; splitting the 32-bit constant adds partial-product and extraction
work instead of deleting a multiply.  No assembly is emitted because neither
candidate meets the required smaller/shorter-DAG gate.  Reopen only with a
native packed 16x32 high product, an exact two-multiply formulation, or a
tighter output range that removes a later checkpoint.  Artifact:
`generated/tile4_fixed_mul_primitive_gate.json`.

### GT32-Q24-CODEC-001

Q24 changes the wire unpack atom instead of routing an already unpacked
Official-shaped polynomial.  The generator proves that every consecutive
24-byte wire packet contains sixteen coefficients that belong to exactly one
TILE4 YMM.  Quartic degrees are already `(0,1,2,3)` within each qword, and the
only qword placements are `0123`, `1032`, `2310`, and `3201`, with counts
14/11/11/12.  A lane-local `vpshufb` therefore combines 12-bit unpacking and
the final semantic placement; no scalar `vpextrw`, global semantic route, or
standalone repair pass is used.

The benchmark-only implementation provides raw-wire decoders to TILE4 AoS and
the persistent private SoA, plus the reverse encoders.  Decode performs four
independent canonicality accumulations.  The final packet uses explicit 8+4
byte loads, and encode uses 8+4 byte stores, so neither direction accesses
beyond the 1152-byte object.  Encode currently accepts centered canonical
input only; the lazy N5 bound of 10788 remains outside this gate.  Input and
output buffers are required to be disjoint.

Correctness covers 1,000 zero, maximum, and random trials, 3,072 malformed
single/triple-input cases, exact AoS/private-SoA placement, byte-exact encode,
and guard-page/canary tail checks.  The triple private-SoA entry shares one
3.5-KiB decoder body instead of inlining it three times.  The 2,000-call,
20-sample paired short gate is:

| placement | region | control | Q24 | paired delta | wins |
| --- | --- | ---: | ---: | ---: | ---: |
| normal | Decode AoS | 465.284 | 91.990 | -375.745 | 20/20 |
| reversed | Decode AoS | 471.337 | 91.207 | -382.461 | 20/20 |
| normal | Decode SoA | 170.515 | 115.705 | -54.853 | 20/20 |
| reversed | Decode SoA | 170.487 | 115.703 | -54.857 | 20/20 |
| normal | Encode AoS | 247.404 | 97.035 | -151.359 | 20/20 |
| reversed | Encode AoS | 250.034 | 95.879 | -154.197 | 20/20 |
| normal | Encode SoA | 194.643 | 125.567 | -69.036 | 20/20 |
| reversed | Encode SoA | 202.701 | 114.025 | -87.379 | 20/20 |
| normal | three Decode SoA | 508.596 | 343.779 | -165.965 | 20/20 |
| reversed | three Decode SoA | 508.909 | 341.590 | -166.156 | 20/20 |

The continuation requirement was at least 150 TSC saving and 18/20 wins for
the real three-decoder boundary in both placements.  Q24 passes with about
166 TSC and 20/20 wins.  It remains benchmark-only; the caller-composition
result is recorded separately below.

Artifacts: `generated/tile4_q24_codec.{json,inc}`,
`src/tile4_q24_codec_asm.S`, and `results/tile4-q24-codec-short.json`.

### Arithmetic-DAG freeze and Q24 prefix composition

The practical-ceiling statement is limited to the arithmetic DAG under the
current TILE4 layout, 16-bit lanes, generated N5/B3/I1 range contract, and
target AVX2 CPU.  N5/B3/I1 formulas, local scheduling, identity-lazy variants,
and fixed-factor Montgomery/Barrett/Plantard substitutions are frozen.  Kernel
boundaries are not frozen: first loads, final stores, typed producer/consumer
ABIs, output layouts, and materialization-eliminating Q24/sub/crep/Encodeq
fusion remain in scope.  Reopening arithmetic requires deletion of a complete
materialization or multiply/reduction/shuffle chain, a changed output/range
contract that removes such a chain, or a changed ISA/microarchitecture.

`GT32-Q24-PREFIX-COMPOSITION-001` measures four paired regions in one binary:
Decode2 alone, Decode3 alone, Decode2 plus the first-product consumer chain,
and the production-shaped Decode3 prefix with `hinv` retained.  Both consumers
use the unchanged private-SoA SS B3 scale, I1, T9, and Official crepmod3.

| placement | region | control | Q24 | saving | wins | retention |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| normal | Decode2 | 340.580 | 235.380 | 108.643 | 19/20 | -- |
| normal | Decode2 + consumer | 1211.656 | 1093.019 | 120.475 | 19/20 | 110.9% |
| reversed | Decode2 | 340.500 | 231.012 | 109.793 | 20/20 | -- |
| reversed | Decode2 + consumer | 1220.721 | 1095.535 | 125.399 | 19/20 | 114.2% |
| normal | Decode3 | 508.942 | 342.422 | 166.325 | 20/20 | -- |
| normal | Decode3 + consumer | 1386.669 | 1196.447 | 190.062 | 20/20 | 114.3% |
| reversed | Decode3 | 508.943 | 344.981 | 164.034 | 20/20 | -- |
| reversed | Decode3 + consumer | 1386.310 | 1195.569 | 188.149 | 20/20 | 114.7% |

Retention above 100% is a favorable composition effect, not an arithmetic
speedup claim: the paired prefix eliminates the decoder debt without exposing
a store/frontend penalty at the B3 boundary.  The primary 140-TSC and 18/20
gate passes strongly in both placements.  Correctness covers the valid prefix,
2,304 single-slot malformed cases, six multi-input malformed cases, aggregated
failure, exact `c/f/hinv` private-SoA words, exact first-product message,
scratch canaries, and ASan/UBSan.

The next gate may replace only Decode3 in the complete decapsulation caller.
B3/I1/T9, the second product, Encodeq, verify, and all protocol behavior must
remain unchanged so decode-only closure remains attributable.  Artifact:
`results/tile4-q24-prefix-short.json`.

### Q24 Decode3-only full-decapsulation gate

`GT32-Q24-DECAP-DECODE-ONLY-001` replaces only the three current semantic
private-SoA decoders with Q24 Decode3.  The first product, inverse, second
product, encoder, verify, hashes, SOTP, and failure selection are shared with
the control.  The deterministic eight-round valid/malformed suite remains
byte-exact for return value, shared secret, recovered message, and recovered
`r`.

Two independent 20-sample launches were measured in each link placement:

| placement | launch | Official | current GT | Q24 GT | Q24-control | wins |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| normal | 1 | 12019.779 | 12298.171 | 12209.258 | -170.170 | 17/20 |
| normal | 2 | 12086.334 | 12454.566 | 12399.609 | -161.298 | 17/20 |
| reversed | 1 | 12170.274 | 12668.446 | 12578.984 | -168.844 | 17/20 |
| reversed | 2 | 12204.903 | 12629.382 | 12599.059 | -142.289 | 16/20 |

The decoder replacement is directionally positive in all four launches and
reduces the current GT control by an aggregate median 170.170 TSC in normal
placement and 151.488 TSC in reversed placement.  It does not pass the strong
120-TSC plus 18/20-per-launch stability gate: aggregate paired MAD is
114.349/128.106 TSC and only 34/40 and 33/40 samples win.  Q24 also remains
slower than Official by aggregate medians 215.307 and 421.371 TSC.

The result is therefore a placement-sensitive conditional pass, not a codec
hard stop and not a production or serious-benchmark pass.  The next work is
code-placement/alignment and PMU attribution of frontend and three-decoder
store effects.  Q24 encoders, 100k serious benchmarking, and monolithic fusion
remain blocked until the decode-only gain is stable.  Artifact:
`results/tile4-q24-decap-short.json`.

Non-multiplexed PMU groups corroborate the mechanism but not stable cycle
conversion.  Q24 reduces retired instructions by 0.725%/0.879% and retired
uop slots by 0.998%/1.123% in normal/reversed placement.  Retired loads rise
0.485%/0.363% and stores rise 0.315%/0.196%, so Q24 is not winning by deleting
a memory pass.  The same stable work-count reduction becomes a 3.296% core
cycle reduction in normal placement but only 0.495% when reversed.  This
supports frontend/code-placement attribution before any fusion.  L1-miss and
low-volume bad-speculation events were too noisy to use as decision evidence.
Raw counts, repeat spread, runtime, and PMU running percentages are in
`results/tile4-q24-decap-pmu.json`.

A separate 64-byte alignment corroboration aligned both control and Q24
recover functions without changing the codec or decap suffix.  Aggregate Q24
saving became 180.031 TSC with 33/40 wins in normal placement and 182.120 TSC
with 37/40 wins when reversed.  The four launch win counts were 17, 16, 17,
and 20 out of 20.  Alignment therefore affects retention, but does not meet
the every-launch 18/20 stability requirement.  This closes simple recover
function alignment as a sufficient fix; it does not close Q24 itself.  The
remaining attribution target is placement of the approximately 3.5-KiB codec
body relative to the complete decap frontend.  Artifact:
`results/tile4-q24-decap-align64-short.json`.

### Fixed-size Q24 placement cage

`GT32-Q24-FIXED-CAGE-PLACEMENT-001` moves only the 3,470-byte active
private-SoA decoder body inside a fixed 4-KiB executable cage.  Eight variants
use page offsets 0, 32, ..., 224.  Mechanical `nm`/`size` checks prove that the
body moves by exactly the requested offset while the Decode3 wrapper, caller,
B3, I1, T9, and loaded `.text/.rodata/.data/.bss` addresses and sizes remain
fixed.  One variant changes only non-loaded DWARF file size; that is explicitly
not a runtime invariant.

Each offset was measured with four process launches per normal/reversed link
placement and 20 paired samples per launch.  Every offset retains a large
positive aggregate median saving, but none passes the requirement that every
launch win at least 18/20 samples:

| offset | normal saving | normal launch wins | reversed saving | reversed launch wins |
| ---: | ---: | --- | ---: | --- |
| 0 | 181.839 | 16/19/17/16 | 189.685 | 14/11/16/20 |
| 32 | 183.261 | 16/18/17/15 | 225.547 | 16/19/17/17 |
| 64 | 172.844 | 15/16/17/16 | 228.928 | 14/19/19/20 |
| 96 | 155.567 | 20/18/16/14 | 190.366 | 13/12/12/16 |
| 128 | 159.897 | 17/19/18/17 | 229.156 | 18/19/15/18 |
| 160 | 176.866 | 19/18/17/18 | 227.219 | 18/20/13/16 |
| 192 | 176.484 | 20/18/18/17 | 231.388 | 20/19/13/19 |
| 224 | 180.523 | 18/19/15/15 | 242.810 | 20/18/16/17 |

There is no reproducible mod-256 sweet spot, so magic padding is rejected as
a production solution.  Q24 remains mathematically promoted and
microarchitecturally unpromoted.  Per the gate, the next experiment is a
compact Q24 code shape with identical packet arithmetic and rejection
semantics; encoder integration, caller fusion, and 100k serious benchmarking
remain deferred.  Artifact: `results/tile4-q24-placement-sweep.json`.

### Q24 compact code-shape attribution

Two benchmark-only compact private-SoA bodies preserve the Q24 mapping,
12-bit packet arithmetic, four qword masks, transpose, canonical rejection,
and safe final packet.  The fully table-driven M4 body loads two source
offsets and one mask index for every packet.  The pattern-loop body instead
groups identical four-packet route signatures, so packet offsets and masks
remain fixed instruction operands; only source-group and destination-block
offsets are table driven.

| body | text bytes | normal Decode3 | normal saving/wins | reversed Decode3 | reversed saving/wins |
| --- | ---: | ---: | ---: | ---: | ---: |
| unrolled U | 3470 | 343.779 | 165.966 / 20/20 | 341.590 | 166.156 / 20/20 |
| table M4 | 703 | 441.489 | 71.451 / 18/20 | 437.338 | 70.366 / 20/20 |
| route-pattern loops | 1850 | 363.742 | 144.031 / 20/20 | 365.377 | 143.757 / 20/20 |

M4 is a cycle-level hard stop: the dependent scalar source/mask lookups erase
more than half of the Q24 saving.  Route-pattern loops recover most of the
unrolled speed and make the isolated Decode3 measurement stable, but they do
not stabilize the full caller.  Four-launch decapsulation measurements gave
aggregate Q24-control deltas of -158.054 TSC with 64/80 wins in normal link
order and -157.928 TSC with 65/80 wins when reversed.

The stronger single-variable corroboration places both unrolled and
route-pattern bodies at offset zero in the same fixed 4-KiB cage and links the
same compact control tables into both binaries.  All shared symbol addresses
and loaded `.text/.rodata/.data/.bss` addresses and sizes are identical.  The
unrolled control saved 176.870 TSC with 62/80 wins in normal order and 202.192
TSC with 67/80 wins when reversed.  The pattern body saved 141.266 TSC with
67/80 wins and 196.740 TSC with 61/80 wins.  Its per-launch wins were
17/15/16/19 and 15/15/14/17.  The smaller body therefore does not provide a
consistent caller-stability improvement even under a byte-for-byte sized
cage and address-matched suffix.

Therefore neither low address bits nor active Q24 text footprint alone
explains delivery variance.  The unrolled Q24 algorithm remains the speed
champion, but no implementation is production-stable.  Further attribution,
if continued, must compare PIE/ASLR controls and launch-specific frontend PMU
behavior rather than add padding or make the packet loop smaller.  Encoder
integration, fusion, and 100k benchmarking remain deferred.  Artifacts:
`results/tile4-q24-compact-codec-short.json`,
`results/tile4-q24-pattern-codec-short.json`,
`results/tile4-q24-pattern-decap-short.json`, and
`results/tile4-q24-pattern-cage-short.json`, with its matched unrolled control
in `results/tile4-q24-unrolled-matched-cage-short.json`.

### Q24 PIE/ASLR, runtime, and region-PMU attribution

`GT32-Q24-LAUNCH-ATTRIBUTION-001` freezes the unrolled Q24 assembly and moves
the variable under test outside the codec.  It compares the same PIE binary
with ASLR enabled and disabled (`setarch -R`), plus a separately built
non-PIE `ET_EXEC` control.  Every process reports its text mapping/load bias
and the virtual addresses of the decap wrapper/candidate, Q24 body/Decode3,
B3, I1, and T9.  Two independent batches each contain eight launches per
mode and link order, 20 paired samples per launch, and 2,000 iterations per
sample; this is not a 100k serious benchmark.

| mode | link | aggregate Q24-control | good launches | batch split |
| --- | --- | ---: | ---: | --- |
| PIE, ASLR on | normal | -197.508 TSC | 8/16 | 5/8, 3/8 |
| PIE, ASLR on | reversed | -179.378 TSC | 12/16 | 7/8, 5/8 |
| PIE, ASLR off | normal | -185.510 TSC | 13/16 | 6/8, 7/8 |
| PIE, ASLR off | reversed | -149.128 TSC | 7/16 | 1/8, 6/8 |
| non-PIE fixed | normal | -202.894 TSC | 7/16 | 0/8, 7/8 |
| non-PIE fixed | reversed | -152.763 TSC | 7/16 | 0/8, 7/8 |

All 96 launch-level median deltas favor Q24, and Q24 wins 1,674/1,920
individual paired samples.  Only 54/96 launches satisfy the old `18/20`
rule.  More importantly, identical fixed addresses do not make the result
repeatable across batches: the non-PIE controls change from 0/8 good launches
in both link orders to 7/8 without moving any hot symbol.  ASLR therefore
participates in some observations but absolute virtual address is not a
sufficient cause or production layout rule.  CPU 2, the SMT sibling of the
pinned CPU 1, accumulated zero active scheduler ticks during all 96 launches.

PMU data is collected inside the benchmark with `perf_event_open`.  Every
control/Q24 region is reset, enabled, disabled, and read independently in the
same AB/BA process; setup, KEM correctness, warm-up, and printing are outside
the counter interval.  Four event groups run without multiplexing.  Across
48 core-counter launches, Q24 always saves core cycles (range -594.595 to
-59.904 cycles/call) and its instruction delta is effectively invariant at
-429.001 instructions/call.  The median absolute difference between Q24 and
control core/ref-cycle ratios is only 0.0000286.  I-cache-stall deltas range
from -0.432 to +0.173/call and iTLB-walk deltas from -0.0055 to +0.0034/call;
the IDQ/DSB/MITE good-versus-bad direction reverses with link placement.
APERF/MPERF is unavailable for per-thread counting on this host, so
core/ref-cycles is the region-scoped frequency proxy.

The conclusion is narrower than either “ASLR caused it” or “Q24 is unstable”:
Q24's retired-work and core-cycle advantage is stable, while the old
per-launch `18/20` delivery rule is dominated by broader runtime/statistical
jitter.  Q24 is now core-work-qualified but remains unpromoted.  The next gate
must predeclare hierarchical launch-level paired statistics and corroborate
them under realistic-cold caller cadence; encoder integration, fusion, and
100k serious benchmarking remain deferred.  Artifacts:
`results/tile4-q24-launch-environment.json`,
`results/tile4-q24-launch-pmu.json`, and
`results/tile4-q24-launch-attribution-summary.json`.

### Q24 GT-native codec production promotion

The opt-in GT32 decapsulation candidate now selects both Q24 boundaries:

```text
Official wire bytes
  -> Q24 GT-unpack3
  -> persistent private BM SoA / B3 / I1 / T9
  -> centered-canonical private BM SoA
  -> Q24 GT-pack recovered-r bytes
```

Q24 GT-unpack fuses 12-bit deserialization, canonical rejection, the
Good--Thomas leaf permutation, and TILE4/private-SoA redeposit.  The promoted
GT-pack removes the reverse implementation debt
`SoA -> grouped Official words -> Official pack` and emits the same canonical
1,152-byte wire representation directly.  Public `crypto_kem_dec` and the
repository default remain Official Main; this is a component promotion inside
the opt-in GT32 decapsulation candidate, not a whole-KEM backend promotion.

The recovered-r GT-pack was requalified with process launch as the primary
statistical unit.  The same binary used CPU 1, 2,000 decapsulations per sample,
20 paired AB/BA samples per launch, 48 launches per normal/reversed link
placement, and 100,000 deterministic bootstrap resamples:

| placement | unpack-only control | Q24 GT-pack | paired saving | negative launch medians | bootstrap 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: |
| normal | 12199.919 TSC | 12069.949 TSC | -127.565 TSC | 47/48 | [-134.333, -121.476] |
| reversed | 12307.878 TSC | 12155.510 TSC | -114.316 TSC | 48/48 | [-123.822, -97.654] |

Both placements pass the predeclared requirements: at least 90% negative
launch medians, a bootstrap upper bound below zero, and at least 50 TSC median
saving.  The independent `crypto_kem_dec_gt32_q24_pack_candidate()` body is
kept `noipa`; at this checkpoint the production candidate made a fixed tail
call to it.  The later lazy10788 boundary promotion applies the same fixed-tail
rule to its own independent body while retaining this centered implementation
as the qualified control.  No centered Q24 assembly or arithmetic changed.

A 32-launch, non-multiplexed region-PMU corroboration also favors GT-pack:

| placement | core-cycle saving | cycle-negative launches | bootstrap 95% CI | instruction delta | load delta | store delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| normal | -172.931 | 28/32 | [-201.301, -119.581] | -378.004 | -50.001 | +11.999 |
| reversed | -217.807 | 31/32 | [-250.963, -180.964] | -378.004 | -50.001 | +11.999 |

The codec suite still passes 1,000 exact trials and 3,072 malformed cases.
The full candidate passes eight deterministic KEM rounds and all seven
malformed/failure cases per round with byte-exact return value, shared secret,
recovered message, and recovered-r bytes.  Release disassembly contains no
trace symbols and the selected body calls `gt32_q24_decode3_soa_asm` and
`gt32_q24_encode_soa_asm` directly.  No 100k serious run was performed.

Artifacts: `results/tile4-q24-recovered-r-gtpack-short.json` and
`results/tile4-q24-recovered-r-gtpack-pmu.json`.

### Pre-lazy Q24 GT32 versus Official Main decapsulation

After the centered recovered-r GT-pack promotion, the fresh same-binary short
comparison uses CPU 1, paired AB/BA order, eight launches per link placement,
20 samples per launch, and 2,000 decapsulations per sample:

| link placement | Official | Q24 GT32 | GT32 - Official | change |
| --- | ---: | ---: | ---: | ---: |
| normal | 11990.462 TSC | 12065.547 TSC | +91.044 TSC | +0.759% |
| reversed | 12060.742 TSC | 12102.463 TSC | +25.935 TSC | +0.215% |

Official remains faster in all 16 launch medians, so the whole backend stays
Official-default.  The remaining TSC gap is now only about 0.2--0.8%, but a
four-launch non-multiplexed PMU control still reports more actual core cycles:

| link placement | Official | Q24 GT32 | GT32 - Official | change |
| --- | ---: | ---: | ---: | ---: |
| normal | 19302.236 cycles | 19747.027 cycles | +449.008 cycles | +2.326% |
| reversed | 19359.315 cycles | 19477.576 cycles | +145.630 cycles | +0.752% |

Q24 GT32 now retires about 1,305 fewer instructions per decapsulation, but the
remaining instruction mix has higher average cycle cost.  The next isolated
boundary experiment is the distinct `lazy10788` GT-pack used by the final N5
check; it must not silently widen the centered encoder contract.  N5, B3, and
I1 arithmetic remain frozen.  Artifacts:
`results/tile4-q24-production-official-short.json` and
`results/tile4-q24-production-official-pmu.json`.

### Final-check lazy10788 Q24 GT-pack gate

The final reencryption boundary now has a separate, benchmark-only typed
encoder:

```text
private BM SoA, e=0, |word| <= 10788
  -> v=9 centered reduction
  -> Q24 packet formation
  -> Official canonical 1,152-byte serialization
```

It does not modify the production-qualified centered GT-pack.  The generator
exhaustively proves all 21,577 scalar inputs: the rounded quotient is in
`[-3,3]`, the reduced representative is in `[-2188,2188]`, one sign
correction yields `[0,3456]`, and congruence and signed-int16 safety hold.
The assembly adds three vector instructions to each of 48 packets and creates
no standalone canonical polynomial.  The codec test exhausts the interval,
adds 1,000 mixed-lane/routing trials, checks output canaries and
non-destructive input, and the existing eight-round KEM/malformed suite is
byte-exact.

The 48-launch full-decapsulation gate compares the existing centered-pack
candidate against the candidate that changes only the final-check encoder:

| placement | centered control | lazy10788 GT-pack | delta | negative launch medians | bootstrap 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: |
| normal | 12197.345 TSC | 12086.641 TSC | -95.584 TSC | 48/48 | [-102.588, -90.475] |
| reversed | 12221.485 TSC | 12206.283 TSC | -23.116 TSC | 39/48 | [-30.215, -17.437] |

The normal placement is a strong pass, but reversed reaches only 81.25%
negative launch medians and therefore misses the predeclared 90% promotion
gate despite a fully negative bootstrap interval.  Region PMU explains why
promotion is withheld rather than treating this as ordinary TSC noise:

| placement | core-cycle delta | cycle-negative launches | bootstrap 95% CI | instruction delta | load delta | store delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| normal | -197.721 | 31/32 | [-226.156, -167.563] | -235.004 | -50.000 | +10.999 |
| reversed | -5.587 | 17/32 | [-57.095, 28.156] | -235.004 | -50.000 | +10.999 |

Thus the uncaged boundary algorithm removes invariant work, but that code
shape did not survive reversed placement.  It was retained as the historical
control while the arithmetic, mapping, constants, stores, and typed range
contract were frozen.  N5, B3 and I1 arithmetic remained frozen.  Artifacts:
`generated/tile4_q24_lazy10788_gate.json`,
`results/tile4-q24-lazy10788-gtpack-short.json`, and
`results/tile4-q24-lazy10788-gtpack-pmu.json`.

#### Matched-cage schedule closure and promotion

Four schedules were then emitted into an identical 5,120-byte code cage.  The
cage keeps the lazy encoder entry and every downstream symbol at identical
offsets, so only the reducer/packet scheduling changes:

| schedule | shape | normal delta | reversed delta |
| --- | --- | ---: | ---: |
| L0 | original serial packet reducer | -74.526 TSC | -75.940 TSC |
| L1 | two-packet interleave | -59.538 TSC | -64.441 TSC |
| L2 | four-packet reduce-first | -60.925 TSC | -76.046 TSC |
| L3 | four-packet pipeline | -72.356 TSC | -55.700 TSC |

No interleaved schedule improves L0's worst-placement margin.  The result is a
schedule hard stop, not a new arithmetic result: cross-packet ILP is not an
additional acceleration mechanism on this CPU.  L0 was therefore kept inside
the fixed-size cage and run through the predeclared 48-launch gate:

| placement | centered control | caged L0 | delta | negative launch medians | bootstrap 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: |
| normal | 12185.954 TSC | 12128.678 TSC | -67.083 TSC | 47/48 | [-77.102, -59.540] |
| reversed | 12031.801 TSC | 11967.845 TSC | -74.640 TSC | 47/48 | [-78.352, -63.182] |

The 32-launch non-multiplexed PMU gate also passes in both placements:

| placement | core-cycle delta | cycle-negative launches | bootstrap 95% CI | instruction delta | load delta | store delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| normal | -141.357 | 30/32 | [-201.524, -116.107] | -235.004 | -50.000 | +10.999 |
| reversed | -163.268 | 31/32 | [-201.132, -132.060] | -235.004 | -50.000 | +10.999 |

The typed lazy10788 Q24 GT-pack is therefore production-qualified inside the
opt-in GT32 decapsulation candidate.  The public backend remains Official.
The production selector tail-calls the independent `noipa` qualified body, so
promotion does not fold or move the implementation that passed the cage gate.
Artifacts: `generated/tile4_q24_lazy_schedules.json`,
`results/tile4-q24-lazy-schedules-short.json`,
`results/tile4-q24-lazy-caged-L0-final.json`, and
`results/tile4-q24-lazy-caged-L0-pmu.json`.

#### Fresh lazy-GT-pack candidate versus Official Main

After promotion, the same-binary 2,000-iteration, eight-launch comparison was
rebuilt and rerun from the new selector:

| link placement | Official | GT32 | GT32 - Official | change | GT32-faster launches |
| --- | ---: | ---: | ---: | ---: | ---: |
| normal | 12038.826 TSC | 12092.114 TSC | +114.351 TSC | +0.950% | 2/8 |
| reversed | 12031.537 TSC | 11941.207 TSC | -97.293 TSC | -0.809% | 8/8 |

GT32 now wins the reversed binary but loses the normal binary.  PMU confirms
that this is not a two-placement backend win even though GT32 retires about
1,520 fewer instructions per decapsulation:

| link placement | Official | GT32 | paired GT32 - Official | change | negative core-cycle launches |
| --- | ---: | ---: | ---: | ---: | ---: |
| normal | 19265.643 cycles | 19443.914 cycles | +172.410 cycles | +0.895% | 1/8 |
| reversed | 19350.737 cycles | 19329.837 cycles | +28.541 cycles | +0.147% | 4/8 |

The reversed absolute medians are close, but the primary paired launch delta
remains positive.  Consequently the boundary primitive is promoted while the
whole GT32 backend is not: `BACKEND=official` remains the default, and no 100k
serious benchmark is justified.  The remaining blocker is whole-caller code
placement/delivery, not the lazy10788 reduction contract or N5/B3/I1
arithmetic.  Artifacts:
`results/tile4-q24-lazy-production-official-short.json` and
`results/tile4-q24-lazy-production-official-pmu.json`.

### Whole-decapsulation cumulative phase attribution

`GT32-DECAP-CUMULATIVE-ATTRIBUTION-001` replays one semantic caller prefix at
a time without inserting timers into production kernels.  C1 through C5 use
byte-exact Official and GT32 prefix copies; C6 calls the actual
`crypto_kem_dec` and `crypto_kem_dec_gt32_candidate` symbols.  The real caller
must recover and serialize `r` before `hash_g` and SOTP decode, so the measured
order is C1 Decode3, C2 first product/inverse/crepmod3, C3 Forward(m)/sub/
general-BM/recovered-r pack, C4 hash_g/SOTP/hash_h, C5 CBD/N5/lazy-pack/verify,
and C6 select/cleanup.  All six checkpoints are byte-exact, including the
three decoded polynomials, ternary `m`, recovered-r bytes, message and hashes,
reencryption bytes/failure, and final shared secret.

Eight 2,000-iteration paired TSC launches and eight non-multiplexed grouped-PMU
launches were run for each link placement.  The table reports incremental
GT32-minus-Official phase deltas rather than isolated kernel costs:

| phase | normal TSC | reversed TSC | normal core cycles | reversed core cycles | instructions |
| --- | ---: | ---: | ---: | ---: | ---: |
| C1 Decode / GT-unpack | +31.544 | +35.701 | +52.212 | +49.483 | +197 |
| C2 first BM + inverse + crepmod3 | +33.310 | +29.041 | +54.424 | +61.231 | -314 |
| C3 recovered-r pipeline | -37.349 | -46.744 | -86.413 | -76.312 | -770 |
| C4 hash/SOTP middle | -56.540 | +48.240 | -14.582 | +56.818 | +1 |
| C5 final N5/pack/verify | +49.672 | +17.023 | +106.480 | +0.614 | -277 |
| C6 select/cleanup and residual code shape | +68.644 | -32.161 | +66.130 | -30.448 | -357 |

C1 and C2 are the only positive phases whose core-cycle debt retains at least
half of its larger-placement value.  C2 is the largest actionable phase: Q24
packet mathematics and local scheduling are frozen, while C2 adds 54--61 core
cycles and 29--33 TSC despite retiring 314 fewer instructions.  C3 is a real
76--86-core-cycle win.  C4--C6 change magnitude or sign with placement and are
not selected as a stable optimization target.

The selected scope is therefore the C2 ternary-result composition boundary,
not another B3/I1 arithmetic rewrite.  The measured B3-to-I1 local fusion and
the T10 crep-only fusion are existing hard stops.  Reopening this region must
delete the complete coefficient-result materialization by producing both the
N5 consumer input and a compact SOTP consumer representation from the
T9/crep terminal.  No prototype was added in this gate, no production symbol
changed, and the 100k serious benchmark remains deferred.

C6 uses the real production functions in the attribution binary.  Its gap is
+89.280 TSC in normal placement and +51.100 TSC in reversed placement.  The
older fresh-Official artifact used a different binary layout (+114.351 and
-97.293 TSC), so that comparison is corroboration of placement sensitivity,
not a strict closure error.  The full raw data and PMU scaling metadata are in
`results/tile4-decap-cumulative-attribution.json`; the reusable harness and
runner are `bench/bench_decap_cumulative.c` and
`tools/run_decap_cumulative.py`.

### C2 dual-consumer terminal gate

`GT32-C2-DUAL-CONSUMER-TERMINAL-001` tests the selected C2 boundary without
changing N5, B3, or I1 arithmetic.  The generator proves that the six vectors
produced by each T9 group are exactly the six inputs consumed by the matching
N5 wide-frontend iteration.  It also maps every ternary coefficient to two
canonical 96-byte SOTP bitplanes:

```text
neg[i] = (m[i] == -1)
nz[i]  = (m[i] != 0)
```

The benchmark endpoint includes both consumers: N5 frontend output and the
completed SOTP decode.  The control materializes the full 1536-byte ternary
polynomial.  None of the three candidates does so:

- direct: T9 group -> center/crep -> N5 + sidecar, with no stack scratch;
- B2: the same graph through a 384-byte two-group rotating scratch;
- B4: the same graph through a 768-byte four-group rotating scratch.

The first 1,000-trial differential found a rare representative mismatch in
the prior T10 assumption that raw precenter T9 output could feed crepmod3
directly.  The production T9 center is therefore retained in registers before
crepmod3.  With that correction, 1,000 random product trials pass exact N5
frontend, exact `neg`/`nz`, valid and malformed SOTP failure, zero-on-failure,
and guard-buffer checks for all three variants.

Eight 2,000-iteration launches per placement give:

| region / candidate | normal delta | reversed delta | normal bootstrap 95% CI | reversed bootstrap 95% CI |
| --- | ---: | ---: | ---: | ---: |
| direct producer | +172.595 TSC | +172.240 TSC | [+170.323,+173.120] | [+171.932,+172.672] |
| B2 producer | +69.294 TSC | +69.766 TSC | [+67.287,+70.933] | [+67.386,+71.555] |
| B4 producer | +71.502 TSC | +71.780 TSC | [+70.333,+73.166] | [+70.364,+72.415] |
| compact SOTP consumer | -78.995 TSC | -78.983 TSC | [-79.050,-78.959] | [-79.012,-78.977] |
| full B2 dual terminal | -9.128 TSC | -8.098 TSC | [-11.754,-0.607] | [-10.620,-5.543] |
| full B4 dual terminal | -5.995 TSC | -6.393 TSC | [-7.479,-3.514] | [-7.608,-5.440] |

The sidecar consumer is a real approximately 79-TSC improvement, but restoring
enough cross-group ILP costs 69--72 TSC in the producer.  The resulting 6--9
TSC caller improvement is below the predeclared 30-TSC continuation gate.
This is therefore a cycle-level hard stop: no PMU/100k run, production
integration, or selector change is performed.  N5/B3/I1 remain frozen.

Artifacts are `generated/tile4_dual_terminal_gate.json`,
`bench/bench_dual_terminal.c`, `tools/run_dual_terminal.py`, and
`results/tile4-dual-terminal-short.json`.

### Crepmod3 sidecar-tap gate

`GT32-CREPMOD3-SIDECAR-TAP-001` keeps the production coefficient-order
`m[768]` stores and the complete N5 path unchanged.  It extends only the
post-crep boundary:

```text
production T9 CENTER -> crepmod3 -> full m store
                                  -> neg[96] / nz[96] sidecar
```

The sidecar is extracted only after every coefficient is exactly one of
`{-1,0,+1}`.  S1 processes one 64-coefficient batch per loop and S2 is a
two-batch unrolled control.  Both preserve the Official `poly_crepmod3` word
representatives and stores.  The differential harness passes an exhaustive
three-value truth table in every physical lane, 1,000 random product trials,
exact full-m output, exact sidecar bits, unchanged N5 frontend output, valid
and malformed SOTP behavior, zero-on-failure, and guard buffers.
The same harness also passes an ASan/UBSan build.

Eight 2,000-iteration launches per placement give the local boundary result:

| region | normal delta | reversed delta |
| --- | ---: | ---: |
| S1 producer overhead | +31.344 TSC | +31.003 TSC |
| S2 producer overhead | +31.397 TSC | +31.278 TSC |
| compact SOTP consumer | -78.839 TSC | -78.951 TSC |
| S1 crep + SOTP | -40.824 TSC | -41.585 TSC |
| S1 crep + unchanged N5 + SOTP | -45.631 TSC | -45.746 TSC |

The local S1 gate is a strong pass: the producer is below the 40-TSC target,
the full unchanged-N5 region saves about 46 TSC, all eight launch medians are
negative in both placements, and both bootstrap intervals exclude zero.  S1
is retained as the simpler benchmark implementation; S2 has no useful
advantage.

The full-decapsulation gate does not preserve that stability:

| placement | sidecar - qualified lazy control | negative launches | bootstrap 95% CI |
| --- | ---: | ---: | ---: |
| normal | -130.653 TSC | 7/8 | [-191.288,-101.248] |
| reversed | -10.347 TSC | 6/8 | [-30.010,+8.795] |

The candidate reuses the dead prefix of `buf3` for the 192-byte sidecar, so
the failure is not caused by a new stack object or an extra clear.  The
reversed median misses the predeclared 30-TSC gate and its confidence interval
crosses zero.  A fresh sidecar-candidate comparison with Official Main is also
placement-dependent: normal is +49.695 TSC (+0.411%), while reversed is
-34.807 TSC (-0.289%).

Consequently the tap is a **dormant performance-qualified component**, not a
component-level hard stop.  Its intrinsic approximately 46-TSC saving is
stable; the failed gate is only the current full-decapsulation delivery shape.
`crypto_kem_dec_gt32_candidate` continues to select the previously qualified
lazy10788 Q24 GT-pack body.  Dedicated sidecar placement tuning is stopped, but
the unchanged sidecar must be cheaply re-gated after a whole-caller pipeline or
code-shape change (in particular after any final-check boundary promotion).
Production still requires at least 30 TSC in both placements.  No PMU or 100k
run is justified by the current full-decapsulation gate.

Artifacts: `src/tile4_crep_sidecar_asm.S`, `bench/bench_crep_sidecar.c`,
`tools/run_crep_sidecar.py`, `tools/run_crep_sidecar_decap.py`,
`results/tile4-crep-sidecar-short.json`,
`results/tile4-crep-sidecar-decap-short.json`, and
`results/tile4-q24-sidecar-production-official-short.json`.

### Lazy10788 Q24 GT-pack-and-verify gate

`GT32-Q24-PACK-VERIFY-001` tests whether the final check can avoid the
1,152-byte candidate-ciphertext materialization:

```text
control:   N5 -> lazy10788 Q24 GT-pack -> buffer -> full-YMM verify
candidate: N5 -> lazy10788 Q24 packets -> direct fixed-scan compare
```

The benchmark-only candidate preserves the qualified lazy reduction, Q24
mapping, packet order, and fixed 48-packet control flow.  It returns the exact
zero/one mismatch result, never writes a packed output buffer, and uses safe
8+4-byte loads for the last expected packet.  Tests cover the complete scalar
range `[-10788,10788]`, 1,000 random N5 outputs, every serialized byte as the
sole mismatch, a guard-page tail, read-only expected input, input
non-destruction, and output canaries.

The first two-XMM/single-accumulator schedule was about 42--43 TSC slower than
materialize-and-verify.  A bounded second schedule compares one padded YMM per
packet and uses three independent mismatch accumulators; it recovers that
regression but leaves only a near-neutral result:

| placement | candidate - control | wins | negative launch medians | bootstrap 95% CI |
| --- | ---: | ---: | ---: | ---: |
| normal | -1.974 TSC | 202/320 | 15/16 | [-2.542,-1.322] |
| reversed | -1.672 TSC | 203/320 | 15/16 | [-2.138,-1.206] |

The direction is repeatable, but the saving is far below the predeclared
30-TSC continuation gate.  This is a clean **hard stop** for GT-pack-and-verify:
the control verify is already an efficient full-YMM loop, fusion extends the
pack critical path, the active body grows from 5,120 to 5,259 bytes, and the
caller-visible gain is only about 2 TSC.  The eliminated stores and reloads
were not on a corresponding critical path.  No full-decapsulation integration
is performed; the production selector, Official comparison, and dormant
sidecar state are unchanged.  N5/B3/I1 arithmetic remains frozen.

Artifacts: `src/tile4_q24_codec_asm.S`, `bench/bench_q24_pack_verify.c`,
`tools/run_q24_pack_verify.py`, and
`results/tile4-q24-pack-verify-short.json`.

### Q24 Decode2 to first-B3 streaming frontier

`GT32-Q24-DECODE2-B3-FRONTIER-001` is the final bounded decapsulation
materialization gate.  The generator proves that every four consecutive Q24
packets form exactly one complete 16-quartic B3 block.  The wire-group to B3
block order is:

```text
0, 1, 9, 8, 4, 5, 11, 10, 6, 7, 3, 2
```

It is a bijection, the quartic products have no cross-block dependency, and
the block-specific lambda stream can be selected directly.  A 16-YMM plan
exists without spill: q in YMM0, decoded c planes in YMM1--4, decode/qinv
temporaries in YMM5--8, decoded f planes in YMM9--12, and shared decode/B3
temporaries in YMM13--15.

Static accounting therefore passed the assembly gate:

| item | count |
| --- | ---: |
| Decode(c,f) private-SoA stores removed | 96 vector stores |
| B3 immediate input reloads removed | 96 vector loads |
| materialized traffic removed | 6,144 bytes |
| streaming validity debt | +36 instructions |
| low12 reload debt | +10 instructions |
| dynamic instruction saving lower bound | 146 instructions |

The benchmark-only assembly decodes each c/f group, validates it with fixed
control flow, transposes directly into the production B3 input registers, and
executes the unchanged scale-B3 arithmetic/output sequence.  It passes 1,000
random canonical products word-exactly, every serialized slot independently
set to q for each operand, simultaneous malformed operands, read-only
guard-page inputs, safe final-packet loads, and output canaries.  There is no
stack use or spill.

Despite the favorable static count, the cycle gate fails decisively:

| placement | streaming - materialized | wins | negative launch medians | bootstrap 95% CI |
| --- | ---: | ---: | ---: | ---: |
| normal | +65.807 TSC | 3/320 | 0/16 | [+65.073,+67.111] |
| reversed | +64.269 TSC | 7/320 | 0/16 | [+62.503,+65.908] |

The streaming symbol expands to 13,753 bytes and 2,529 static instructions,
whereas the control reuses the 3,470-byte Q24 body twice and the 655-byte B3
loop twelve times.  Eliminating the data materialization does not compensate
for losing those compact, independently scheduled hot loops and their clean
producer/consumer boundary.  This is a cycle-level hard stop for the current
Q24 Decode2 -> first-B3 frontier; no I1/full-decapsulation integration, PMU, or
100k run is performed.

Together with the closed C2 and C5 gates, this ends the current decapsulation
micro-optimization line.  The qualified Q24 boundaries remain selected, the
sidecar remains a dormant qualified component, and subsequent performance work
should move to keygen/encap unless a new mechanism removes an additional full
boundary without expanding the same Q24/B3 DAG.

Artifacts: `tools/generate_q24_b3_frontier.py`,
`generated/tile4_q24_b3_frontier_gate.json`,
`generated/tile4_q24_b3_frontier.inc`,
`src/tile4_q24_b3_frontier_asm.S`,
`bench/bench_q24_b3_frontier.c`, `tools/run_q24_b3_frontier.py`, and
`results/tile4-q24-b3-frontier-short.json`.
## GT32 decap closure and keygen/encap attribution

The decapsulation micro-optimization phase is closed.  N5/B3/I1 arithmetic,
Q24 codec shape, C1 unpack-to-B3 streaming, C2 terminal fusion, and C5
pack/verify fusion are no longer active search spaces.  The decisive C1
control is especially important: deleting 6,144 bytes of traffic and at least
146 dynamic instructions produced a 13.7-KiB streaming body and regressed by
64--66 TSC.  A materialized boundary can be the cheaper executable schedule
when it preserves two compact, reusable hot loops.

The next caller-first experiment therefore built a complete deterministic
GT32 encapsulation candidate before doing phase attribution.  Its typed path
is Q24 GT-unpack of `h`, two coefficient-to-private-SoA N5 Forwards, private
SoA general B3, elementwise add, and the already-proven grouped bridge into
the unchanged Official final pack.  The `rhat` wire boundary uses the
production-qualified lazy10788 Q24 GT-pack.  One hundred deterministic valid
encapsulations and all 768 single-slot `q` noncanonical public keys are
byte-exact to Official, including return codes and all-zero failure outputs.

The authoritative short result uses eight process launches per placement,
2,000 calls in each of 20 paired samples, and launch medians as the primary
unit.  Absolute TSC exposed two frequency/runtime regimes, so cross-placement
absolute values are not combined; paired directions are:

| Encap region | normal GT-Official | reversed GT-Official | interpretation |
| --- | ---: | ---: | --- |
| E1 Decode/CBD/SOTP | +12.041 | +12.036 | small stable input-boundary debt |
| E2 two Forwards | -114.496 | -118.785 | stable GT advantage, 8/8 launches |
| E3 general BaseMul | -12.833 | -13.824 | small stable GT advantage |
| E4 add + two serializations | +87.857 | +85.029 | largest stable encap debt, 0/8 negative launches |
| E5 hash/glue | -7.257 | -11.206 | common/noisy, not an optimization target |
| **full deterministic encap** | **+170.998** | **+150.823** | **GT loses all 8 launch medians in both placements** |

The PMU corroboration uses 10,000 region calls and records core cycles,
instructions, retired loads, and retired stores in both placements.  It is a
directional corroboration rather than a serious benchmark: separate-process
setup baselines and event multiplexing make the smallest regions unsuitable
for exact subtraction.  The full GT caller retires about 75--517 fewer
instructions but 785--844 more loads and 22--33 more stores per call.  E2
reduces instructions strongly; E4 increases both instructions and loads.
This agrees with the TSC ranking and identifies representation delivery, not
extra arithmetic, as the remaining encap debt.

Keygen is deliberately coverage-aware rather than a synthetic full-caller
claim.  K1 and K6 are shared controls.  K2 two-Forward attribution saves
70.324/72.144 TSC.  The missing GT phases have the following Official short
costs:

| Keygen phase | normal Official TSC | reversed Official TSC | GT coverage |
| --- | ---: | ---: | --- |
| K3 two BaseInv | 1342.045 | 1342.096 | missing |
| K4 two general BaseMul | 680.146 | 740.961 | blocked on K3 representation |
| K5 three serializations | 418.303 | 418.033 | blocked on K4 representation |

No Official-vs-GT keygen total is reported: there is still no GT32 BaseInv J1
implementation or byte-exact full keygen caller.  The next keygen gate is not
the already-hard-stopped `F0 x J1 -> P0 -> Official pack` family.  Q24 changes
the consumer boundary, so the valid reopen is `BaseInv -> J1 AoS`, then
`F0 x J1 -> R1-U AoS e=0 -> Q24 GT-pack`, measured as the complete K3--K5
region.  The encap continuation is separately bounded to E4: first compare a
consumer-native `BM + add(m) -> GT-pack` region, and reject any giant fused
symbol that loses the compact/reusable scheduling shape.

The follow-up E4 split changes that continuation from a fusion hypothesis to
a precise serializer contract.  Region-scoped PMU (20,000 calls) and TSC give:

| E4 subregion | core-cycle GT-Official normal/reversed | TSC normal/reversed |
| --- | ---: | ---: |
| E4a add(m) | inconclusive tiny shared kernel | -0.045 / -0.091 |
| E4b serialize rhat | +22.61 / +23.50 | +12.371 / +12.362 |
| E4c serialize chat | **+98.33 / +102.23** | **+60.765 / +60.139** |

E4c also retires 302--314 extra instructions, 152--158 extra loads, and
51--53 extra stores.  The first implementation gate is therefore a compact,
reusable high-range private-SoA ciphertext Q24 GT-pack.  It is not a
BM/add/pack mega-kernel.  E4b may be revisited only after E4c because its
23-core-cycle debt is much smaller.

Artifacts:

- `results/tile4-keygen-encap-attribution-short.json`
- `results/tile4-keygen-encap-attribution-pmu.json`
- `src/tile4_kem_encap_candidate.c`
- `bench/bench_keygen_encap_attribution.c`

### Encap high-range private-SoA Q24 GT-pack

The E4c follow-up first freezes a typed range contract rather than silently
reusing the lazy10788 name.  The implementation-shaped proof starts from two
N5 private-SoA operands with bound 10788.  B3 general pays its mandatory
`Mont(R^2)` scale finalizer, yielding coefficient-plane bounds
`[1792,1838,1888,1911]`; adding the N5 `m` operand gives
`[12580,12626,12676,12699]`.  The resulting ABI is therefore:

```text
private BM SoA, e=0, |word| <= 12699
    -> Official canonical 1152-byte ciphertext
```

The existing `v=9` reduction is exact on this complete interval and produces
`[-2328,2328]`, so one sign correction remains sufficient.  Exhaustive scalar
tests over `[-12699,12699]`, 1,000 mixed-lane vectors, guard-page/canary
checks, and 100 deterministic complete encapsulations are byte-exact.  The
proof additionally records that this reducer happens to cover the complete
signed-int16 domain, but the public encap symbol deliberately keeps the
narrower 12699 contract.

Only two bounded schedules were emitted.  H1 is a five-byte typed tail jump to
the already placement-qualified packet-first reducer.  H2 reduces four source
planes before the transpose; it has the same 48 vector reductions and adds a
4,543-byte body.  Against the old grouped-bridge plus Official-pack control:

| candidate | normal TSC | reversed TSC | normal/reversed core cycles |
| --- | ---: | ---: | ---: |
| H1 | **-44.34** | **-44.48** | **-125.47 / -78.21** |
| H2 | -39.92 | -40.11 | -88.75 / **+22.54** |

H1 is selected and H2 is stopped: H1 lowers core cycles, retired
instructions, and loads in both placements, while H2 reverses direction in
the primary metric.  The selected H1 boundary is integrated into the opt-in
encapsulation candidate; E4b remains unchanged.

Fresh eight-launch full-caller TSC now places GT32 at `+28.97` TSC normal and
`+65.85` TSC reversed relative to Official, down from the earlier
`+170.998/+150.823`.  It therefore substantially closes E4c but does not
promote the whole encapsulation backend.  No 100k serious benchmark was run.
The next action is fresh residual phase attribution, not another pack variant
or a BM/add/pack mega-kernel.

Artifacts: `tools/generate_q24_encap_highrange.py`,
`generated/tile4_q24_encap_highrange_gate.json`,
`generated/tile4_q24_encap_highrange.inc`,
`results/tile4-keygen-encap-highrange-short.json`, and
`results/tile4-keygen-encap-highrange-pmu.json`.

### Fresh residual encap attribution and E4b bounded close

After selecting H1, the phase harness measures the selected symbols directly
instead of attributing the old bridge.  Sixteen-launch paired TSC gives the
following GT-minus-Official residuals:

| phase | normal | reversed |
| --- | ---: | ---: |
| E1 Decode/CBD/SOTP | +12.08 | +11.90 |
| E2 two N5 Forwards | **-115.83** | **-120.45** |
| E3 general B3 | **-13.35** | **-11.95** |
| E4b serialize rhat | +12.47 | +20.97 |
| E4c selected H1 residual | +15.60 | +22.96 |
| E5 hash/glue | +12.86 | +17.11 |
| full encap | +63.79 | +60.30 |

Four independent 20,000-call PMU runs use the median run as the primary
microarchitecture evidence.  E4b is the only individual phase above the
predeclared 30-core-cycle continuation threshold in both placements:
`+67.94/+35.02` core cycles.  E4c is `+36.82/+21.24`, and E1 is
`+22.88/+23.70`.  E2 and E3 remain wins and frozen.  Full-caller and common
hash PMU values remain sensitive to runtime/placement, so they are not used to
invent a new arithmetic experiment.

The one permitted E4b bounded gate asks whether the CBD provenance makes the
Forward-produced `rhat` small enough to omit Q24's `v=9` reduction.  It does
not.  A deterministic probe using the real `poly_cbd1` producer finds a valid
`4042` word in the first trial and a maximum observed absolute word of 12,884
over 10,000 trials.  Thus the sign-only centered encoder, whose exact domain
requires `|x| <= 3456`, is invalid for this callsite.

The remaining alternatives do not delete work.  A standalone reduce pass
keeps all 144 vector reduction instructions and adds 48 loads plus 48 stores;
moving the same reductions to the Forward terminal removes 144 instructions
from pack but adds the same 144 instructions to Forward.  Neither has a new
acceleration mechanism, so no assembly variant is emitted.  The current
packet-first `v=9` reducer is retained; it is exact over the complete signed
16-bit domain and leaves `|x| <= 3291` for the final sign correction.

Encap micro-optimization is therefore closed in the parity band.  Its reopen
condition is a producer that deletes the complete reduction chain, a consumer
that no longer requires canonical bytes, or a different ISA with a cheaper
packed reduction.  The next major gate is the already-defined keygen
`BaseInv -> J1 AoS -> F0 x J1 R1-U -> Q24 GT-pack` path, not another E2/E3 or
serializer scheduling variant.

Artifacts: `results/tile4-keygen-encap-residual-attribution-short.json`,
`results/tile4-keygen-encap-residual-pmu.json`,
`generated/tile4_encap_rhat_pack_gate.json`,
`tools/generate_encap_rhat_pack_gate.py`, and
`tests/probe_encap_rhat_range.c`.

### K3-A executable BaseInv J1 typed ABI

Keygen now owns explicit C types for the two scale domains rather than relying
only on prose: `gt32_f0_aos_e0_t` and `gt32_baseinv_j1_aos_e1_t`.  The only
declared producer for the latter is `gt32_tile4_baseinv_j1_aos_ref()`, and its
only future arithmetic edge is `F0 e=0 x J1 e=1 -> R1-U e=0`.  No P0 or
Official-layout redeposit is part of this ABI.

The K3-A implementation is a fixed-control scalar correctness reference, not
a performance candidate.  It visits all 192 physical quartic leaves directly
in TILE4 AoS, applies the existing lambda relabeling, returns `a^-1*R`, and
uses one whole-output mask when any determinant is zero.  Its executable
differential covers 1,000 random small-polynomial Official NTT/BaseInv cases,
the all-zero failure case, and `out == in` aliasing.  Every successful word
equals `centered(OfficialBaseInv(word) * R)`; failure return and complete-zero
output are identical.  ASan/UBSan pass.  Disassembly contains only the public
fixed-count leaf/vector/tile/output loops, with no data-dependent early exit.

This upgrades the previous generator-only scale argument into an executable
typed semantic checkpoint.  It does not claim BaseInv performance and is not
integrated into keygen.  K3-A passes; the next implementation task is a native
AVX2 TILE4-AoS J1 schedule.  Its first performance endpoint is K3-B
`BaseInv -> J1 -> F0 x J1 R1-U`, not isolated BaseInv.  Q24 GT-pack is appended
only after K3-B passes.

Artifacts: `src/tile4_baseinv_j1_ref.c`,
`tests/test_tile4_baseinv_j1.c`,
`tools/generate_keygen_j1_typed_gate.py`, and
`generated/tile4_keygen_j1_typed_gate.json`.

### K3-B native J1 BaseInv plus R1-U gate

K3-B implements a reusable AVX2/intrinsic `gt32_tile4_baseinv_j1_aos_avx2`
symbol.  It keeps TILE4 leaf order, locally transposes four AoS vectors into
16 independent quartic lanes, uses the existing quartic inverse formula, and
emits centered `BASEINV_J1_AOS_E1` directly.  Its denominator inversion uses
the same six independent two-vector hierarchical batch topology as Official;
the public final `Mont(x,1)` fixes the simple-batch reciprocal from `e=5` to
the J1-required `e=4`.  The numerator finalizer then emits `e=1`.  The native
symbol passes the same 1,000-trial, zero, and alias differential as K3-A, plus
ASan/UBSan (LeakSanitizer disabled because it is unavailable under the runner
ptrace environment).

The performance endpoint contains the two real keygen edges, not isolated
BaseInv: two BaseInv operations followed by `g*finv` and `f*ginv`.  A0 is
reported only for attribution, `consumer` measures the two downstream BMs,
and A1 is the promotion gate.  Twenty paired PMU samples in both link orders
give:

| region | normal core-cycle delta | reversed core-cycle delta | wins |
| --- | ---: | ---: | ---: |
| A0: 2x BaseInv | +538.898 | +546.824 | 0/20, 0/20 |
| consumer: 2x BM | +288.988 | +283.679 | 0/20, 0/20 |
| A1: 2x BaseInv + 2x BM | +781.440 | +782.788 | 0/20, 0/20 |

A1 TSC also regresses by `+453.771/+453.947`.  All bootstrap 95% intervals
are strictly above zero.  Critically, the consumer alone loses about 284--289
core cycles; even a hypothetical BaseInv at exact Official parity cannot make
the J1/R1-U edge win.  Reaching the continuation floor of -50 core cycles
would require J1 BaseInv to beat Official BaseInv by roughly 334 cycles, while
the measured producer is instead about 543 cycles slower.  Therefore K3-B is
a cycle-level hard stop and K3-C/Q24 is not run.

The typed K3-A ABI and correctness implementation remain useful research
artifacts, but neither native J1 nor R1-U is selected for keygen.  Reopen only
if a new producer/consumer mechanism first demonstrates at least 330 core
cycles of structural saving; store/reload fusion or rescheduling the same
quartic/batch DAG is insufficient.

Artifacts: `src/tile4_baseinv_j1_avx2.c`,
`bench/bench_keygen_j1_k3b.c`, `tools/run_keygen_j1_k3b.py`, and
`results/tile4-keygen-j1-k3b-pmu.json`.

### GT32-N5-I1-SUPEROPT-001 bounded S4/S5 wavefront

The arithmetic freeze was opened only for two same-DAG scheduling probes.
W1 completes S4 and its dependent S5 immediately for each pair, minimizing
live range.  W2 retains a two-pair S4 cadence and interleaves ready S5 work
before later S4 pairs.  Constants, Montgomery-chain count, range, private-SoA
output, plane redeposit, and all consumer kernels are unchanged.  Both
candidates are word-exact for the Forward core and the complete
`2F+B3+I1+T9` chain.

The normal-placement necessary PMU gate fails:

| candidate region | core-cycle delta | bootstrap 95% CI | TSC delta |
| --- | ---: | ---: | ---: |
| W1 Forward core | +13.312 | [-28.536, +36.607] | +0.753 |
| W2 Forward core | +16.650 | [-3.035, +20.116] | +7.218 |
| W1 `2F+B3+I1+T9` | +25.372 | [+23.162, +28.947] | +11.589 |
| W2 `2F+B3+I1+T9` | +31.141 | [+23.005, +44.364] | +16.129 |

Neither Forward candidate reaches the required -5 core cycles, while both
consumer chains are significantly slower.  W1 removes the four-independent-
S4-chain window by following each S4 with its dependent S5.  W2 preserves
some S4 ILP but extends later-pair lifetimes; its S5 work still cannot issue
until the corresponding S4 completes.  The out-of-order core already extracts
the useful ILP from the adjacent control S4 macros, so source-level wavefront
ordering creates no independent work and only constrains scheduling.

The sequential necessary gate therefore stops the experiment before reversed
placement.  N5/I1 arithmetic and local scheduling remain frozen.  Reopen only
for a mechanism that removes a complete multiply/reduction/shuffle chain or a
producer/consumer boundary, not another topological order of these same S4/S5
instructions.

Artifacts: `tools/run_s45_wavefront.py` and
`results/tile4-s45-wavefront-pmu.json`.

### GT32-FWD-LANDING-BASEINV-001

This gate tested the three linked Forward-terminal hypotheses without
reopening N5/B3/I1 arithmetic.  The existing P terminal is the first exact
progressive cut: Stage 4 keeps its packed sums/differences and Stage 5 lands
directly in coefficient planes.  It removes 48 terminal shuffles per Forward;
the previously measured standalone benefit is real but small (`3.402 TSC`).

The original `1728`-uniform core-entry range model was rejected by the first
executable probe.  The current wide-raw frontend can reach `5232`, so the new
generator exhaustively enumerates the `[-3,4]` raw top split, twist and DFT3,
then propagates each tile/Q bound through NTT32.  The ordinary P terminal has
a conservative bound of `17724`.  Searching whole-YMM checkpoint placement
finds one minimal two-vector schedule: center vectors 0 and 4 immediately
after S1.  It proves a terminal bound of `9586`, below the direct BaseInv
product limit `10643`; 1,000 executable trials observed at most `8364`.

The checkpointed Forward costs `+17.641 TSC` versus the ordinary P Forward
(`0/20` wins), so it passes only the predeclared `+20 TSC` downstream-
amortization gate.  The consumer gate then instantiates the mature GTN SoA
BaseInv unchanged except for P-lane lambda metadata.  No data repair or
center-on-load pass is used.  Results are:

| region | paired delta | MAD | wins |
| --- | ---: | ---: | ---: |
| P-lane SoA BaseInv, direct vs center-on-load | `-78.686 TSC` | `6.659` | 20/20 |
| full Forward landing + BaseInv | `-57.805 TSC` | `7.221` | 19/20 |

Thus all three hypotheses pass this bounded gate.  The conclusion is not that
GTN-L3 and TILE4 NTT are identical: their early/middle transforms and physical
packetization differ.  The useful equivalence is at the terminal semantic
ABI—both can expose coefficient planes, and leaf-order differences are
absorbed by lambda metadata.  This remains benchmark-only pending a complete
keygen endpoint including the SoA multiplication and Q24 pack.

Artifacts: `tools/generate_forward_landing_baseinv.py`,
`generated/tile4_forward_landing_baseinv_gate.json`,
`generated/tile4_baseinv_p_tables.inc`,
`src/tile4_baseinv_p_soa.c`,
`src/tile4_permutation_relaxed_asm.S`,
`results/tile4-forward-landing-baseinv-short.json`, and
`results/tile4-forward-landing-baseinv-chain-short.json`.

### GT32-KEYGEN-SOA-ISLAND-001

The next gate closes the arithmetic island at the same semantic endpoint for
two keygen edges.  The control executes two Official Forwards, two Official
BaseInv operations and two Official BaseMul operations.  The candidate uses
the checkpointed progressive-P Forward, direct P-lane SoA BaseInv and the
mature native SoA BaseMul.  No Q24 serialization is included yet.

The generated semantic-word map compares every candidate output against the
corresponding Official leaf/degree word.  All 1,000 random trials passed,
including BaseInv status and both multiplication outputs.  The same-binary
10,000-iteration PMU gate used 20 alternating pairs in normal and reversed
link placement:

| placement | region | core-cycle delta | bootstrap 95% CI | wins | TSC delta |
| --- | --- | ---: | ---: | ---: | ---: |
| normal | 2 Forward + 2 BaseInv | `-597.011` | `[-636.940, -584.804]` | 19/20 | `-377.968` |
| normal | 2 native SoA BaseMul | `-85.631` | `[-105.276, -77.376]` | 17/20 | `-53.961` |
| normal | complete arithmetic island | `-765.336` | `[-818.554, -708.036]` | 20/20 | `-479.447` |
| reversed | 2 Forward + 2 BaseInv | `-619.489` | `[-664.670, -550.736]` | 20/20 | `-402.400` |
| reversed | 2 native SoA BaseMul | `-72.336` | `[-88.986, -63.018]` | 19/20 | `-49.791` |
| reversed | complete arithmetic island | `-738.299` | `[-760.764, -691.396]` | 20/20 | `-465.941` |

The complete island also retires about 3,100 fewer instructions and 741 fewer
stores per two edges, although it executes about 312 more retired loads.  The
result passes the predeclared `-50` core-cycle continuation threshold in both
placements.  It overturns only the AoS J1/R1-U keygen architecture: BaseInv is
not intrinsically unsuitable for GT32, but its efficient AVX2 execution shape
is coefficient-plane SoA.  The candidate remains benchmark-only until the
Q24 serialization endpoint and full keygen failure/clearing semantics pass.

The immediate serialization probe also establishes that the qualified
standard-private-SoA Q24 body cannot be tail-called directly: progressive-P
uses a different physical Q/lane order, and the first differential trial
correctly rejects that substitution.  The next bounded gate must generate a
P-aware Q24 route (or explicitly pay and measure a P-to-standard repair); it
must not treat the two SoA ABIs as byte-identical.

Artifacts: `bench/bench_keygen_soa_island.c`,
`tools/run_keygen_soa_island.py`,
`generated/tile4_baseinv_p_mapping.h`, and
`results/tile4-keygen-soa-island-pmu.json`.

### GT32-KEYGEN-P-Q24-001

The serialization closure keeps hypotheses A/B/C frozen and generates a
direct progressive-P-aware Q24 route.  After the existing four-plane
transpose, every wire packet consists of one 128-bit half from each of two
registers.  One `vperm2i128` per packet creates the carrier consumed by the
unchanged qualified lazy10788 reducer and packet packer.  The route therefore
adds exactly 48 cross-lane shuffles, needs no global P-to-standard pass and
uses no spill.  Three keygen outputs pass 1,000 random byte-exact differential
trials against Official serialization.

The 10,000-iteration, 20-pair PMU closure includes normal and reversed link
placement.  Because adding the Q24 body changes the binary layout, the
arithmetic region is remeasured in that same binary rather than copied from
the prior result:

| placement | region | core-cycle delta | bootstrap 95% CI | wins | TSC delta |
| --- | --- | ---: | ---: | ---: | ---: |
| normal | arithmetic island | `-191.320` | `[-224.169, -179.339]` | 17/20 | `-115.956` |
| normal | three serialization endpoints | `+176.950` | `[+161.128, +194.425]` | 1/20 | `+78.894` |
| normal | island + serialization | `+16.270` | `[-20.783, +38.414]` | 8/20 | `+23.293` |
| reversed | arithmetic island | `-201.965` | `[-332.351, -153.880]` | 20/20 | `-116.457` |
| reversed | three serialization endpoints | `+170.172` | `[+145.093, +186.075]` | 0/20 | `+99.681` |
| reversed | island + serialization | `-9.117` | `[-65.470, +10.551]` | 13/20 | `-1.093` |

Thus direct P-aware serialization is correct and bounded, but it consumes the
measured arithmetic advantage and leaves the common endpoint at parity with
confidence intervals crossing zero.  A/B/C remain architecture-qualified;
the full progressive-P keygen path stops before production integration.  A
reopen requires a packet route that removes the 48 half-merges (for example a
different consumer-shaped terminal permutation), not a standalone global
P-to-standard repair or rescheduling of the same route.

Artifacts: `generated/tile4_q24_p_encode.inc`,
`generated/tile4_q24_p_encode_gate.json`,
`src/tile4_q24_codec_asm.S`, and
`results/tile4-keygen-soa-island-q24-pmu.json`.

### GT32-KEYGEN-P-Q24-D1-D2-001

The follow-up isolates the 128-bit half-pairing debt.  D1 re-runs the exact
S4/S5 terminal-family search with wire packet co-residency as the objective.
All 24 legal full-SoA terminal candidates still require four packet-half
merges per 16-quartic block; the repair distribution is exactly `{4: 24}`.
There is therefore no zero-merge wire-paired terminal inside the existing
no-extra-shuffle Forward family.  D1 stops statically.

D2 keeps progressive-P unchanged.  After the four-plane transpose, each
source YMM is reduced and packed in place; a lane-local `vpshufb` independently
orders its two qword pairs, and the two packed 12-byte halves are stored to
their respective packets.  It removes every `vperm2i128` carrier without
creating a source-first giant kernel, changing the reducer, or spilling.
All three keygen serializations are byte-exact in 1,000 random trials.

Against the D1 merge-pack in the same binary, D2 pack-only saves `73.008` and
`72.140` core cycles in normal/reversed placement.  Against Official, the
complete arithmetic-island plus three-pack endpoint gives:

| placement | core-cycle delta | bootstrap 95% CI | wins | TSC delta |
| --- | ---: | ---: | ---: | ---: |
| normal | `-51.858` | `[-65.715, -21.548]` | 15/20 | `-44.999` |
| reversed | `-69.695` | `[-86.682, -53.186]` | 16/20 | `-40.472` |

D2 is therefore performance-qualified at the polynomial endpoint.  A final
deterministic caller adds SHAKE, CBD/triple and `hash_f`.  At 48 pairs it
retires about 2,900 fewer instructions in both placements, but the small
latency signal remains placement-sensitive:

| placement | core-cycle delta | bootstrap 95% CI | TSC delta | TSC CI |
| --- | ---: | ---: | ---: | ---: |
| normal | `-91.718` | `[-160.612, +114.200]` | `-27.681` | `[-41.884, +33.853]` |
| reversed | `-178.947` | `[-231.825, -98.818]` | `-104.606` | `[-114.660, -71.272]` |

Consequently D2 is retained as a qualified component, while whole-keygen
production promotion remains inconclusive.  A/B/C are unchanged.  Further
work must address full-caller placement/delivery or demonstrate the same
benefit in the actual retry/clearing entry point; no additional half-pairing
or packet arithmetic search is justified.

Artifacts: `generated/tile4_terminal_layout_family_gate.json`,
`generated/tile4_q24_p_encode.inc`,
`generated/tile4_q24_p_encode_gate.json`,
`results/tile4-keygen-soa-island-q24-halfscatter-pmu.json`,
`results/tile4-keygen-q24-halfscatter-vs-merge-pmu.json`, and
`results/tile4-keygen-full-p2-halfscatter-serious.json`.

### GT32-KEYGEN-PRODUCTION-G1-G2-001

A production-shaped closure freezes A/B/C/D2 and adds the lifecycle omitted
from the component gate.  G1 executes deterministic SHAKE sampling with a
known-invertible f/g pair, both retry checks, the full arithmetic island,
three serializations, `hash_f`, production-sized stack frames and hardened
clearing.  G2 consumes an identical deterministic candidate stream in the
Official and GT callers and records f/g attempt counts.  Across 1,024 random
streams every Official/GT status and pk/sk byte matched.  No natural retry was
observed in that sample (`retry_f=retry_g=1`); a targeted zero-g test separately
checks identical noninvertible status and complete zero-output semantics.

The 48-pair normal/reversed production result is:

| gate | placement | core-cycle delta | bootstrap 95% CI | TSC delta | TSC CI |
| --- | --- | ---: | ---: | ---: | ---: |
| G1 single attempt | normal | `+110.549` | `[+57.417, +193.206]` | `+122.163` | `[+75.560, +148.876]` |
| G1 single attempt | reversed | `+73.374` | `[-17.037, +155.640]` | `+75.571` | `[+23.000, +108.221]` |
| G2 shared stream | normal | `-44.633` | `[-134.297, +10.120]` | `-31.379` | `[-51.796, -11.198]` |
| G2 shared stream | reversed | `+127.964` | `[+63.718, +219.274]` | `+99.163` | `[+58.246, +134.806]` |

GT retires roughly 2,500 fewer instructions and about 420 fewer stores per
call, but performs about 910--923 additional retired loads.  The G1/G2
placement inversion remains after controls that remove clearing, move scratch
from stack to global storage, and reuse one h buffer.  Therefore neither
clearing byte count nor stack-frame size is the sole cause; the remaining
problem is whole-caller delivery/cache/code-placement interaction.  The
production promotion gate fails.  A/B/C/D2 remain qualified and frozen, while
the whole GT keypair caller remains benchmark-only.  Reopening requires a
production-compatible caller/code-layout rule that makes both placements'
core-cycle confidence intervals negative; it must not alter the frozen
arithmetic or D2 packet route.

Artifacts: `bench/bench_keygen_production.c`,
`results/tile4-keygen-production-g1-g2-pmu.json`,
`results/tile4-keygen-production-clear-attribution.json`, and
`results/tile4-keygen-production-frame-attribution.json`.

### GT32-KEYGEN-INTEGRATION-TAX-ATTR-001

The final reopen gate instruments one production-shaped G1 caller with six
cumulative semantic checkpoints.  C1 ends after the f sampling/Forward/BaseInv
attempt, C2 after the corresponding g attempt, C3 after the first BM+pk pack,
C4 after the second BM+two sk packs, C5 after `hash_f`, and C6 after hardened
clearing.  A/B/C/D2 are unchanged.

The 48-pair cumulative core-cycle deltas are:

| checkpoint | normal | reversed |
| --- | ---: | ---: |
| C1 f attempt | `-32.321` | `+9.423` |
| C2 both attempts | `-40.713` | `+11.131` |
| C3 first BM+pack | `+20.438` | `+39.289` |
| C4 all BM+packs | `+6.044` | `+152.548` |
| C5 plus hash | `+83.221` | `+118.197` |
| C6 plus clear/return | `+92.117` | `+92.645` |

Adjacent median differences identify no placement-stable 100-cycle phase.
Normal's largest addition is C4->C5 (`+77.177`, hash/context), while reversed's
is C3->C4 (`+113.259`, the second BM+pack boundary).  Hash then removes
`34.351` cycles in reversed, and clearing adds only `8.896` in normal while
removing `25.552` in reversed.  Thus the integration tax migrates with whole
code placement instead of belonging to one arithmetic, hash, or clearing
phase.  No eligible hot-cluster experiment has a stable >=100-cycle target.

Under the predefined stop rule, NTRU+768 AVX2 keygen optimization is closed.
A/B/C/D2 remain preserved qualified components and the polynomial endpoint
remains a GT win, but the public keygen backend remains Official.  Reopening
requires a new target ISA/microarchitecture or independently demonstrated
production-level delivery mechanism, not local arithmetic, layout, alignment,
or another linker-order search.

Artifact: `results/tile4-keygen-production-cumulative-serious.json`.

### GT32-REP-FAMILY-001

The production keygen stop may be reopened only by a structural mechanism,
not another uniform leaf permutation or a reschedule of A/B/C/D2.  This
generator-only gate therefore evaluates the 128-bit microtile family between
TILE4 and full coefficient-plane SoA.  Its primary candidate is Pair02/E–O:
each half contains four leaves and the degree pairs `(a0,a2)` or `(a1,a3)`.
The representation is persistent across producer, BaseInv, BaseMul and wire
delivery; operands are not reconstructed at the BaseMul entry.

The generator proves all Pair01/02/03 maps are bijections and proves the
Pair02 quadratic-tower product equals quartic schoolbook multiplication by
324 bilinear basis/sign tests.  With the qualified progressive-P bounds, the
largest two-term `vpmaddwd` accumulators are `183782792` for Forward×Forward
and `67178688` for Forward×BaseInv, both safely inside signed 32-bit.  A direct
Pair02 dot produces one leaf per dword and requires no `vphaddd` or algebraic
cross-128 repair.

Pair01 is wire-adjacent and Pair03 may align some wrapped terms, but neither
directly exposes BaseInv's `(a0,a2)` / `(a1,a3)` quadratic inputs; both would
reintroduce degree-pair regrouping without a demonstrated compensating
mechanism.  TILE4 is the already-rejected AoS keygen control and full SoA is
the qualified A+B+C+D2 baseline, leaving Pair02 as the only continued family.

This is not the old pair-native BaseMul experiment.  That experiment paid a
48-instruction operand-construction pass at the BaseMul boundary.  Persistent
Pair02 removes that premise and permits a new direct `vpmaddwd`/REDC16 DAG, so
the old hard stop is recorded but deliberately not reused.

The optimistic whole-keygen static accounting is nevertheless very narrow:

| term | instructions |
| --- | ---: |
| two Pair02 BaseInv minimum extra vs full SoA | `+216` |
| progressive Forward landing minimum extra | `+48` |
| three Pair02 Q12 wire endpoints maximum saving | `-288` |
| optimistic Pair02 BaseMul delta vs B3 | `0` |
| **best-case net** | **`-24`** |

The BaseInv lower bound excludes lambda-companion formation, determinant
packing for the 16-lane batch inverse, loads/stores, loop control and register
moves.  Consequently Pair02 passes only the first generator filter; it is not
assembly-qualified and does not reopen the frozen production components.
Before any ASM, a bounded one-block exact-DAG gate must prove the complete
BaseInv and BaseMul routes, the progressive landing/range chain, peak at most
16 YMM registers and no spill.  It must also retain a credible mechanism for
at least 100 core-cycle polynomial-endpoint improvement over A+B+C+D2 in both
placements.  If the excluded work consumes the 24-instruction headroom, the
representation family stops statically.

Artifacts: `tools/generate_rep_family_gate.py` and
`generated/tile4_rep_family_gate.json`.

### GT32-BASEINV-OFFICIAL-REUSE-O1-O2-001

O1 mechanically compares all 768 semantic words in progressive P-SoA and
the Official BaseInv input.  Both use exactly `12 blocks × 4 degree planes ×
16 leaves`; degree-plane grouping is identical and the leaf permutation is
independent of degree.  The `e=0` contract is unchanged and the P terminal
bound `9586` remains below the direct BaseInv product limit `10643`.

Calling the unmodified Official symbol is nevertheless invalid: every P
block contains leaves belonging to exactly two Official blocks, so neither an
outer block permutation nor a different call order can reproduce its physical
ABI.  A P-native clone needs no data transpose, however.  The quartic schedule
can remain lane-wise while P-ordered lambda/qinv metadata supplies the correct
leaf constants; batch inversion is order-independent.  O1 therefore passes
for arithmetic-DAG reuse and fails for a direct symbol call.

The implementation audit found that the qualified A+B+C benchmark had only
compiled `tile4_baseinv_p_soa.c` as C/intrinsics.  O2 consequently enables the
existing `gt_baseinv_native_prepare_asm.S`, which generalizes Official's
quartic schedule to one generated P-native lambda vector per block.  It keeps
Forward, batch inversion, SoA BaseMul and D2 unchanged.  One thousand random
trials pass in both link placements, including BaseInv status and downstream
BaseMul semantics.

Paired 10,000-iteration PMU results compare this ASM directly with the
intrinsic P-SoA control in the same binary:

| placement | region | core-cycle delta | 95% CI | wins | TSC delta |
| --- | --- | ---: | ---: | ---: | ---: |
| normal | two Forward+BaseInv | `+43.558` | `[+36.688,+106.588]` | 2/20 | `+23.869` |
| normal | plus two SoA BaseMul | `+44.454` | `[+38.575,+53.021]` | 1/20 | `+27.917` |
| reversed | two Forward+BaseInv | `+51.673` | `[+49.708,+57.860]` | 0/20 | `+31.121` |
| reversed | plus two SoA BaseMul | `+63.071` | `[+59.632,+76.243]` | 0/20 | `+31.684` |

The ASM retires roughly 60--68 more instructions while eliminating about 98
loads and 103 stores per region.  Thus its compact one-block generalized
schedule does not retain the paired scheduling advantage of the exact
Official implementation; lower memory traffic does not compensate for the
extra control/schedule work.  O2 is a measured hard stop.  A two-block unroll
could at best recover roughly this small instruction debt and has no credible
path to the predeclared 30--50 core-cycle improvement over the intrinsic
control, so it is not implemented.  The intrinsic P-SoA BaseInv remains the
qualified A+B+C component.  Pair02 remains a separate exact-DAG-only proposal.

Artifacts: `tools/generate_baseinv_official_compat.py`,
`generated/tile4_baseinv_official_compat_gate.json`, and
`results/tile4-keygen-baseinv-official-reuse-pmu.json`.

### GT32-PAIR02-EXACT-DAG-TILE-001

O2 establishes that representation compatibility must include execution
tiling.  The Pair02 continuation therefore extends the typed state from
`(R,B,e)` to `(R,B,e,T)` and compares the exact primitive dependency graphs
needed by BaseInv, rather than using the earlier `-24` instruction estimate as
performance evidence.

A full-width P-SoA two-term expression consists of two independent Montgomery
products and one add: its optimistic floor is 11 instructions and dependency
depth 5.  Pair02 performs one `vpmaddwd`/REDC16 chain for each eight-leaf half,
then must compact dwords and merge both halves before the determinant/batch
inverse or reconstructed output can consume a 16-word vector.  Its optimistic
floor is 12 instructions and depth 7.  It therefore has neither a shorter
primitive critical path nor an eliminated reduction interface.

The execution-tile register lower bounds close the remaining ILP hypothesis:

| tile | requested initial chains | full-wave YMM lower bound | result |
| --- | ---: | ---: | --- |
| T1, one 16-leaf block | 8 half-width chains | `18` | exceeds AVX2's 16 registers |
| T2, two interleaved blocks | 16 half-width chains | `34` | cannot be resident |
| T3, current P-SoA | 6 full-width chains | qualified | measured champion |

For T1, reserving four E/O inputs, q/qinv, two lambda companions and two
compact/merge outputs leaves room for only six active half-width chains.  That
does not improve upon P-SoA's six initial full-width product chains.  T2 can
avoid spills only by loading/processing waves, which serializes the proposed
cross-block parallelism instead of creating a larger scheduling window.

Consequently the previous best-case `-24` instruction estimate is downgraded
to economically neutral.  Pair02 has no shorter critical path, no spill-free
independent-chain advantage and removes no complete reduction/determinant
interface.  It is statically stopped before ASM; A/B/C/D2 remain frozen.  A
reopen requires a consumer that keeps Pair02 results in dwords and removes
compaction, a wider-register ISA, or a factorization that deletes a complete
reduction/interface—not another Pair02 schedule or unroll.

Artifact: `generated/tile4_pair02_exact_dag_tile_gate.json`.

### Polynomial-only scope reset and P1/P2 gates

The optimization objective is now the polynomial subsystem, with Keccak,
SHAKE and KEM control flow frozen.  The primary generic KPI is `2F+B+I`.
A fresh 1,000,000-iteration PMU run against Official Main gives:

| placement | Official core cycles | GT32 R1-U core cycles | delta |
| --- | ---: | ---: | ---: |
| normal | `2723.195` | `2788.785` | `+65.590` (`+2.409%`) |
| reversed | `2731.158` | `2765.678` | `+34.520` (`+1.264%`) |

The isolated BaseMul debt remains stable at about `+200`--`+212` core
cycles.  This confirms that the project-level target is still the BaseMul
representation boundary, not a full-KEM runtime effect.

P1 tested whether N5 Stage 5 could land directly in Official's BaseMul input
vectors within a maximum budget of about 15 core cycles per Forward.  Exact
symbolic inversion of the qualified Stage-5-to-private-plane network proves a
bijection, but every Official target vector needs five or six independent
source-half routes.  The exact direct route costs 256 `vperm2i128`, 256
`vpshufb`, 208 `vpor` and 48 stores: 720 route instructions, or 576 more than
the selected private terminal.  P1 is therefore a static hard stop and emits
no assembly.  Artifact:
`generated/tile4_forward_official_landing_gate.json`.

The pure-polynomial scope changes the old ABI-003 Phase-C decision.  Its best
typed inverse-entry packet, `I-112-pair-01-orders-21430-21430-21430-21430`,
was stopped only because combined Decode/Encode weighted savings were below a
full-KEM threshold.  For the present `2F+B+I` KPI it replaces the current
144-instruction B3-output-to-inverse transition with 24 `vperm2i128`, saving
120 static instructions.  It adds no Montgomery chain or checkpoint, removes
a complete materialized transition, peaks at 15 YMM registers, needs no spill
and has a 120-byte code estimate.  It is consequently reopened only as a
bounded P2 assembly candidate.  The 120-instruction count is a filter, not
cycle evidence, and is relative to the current private-M path rather than the
R1-U benchmark.  Artifact:
`generated/tile4_polymul_joint_rescore_gate.json`.

P3's native GT64/degree-2 proposal is also closed by an optimistic static
lower bound.  Replacing one quartic product by two quadratic products saves at
most three modular products per quartic, or 36 full-YMM Montgomery chains over
192 leaves.  Extending each transform from 32 to 64 points necessarily adds
one radix-2 layer over 384 coefficient-word butterflies.  Even granting one
complete identity-vector exemption, this costs at least 23 chains per
transform and 69 across `2F+I`.  The net is therefore at least 33 additional
chains (132 vector instructions at the four-instruction Montgomery floor),
before extra add/sub, routing or range costs.  This is a static hard stop for
the proposed AVX2 `2F+B+I` path.  The older GT16 quadratic experiment is only
empirical corroboration because its topology differs.  Artifact:
`generated/tile4_gt64_d2_static_gate.json`.

P4, the keygen algebraic rewrite, passes its exact algebra/retry-cost gate.
Once `f` is known invertible, `h=g*f^-1` is invertible exactly when `g` is,
and `h^-1=f*g^-1`.  The accepted path can therefore replace
`BaseInv(g)+BM(g,finv)+BM(f,ginv)` with `BM(g,finv)+BaseInv(h)`, deleting one
BaseMul.  If `p` is the probability that a sampled `g` is invertible, the new
minus old expected cost after `f` is `(1/p-2)*BM`, so it wins for `p>1/2`.
Existing production-shaped samples observed one attempt per success, but that
is supporting evidence rather than a probability proof.  The next bounded
step is caller-level C correctness/cycle measurement with forced failures and
exact retry counts; no assembly change is needed.  Artifact:
`generated/tile4_keygen_bm_elimination_gate.json`.

### NTT32-first / split-twist gate

`GT32-N32FIRST-SPLIT-TWIST-001` tests the proposed axis exchange before any
assembly is emitted.  The axes themselves commute, but the proposed scalar
identity does not: the frontend uses `s^-n` with
`n=(64*n3+33*n32) mod 96`, while both branch scales have order 576 rather
than 96 (`2^96=723`, `22^96=2735 mod 3457`).  Consequently the unreduced
product split misses a carry factor in 83 of 96 coordinates and has six
distinct carry values per branch.

The generator repairs the proposal exactly by conjugating each row's full
32-entry diagonal twist into the CT network.  It uses the high/low residual
ratio on every butterfly and verifies all 96 basis vectors for both branches
against current `twist -> DFT3 -> NTT32`.  The repaired transform is exact,
signed-int16 safe and ends at conservative bounds 5373/5522, inside B3's
10788 contract.

The repaired schedule still loses the static AVX2 gate.  Qualified N5 uses
160 full-width Montgomery chains: 48 full-twist, 16 DFT3 and 96 NTT32.
N32-first uses 120 row-conjugated NTT32, 32 residual-T3 and 16 DFT3 chains,
for 168 total, or eight extra chains/32 instructions at the four-instruction
floor.  No conjugated stage-1 lane is identity.  Moreover zero-debt DFT3
consumption would require three 8-YMM rows (24 data YMM before temporaries),
so a compact AVX2 implementation adds a row materialization boundary.

The candidate is therefore stopped before ASM.  It may reopen only with an
exact two-chain residual-T3/DFT3 circuit plus no extra row materialization, or
with an ISA providing at least 24 data vector registers plus temporaries.
Artifact: `generated/tile4_n32first_split_twist_gate.json`.

### N32-MR-S3LOCAL mixed-radix gate

`GT32-N32-MR-S3LOCAL-001` evaluates the corrected mixed-radix proposal with
the integer coordinate `n=r+3*m`.  Unlike the stopped PFA split, its twist
factorization `s^-n=s^-r*(s^-3)^m` is exact and has no mod-96 carry.  The
generator proves both branch transforms over all 96 basis vectors against a
direct 96-root evaluation.  The output permutation is frequency
`bitreverse5(Q)+32*k3`, and all conservative bounds remain signed-int16 safe.

The proposed baseline nevertheless fails before ASM.  Its arithmetic floor is
168 full-width Montgomery chains versus N5's 160.  More importantly, the
previously uncosted 12-Q suffix begins with the AVX2 three-way deinterleave

```text
[0..3] [4..7] [8..11]
  -> [0,3,6,9] [1,4,7,10] [2,5,8,11].
```

A mechanically verified constructive route needs seven `vpermq` and six
qword blends per branch/block: 13 instructions, 208 over one Forward.  That is
112 more routing instructions than the 96 `GT_BLEND3` instructions it was
intended to remove.  This is an upper bound rather than a global minimum, but
it disproves the claimed free row-major transition.

The conservative radix-3 terminal bounds are 16271/16147.  They are int16
safe but exceed B3's qualified 10788 input contract, so the baseline also
needs a new high-range BM proof or a reduction checkpoint.  Assembly is not
emitted.  The mixed-radix family remains generator-only and may continue only
as a joint S4/S5/radix3/BM-entry search that eliminates the explicit 13-op
route, absorbs the wider range, stays within 16 YMM without spills and repays
the eight-chain arithmetic debt.

Artifact: `generated/tile4_n32_mr_s3local_gate.json`.

### Pure-GT NTT32-first PFA gate

`GT-N32-PFA-NATIVE-001` keeps explicit twist and uses the exact PFA coordinate
`n=64*r+3*q`, `k=32*k3+33*k32`.  All cross terms vanish modulo 96.  The
generator verifies both branches over all 96 basis vectors against direct
root evaluation, and the nominal arithmetic count is exactly N5's 160
full-width Montgomery chains.  Thus the MR eight-chain debt is genuinely
absent.

The unchanged N5 reducer schedule is not legal after swapping the axes.
Explicit twist gives bounds 1799/1797, NTT32-first grows them to 10933/10929,
and the final cheap cyclic DFT3 has `Y0=x0+x1+x2` bounds 32799/32787.  Those
exceed signed-int16 by 32/20.  Pure axis commutation therefore does not imply
range-schedule commutation; a new reducer placement is required.

The physical suffix is also more fragmented than the proposed three-vector
picture.  For every four-frequency group, its 12 `(r,q)` values occupy nine
natural YMM vectors and 12 distinct 128-bit halves.  S1--S3 do retain 48
whole-YMM/same-lane edges per stage, but S4 and S5 change qword lanes.  The
straight correctness implementation additionally needs three polynomial
passes versus N5's two.

No assembly is emitted.  Pure-GT mathematics and the 160-chain target remain
valid, but implementation stays generator-only until a joint lazy-range plus
S4/S5/DFT3/BM layout proves int16 safety without a full checkpoint, two memory
phases, at most 16 YMM and no canonical suffix materialization.

Artifact: `generated/tile4_n32_gt_pfa_native_gate.json`.

### Pure-GT joint coordinate/stage-order gate

`GT-N32-PFA-JOINT-002` enumerates all 32 axis-automorphic PFA embeddings and
places DFT3 after S3, S4 or S5 while retaining the 160-chain limit.  DFT3
after S3 and S4 is range-safe, ending at 25887/25875 and 29380/29368;
DFT3-last remains unsafe at 32799/32787.

The best physical coordinate uses `B=33` (`u=11`).  Every four-frequency
component then touches only three YMM and six halves instead of nine/twelve.
This is, however, the same geometry already exploited by current
`n=64*r+33*q` and `GT_BLEND3`: it moves the 96 blends to the middle rather
than deleting them.  The naive implementation also remains three-phase.
Consequently range and coordinate selection pass, but no new static
acceleration mechanism is established and no ASM is emitted.  Reopening needs
a joint DFT3/S4 or DFT3/S5 network below six blends per branch/block, a proven
two-phase register schedule, or elimination of a complete BM terminal
conversion.  Artifact: `generated/tile4_n32_gt_pfa_joint_gate.json`.

### Pure-GT final half-native / wave-producer gate

`GT-N32-FINAL-003` evaluates the last two mandatory acceleration mechanisms
without emitting assembly.  At fixed `B=33`, exhaustive whole-half selection
proves that three `vperm2i128` instructions cannot form legal DFT3 packets:
the two qwords in every natural half require different `r` input
permutations.

The packet search nevertheless finds a real local improvement.  Five
`vpblendd` instructions form three DFT3 inputs whose low halves use
`(r0,r1,r2)` and high halves use `(r0,r2,r1)`.  The high-half reflection only
swaps the `k3=1/2` output labels, introduces no scale debt, retains the
JOINT-002 signed-int16 bounds, and fits in eight YMM including the DFT3
temporary and `q`.  Thus the half-native idea is not empty: its DFT3
preparation falls from six blends to five.

The original producer decision inferred a 17-YMM lower bound from the rank-16
final matrix plus the temporary used by the current Montgomery macro.  That
inference is withdrawn.  Matrix rank and dense final support do not determine
the live frontier of a factored destructive DAG, and the artificial S3 cut
also excludes immediate suffix/BM consumption.  What remains stopped is only
the exact zero-spill, 6144-byte, isolated-producer formulation as currently
constructed; it is not an architecture-level impossibility result.

The family therefore remains open but narrowly scoped to `B=33` and the
five-blend half-native ABI.  The next gate must pebble the actual
top/twist/S1--S5/DFT3/BM-consume DAG and compare C0 destructive zero-spill,
C1 one source reload per wave, and C2 one controlled spill/reload.  The
96-byte C1 and 192-byte C2 figures are optimistic lower-bound relaxations;
actual source reconstruction and temporary-slot counts remain unallocated.
Neither byte count alone is a valid reason to reject an executable
`Forward -> BM -> inverse` island.

Artifacts: `generated/tile4_n32_gt_suffix_superopt_gate.json`,
`generated/tile4_n32_gt_wave_producer_gate.json`, and
`generated/tile4_n32_gt_final_gate.json`.

### NTT32-first half-native BaseMul island gate

`GT-N32-BM-ISLAND-004` now tests the first real consumer boundary instead of
closing the family from the artificial S3 cut.  The five-blend terminal ABI
uses `(r0,r1,r2)` in the low 128-bit half and `(r0,r2,r1)` in the high half.
The latter is only a physical `k3=1/2` label swap.  A generated lambda stream
absorbs that swap, so the qualified R1-U qword-local arithmetic consumes all
192 quartic leaves with zero runtime repair, no new Montgomery chain and no
new reduction checkpoint.

The benchmark-only symbol `gt32_n32_basemul_half_r1u_asm` is bit-exact to the
standard-order R1-U after semantic relabeling.  A scalar NTT32-first reference
also matches the qualified N5 Forward modulo q after half-native relabeling for
64 random small-input trials.  One thousand random BM trials and both alias
orientations pass.  A same-binary short benchmark also establishes cycle
parity for the landing itself:

| placement | half-native minus standard R1-U | MAD | wins |
| --- | ---: | ---: | ---: |
| normal | -0.802 TSC | 2.589 | 13/20 |
| reversed | +0.349 TSC | 1.880 | 9/20 |

The inverse-side label proof also passes: heterogeneous low/high fixed-factor
vectors let IDFT3 interpret physical `[0,1,2]` in the low half and `[0,2,1]`
in the high half without a repair shuffle or an additional Montgomery chain.
This is an algebra/static result; native inverse assembly is still pending.

This is deliberately not a full-island performance claim.  It proves that the
half-native output ABI reaches BaseMul without paying back the saved terminal
blend.  The producer remains the unresolved part.  C1's 96-byte/Forward figure
assumes that one 32-byte source YMM is sufficient to reconstruct the omitted
branch vector; the real frontend may need both low and high source halves plus
recomputation.  C2's 192-byte/Forward figure similarly assumes exactly one
spill/reload slot per wave.  Their optimistic route deltas are respectively
-26 and -20 instructions over two Forwards, but neither is a complete
instruction schedule.  The next implementation must allocate the factored
top/twist/S1--S5/DFT3 DAG and benchmark C1/C2 through `2F+BM+I` before the
NTT32-first family can be promoted or rejected.

Artifacts: `generated/tile4_n32_gt_bm_island_gate.json`,
`generated/tile4_n32_gt_bm_island_constants.inc`, and
`results/tile4-n32-bm-island-short.json`.

### NTT32-first physical R0--R4 closure

`GT-N32-PHYSICAL-SCHEDULE-005` turns the fixed-layout register-pressure
question into an executable AVX2 probe.  R0 is not allocatable with the
current multiply temporary, R1 needs both source vectors rather than the
previously assumed 32-byte reconstruction, R2 does not free an architectural
YMM at the S1--S3 cut, and R4 is dominated by the measured R3 schedule.

R3 is exact and executable: it uses one controlled full-YMM spill/reload per
`n3` wave, destructive raw S1, a one-temporary serial S2/S3 for the first
branch and the normal parallel schedule for the second.  One thousand exact
and alias trials pass.  The same-binary short benchmark measures the actual
cost of this repair:

| region | normal candidate-control | reversed candidate-control | wins |
| --- | ---: | ---: | ---: |
| one S1--S3 wave | +3.858 TSC | +3.804 TSC | 0/20, 0/20 |
| five- vs six-blend suffix route | -2.981 TSC | -2.816 TSC | 20/20, 20/20 |
| three waves plus route | +8.592 TSC/Forward | +8.597 TSC/Forward | derived |

Thus the fixed-layout R-series is closed: the fifth suffix blend is a real
local win, but it does not repay the three-wave register-pressure tax.  This
does not close NTT32-first mathematics or a different execution geometry.
Artifacts: `generated/tile4_n32_physical_schedule_gate.json`,
`src/n32_wave_schedule_asm.S`, and
`results/tile4-n32-wave-schedule-short.json`.

### NTT32-first stage-native tile gate

`GT-N32-STAGE-NATIVE-TILE-006` searches the proposed 8/10/12-data-YMM
execution geometry without treating semantic relabeling as a physical
shuffle.  It regenerates every S1--S3 twiddle from the logical `q` carried by
the current slot and proves 32 component basis vectors exactly modulo `q`.
Two concrete AVX2 packet families are checked:

* a four-component, eight-YMM cohort keeps each component in one qword lane
  and requires no S1--S3 inter-stage shuffle;
* a component-local representation uses two YMM per component.  S1->S2 is
  exactly two `vperm2i128`, and S2->S3 is exactly two
  `vpunpcklqdq`/`vpunpckhqdq`, or four physical routes per component.

The current packet families do not pass the assembly filter:

| candidate | physical benefit | blocking cost |
| --- | --- | --- |
| T0, 8 YMM | zero S1--S3 route | capacity four cuts the connected six-component producer/DFT3 graph; avoiding a new materialization replays at least 48 source loads per Forward, versus R3's six spill memory instructions |
| T1, 10 YMM | peak 11 YMM with the Montgomery temporary | five components still do not close producer/DFT3, while component-local transitions add 96 routes per Forward |
| T2, 12 YMM | all six `(n3,branch)` components close and DFT3 can consume directly | 96 inter-stage routes plus 144 extra source loads for four separately executed qword-lane tiles exceed the complete 80-blend suffix credit by 160 instructions before output redeposit |

No assembly is emitted.  This is a static rejection of these concrete
packetizations, not a global AVX2 impossibility proof.  Reopening requires a
packet that deletes a complete producer/S1--S3 wave, a standalone Forward ABI
that makes narrow source packets reusable without replay, a new factorization
with a smaller closure frontier, or a wider register/SIMD ISA.  Artifact:
`generated/tile4_n32_stage_native_tile_gate.json`.

### NTT32-first half-native inverse gate

`GT-N32-NATIVE-INVERSE-007` changes the intended decision unit from an
isolated Forward to the eventual `2F + half-native R1-U + inverse` island.
The half-native layout itself passes exactly: the low 128-bit half carries
`k3=[0,1,2]`, the high half carries `k3=[0,2,1]`, lane-typed inverse-DFT3
factors absorb that reflection with no new Montgomery chain, and the reverse
route to the six natural InvNTT32 components needs five blends instead of the
current six.  InvNTT32 twiddles depend on the logical q edge, not the k3 or
branch label, so no additional inverse table or permutation repair is needed.

The current R1-U range contract fails when inverse DFT3 is moved before the
raw length-2 butterfly.  Exhausting all 128 `(physical q, coefficient)`
interval contracts gives an exact independent-interval IDFT3 output bound of
`19387`.  The adjacent q=30 and q=31 c3 contracts admit the same extremum, so
the raw length-2 contract admits a sum of `38774`, outside signed int16.  This
is a typed-contract witness; it does not claim that one BaseMul input realizes
every interval extremum simultaneously.

The cheapest known proof-safe repair centers the four pair-packed high arms
before length 2.  Across six inverse tiles this costs `4 * 6 * 3 = 72`
instructions.  It reduces the high-arm bound to `2719` and proves the complete
length 2/4/8/16/32 chain at `22106, 23953, 26082, 28331, 30728`, but the full
native-route credit is only 16 blends, leaving a static delta of +56 before
other boundary costs.  Keeping IDFT3 late avoids the checkpoint but exposes
only the measured five-vs-six-blend proxy of about 2.8--3.0 TSC, below the
roughly 17.2 TSC estimated debt of two R3 Forwards.

No inverse assembly or `2F+B+I` benchmark is emitted.  R3 is an executable
S1--S3 wave microprobe, not a complete executable N32 Forward, so reporting a
full-island measurement here would be incorrect.  Reopening requires a fused
IDFT3-times-length2 circuit that absorbs the repair into an existing
reduction, a BaseMul representative that is proof-safe without a separate
finalizer, a complete N32 Forward with a new execution geometry, or a wider
register/SIMD ISA.  Artifact:
`generated/tile4_n32_native_inverse_gate.json`.

### Fused IDFT3 x length-2 and safe-representative gates

`GT-N32-IDFT3-L2-FUSED-008` refines the previous global bound by output row.
The exact R1-U independent-box bounds are `12919, 19387, 19387`.  Row 0 is
safe at the first raw length-2 boundary, while rows 1 and 2 have 17 unsafe
coefficient/q-pair lanes each; coefficient 3 makes all 16 physical q pairs
unsafe.  At current AVX2 packing this means 16 immediate high-arm vector
repairs, or 48 instructions.  Row 0 cannot be ignored: without a later repair
its length 2/4/8/16/32 chain reaches
`25838, 27705, 29882, 32205, 34710`, so eight later vector repairs add another
24 instructions.  The cheapest known complete schedule therefore remains 72
instructions.

The bounded joint-circuit candidates do not remove that operation:

* commuting length 2 before IDFT3 is algebraically exact and its first output
  bound `21120` is safe, but the following IDFT3 `r1 +/- r2` frontier reaches
  `42240`;
* reusing the two existing IDFT centers and two Montgomery differences leaves
  the wide row-1/2 output representatives unchanged;
* CT reduces the high arm but adds 16 Montgomery chains (64 immediate
  instructions, 88 including row 0), while GS leaves an unsafe raw sum;
* a nontrivial row scale cannot be free because every IDFT row contains the
  untouched `r0` coefficient; only `+/-1` is chain-free and range-neutral;
* all signed-int16 representatives `w+kq` of the IDFT twiddle were checked;
  the best dangerous-row witness bound is `19358`, still above the required
  `13380`.

`GT-N32-R1U-SAFE-REP-009` independently checks the producer side.  Even an
idealized per-k3 choice between unsigned R1-U and signed R1-S over all eight
combinations has a best dangerous-row witness bound of `19386`.  A constant
q bias cannot make both the length-2 sum and difference narrower.  Centering
one complete k3 stream reaches only `14462`; two streams still leave one row
above target, while all three streams cost an estimated 144 instructions.
The existing REDC16 signedness choice changes the representative but does not
compute the second quotient required to narrow its approximately 17663-wide
c3 interval.

Neither gate emits assembly.  They reject the current CT/GS, commute, scale,
twiddle-representative and same-REDC-DAG families, not every possible six-input
modular circuit.  Reopening requires a circuit that shares an existing
reduction across the tensor axes, a tighter producer-realizable joint-range
proof, or a BM partial-accumulator/finalizer change that supplies the second
quotient without adding a new chain.  Artifacts:
`generated/tile4_n32_idft3_l2_fused_gate.json` and
`generated/tile4_n32_r1u_safe_rep_gate.json`.

### Inverse IDFT3 insertion-point gate

`GT-N32-INVERSE-INSERTION-010` checks all six boundaries around the five
InvNTT32 stages instead of assuming that inverse DFT3 must be first.  The
three-point and 32-point transforms commute exactly: all 96 basis vectors at
each of P0--P5, 576 executions in total, match modulo q.  No inter-axis
twiddle, new Montgomery chain or k3-reflection repair is required.

The current R1-U independent interval contract nevertheless rejects every
insertion point:

| point | inverse lengths before IDFT3 | prefix bound | IDFT3 internal bound | IDFT3 output bound | decision |
| --- | --- | ---: | ---: | ---: | --- |
| P0 | none | 10560 | 21120 | 19387 | later InvNTT32 range failure |
| P1 | 2 | 21120 | 42240 | 37050 | IDFT3 and later range failure |
| P2 | 2,4 | 22535 | 45070 | 39980 | IDFT3 range failure |
| P3 | 2,4,8 | 24312 | 48624 | 43883 | IDFT3 range failure |
| P4 | 2,4,8,16 | 26068 | 52136 | 47419 | IDFT3 range failure |
| P5 | 2,4,8,16,32 | 28053 | 56106 | 51543 | IDFT3 range failure |

The key correction to the proposed P2/P3 mechanism is that an existing
inverse Montgomery operation reduces only the high butterfly multiplicand.
The low arm remains an accumulating representative, so the whole state is
not freshly reduced at a stage boundary.  Moving IDFT3 later therefore makes
its independent-box input progressively wider rather than repairing it.
P5 also fails the formal range gate; its approximately 2.8--3.0 TSC route
proxy would in any case not repay the approximately 17.2 TSC estimated debt
of two R3 Forwards.

No assembly or benchmark is emitted.  This does not reject a tighter
producer-realizable joint range: the independent interval witness can ignore
correlations between values produced by one BaseMul.  That route remains a
valid reopen condition, but a complete executable N32 Forward is not yet
available and random trials cannot replace a proof.  Other reopen conditions
are a reduction policy that narrows all butterfly outputs, or a bounded
checkpoint whose complete physical cost is below the measured producer debt.
Artifact: `generated/tile4_n32_inverse_insertion_gate.json`.

### Producer-specific BM to inverse range gate

`GT-N32-BM-INV-JOINT-RANGE-011` separates the already-qualified physical and
scale ABI from the numerical representative contract.  The P0--P5 control
used the reusable N5/B3 Forward envelope of 10788; that is a valid generic
contract but is not the generated row-conjugated N32-first producer's actual
bound.  Binding the same half-native R1-U to that producer gives branch/k3
bounds of `[5373,5367,5295]` and `[5522,5341,5488]`.

The gate regenerates every lambda-product bound and exhausts the unsigned
REDC16 output interval for all 768 `(branch,k3,q,degree)` contracts.  Current
R1-U then reaches at most 5318, rather than the generic-envelope IDFT3 bound
of 19387.  Exact independent-box propagation through the typed inverse gives:

| frontier | maximum absolute bound | signed int16 safe |
| --- | ---: | --- |
| R1-U output | 5318 | yes |
| typed IDFT3 internal add/sub | 10493 | yes |
| typed IDFT3 output | 8880 | yes |
| inverse length 2 | 17760 | yes |
| inverse length 4 | 19581 | yes |
| inverse length 8 | 21637 | yes |
| inverse length 16 | 23752 | yes |
| inverse length 32 | 26043 | yes |

This result is stronger than the proposed joint-correlation proof: no
cross-leaf correlation is required, because the tighter producer-specific
independent interval box already passes the complete inverse.  The physical
half-native ordering, `e=0 x e=0 -> e=-1` scale, current unsigned R1-U
REDC16, and zero-checkpoint inverse ABI can all remain unchanged.

A separate bit-exact concrete producer search covers 64 structured inputs,
100,000 random polynomial pairs and 12 x 20,000 greedy mutations.  Its best
observed length-2 frontier is 10390 and it finds no overflow.  This search is
recorded only as corroboration; the generated interval chain above is the
safety proof.

The qualification is conditional on implementing the exact generated
row-conjugated reduction policy.  A different producer schedule must rerun
the proof.  At the time of this gate a complete executable N32 Forward did not
exist; `GT-N32-FORWARD-CHAIN-014` below implements it and also corrects this
gate's hidden residual-row-0 identity-reduction assumption.  No
assembly or cycle benchmark is emitted by this gate; the next eligible work
is the typed half-native IDFT3 plus InvNTT32 assembly, followed eventually by
a complete-producer `2F+B+I` benchmark.  Artifacts:
`generated/tile4_n32_bm_inv_joint_range_gate.json` and
`generated/tile4_n32_bm_inv_joint_range_search.json`.

### Typed half-native IDFT3 plus InvNTT32 assembly

`GT-N32-INVERSE-ASM-012` implements the producer-specific range pass as an
executable AVX2 symbol.  It does not first repair the high 128-bit half into
canonical row order.  Instead it freezes the physical row action
`P(q)=[0,1,2]` for qwords 0/1 and `P(q)=[0,2,1]` for qwords 2/3:

* two group packets run the existing bit-exact `IDFT3_V2` operation order in
  parallel;
* raw inverse length 2 is consumed immediately in the reflected streams;
* inverse length 4 is the only edge crossing the two `P(q)` classes.  Row 0
  uses an ordinary pair-packed butterfly, while rows 1/2 use one crossed
  pair that reconstructs `[S1|D2]` and `[S2|D1]` directly;
* lengths 8/16/32 preserve `q mod 4`, so the qualified I1 tables and
  four-chain cross-register schedule apply unchanged to each reflected
  component tile.

The generator checks all 96 basis vectors against logical
`IDFT3 -> InvNTT32` and exhaustively verifies the signed-word IDFT difference
oddness over `[-10493,10493]`.  Thus the row reflection is exact at the
representative level, not merely modulo q.  The ASM correspondence preserves
the proved arithmetic order and adds no standalone center, checkpoint,
Montgomery chain, YMM spill, or canonical row materialization.  The only
center is the one already intrinsic to the frozen `IDFT3_V2` schedule.

The typed output is component-major reflected inverse rows,
`((branch*3+slot)*8+group)`, still at `e=-1`, for the future untwist/top
reconstruction.  The complete and IDFT helpers require disjoint input/output;
the L8--L32 suffix supports in-place use.

One thousand exact-word trials, including complete generated interval-box
min/max patterns, pass with canaries and an unchanged input buffer.  The
largest observed frontiers are below the formal bounds:

| frontier | observed | formal bound |
| --- | ---: | ---: |
| IDFT3 internal | 10493 | 10493 |
| IDFT3 output | 8612 | 8880 |
| L2 | 15499 | 17760 |
| L4 | 17026 | 19581 |
| L8 | 16956 | 21637 |
| L16 | 18512 | 23752 |
| L32 | 19535 | 26043 |

The short isolated benchmark is attribution only:

| placement | combined inverse | combined - split | wins | IDFT3+L2+L4 | L8+L16+L32 |
| --- | ---: | ---: | ---: | ---: | ---: |
| normal | 266.886 TSC | -0.938 TSC | 16/20 | 151.613 | 117.414 |
| reversed | 268.600 TSC | +0.177 TSC | 9/20 | 151.573 | 117.569 |

The split/combined difference is effectively neutral, so the result should
be read as an approximately 267--269 TSC executable typed inverse, not as an
architecture promotion.  The required next gate remains a complete
executable N32 Forward followed by `2F + half-native R1-U + inverse`.
Artifacts: `generated/tile4_n32_inverse_asm_gate.json`,
`generated/tile4_n32_inverse_constants.inc`, `src/n32_inverse_asm.S`, and
`results/tile4-n32-inverse-asm-short.json`.

### Complete N32-first Forward and `2F+B+I` architecture gate

`GT-N32-FORWARD-CHAIN-014` closes the last executable hole in the NTT32-first
path.  `gt32_n32_forward_half_conjugated_asm` consumes ordinary small
coefficient-order input and emits the frozen group-major half-native quartic
ABI at `e=0`; the same half reflection is then consumed by the qualified
R1-U BaseMul and native inverse.

Implementing the exact physical schedule exposed a hidden inconsistency in
the older `GT-N32-BM-INV-JOINT-RANGE-011` accounting.  Its 5.3--5.5k producer
bound applies Montgomery reduction to residual row 0 even though that factor
is Montgomery identity and the stated 168-chain cost omits the chain.  If the
identity chain is really omitted, the Forward bounds become
`[15807,15801,15729]` and `[16008,15827,15974]`; R1-U reaches 19097 and an
independent-box typed-IDFT3 difference reaches 34319, so the zero-checkpoint
claim is not signed-int16 safe.

The executable candidate keeps the 168 nonidentity Montgomery chains and
centers only the 16 typed row-0 packets before DFT3.  This costs 48 vector
instructions, rather than centering all 48 output packets.  Regenerated bounds
are:

| frontier | maximum absolute bound | signed int16 safe |
| --- | ---: | --- |
| Forward branch 0, k3 0/1/2 | 5977 / 5971 / 5899 | yes |
| Forward branch 1, k3 0/1/2 | 6126 / 5945 / 6092 | yes |
| R1-U output | 5747 | yes |
| typed IDFT3 internal/output | 11336 / 9736 | yes |
| inverse L2/L4/L8/L16/L32 | 19472 / 21306 / 23385 / 25532 / 27876 | yes |

One thousand small-input trials pass exact mod-q comparison with N5, the
generated per-branch/k3 bounds, guards, unchanged-input checks and `out==in`.
The largest observed conjugated Forward representative is 5366.

The same-binary short benchmark uses a common post-InvNTT32+IDFT3 semantic
endpoint.  Raw and full-centered Forward remain attribution controls; the
whole N32 chain uses only the proved row-0-centered conjugated producer.

| region | first normal delta | first reversed delta | repeat normal delta | repeat reversed delta |
| --- | ---: | ---: | ---: | ---: |
| one conjugated Forward | +7.736 | +7.662 | +19.809 | +22.513 |
| two conjugated Forwards | +17.102 | +19.391 | +20.638 | +44.243 |
| half-native BaseMul | +0.830 | +2.262 | +3.090 | -7.025 |
| common inverse | -21.880 | -24.064 | -30.262 | -30.959 |
| **complete `2F+B+I`** | **+1.382** | **-3.960** | **-0.099** | **+5.898** |

The repeat ran at roughly twice the absolute TSC per region, so its component
deltas must not be averaged with the first launch.  It is retained as a
runtime/frequency sensitivity control.  The latest machine-readable artifact
contains the repeat launch and its paired samples.

The executable architecture is therefore correct and approximately at
parity, but it has no placement-stable performance case: normal and reversed
link order disagree on the whole-chain winner.  No 100k benchmark is run and
the NTT32-first path is not promoted.  This closes the current AVX2 physical
schedule, not the mathematics or half-native ABI.  Reopen only if a tighter
producer-correlated proof safely deletes the row-0 checkpoint, a schedule
removes the extra eight nonidentity chains or controlled spill traffic, a
downstream consumer eliminates a complete boundary with more than the observed
parity margin, or the target ISA/register file changes.  Artifacts:
`generated/tile4_n32_forward_asm_gate.json`,
`generated/tile4_n32_forward_constants.inc`, `src/n32_forward_asm.S`, and
`results/tile4-n32-forward-chain-short.json`.

### Production-shaped suffix scheduling closure

`GT-N32-SUFFIX-RESCHEDULE-015` through `GT-N32-SUFFIX-MLKSTYLE-018`
tested the remaining local execution ideas exposed by the complete assembly,
without changing the transform, tables, chain count, range contract, or
external half-native ABI.

The S4-output/S5-input route was searched mechanically over a superset of
useful AVX2 qword routes (arbitrary `vpermq`, `vperm2i128`, lane-local
unpacks, and qword blends).  No two- or three-instruction construction exists;
the current two S4 reconstructs plus two S5 unpacks are a four-instruction
lower bound in that model.  Exact-word probes then measured:

| candidate versus serial suffix | normal delta | reversed delta | wins |
| --- | ---: | ---: | ---: |
| three-way S4/S5 | +5.175 TSC | +5.810 TSC | 3/20, 3/20 |
| dual/move-free DFT3 | +1.111 TSC | +0.206 TSC | 8/20, 9/20 |
| complete MLKEM-style suffix | +8.058 TSC | +8.464 TSC | 1/20, 4/20 |

The MLKEM-style candidate uses all 16 YMM registers without spilling, batches
the two row-0 centers, launches four residual chains together, interleaves the
two DFT3s, and distributes Montgomery update as
`(L+H)-C` / `(L-H)+C`.  Its conservative intermediate bounds are 10264 at S4
and 12244 at S5, and 1,000 complete suffix trials are word-exact.  It is still
slower because the current N32 suffix already uses dead inputs to avoid the
output moves that make distributed update instruction-neutral in MLKEM.  Here
the rewrite removes no route and adds 48 dynamic add/sub instructions.

Two other narrow gates also close:

* Keeping `q` in a register for twelve Branch-1 corrections saves only
  1.363/1.226 TSC (18/20 and 19/20), below the two-TSC expansion floor.
* A one-instruction lane-wise fixed `kq` row-0 bias preserves signed-int16
  safety but leaves Forward output as large as 15839, above the frozen B3
  10788 contract, so it cannot replace data-dependent center10.

The production symbol remains unchanged.  These results close local suffix
scheduling, not a future 168-to-160-chain factorization.  Artifacts:
`generated/tile4_n32_suffix_reschedule_gate.json`,
`generated/tile4_n32_suffix_mlkstyle_gate.json`,
`generated/tile4_n32_row0_fixed_bias_gate.json`,
`results/tile4-n32-suffix-reschedule-short.json`, and
`results/tile4-n32-branch1-qresident-short.json`.

### Conjugated branch-at-a-time producer gate

`GT-N32-CONJ-BRANCH-AT-A-TIME-019/020` tests a distinct solution to the
17th-register problem in S1--S3.  The shared top split is retained, but each
inactive branch is immediately stored into its existing post-S3 scratch
slots.  Each active branch then becomes a closed eight-YMM transform and all
three stages use four-way Montgomery scheduling with register-resident `q`.
No arithmetic chain, range, suffix, or external ABI changes.

Relative to the production wave, this replaces the one-vector spill with
eight stores and eight reloads: seven extra stores, seven extra loads, and
448 extra L1 bytes per wave (42 extra memory instructions and 1344 bytes per
Forward).  One thousand one-wave and complete-Forward trials are word-exact;
the complete symbol also passes alias, guard, semantic, and generated-bound
checks.

Two one-wave launches gave aggregate medians of -2.336 TSC normal (37/40
wins) and -2.097 TSC reversed (35/40).  That was sufficient to build the
complete three-wave candidate, but the gain did not scale fully:

| complete Forward | control | branch-at-time | paired delta | wins |
| --- | ---: | ---: | ---: | ---: |
| normal | 420.542 | 413.845 | -3.993 TSC | 19/20 |
| reversed | 429.659 | 426.855 | -2.093 TSC | 17/20 |

This confirms that the cleaner four-way source schedule has a real benefit,
but register renaming already hides much of the apparent serial-source cost;
the remaining 2--4 TSC per Forward does not meet the five-TSC expansion floor
and is not placement-stable enough to enter `2F+B+I`.  The implementation is
kept benchmark-only and the production symbol remains unchanged.  Artifacts:
`src/n32_branch_at_time_asm.S`, `tests/test_n32_branch_at_time.c`,
`results/tile4-n32-branch-at-time-short.json`,
`results/tile4-n32-branch-at-time-short-repeat.json`, and
`results/tile4-n32-branch-at-time-forward-short.json`.

### Branch-local raw160 architecture closure

`GT32-N32-BRANCHLOCAL-RAW160-019` evaluates the proposed architecture as a
new factorization rather than another 168-chain scheduling edit.  The shared
top split remains, but only one eight-YMM branch is active; its sibling occupies
the existing 1536-byte post-S3 scratch.  Explicit twist, raw S1, four-way S2/S3,
DFT3 at the S3 closure boundary, and the current S4/S5 mathematics give exactly
160 Montgomery chains:

| component | chains |
| --- | ---: |
| explicit twist | 48 |
| raw S1 | 0 |
| S2--S5 | 96 |
| DFT3 omega | 16 |
| **total** | **160** |

All 96 basis vectors for both branches match the qualified transform exactly;
the output remains e=0 with the current B=33 leaf map and group-major
half-native `[0,1,2]/[0,2,1]` ABI.  The branch-local schedule peaks at 13 YMM,
needs no spill, reuses the current scratch, and therefore genuinely solves the
17th-register problem.

It nevertheless fails the required zero-checkpoint consumer closure.  The
generated conservative range proof gives pre-DFT3 bounds 7153/7149 and final raw bounds
25887/25875.  These are signed-int16 safe, but exceed the frozen B3/R1-U input
contract 10788.  This is the same raw representative already exposed by the
R3 raw Forward, not a new consumer-safe representative.  A full final center
would cost 144 instructions; the 48-instruction row-0 repair belongs to the
168-chain conjugated representative and cannot simply be transplanted.

Thus checks 1, 2, 4 and 5 pass, while checks 3 and 6 fail.  No assembly or
benchmark is emitted.  This closes only `branch-local + raw160 + unchanged
consumer ABI + zero checkpoint`; reopen if a producer-correlated proof closes
raw160 through R1-U/inverse, the consumer representative contract changes, or
a selective raw160 repair costs less than the saved eight chains.  Artifact:
`generated/tile4_n32_branchlocal_raw160_gate.json`.

### Branch-local 160-chain scale-placement gate

`GT32-N32-BRANCHLOCAL-160-SCALE-PLACEMENT-022` keeps branch-local ownership,
DFT3 after S3, 160 chains, the half-native e=0 output ABI, and the existing
R1-U/inverse consumer fixed.  It searches whether an existing one-chain CT
butterfly can reduce its low arm instead of its high arm.  Both forms are exact:
the output carries a different diagonal scale, but still uses one Montgomery
chain.  The search contains all 65,536 S2--S5 H/L schedules expressible with
four uniform pair-packed decisions per stage and no lane repair.

Only 16 schedules return every output wire to the current e=0 ABI.  In every
one, S3, S4, and S5 are forced back to ordinary high-arm CT; the remaining
freedom is confined to early S2 operations.  Exact matrix comparison checks
3,072 basis executions.  The best schedule (`0x0008`) reduces the natural
output envelope only from the exact control's 25577 to 25354, still far above
the frozen B3 bound 10788.  It therefore cannot turn S5 into a final reducing
layer at the current packet granularity.

The backup consumer probe also fails.  Raw x raw has 64 physical q positions
whose conservative quartic accumulator exceeds signed 32-bit.  Centering only
the 16 k3=0 vectors of one operand repairs the accumulator, but leaves an IDFT3
internal bound 55963.  An exhaustive search over all 64 branch/k3 group masks
finds no one-sided repair that completes the existing inverse; even centering
all 48 vectors of one operand leaves terminal bound 34319.  Centering both
operands costs 288 instructions and is not credible against the 32-instruction
credit from removing eight chains.

No assembly is emitted.  This closes zero-extra-chain/zero-extra-route scale
relocation at the current pair-packed operation granularity.  It does not claim
an impossibility for mixed-lane arm placement or a nonuniform diagonal output
ABI; either may reopen the search only if its blend/repair cost is accounted
for.  Artifact: `generated/tile4_n32_branchlocal_scale_placement_gate.json`.

### Raw160 mixed-lane arm gate

`GT32-N32-RAW160-MIXEDLANE-ARM-GATE-023` performs the remaining bounded
uniform-e0 search.  A nonuniform four-qword H/L pattern can be implemented by
two `vpblendd` instructions which form the reducing and nonreducing arms; the
ordinary plus/minus destinations remain unchanged and lane-ordered factors are
generated as constants.  One packed operation is executed for two branches and
three row/k3 streams, so one mixed slot has a 12-instruction dynamic lower
bound.  The 20-instruction gate can therefore admit at most one mixed slot.

The generator exhausts every uniform schedule plus every placement of one of
the 14 nonuniform four-qword masks.  It finds 1,184 schedules which restore the
existing uniform e=0 output ABI:

| mixed slot location | schedules |
| --- | ---: |
| none (uniform controls) | 16 |
| S2 | 448 |
| S3 | 448 |
| S4 | 256 |
| S5 | 16 |

The best schedule uses one S2 mixed slot (`slot 2`, L-mask `0x4`) and costs at
least 12 extra instructions.  Its exact conservative output bound is 25224,
only 130 below the best uniform schedule's 25354 and still far above the frozen
B3 limit 10788.  Exact comparison of all 96 basis vectors on both branches
matches the qualified transform and confirms the ordinary e=0 output scale.
The schedule fits with a conservative 14-YMM peak and no spill, so register
pressure is no longer the blocker.

Direct consumer closure fails earlier than the inverse: the conservative R1-U
quartic accumulator reaches 2545000704, above signed 32-bit.  Consequently the
candidate cannot reach the existing inverse without a repair, and no assembly
or benchmark is emitted.  This closes uniform-e0 raw160 on AVX2 under the saved
32-instruction budget.  Reopen only for a proven nonuniform per-leaf typed-scale
ABI, a complete joint consumer repair below that credit, or a wider-register
ISA which changes the routing/reduction cost model.  Artifact:
`generated/tile4_n32_raw160_mixedlane_arm_gate.json`.

### Polynomial Priority 1--3 executable follow-up

The polynomial-only rescore's three priorities were tested without changing
production selectors.

Priority 1 implemented the selected `I-112` mapping, its exact reverse map,
and a bounded inverse entry.  The packet formation is indeed only 24
`vperm2i128` instructions.  The earlier generated claim that the inverse
consumer then costs zero routing instructions was not executable, however:
the qualified private inverse must first restore the M frontier with four
half permutes per tile.  A complete common-endpoint test now covers
`SoA BM -> I-112 -> inverse -> TILE4 AoS` for 1,000 trials.  Repeated short
runs place the regression at roughly 164--168 TSC across the two link
placements, with 0/20 wins in both.  The 120-instruction static saving therefore
does not survive the actual consumer and final common-endpoint contract.

Priority 2 kept the N5 arithmetic DAG and implemented the exact route from
its terminal TILE4 order to the N32 half-native BM/inverse ABI.  For each
`(branch,group)`, the route copies k3=0 and uses two `vperm2i128` instructions
to form the reflected k3=1/2 slots; all 1,000 exact tests pass.  It cannot be
absorbed into the existing N5 terminal schedule: N5 completes one eight-vector
`(k3,branch)` tile at a time, while the destination needs all three k3 tiles,
which would require 24 live data YMM before temporaries.  The materialized
route uses 32 permutes, 48 loads, and 48 stores.  The full
`2F + half-native BM + native inverse` candidate is roughly 26--36 TSC slower
across the two link placements, so this crossover is closed.

Priority 3 re-gated the proved A2-F S0 fusion with an I-112-like typed
terminal.  The arithmetic range remains valid: raw BM leaves are bounded by
465523776, `U+/-V` by 931047552, the REDC numerator by 1157602047, and the
16-bit result by 17664.  The next nontrivial inverse twiddle still reaches
660112714368 and cannot remain in signed int32.  More importantly, the safe
form changes neither the six reduction chains nor the 16-YMM one-pass live
frontier, and the measured typed packet still owes 24 inverse-entry permutes.
The split allocation can avoid spills only by rebuilding A1/D operands.
Consequently this exact combined DAG stops before assembly; its reopen rules
are a <=15-YMM pair-streaming proof including constants, a genuinely shared
dynamic pre-twiddle, a packet consumed without restoring M, or a wider ISA.

Executable measurements are in
`results/tile4-priority12-executable-short.json`; the Priority-3 proof is in
`generated/tile4_bm_s0_typed_gate.json`.  Reproduce them with
`make bench-priority12-short priority3-bm-s0-typed-generate`.

### Global per-stage physical-layout gate

`GT32-GLOBAL-PHYSICAL-LAYOUT-001` replaces the old terminal-only question
with a layered physical-state search.  A state assigns the seven semantic
bits `(c0,c1,q0..q4)` to four 16-bit lane bits and three YMM-selector bits.
All 5,040 states are available before, between, and after every Forward and
inverse NTT32 stage.  The search therefore covers frontend landing, S1--S5,
the B3 entry/output, inverse S1--S5, and the T9 entry; it does not freeze S1--S4
and optimize only S5.

Every state edge has an executable AVX2 circuit.  Lane/YMM bit transposes use
`vpunpck*` or `vperm2i128`; lane-only permutations use `vpshufb`, `vpshufd`,
or `vpermq`; YMM-selector permutations are register renames.  Crucially,
`vpunpckwd` and `vpunpckd` are modeled as their real bit cycles rather than as
arbitrary lane/YMM swaps.  Three independent scalarizations (balanced,
latency-heavy, shuffle-port-heavy) find equal multi-metric cost.  The
shuffle-heavy profile selects a different tied circuit, so the balanced
circuit is the single bounded assembly candidate rather than a claim of a
unique optimum.

The selected path progressively exchanges completed Q axes with coefficient
axes.  Forward S1/S2/S3/S5 are cross-YMM and S4 retains the qualified
pair-packed half-local shape.  The terminal is already the production private
B3 SoA layout (lane axes `q2,q3,q0,q1`, vector axes `c0,c1,q4`), B3 emits the
same layout, and the inverse performs the reverse progressive exchange while
returning exactly to the current AoS T9 entry.  There is no standalone
Forward-to-BM or BM-to-inverse repair.

Static per-tile accounting for the complete `2F+B+I` layout/arithmetic region
is:

| metric | current N5 AoS + B3 boundaries + I1 | selected | delta |
| --- | ---: | ---: | ---: |
| uops | 480 | 432 | -48 |
| shuffle-port uops | 168 | 120 | -48 |
| critical-path layers | 69 | 66 | -3 |

Across six tiles this is a static reduction of 288 uops and 288 shuffle-port
uops.  This is not a cycle prediction.  It is strong enough to pass the
bounded assembly filter: 160 Forward Montgomery chains, no new checkpoint,
peak 15 YMM, no spill, zero B3 repair, and an explicit inverse schedule.

Correctness is not inferred from conjugation alone.  The generator executes
all 128 `(degree,Q)` basis vectors through the selected physical Forward and
all 128 through the selected physical inverse, applying every emitted layout
transition, then compares the recovered semantic vectors with the qualified
five-stage matrices.  Separately, all nine `vpunpck{w,d,q}` bit-cycle circuits
and all three `vperm2i128` half/YMM circuits are simulated over all 128 words
and compared with the physical-state transition claimed by the search.  The
existing range chain remains unchanged under these
bijective lane permutations: Forward ends at 10788, centered B3 output enters
the inverse at 2359, and the inverse stage bounds remain signed-int16 safe.

The bounded generated assembly is now executable.  One thousand exact random
trials cover Forward, inverse, the complete core `2F+B+I` chain, and in-place
aliases.  A coefficient-input through T9 coefficient-output whole-only gate
then compared against the production private-SoA Forward/B3/AoS-I1 chain in
four launches and both link placements.  The latest paired launch medians are:

| placement | TSC delta | core-cycle delta | instruction delta |
| --- | ---: | ---: | ---: |
| Normal | -55.346 | -87.154 | -511 |
| Reversed | -55.176 | -87.941 | -511 |

Every launch achieved at least 18/20 TSC wins.  Thus the architecture passes
the bounded whole-chain gate.  It
also passes the 100,000-iteration hierarchical serious gate:

| placement | serious TSC delta | serious core-cycle delta | paired wins |
| --- | ---: | ---: | ---: |
| Normal | -54.807 | -90.737 | 79/80 |
| Reversed | -53.880 | -86.383 | 76/80 |

All eight launch medians and all eight core-cycle medians are negative.  The
candidate is exposed through the reusable private symbol
`gt32_global_physical_polymul_private` with an explicit aligned scratch ABI.

The same exported symbol also passes a same-binary 100,000-iteration Official
Main comparison:

| placement | Official TSC | GT32 TSC | paired GT-Official | core cycles | instructions |
| --- | ---: | ---: | ---: | ---: | ---: |
| Normal | 1704.194 | 1539.066 | -161.111 | -258.010 | -1515 |
| Reversed | 1703.393 | 1545.369 | -157.248 | -249.389 | -1515 |

This is about a 9.69%/9.28% absolute-median TSC saving.  All eight launch medians are
negative; paired wins are 79/80 and 80/80.  The Official caller copies its two
inputs before its in-place NTT, while the GT32 typed frontend writes directly
to caller scratch and preserves the inputs.  That is part of this private
caller contract and is intentionally included; this is not an isolated NTT
kernel comparison.

The candidate remains private/opt-in: no KEM selector is changed.  The current
KEM call graph has no exact `Forward x Forward -> scale BM -> inverse` edge, so
these numbers qualify the polynomial primitive, not keygen/encap/decap as a
whole.  Reproduce with
`make gt32-global-physical-layout-generate gt32-global-physical-asm-check
bench-gt32-global-physical-serious
bench-gt32-global-physical-official-serious`.

### First KEM edge: decapsulation M-native inverse

The whole `2F+B+I` source-type edge does not occur unchanged in NTRU+ KEM.
The first compatible production-shaped edge is decapsulation's first product:

```text
Q24 Decode(c,f) -> private SoA -> scale B3 -> inverse -> T9 -> crepmod3
```

An opt-in candidate therefore preserves the qualified Q24 decoders and the
persistent-SoA B3 arithmetic, changes only B3's output contract from AoS to M,
and invokes `gt32_global_inverse_core_asm` to return to the existing AoS T9
entry.  Encap is not changed because its general BaseMul is followed by add and
serialization rather than inverse; keygen is not changed because it still
requires the BaseInv/J1/general-scale contract.

Eight 10,000-iteration launches per placement give:

| placement | vs current Q24 GT | wins | negative launches | bootstrap 95% CI | vs Official |
| --- | ---: | ---: | ---: | ---: | ---: |
| Normal | -87.780 TSC | 112/160 | 8/8 | [-177.223, -17.255] | +76.370 TSC |
| Reversed | -27.166 TSC | 105/160 | 6/8 | [-49.279, +4.152] | -86.238 TSC |

The new edge is real in Normal placement but is not delivery-stable in
Reversed placement, whose launch-median confidence interval crosses zero.
Consequently `crypto_kem_dec_gt32_global_inverse_candidate` remains opt-in and
the existing KEM selector is unchanged.  The differential test covers eight
valid rounds and seven malformed/canonicality cases per round with zero
failures.  Reproduce with `make bench-gt32-global-inverse-decap-short`; the
launch-level result is in
`results/tile4-global-inverse-decap-short.json`.

### Full KEM 100k closure

The three requested KEM follow-ups are now closed against the actual typed
contracts rather than treated as missing implementation work.

For decapsulation, a four-launch 100,000-iteration gate qualifies the new
M-native inverse edge relative to the promoted Q24 GT control.  It saves
59.474/93.659 TSC in Normal/Reversed placement; all eight launch medians are
negative.  Paired 100k PMU also records -176.994/-49.445 core cycles and
exactly about 261 fewer retired instructions per call.  The complete caller,
however, remains split relative to Official: +33.689 TSC in Normal and
-89.297 TSC in Reversed.  The edge is therefore qualified internally but does
not select the whole GT decapsulation backend over Official.

For encapsulation, the typed general-BM path remains the existing
decode-to-SoA, two Forward-to-SoA, native general B3, add and high-range Q24
GT-pack pipeline.  The 100k complete-caller result is:

| placement | Official TSC | GT32 TSC | paired delta | GT wins |
| --- | ---: | ---: | ---: | ---: |
| Normal | 17534.200 | 17884.058 | +275.206 | 4/20 |
| Reversed | 17482.594 | 17630.872 | +157.303 | 3/20 |

Thus the earlier 14--16 TSC mixed-BM local signal does not justify a different
full-caller selector; the current typed SoA general-BM implementation is
correct but the GT encap backend is not promoted.

For keygen, the requested AoS `BaseInv -> J1 -> R1-U` path had already passed
1,000-trial correctness and failed its cycle gate by about 781--783 core
cycles.  The final 100k comparison therefore uses the faster qualified
progressive-P SoA BaseInv/BM plus D2 half-native Q24 implementation.  Even
that best production-shaped candidate gives:

| placement | Official TSC | GT32 TSC | paired delta | GT wins |
| --- | ---: | ---: | ---: | ---: |
| Normal | 13544.461 | 13701.951 | +179.276 | 7/20 |
| Reversed | 13299.208 | 13642.531 | +216.618 | 5/20 |

Consequently all requested gates have been implemented and measured, but the
scientific outcome is not a whole-KEM promotion.  Official remains the public
selector.  The reusable qualified pieces remain available as opt-in research
components.  Reproduce all three 100k runs with
`make bench-full-kem-serious-100k`.

### Whole-caller delivery attribution and benchmark-method change

Normal and Reversed are the same code and data linked in opposite input
orders; they are not distinct algorithms.  The resulting `.text` remapping
changes the Q24/B3/inverse/T9/caller address relationships.  Fresh paired PMU
shows that the global-inverse edge retires the same approximately 261 fewer
instructions, 41 fewer loads and 42 fewer stores in both placements, while
the DSB/MITE delivery mixture changes substantially.  L1I-stall and completed
iTLB-walk counts are negligible.  The current attribution is therefore
link-order-dependent instruction-front-end delivery, without claiming that a
specific DSB set collision has been uniquely proven.

Formal KEM benchmarks from this checkpoint use the SUPERcop method in
`/home/nuc/supercop-20260627/crypto_kem/measure.c`: single-operation adjacent
`cpucycles()` differences, 32 timings per loop, and the stabilized second
quartile.  The existing host uses `default-perfevent`.  The batched 100k
Normal/Reversed paired harness remains an attribution tool only.  Full detail
and the exact PMU counts are in
`docs/whole-caller-delivery-and-supercop.md` and
`results/tile4-global-inverse-delivery-attribution.json`.

### Formal SUPERcop export and Official comparison

The current opt-in candidate is now exported as the standalone implementation
`crypto_kem/ntruplus768/avx2-gt-global-inverse` under
`/home/nuc/supercop-20260627`.  The export contains the progressive-P keypair,
typed-SoA/Q24 encapsulation, and Q24 plus global-M-native-inverse
decapsulation entry points.  SUPERcop `try` passed for every measured run.

Two GT and two Official runs were interleaved.  Each implementation therefore
contributes 192 single-operation observations per operation (two runs, three
measure loops, 32 adjacent timings).  Applying SUPERcop's own stabilized
quartile procedure to the combined observations gives:

| operation | Official Q2 cycles | GT32 Q2 cycles | GT32 - Official | result |
| --- | ---: | ---: | ---: | --- |
| Keypair | 21528.375 | 21607.292 | +78.917 (+0.367%) | Official wins |
| Encapsulation | 28151.708 | 28025.688 | -126.020 (-0.448%) | GT32 wins |
| Decapsulation | 19459.229 | 19419.542 | -39.687 (-0.204%) | GT32 wins |

This supersedes the old batched 100k result as the formal same-host operation
comparison.  The old phase-PMU data remains useful for attribution only:
encapsulation still loses locally at input/glue and serialization boundaries,
but its two Forward calls and B3 more than recover those costs; decapsulation's
global inverse removes enough first-product edge work to leave a narrow win;
keypair still gives back its Forward advantage in BaseInv/consumer delivery,
the second multiplication and serialization, with earlier PMU data also
showing approximately 908--930 extra loads despite fewer retired instructions.

The SUPERcop compiler search selected `-O3` for GT32 and `-O2` for Official.
That is a valid per-implementation SUPERcop result, but it is not a forced
same-flag compiler experiment.  The margins are all below 0.5%, so they remain
host/toolchain-specific rather than a portable promotion claim.  Full raw-run
paths and quartiles are recorded in
`results/tile4-supercop-global-inverse-official-comparison-20260812.json`.

### Global-inverse KAT closure

The exported `avx2-gt-global-inverse` implementation also passes the standard
NTRU+768 NIST-style KAT.  `PQCgenKAT_kem` was compiled against the GT keypair,
encapsulation and global-inverse decapsulation entry points and executed all
100 AES256-CTR-DRBG-seeded vectors.  Its generated request and response are
byte-for-byte identical to the distributed canonical
`KAT/NTRU+768/PQCkemKAT_2336.req/.rsp` files.  This compares every deterministic
`pk`, `sk`, `ct` and `ss`, and the decapsulated shared secret is checked by the
generator before the response is accepted.

The response SHA-256 is
`22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.
Reproduce with `tools/run_supercop_global_inverse_kat.sh`; the structured
result is in `results/tile4-supercop-global-inverse-kat-20260812.json`.
PQCgenKAT contains valid deterministic vectors only, so malformed ciphertext
and noncanonical-input coverage continues to come from the existing
differential tests and SUPERcop `try`, rather than being attributed to KAT.
### SUPERcop crossed compiler/placement delivery gate (2026-08-12)

The formal comparison was expanded from SUPERcop's independently selected
compilers (Official O2 and GT O3) to a forced O2/O3 cross matrix.  With O2 on
both implementations, GT minus Official is `-4.312`, `-20.167`, and
`-204.500` stabilized-Q2 cycles for keypair, encapsulation, and decapsulation.
With O3 on both, the corresponding deltas are `+51.979`, `+366.208`, and
`+95.562`.  The compiler choice is therefore part of the delivery result, not
an implementation-neutral detail.

Four mathematically identical GT/O2 placements were then measured by adding
0/32/64/96 bytes before the global physical Forward/Inverse object.  Decap
beats Official/O2 in only three of four placements: `-204.500`, `+27.125`,
`-172.979`, and `-168.542` cycles.  Only the original and pad96 variants beat
Official across all three operations.  The candidate remains opt-in; the
sub-percent result is not placement-robust enough for default promotion.

The Keygen `+900` retired-load debt was also localized.  The 48-pair
cumulative PMU gate assigns about `280` extra loads to the two
sampling/Forward/BaseInv attempts, another `245-254` to the first BM+pack, and
`392-419` to the second BM+two packs.  Independent component gates close the
accounting: three Q24 half-scatter packs contribute about `540.6` loads
(`59.7%`), the two native BaseMul consumers about `178.4` (`19.7%`), and the
two Forward+BaseInv operations about `159.1` (`17.6%`).  BaseInv is not the
dominant load source; the next structural Keygen target is wire delivery,
especially the three P-SoA Q24 packs.

A separate 12-pair cache/load-pressure control shows why the load count must
not be treated as a cycle model.  GT retires another `844-860` loads per
Keygen, but incurs only `0.18-0.22` extra L1 misses and approximately zero L2
misses.  L1-miss pending/stall time changes by only about `1-5` cycles.  The
extra loads are almost entirely L1 hits: they identify the responsible code
shape, but cache-miss latency does not explain the placement-sensitive cycle
delta.  Any pack rewrite must therefore demonstrate a caller-level critical-
path or load-port benefit; static load deletion alone is insufficient.

Artifacts:

- `results/tile4-supercop-cross-compiler-20260812.json`
- `results/tile4-supercop-placement-robustness-20260812.json`
- `results/tile4-supercop-delivery-and-keygen-loads-20260812.json`
- `results/tile4-keygen-load-provenance-pmu-20260812.json`
- `tools/run_supercop_cross_flags.sh`
- `tools/analyze_supercop_matrix.py`

### SUPERcop follow-up priorities: compiler, placement, and Q24 pack closure (2026-08-12)

The compiler sensitivity is real, but it does not localize to one C translation
unit.  Compiling the complete hot glue set at O2 inside an otherwise O3 GT build
recovers most of the O3 regression: stabilized Q2 becomes `21630.458`,
`28032.708`, and `19293.042` cycles for keypair, encapsulation, and
decapsulation, versus the global-O3 control's `21636.083`, `28511.604`, and
`19524.062`.  The reciprocal global-O2 plus hot-glue-O3 build regresses to
`21704.292`, `28243.583`, and `19487.229`.  However, switching only api,
keygen, encap, or decap to O2 changes all three operations.  This is evidence
for compiler-generated code shape/address interaction, not ownership by a
single source file.

A matched 64-byte Forward/Inverse placement cage makes the same point more
directly.  All four objects have identical 6504-byte object size and 1972-byte
`.text`; only the two function offsets move by 32 bytes.  Nevertheless, moving
the inverse symbol changes encapsulation by about 205 cycles even though encap
does not call inverse.  Forward and inverse effects also reverse sign depending
on the other symbol's offset.  There is therefore no simple independent
"align Forward here, align Inverse there" rule.  The remaining delivery
variance belongs to whole-image frontend mapping and launch state.

The keygen Q24 follow-up also closes the obvious load-count hypothesis.  The
current pack already maps private P-SoA directly to the final serialized bytes;
there is no later serializer to fuse away.  A benchmark-only RR variant keeps
the pair and pack masks in `%ymm12/%ymm11`.  It is word-exact for 1,000 trials,
shrinks the symbol from 4591 to 4271 bytes, and removes about 357--360 retired
loads across the three packs with 20/20 load wins.  Yet it saves only 9.856 and
14.654 median core cycles; Normal's 95% CI crosses zero and the Reversed TSC
delta is `+2.531`.  The required 60-cycle continuation gate fails.  These loads
are inexpensive L1-hit work overlapped by the current schedule, not the keygen
critical path.

P2's proposed producer-to-final boundary is already the existing Q24 contract.
P3 three-pack interleaving is stopped statically: tripling the fully unrolled
body would create an approximately 13 KiB hot symbol, repeating the known giant
fusion failure without a demonstrated latency bottleneck.  No production
selector was changed; the RR symbol remains benchmark-only.  The consolidated
record is `results/tile4-supercop-followup-priorities-20260812.json`.

### Q24-TF1 transpose-tail orientation fusion (2026-08-12)

The next routing-specific Q24 gate succeeds.  Among the 48 half masks in one
P-SoA pack, 19 are identity (`00`) and 16 swap both qwords (`11`).  TF1 deletes
the identity instructions and absorbs each symmetric swap by reversing the two
source operands of the final `vpunpck{l,h}qdq` transpose layer.  Only the 13
asymmetric `01/10` masks remain.  Reduction, canonicalization, packet stores,
range, scale, and final 1152-byte wire format are unchanged.

The generated body therefore reduces half-routing `vpshufb` instructions from
48 to 13 and shrinks the symbol from 4591 to 4276 bytes.  It passes 1,000
production-shaped keygen differential trials.  In the direct three-pack PMU
gate it saves 73.266 core cycles Normal and 63.939 Reversed, or approximately
24.4 and 21.3 cycles per pack.  TSC improves by 35.344 and 35.143 respectively;
both core-cycle and TSC bootstrap intervals are below zero.  This exceeds the
8-core-cycle-per-pack continuation threshold and proves that P-to-wire routing,
unlike constant-load deletion, is genuine Q24 headroom.

The first complete keygen composition check is directionally positive but not
yet promotion-stable: median TSC changes are `-82.673` Normal and `-61.749`
Reversed, while the Normal core-cycle CI crosses zero and Reversed TSC CI
crosses zero.  TF1 consequently remains a benchmark-only qualified Q24
component; the production selector is unchanged.  Results are in
`results/tile4-keygen-q24-tf1-pmu.json` and
`results/tile4-keygen-q24-tf1-full-pmu.json`.

### Q24-SP1 next-block preload scheduling (2026-08-12)

SP1 preserves TF1's arithmetic, routing, stores, and instruction multiset.
After the four current-block `vpmulhrsw` quotient estimates, it issues the
next P block's four loads into `%ymm8..%ymm11`; correction,
canonicalization, packing, and stores for the current block then provide the
overlap window.  The next transpose consumes `%ymm8..%ymm11` directly, so
there are no register-copy or spill instructions.  The generated proof records
zero instruction/load/store delta and no changed range or wire semantics.

The local three-pack gate passes.  Relative to TF1, SP1 saves 60.191 core
cycles and 30.038 TSC Normal, and 59.749 core cycles and 34.334 TSC Reversed.
Both placements' cycle and TSC bootstrap intervals are below zero, equivalent
to approximately 20 core cycles per pack and well above the 5-cycle SP1 gate.
Normal and Reversed both pass 1,000-trial byte-exact differential tests.

Full-keygen delivery remains placement-sensitive.  Relative to TF1, the
complete caller changes by `-14.290` and `-153.328` median core cycles; the
Normal CI crosses zero.  A direct TF1+SP1 versus production comparison is also
non-robust and even changes TSC sign, confirming that the local scheduling win
cannot yet be promoted through the current whole-binary layout.  SP1 is kept
as a locally qualified benchmark component; production remains unchanged.
The next local research gate is TF2 exact synthesis of the remaining 13
asymmetric `01/10` routes, before a fresh placement matrix.

Artifacts are `results/tile4-keygen-q24-sp1-pmu.json`,
`results/tile4-keygen-q24-sp1-full-pmu.json`, and
`results/tile4-keygen-q24-tf1-sp1-vs-production-full-pmu.json`.

### Q24-TF2 exact residual-routing search (2026-08-12)

TF2 stops before assembly.  The generator exhaustively evaluates all 4096
orientations of the 12 word/dword/qword unpack operations for each of the 12
P blocks.  For every network it also evaluates all 256 four-vector post-mask
schedules and permits an arbitrary bijective reassignment of the eight
128-bit output halves to packet stores.  Equality is checked word-for-word on
a 64-symbol basis, rather than inferred from topology.

The minimum remains exactly 13 asymmetric repairs: per-block minima are
`[1,1,0,1,2,2,1,2,1,1,0,1]`.  This equals TF1, so neither earlier unpack
orientation nor free half-store reassignment can absorb any remaining
`01/10` repair.  TF2 therefore has zero static instruction headroom and emits
no assembly.  It may reopen only with a primitive that repairs multiple
asymmetric vectors per uop, a changed half-scatter/producer packetization, or
a wider permutation ISA.  The proof is
`generated/tile4_q24_tf2_gate.json`; generator source is
`tools/generate_q24_tf2_gate.py`.

### Same-position CRT / AUTO11 generator gate (2026-08-12)

`GT32-SPCRT-AUTO11-001` tested whether the exact same-position CRT coordinate
can remain physical instead of materializing the current
`(k3,k32)=(2r,11j)` leaf coordinate.  There is one important correction to the
informal derivation: multiplication by 11 is an output-frequency
automorphism, not an input permutation.  The NTT32 input stays in natural
`j` order.  With root `omega^11`, candidate output at physical `brv5(j)` is
exactly the current output at `brv5(11j)`.

All four initial generator gates pass.  Three source YMMs form all three
same-position row mosaics with exactly six `vpblendd` and no cross-half
shuffle.  Exhaustive basis tests prove the complete 3x32 invariant
`SP[r,j] = Current[2r,11j]`, including inverse recovery.  The natural-`j`
NTT32 geometry has whole-register butterflies at distances 16, 8 and 4,
followed by the known pair-packed distance-2 and distance-1 stages.  A
constructive routing-plus-S1 schedule peaks at 10 YMM and needs no spill.

This does not yet qualify a persistent Forward/BaseMul/inverse assembly path.
The automorphism changes coordinates but not the 160-chain raw arithmetic
representative.  Its exact branch bounds remain 25887 and 25875, above the
frozen B3/R1-U input contract of 10788.  The known full repair costs 144
instructions, so S2 is stopped before assembly.  S0 routing and S1 semantics
remain valid positive generator results; a routing-only microbenchmark is
allowed but must not be reported as a polynomial-chain candidate.  The exact
proof, regenerated twiddle/lambda manifest, geometry and reopening conditions
are in `generated/tile4_spcrt_auto11_gate.json`.

### SPCRT raw-consumer closure (2026-08-12)

`GT32-SPCRT-RAW-CONSUMER-CLOSURE-001` replaces the overly broad question
"is 25887 above 10788?" with an operation-by-operation audit of B3 and R1-U.
It retains exact raw160 per-leaf producer intervals, applies the AUTO11 leaf
reindex, and charges repair at the real AoS granularity of one three-instruction
`center10` sequence per YMM and operand.

The first-use distinction is decisive.  B3 sends both operands through a
mandatory variable Montgomery product before accumulation.  R1-U sends every
A coefficient and the direct copy of every B coefficient into raw
`vpmaddwd`; its lambda-Montgomery copy only covers wrapped terms.  R1-U's
final REDC16 is the product's required `R^-1` operation, not a separable scale
multiply which can be moved to an input for free.

For both consumers, 32 of 48 physical vectors need no input repair.  The other
16 are exactly candidate row `r=0` in both top branches.  Repairing only the A
operand for those vectors costs 48 instructions.  For B3 this is sufficient:
all B3 intermediate i16 nodes are safe, the centered B3 output is at most 2359,
and the complete inverse proof ends at bounds 15046, 16854, 18501, 20555 and
22413.  R1-U's same 48-instruction repair makes the int32 dot products safe,
but its output still gives an IDFT3 internal bound 53326 and does not close the
inverse.

This is a positive B3 consumer result but not yet an assembly promotion.  It
saves 48 repair instructions versus repairing row0 in both executable
conjugated Forward calls and the raw160 factorization saves another 64
instructions across two Forwards.  Against the qualified N5+B3 chain,
however, there is no chain or B3 credit and SP must first repay the new
48-instruction one-sided repair through cheaper producer/routing delivery.
Switching an already half-native R1-U control to B3 is statically rejected:
B3's complete loops contain about 432 more instructions, well above the
maximum 112-instruction N32 chain-and-repair credit.

No assembly was emitted.  The next bounded experiment is an S0/SP producer
same-endpoint cycle gate against N5+B3.  Continue only if it repays the
48-instruction repair with a clear cycle margin.  Artifact:
`generated/tile4_spcrt_raw_consumer_closure_gate.json`.

### SPCRT selective-B3 executable gate (2026-08-12)

`GT32-SPCRT-B3-EXEC-001` implemented the exact natural-`j`/AUTO11 Forward,
candidate-root DFT3, SP-relabelled lambda stream, and the qualified B3
arithmetic.  The only range repair is `center10` on operand A's 16 physical
row-0 vectors, emitted immediately before their Forward stores; it adds the
proved 48 arithmetic instructions and no repair loads or stores.  The raw and
repaired Forward entries share one body, and the B3 endpoint is centered AoS
`e=-1` in SP physical order.  Exact mapping, 1,000 randomized Forward/B3
trials, and Forward in-place alias tests pass.

The executable cycle gate does not promote SPCRT.  The raw two-Forward
producer retires about 244 fewer instructions and saves 24.1/27.9 core cycles
in normal/reversed placement.  The selective repair itself costs 47 net
retired instructions (48 arithmetic instructions, offset by the shared-entry
dispatch) and 34.2/34.5 core cycles.  Consequently the primary `2F+B3`
region retires about 197 fewer instructions but is slower by 5.4/6.4 core
cycles.  Median TSC deltas are +2.776/+1.303, with only 38/80 and 34/80 wins.
The SP B3 body is an arithmetic-identical clone, so the loss is already
visible at `2F + selective repair`; B3 does not create or recover the margin.

This result is a microarchitectural hard stop for the current representative:
the six-blend/natural-`j` routing saving is real, but it does not pay the
row-0 reduction critical path.  SPCRT remains mathematically and physically
valid, but is not executable-promotion eligible against qualified N5+B3.
Reopen only if the producer representative removes the row-0 repair, the B3
consumer accepts it without repair, or a target ISA makes the 16-vector
repair materially cheaper.  Artifacts are
`generated/tile4_spcrt_b3_exec_manifest.json` and
`results/tile4-spcrt-b3-exec-short.json`; implementation is in
`src/spcrt_b3_exec_asm.S`.

### SPCRT repair scheduling closure (2026-08-12)

`GT32-SPCRT-REPAIR-SCHED-001` performed the final bounded repair experiment
without changing SP mapping, AUTO11, B3 arithmetic, range, or the inverse
contract.  R0 is the original serial center chain.  R1 issues four independent
`vpmulhrsw`, four `vpmullw`, then four subtracts while retaining memory-source
constants.  R2 uses the same four-way schedule, keeps center10 and q resident
in YMM registers, and selects a compile-time repaired terminal after one
shared producer branch; raw and repaired R2 entries share the complete input
packet producer rather than duplicating it.

All three variants are bit-exact and the 1,000-trial Forward/B3 and alias gate
still passes.  Repair-only core-cycle costs in normal/reversed placement are
35.9/34.2 for R0, 32.8/33.0 for R1, and 29.1/29.0 for R2.  R2 therefore saves
about 5--7 core cycles over serial repair, but misses the <=24-cycle
continuation target.  Its net repair instruction delta is +50: the original
48 arithmetic instructions plus two constant loads.

The common-endpoint `2F+B3` result is not placement-stable.  R2 is slower by
12.1 core cycles and 6.363 TSC in normal placement, while reversed is faster
by 5.6 core cycles and 4.438 TSC.  Win counts are only 25/80 and 51/80.  R1
loses in both placements.  Thus instruction scheduling improves the local
repair, but not enough to establish an executable SPCRT win; linked placement
can still move the small residual across zero.

This closes SPCRT for the current raw160 representative.  The positive result
to retain is that raw SP routing/production is genuinely cheaper; the final
blocker is the required row-0 representative repair, not Good mapping or B3.
Reopen only when that repair disappears from the contract or a different ISA
makes it materially cheaper.  Result:
`results/tile4-spcrt-repair-sched-short.json`.

### Q24 TF1+SP1 formal SUPERcop matrix (2026-08-12)

TF1+SP1 was exported as four independent, opt-in SUPERcop implementations.
Only the three keygen P-SoA pack calls select SP1; encap and decap sources are
unchanged.  A fixed 96-byte section cage moves the SP1 body by 0, 32, 64 or
96 bytes while preserving the cage size.  Official and every candidate were
measured in the same session with forced `-O2` and `-O3`, two SUPERcop runs
per cell.  Each operation/cell therefore contains 192 observations and uses
SUPERcop's stabilized second quartile as the primary cycle estimator.  All
SUPERcop correctness and measurement checks pass.

The whole-caller result does not promote SP1.  Under `-O2`, all four SP1
placements lose keypair to Official by 96.917--116.312 cycles
(0.450--0.540%).  Under `-O3`, Pad0/32/96 win keypair by 22.625, 67.438 and
43.021 cycles, while Pad64 loses by 31.312 cycles.  Pad32/O3 is the sole cell
which wins all three operations simultaneously: keypair `-67.438`, enc
`-47.250`, and dec `-79.417` cycles relative to Official.

This is not a stable production result.  Encapsulation and decapsulation do
not call SP1, yet their measured deltas move substantially across the four
cage positions.  Compiler choice also changes the keypair sign.  The local
TF1/SP1 packet result is therefore real, but its delivery is dominated by the
broader linked-image layout.  SP1 remains benchmark-only, the production
selector is unchanged, and Official remains the default KEM implementation.

The complete aggregate is
`results/tile4-supercop-q24-tf1-sp1-matrix-20260812.json`.  Reproduction tools
are `tools/install_supercop_q24_sp1_variants.sh` and
`tools/run_supercop_q24_sp1_matrix.sh`.

### Fixed executable geometry closure for TF1/SP1 (2026-08-12)

The placement confounder was removed explicitly.  TF1 and SP1 are both
present in the same exported assembly and each occupies a fixed 5120-byte ELF
text-section cage.  The two SUPERcop implementations differ only in the three
keygen call targets.  O2 and O3 `nm` maps give identical addresses for every
hot symbol, `readelf` section maps are identical, and `objdump` changes only
implementation-name labels plus the three TF1/SP1 calls.

With two aggregate runs per cell, SP1 initially saves 109.104 keypair cycles
under O2 and 48.917 under O3.  However, functions which do not call SP1 still
move: O3 encapsulation changes by 151.396 cycles.  An ABBA-interleaved run was
therefore expanded to eight process launches per variant/compiler.  The
median of per-launch SUPERcop Q2 values gives SP1-minus-TF1 keypair changes of
`-22.042` O2 and `-32.167` O3.  These have the right sign and meet the nominal
20-cycle continuation threshold, but the negative controls remain too large:
standard-sequence encap changes by `-91.396/+9.771` and decap by
`-1.063/-35.188` cycles for O2/O3.

The stock SUPERcop measure order runs 33 keypairs before encapsulation and
decapsulation.  Operation-first controls were added using the same 32 adjacent
`cpucycles()` samples and stabilized Q2.  They still show 16--110 cycle
cross-launch differences even though the encap/decap code and all symbol
addresses are identical.  Consequently the remaining 20--32 cycle whole
keypair signal is below the attributable cross-process resolution of this
binary/host benchmark.  Fixed geometry succeeded as infrastructure; SP1 does
not pass Phase B and is now stopped.  TF1 remains the local Q24 champion, but
neither changes the production selector.

Artifacts are `results/tile4-supercop-q24-fixed-geometry-20260812.json`,
`results/tile4-supercop-q24-fixed-interleaved-20260812.json`, and
`results/tile4-supercop-q24-operation-first-controls-20260812.json`.  The
fixed-layout and control tools are under
`tools/{install,run}_supercop_q24_fixed*` and
`tools/run_supercop_q24_negative_controls.sh`.

### Keygen P1 BaseInv terminal -> BaseMul entry gate (2026-08-12)

`GT32-KEYGEN-BASEINV-BM-EDGE-P1-001` tested the first post-SP1
architecture candidate with a matched producer/consumer endpoint.  The
BaseInv adjugate, determinant computation, lane-wise batch inversion,
progressive-P layout, Montgomery domain and native quartic BaseMul are
unchanged.  The control scales the pre-sign adjugate, writes the complete
final inverse polynomial, and lets BaseMul reload it.  The candidate forms
the same four inverse planes in `ymm9..ymm12` and consumes them immediately.

This is a real whole-layer deletion.  Per edge it removes 48 final-inverse
YMM stores and 48 BaseMul inverse loads.  The scheduled candidate is a
763-byte, zero-spill loop with a 16-YMM peak.  A 1,000-trial differential
passes direct-vs-split BaseInv, materialized-vs-fused product, failure-zero
semantics and all 768 output words modulo q.

The local effect is positive but below the predeclared architecture floor.
For two keygen edges, normal placement saves 56.820 core cycles (19/20 wins)
and reversed saves 28.712 core cycles (14/20 wins).  Retired work drops by
348--368 instructions, 112--116 loads and about 112--113 stores.  TSC saves
25.859/32.324.  Therefore the deleted memory work is real, but its L1-hot
materialization cost is not large enough or placement-stable enough to
justify whole-Keygen/SUPERcop integration; the required gate was at least 50
core cycles in both placements.

P1 is retained as a benchmark-only executable proof and stopped before the
production caller.  Reopen only if the pre-sign buffer can also disappear,
batch inversion can return consumer packets directly, or this edge composes
with another whole-layer deletion worth at least 100 caller cycles.  Static
and measured details are in
`generated/tile4_keygen_baseinv_bm_edge_gate.json` and
`results/tile4-keygen-baseinv-bm-edge-pmu.json`.

### Compact three-polynomial Q24 serializer gate (2026-08-12)

`GT32-KEYGEN-Q24-PACK3-P2-001` tested the explicit compact-code reopen
condition left by the earlier 13-KiB interleaved serializer stop.  The
candidate keeps the qualified TF1 packet arithmetic and wire mapping, emits
the twelve group bodies only once, and calls each body for `h`, `f`, and
`hinv`.  Its symbol is 4,723 bytes versus 4,276 bytes for one TF1 body, so it
successfully avoids tripling the serializer code.  A 1,000-trial three-stream
byte-exact differential passes.

The executable result is a hard stop.  Relative to three calls to the reusable
TF1 serializer, the compact joint body is slower by 52.330 core cycles in
normal placement and 62.058 in reversed placement.  The bootstrap 95% CIs
are `[40.447,70.346]` and `[38.832,80.640]`, with only 1/20 and 4/20 wins.
It also retires about 166/178 more instructions, 37/38 more loads, 43/44 more
stores, and costs 35.180/37.040 additional TSC.

The compact footprint therefore does not supply an acceleration mechanism:
36 small group calls plus pointer dispatch serialize useful work instead of
creating profitable cross-stream overlap.  P2 is stopped before whole
Keygen or SUPERcop, and TF1 remains the local three-polynomial serializer.
Reopen only if a packet kernel handles all three streams without per-group
calls or tripled code, a downstream consumer removes another complete
materialized boundary, or the target ISA/microarchitecture changes.  Details
are in `generated/tile4_q24_pack3_compact_gate.json` and
`results/tile4-keygen-q24-pack3-compact-pmu.json`.

### B3 quartic-twist algebra gate (2026-08-13)

`GT32-B3-QUARTIC-TWIST-001` tested whether each production leaf
`F_q[z]/(z^4-lambda_Q)` can be twisted to the common cyclic ring
`F_q[y]/(y^4-1)` and thereby remove B3's per-leaf lambda Montgomery chains.
The production Montgomery lambda table was converted back to the ordinary
field before testing.  All 192 lambda values are distinct and all satisfy
`lambda_Q^864 = -1 (mod 3457)`.  Consequently none is a fourth power in
`F_3457`, and exhaustive root construction finds no `tau_Q` satisfying
`tau_Q^4 = lambda_Q`.  The requested `y^4-1` twist is therefore algebraically
impossible over the current base field; no assembly or benchmark was emitted.

The gate also found a narrower continuation.  Every ratio of two production
lambda values is a fourth power, so all leaves can instead be normalized to
one common non-fourth-power ring.  Its smallest signed representative is
`rho=2`: choose `tau_Q^4=lambda_Q/2` and obtain `F_q[y]/(y^4-2)`.  Within B3,
this replaces three four-instruction lambda Montgomery chains per 16-leaf
block with three `vpaddw` doublings.  Across twelve blocks the static saving
is 108 instructions.  With the frozen Forward bound 10788, the resulting
pre-center coefficient bounds `[24535,21030,17525,14020]` remain signed-i16
safe.

That saving cannot be obtained by merely regenerating constants in the
current CT Forward.  The required `tau_Q^c` is a leaf-dependent output
diagonal, while a CT butterfly emits both outputs with one common low-arm
scale.  Distinct paired lambdas therefore require extra output scaling or a
different producer topology.  The current-constants proposal is stopped;
the only active reopen is a generator-only same-chain GS/DIF (or equivalent
conjugated) Forward and inverse that natively deliver the `rho=2` basis before
any assembly is written.  Full records and bounds are in
`generated/tile4_b3_quartic_twist_gate.json`; regenerate with
`make b3-quartic-twist-generate`.

### N5 consumer-contract audit (2026-08-13)

`GT32-N5-CONSUMER-AUDIT-001` audited the six production-shaped Forward roles
before opening another terminal-layout search.  No assembly was changed.  The
audit checks the actual Keygen, Encap and global-inverse Decap callsites and
binds each edge to a `(layout, Montgomery exponent, range, reuse/liveness)`
state instead of treating N5 output as one universal ABI.

The two Keygen outputs are persistent BaseInv/native-BM values and therefore
remain P-like candidates.  Three Encap/Decap outputs are consumed by B3 or by
add/sub against an M-layout peer and therefore select current private-B3 M.
The remaining Decap check-r output is serialization-only and is the sole
primary Q24-native/no-full-materialization candidate.  The resulting endpoint
weight is P-like=2, M=3 and Q24-native=1 per successful Keygen/Encap/Decap
triple.

The range audit prevents layout-only mistakes.  Qualified M is `e=0`,
`abs<=10788`.  Qualified progressive P is `e=0`, `abs<=9586`, below the
direct BaseInv limit 10643; ordinary P at 17724 is illegal without its proved
checkpoint.  P remains arithmetically attractive for Keygen but its current
Q24 route owes 48 cross-lane shuffles.  R1-U remains a valid secondary
BM-specialized representation, not a primary KEM terminal objective.

The next generator survey must therefore score three separate endpoints:
M for Encap/Decap arithmetic, P-like plus Q24 packet cost for Keygen, and a
Q24-native stream for Decap check-r.  Its objective is Forward-to-L plus every
real consumer edge from L, spanning Good routing through the consumer entry;
an S5-only or universal-permutation search is explicitly excluded.  Artifact:
`generated/tile4_n5_consumer_contract_audit.json`; reproducible audit:
`tools/generate_n5_consumer_contract_audit.py`.

### M/BaseInv unification gate (2026-08-13)

`GT32-M-BASEINV-UNIFICATION-001` tested the stronger alternative suggested by
the consumer audit: keep one persistent coefficient-plane M ABI throughout
Keygen instead of retaining P solely for BaseInv.  This was a generator-only
gate; it emitted no assembly and changed no production symbol.

The range half passes.  The balanced M topology begins with a free q2/q3 YMM
selector rename and then a raw q4 stage.  After that stage, physical vectors 0
and 4 contain exactly logical Q sets `{0,1,2,3}` and `{16,17,18,19}`.  These are
the same logical values selected by the exhaustive P checkpoint proof.  The
existing two whole-YMM centers therefore transfer unchanged to M: 6 dynamic
instructions per tile, 36 per Forward, no new Montgomery chain, peak 13 YMM,
no spill, and an exact terminal bound of 9586 below the direct-BaseInv limit
10643.  This proof applies to the wide-raw Keygen M variant; it does not
replace the separate abs<=10788 production-M range proof.

The BaseInv layout half also passes.  M is four contiguous coefficient planes
per 16-leaf batch, with local Q lane order
`[0,4,8,12,1,5,9,13,2,6,10,14,3,7,11,15]`.  Regenerating lambda/qinv metadata
in that order makes every M table row a permutation of its P counterpart.
Quartic determinant/adjugate arithmetic remains lane-local, and each of the
16 SIMD batch-inversion chains still covers 12 unique leaves; their union is
all 192 leaves exactly once.  No M-to-P data pass, new reduction, or new
Montgomery chain is required.

The result is `generator-pass-bounded-assembly-eligible`, not a performance
promotion.  The next executable gate must compare the complete Keygen K3-K5
region `2F_M-safe + 2BaseInv_M + 2B3_M + 3Q24_M` against the current P region
in normal and reversed placement.  P currently owes 48 extra Q24 cross-lane
shuffles per serialized polynomial (144 across three), but this is only a
static upper-bound credit and must not be reported as cycles.  Stop if the M
implementation needs any global M/P conversion, spills, or fails to improve
whole-region core cycles in both placements.  Artifacts:
`generated/tile4_m_baseinv_unification_gate.json`,
`generated/tile4_baseinv_m_tables.inc`, and
`tools/generate_m_baseinv_unification_gate.py`; regenerate with
`make m-baseinv-unification-generate`.

### Executable M/BaseInv unification M1--M4 gate (2026-08-13)

`GT32-M-BASEINV-UNIFICATION-EXEC-001` implemented the bounded continuation as
independent reusable symbols rather than a fused Keygen kernel.  The generated
global-M Forward now has a benchmark-only BaseInv-safe entry with the proved
post-S1 vector-0/vector-4 centers.  The mature BaseInv prepare/finish schedule
was instantiated directly on M with generated M lambda/qinv tables and no data
transpose.  A 1,000-trial differential passed Forward semantics, BaseInv
status/values, both general products and all three Q24 byte streams.  In-place
M BaseInv and the noninvertible whole-output-zero failure behavior also pass.

M1 measures a small but real entry fee: one M-safe Forward costs about
13--14 core cycles more than uncheckpointed M in this matched binary.  M2
confirms the generator prediction: two M-native BaseInv calls are at parity
with P (`+0.192/-1.584` core cycles in normal/reversed placement).  M3 is a
positive architecture result.  The complete two-Forward, two-BaseInv,
two-general-BM arithmetic island saves 64.553 and 68.581 core cycles, with
bootstrap upper bounds below zero in both placements; TSC improves by 39.663
and 46.459.

M4 nevertheless fails.  The generator's earlier 48-shuffle P Q24 debt was
relative to an obsolete P route, not the current SP1 half-scatter champion.
Executable disassembly has 773 meaningful instructions through `ret` for M
L0 lazy10788 pack and 738 for P SP1: M is 35 instructions larger per
polynomial, or 105 across Keygen's three outputs.  The isolated three-pack
gate measures M slower by 59.053/57.209 core cycles and about 34 TSC.  This
consumes essentially all of M3's arithmetic gain.  Complete M4 is
`-7.294` core cycles with CI crossing zero in normal placement and `+1.843`
with CI crossing zero in reversed placement; it is parity/placement-sensitive,
not a promotion margin.

The executable decision is therefore to retain P for Keygen and stop before
whole-KEM integration.  M-safe Forward and M-native BaseInv remain qualified
benchmark components, and M3 proves that the unified arithmetic architecture
is viable, but the premise that M had a three-polynomial serialization credit
is false against current SP1.  Reopen only if a compact reusable M serializer
removes at least the 35-instruction-per-polynomial gap, removal of all
P-specific code gives M4 a two-placement win, or another M consumer deletes a
complete materialized boundary.  Results:
`results/tile4-m-baseinv-unification-pmu.json`; decision summary:
`generated/tile4_m_baseinv_unification_exec_gate.json`.

### N5 P/M progressive-suffix survey and executable gate (2026-08-13)

`N5-P/M-PROGRESSIVE-SUFFIX-SURVEY-001` searched all 5,040 assignments of
the seven semantic axes to AVX2 lane/YMM selector bits.  It constrained P and
M to one physical schedule through successively later NTT32 stages, then
required executable zero-repair landings in production P and M.  Every route
was checked on all 128 degree/Q basis vectors.  Range policy was tracked
separately: P still performs its qualified post-S1 selective center while M
does not, even if their physical layout has not yet diverged.

All three scalar cost profiles found a nominal zero-penalty S5-only split.
The shared state after S4 is `(c0,c1,q0,q2,q1,q3,q4)`, peak usage is 13 YMM,
and neither suffix spills.  This passed the generator filter and produced two
benchmark-only cores.  A 1,000-trial differential against the existing P and
M cores passed modulo-q output equality.

Executable PMU rejects the shared schedule as a universal implementation.
The P suffix is strong in isolation: two P Forward cores save
72.919/77.250 core cycles and about 47 TSC in normal/reversed placement.  The
M suffix, however, makes four M Forward calls slower by 224.523/221.795 core
cycles and about 137 TSC.  Consequently the six-call weighted region loses
146.315/148.357 core cycles despite retiring about 335 fewer instructions.

The static model missed placement of the dependencies.  Current M distributes
routing before the terminal and uses a stage-4 half-local butterfly.  The
shared candidate defers three eight-instruction routing layers until after or
adjacent to the final Montgomery work, serializing the terminal handoff.  Equal
aggregate uops and nominal depth therefore do not imply equal executable
overlap.

The positive P result was carried through the unchanged BaseInv, P-native BM
and three SP1 packs.  K3--K5 improves by 85.754 core cycles in reversed
placement, but normal placement is only -24.199 with a bootstrap interval
crossing zero.  It is retained as a dormant benchmark candidate, not a
production replacement.  The decision is to keep the already specialized P
and M schedules, not expand toward S3/DFT3, and change no selector.  Artifacts:
`generated/tile4_n5_pm_progressive_suffix_survey.json`,
`generated/tile4_n5_pm_progressive_suffix_exec_gate.json`,
`results/tile4-n5-pm-progressive-suffix-pmu.json`, and
`results/tile4-n5-p-s5-suffix-k3k5-pmu.json`.

### Specialized P/M follow-up and formal SUPERcop closure (2026-08-13)

The follow-up stopped searching for a shared P/M physical trajectory and
tested the two specialized continuations independently.  For M, the current
wide frontend is packet-major: each of eight packet iterations produces one
vector for each of six tiles, while the frozen M core consumes eight vectors
of one tile at a time.  No tile is complete before packet 7, and the frontend
already uses all 16 YMM registers.  Pairing packets to run S1 early would
increase vector memory operations from 96 to 144 because it destroys the
current in-register S1-to-S2 handoff; retaining the six low vectors would need
22 registers.  The M seam is therefore a static hard stop under the current
packet-major producer, with no assembly emitted.  The machine-readable proof
is `generated/tile4_n5_m_frontend_seam_gate.json`.

For P, a fresh cumulative same-binary PMU gate shows that the suffix saving is
not lost at BaseInv or Q24.  Normal placement saves 64.742 core cycles through
Forward, 66.635 through BaseInv, and 69.575 through complete K3--K5.  Reversed
placement saves 64.577, 72.942, and 74.163 respectively.  The intermediate BM
cut is noisy, but the complete endpoint recovers in both placements.  This
narrows the remaining risk to whole-image delivery rather than P arithmetic
or the BaseInv handoff.

The candidate was exported as
`crypto_kem/ntruplus768/avx2-gt-global-inverse-p-suffix` and passed the
canonical 100-vector KAT request/response differential byte-for-byte.  A
formal forced-O3 SUPERcop matrix then collected ten runs and 960 observations
per operation for Official, current GT, and P-suffix GT.  Stabilized-quartile
Q2 cycle counts are:

| implementation | Keypair | Encap | Decap |
|---|---:|---:|---:|
| Official `avx2` | 21610.392 | 28213.204 | 19447.225 |
| current GT | 21651.133 | 28302.492 | 19422.183 |
| P-suffix GT | 21562.588 | 28439.108 | 19536.729 |

P-suffix therefore improves Keypair by 47.804 cycles (0.221%) versus Official
and by 88.546 cycles versus current GT.  Encap and Decap do not execute the new
P Forward, yet regress by 136.617 and 114.546 cycles versus current GT.  Those
two changes are whole-binary delivery/code-placement effects, not arithmetic
work added to those operations.  The correct decision is not to promote one
monolithic backend: retain P-suffix as a Keypair-specific export candidate,
keep current GT Decap/Encap, and next isolate the Keypair symbol/section so it
cannot perturb the other hot paths.  Formal data is in
`results/tile4-supercop-p-suffix-matrix-20260813.json`; the KAT record is in
`results/kat-supercop-p-suffix-20260813/`.

### P-suffix section-isolation closure (2026-08-13)

The first formal export did not isolate the proposed change.  The installed
current SUPERcop implementation predates the P suffix, while the candidate
re-exported the complete newer global-physical assembly and accidentally left
the renamed keygen source as a second C translation unit.  A clean wrapper
removed the latter pollution, but the linked `.text` was still about 17.5 KiB
larger than current GT because unrelated experimental functions were present.
That clean whole-worktree export saved 97.880 Keypair cycles versus current
GT, but changed Encap/Decap by +94.594/+14.448 cycles and therefore was not a
valid presence-only control.

`tools/generate_p_suffix_isolated_asm.py` now extracts only the qualified P
function and its private constants into `.text.gt32_keypair_psuffix` and
`.rodata.gt32_keypair_psuffix`.  The function is 926 bytes and the complete
text/constant payload is about 2.0 KiB.  Installing this object on top of the
exact current production export passed the canonical 100-vector KAT
request/response differential.  In an eight-run formal matrix the isolated
late object changed Keypair/Encap/Decap versus current GT by
`+36.172/-83.964/-46.948` cycles: isolation protected the unrelated operations,
but the local Keypair gain disappeared at that placement.

A bounded 0/64/128/256-byte padding sweep then tested the attachment's
alignment hypothesis without changing the P arithmetic.  Keypair deltas versus
the same current-GT control were `-32.698`, `-25.198`, `-3.375`, and `-34.396`
cycles.  None retained the required 50-cycle gain, while Encap and Decap moved
substantially with padding.  This proves that the P suffix is algorithmically
qualified but has no production-stable section placement under the current
link model.  No magic padding is selected and the production selector remains
unchanged.  The complete decision record is
`results/tile4-p-suffix-section-isolation-20260813.json`.

### P-prime BaseInv/BM/Q24 joint ABI survey (2026-08-13)

P-suffix is now a reference oracle rather than an integration candidate:
current progressive-P remains the production baseline, while the isolated
926-byte suffix records the best proven local arithmetic schedule.  The next
generator gate therefore searched for a consumer-amortized P-prime ABI rather
than another suffix schedule.

The survey fixed coefficient-plane SoA, the monomial quartic basis, current
Forward arithmetic/range policy and Montgomery exponent.  It exhaustively
assigned the five logical Q bits to four 16-bit lane positions and one YMM
selector, giving 120 placements.  BaseInv and native BM were required to
absorb a leaf bijection solely by relabelling lambda tables.  Q24 was evaluated
from the exact serialized mapping and rejected any placement requiring a
cross-block packet, cross-register wire half, global repair or materialized
transition.

Only 18 placements preserve the compact block-local Q24 half-scatter shape.
The best four Q-axis orders are:

```
q1,q2,q0,q4 | q3
q1,q3,q0,q4 | q2
q2,q1,q0,q4 | q3
q3,q1,q0,q4 | q2
```

Here `|` separates the four lane axes from the YMM-selector axis.  All four
tie current P's executable Forward cost under balanced, latency and
shuffle-port profiles.  They reduce Q24's asymmetric runtime masks from 13 to
3 per polynomial, hence at most 30 instructions across the three Keygen
packs.  BaseInv and BM delete zero runtime instructions: their only change is
constant/table order.  No complete materialization, checkpoint, shuffle
network, Montgomery chain or reduction chain disappears.

This is a generator hard stop.  Thirty instructions of whole-K3--K5 static
headroom is smaller than the already non-deliverable P-suffix local win, so no
ASM was emitted and no placement benchmark was opened.  Twisting/range
co-design is deferred until an existing Forward Montgomery chain can directly
replace a consumer reduction or checkpoint with nonpositive net chain count.
The machine-readable proof is
`generated/tile4_p_prime_joint_abi_survey.json`.

### Keygen joint execution-tile survey (2026-08-13)

`KEYGEN-JOINT-ABI-EXECUTION-TILE-SURVEY-001` tested the remaining narrow
execution-ABI hypothesis while keeping Forward, BaseInv, BaseMul and Q24 as
independent symbols.  It audited the exact Official assembly, current P
sources and the linked production benchmark rather than treating leaf-table
compatibility as an execution cost model.

The central premise required one correction.  Official BaseInv and BaseMul do
advance their outer loops by 256 bytes, but that does not make their arithmetic
tile T32.  In both assembly files the first 16-leaf batch is fully computed and
stored before the second batch is loaded.  The repeated quartic DAGs are
sequential outer-loop unrolls and each uses the full AVX2 register file.  The
real eight-input-YMM T32 reference is Official `poly_tobytes`.  Current P-SP1
already implements the useful analogous overlap by preloading the next four
vectors into `ymm8--ymm11` between the current quotient estimate and
correction.

The linked current-P BaseInv references all 16 vector registers and contains
vector stack temporaries.  The native P BaseMul references all 16 registers
without spilling because all eight input vectors and their four qinv products
remain resident.  A genuine two-batch interleave therefore has a lower bound
above 16 registers, before satisfying the stricter peak-at-most-15 gate.  It
would require spills, reload/recomputation, or abandoning the current compact
schedule.

Four families were scored.  Current P/T16 is retained as control.  Current
P/T32 can only halve scalar loop-control work; it removes no vector arithmetic
and shortens no vector critical tail, while Q24 already has SP1 overlap.
Official-inspired Q pairing has the same limitation: Official itself clobbers
and reloads metadata between the sequential batches.  Best-P-prime/T32 adds
only the already known 30 Q24 shuffle ceiling.  Although a two-way outer-loop
unroll has a generous upper bound of 132 fewer scalar control instructions per
complete Keygen, those instructions overlap the unchanged multiply-heavy
tails and are not the required 100 resource-relevant vector instructions or
50-cycle modeled headroom.

No family removes a reduction, materialization or Montgomery chain, and no
candidate meets peak/live/spill constraints.  The gate is therefore a static
hard stop with no ASM emitted.  Reopen only if a schedule proves at most 15
live YMM without spill/reload debt, deletes vector work or a measured critical
tail, or a wider ISA supplies additional registers.  Full details are in
`generated/tile4_keygen_joint_execution_tile_survey.json`.
### T16 register-lifetime and critical-DAG audit (2026-08-13)

`GT32-T16-REGISTER-CRITICAL-AUDIT-001` separates a nominal 15-register
spelling from a useful 15-register execution schedule.  The current fast
BaseMul contract needs four `a` planes, four hoisted `a*qinv` planes, four
`b` planes, resident `q`, and three Montgomery accumulator temporaries: all
16 YMM registers.  Moving `q` to a memory operand makes the spelling fit in
15 registers, but adds 23 memory-source correction multiplies per T16 block,
removes no vector multiply or Montgomery chain, and frees capacity for only
one next-block preload.  Every current input remains live through the first
product of `c3`, so next-block arithmetic still cannot start.

The linked production C BaseInv uses all 16 vector registers and stack
temporaries; the existing hand-written prepare schedule is the cleaner
spill-free T16 schedule used for the lifetime lower-bound audit.  It also uses
all 16 YMM registers.
Its determinant can be stored as soon as it is formed, releasing that value
during the adjugate tail, but this moves an existing store rather than
removing work.  Moving resident `q` or `qinv` to memory similarly replaces a
register with 21 or 6 memory-source multiply uses per batch without shortening
the critical multiply tail.  Consequently neither kernel has a proven useful
15-register schedule, even though both have nominal memory-constant spellings.

No assembly was emitted.  Cross-batch T32 ILP remains closed until a candidate
removes a vector multiply/reduction layer or otherwise creates enough live
state capacity to begin an independent Montgomery chain, rather than merely
preloading one vector.  The generated audit is
`generated/tile4_t16_register_critical_audit.json`.
### P-J1 BaseInv to finalizer-free P-native BaseMul (2026-08-13)

`KEYGEN-P-J1-BM-FINALIZER-ELISION-001` reuses the current progressive-P
layout and changes only its scale ABI.  The new typed BaseInv instance changes
the field-inversion addition chain's final fixed factor from `R^-1` to ordinary
`1`, so the inverse is returned at exponent `e=1` without an extra pass or
instruction.  The typed BaseMul edge is consequently `P-F0 e=0 x P-J1 e=1 ->
P e=0` and stores the raw quartic accumulators without the four `Mont(R^2)`
output finalizers per 16-leaf block.

The conservative P-safe/J1 bounds are 9586/1910.  The raw BaseMul output
ceilings are `[3897,5853,7809,8036]`, signed-int16 safe.  The unchanged SP1
Q24 reducer was already exhaustively proven over the complete signed-int16
domain.  Static audit confirms 48 removed fixed-Montgomery finalizers per BM,
or 96 chains / 384 vector instructions across the two Keygen products.

The executable differential passed 1,000 invertible trials: J1 equals the
current inverse times R modulo q, the finalizer-free product equals the current
general product modulo q, and unchanged SP1 serialization is byte exact.
In-place BaseInv aliasing and zero/noninvertible failure output also pass.

The bounded `2 BaseInv + 2 BM + 3 Q24` region saves 144.454/149.839 core
cycles and 92.401/97.806 TSC in normal/reversed placement.  Full fixed-retry
Keygen retains 113.823/193.515 core cycles and 84.569/111.389 TSC versus the
current P/SP1 control; both bootstrap core-cycle intervals are below zero.
Against Official in the same binaries, median TSC is favorable by
22.901/119.173, but normal-placement core cycles are inconclusive and cross
zero.  The candidate is therefore algorithmically and full-caller qualified,
but remains opt-in pending SUPERcop/whole-image placement qualification.

Artifacts: `generated/tile4_keygen_p_j1_bm_finalizer_gate.json`,
`results/tile4-keygen-p-j1-bm-finalizer-pmu.json`,
`results/tile4-keygen-p-j1-bm-finalizer-full-pmu.json`, and
`results/tile4-keygen-p-j1-bm-finalizer-vs-official-pmu.json`.

### P-J1 canonical KAT and formal SUPERcop closure (2026-08-13)

The qualified P-J1 sources were exported as the independent SUPERcop
implementation `crypto_kem/ntruplus768/avx2-gt-global-inverse-p-j1`; neither
Official `avx2` nor the current GT `avx2-gt-global-inverse-q24-sp1-fixed`
implementation was overwritten.  The canonical 100-vector KAT is byte exact
for request seed, public key, secret key, ciphertext and shared secret.  Its
request/response SHA-256 values are `36c27b6089b8910733a01fea1136469769b3ca3c35f2b375cfcc592f2112cfaa`
and `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.

The formal O3 matrix used four independent `O-C-P-P-C-O` blocks, where `O` is
Official, `C` is current GT and `P` is P-J1.  Each implementation therefore has
eight process launches and 768 cycle observations per operation.  Pooled
SUPERcop stabilized-Q2 cycles are:

```
                         Keypair       Encap       Decap
Official avx2          21579.964   28186.505   19449.807
current GT             21554.323   28276.141   19425.271
P-J1 candidate         21524.323   28315.714   19475.729
P-J1 - Official          -55.641    +129.208     +25.922
P-J1 - current GT        -30.000     +39.573     +50.458
```

The matched-block estimator is deliberately stricter about launch delivery.
Its median P-J1 deltas versus Official are `-28.406/+123.260/+67.333` cycles
for Keypair/Encap/Decap, with favorable blocks `3/4`, `0/4`, and `1/4`.
Versus current GT they are `-20.135/+83.479/+45.281`, with favorable blocks
`3/4`, `1/4`, and `2/4`.  Thus the local finalizer-elision mechanism survives
only as a small, non-robust Keypair signal; the linked-image change also slows
operations that never execute the new path.

P-J1 is correctness-qualified and remains a reusable opt-in experiment, but
this particular monolithic export fails whole-backend production promotion.
This result does not reject the P-J1 arithmetic edge: Encap and Decap do not
execute it, yet moved by comparable amounts.  Current GT remains the GT
selector and Official remains the default implementation for this export.
The required continuation is a layout-equivalent causal A/B followed by an
operation-specific hybrid.  Formal artifacts are
`results/kat-supercop-p-j1-20260813/`,
`results/tile4-supercop-p-j1-matrix-20260813.json`, and
`results/tile4-supercop-p-j1-blocks-20260813.json`.

### P-J1 fixed-layout causal A/B and operation-specific hybrid (2026-08-13)

The corrected A/B binaries both link current-P and P-J1 BaseInv plus both
native BaseMul entry points.  Their `.text`, data and BSS sizes are identical,
as are every hot symbol address and size.  Of 189,399 `.text` bytes, only eight
bytes differ: the displacements of the two BaseInv and two BaseMul calls in
Keypair.  `.rodata` differs only in seven implementation-name bytes.  Both
binaries pass the canonical 100-vector byte-exact KAT.

Four formal `A-B-B-A` SUPERcop blocks show that the arithmetic win is real.
P-J1 saves 152.901 pooled Keypair cycles; the matched-block median is 177.937
cycles and all 4/4 blocks are favorable.  Encap and Decap pooled deltas are
`-4.703/+7.474` cycles and their matched medians are `-8.906/-17.052`, i.e. the
non-Keypair paths are effectively controls.  P-J1 therefore passes
correctness, arithmetic and fixed-layout whole-Keypair delivery.  The earlier
failure is specifically a monolithic-export integration failure.

The operation-specific hybrid then selects P-J1 Keypair, extracted Official
Encap and current GT-M Decap.  Its P-J1-generated keys are consumed across the
other two implementations in a canonical 100-vector KAT; seed, pk, sk, ct and
ss remain byte exact.  An eight-block formal matrix, with 16 launches and
1,536 observations per implementation/operation, measures stabilized-Q2
cycles as follows:

```
                         Keypair       Encap       Decap
Official avx2          21590.125   28191.260   19456.180
current GT             21562.219   28182.344   19397.065
operation hybrid       21262.328   28062.633   19426.703
hybrid - Official       -327.797    -128.627     -29.477
hybrid - current GT     -299.891    -119.711     +29.638
```

Matched-block hybrid-minus-Official medians are
`-340.250/-59.604/-25.156` cycles with favorable counts `8/8`, `6/8`, and
`5/8` for Keypair/Encap/Decap.  The hybrid is consequently the first opt-in
whole-KEM benchmark candidate whose pooled SUPERcop cycles beat Official in
all three operations.  It is not the default: Encap and Decap do not yet win
every matched block, and current GT remains the faster Decap implementation
by about 29.6 pooled cycles in this linked image.  The next delivery problem is
operation-section isolation for Encap/Decap, not more P-J1 arithmetic work.

Artifacts: `results/tile4-supercop-p-j1-fixed-ab-20260813.json`,
`results/kat-supercop-p-j1-hybrid-20260813/`,
`results/tile4-supercop-p-j1-hybrid-matrix-8blocks-20260813.json`, and
`results/tile4-supercop-p-j1-hybrid-blocks-8blocks-20260813.json`.

### N5 frontend linear-circuit gate (2026-08-13)

`N5-FRONTEND-LINEAR-CIRCUIT-001` is the final bounded arithmetic gate after
the packet-major to tile-major seam was frozen.  It preserves the same six
logical inputs and outputs, Good routing, packet-major scratch ABI and M
NTT32 core.  Only fixed-constant placement, signed common subexpressions and
the twist/DFT3 factorization are variable.

The qualified circuit uses four Montgomery chains per branch: three
independent twist products followed by the one-multiply radix-3 circuit.  It
therefore uses eight chains per packet and 64 per Forward.  Its true multiply
depth is two because the omega product consumes the difference of two twist
results.

The generator then exhausts the natural depth-one circuit class.  Such a
circuit has `M_Q=C+sum c_i(Q) a_i b_i^T`, where `C` is common signed free
wiring, `a_i` and `b_i` are signed output/input forms, and only the fixed
constants may vary by Q lane.  All 19,683 signed `C` matrices and 169 unique
signed rank-one directions were checked over both branches and all 32 Q
values.  No circuit with four or fewer fixed multipliers exists in this
class.  The exact minimum is five per branch, constructively using
`t0*x0`, `t1*x1`, `omega*t1*x1`, `t2*x2`, and `omega*t2*x2` together with
`omega^2*x=-x-omega*x`.

The shorter dependency therefore costs ten chains per packet and 80 per
Forward: 16 additional chains, at least 64 additional vector instructions at
the four-instruction Montgomery floor, and one more add/sub per branch.  Its
representatives are signed-i16 safe, but its exact output bound 6776 is wider
than the current circuit's 5232.  It fails both continuation conditions:
neither fewer than eight chains nor eight chains with a shorter multiply
depth is available.  No assembly or benchmark was emitted.

Together with the seam proof, this freezes the current N5 frontend arithmetic
and scratch boundary.  Reopen only for a changed scaled-output consumer that
deletes a complete chain, a primitive that forms two fixed multiples for less
than two chains, a decomposition creating signed-related twist constants, a
waiting working set of at most ten YMM, or a different ISA/microarchitecture.
The exact matrices, exhaustive search and range proof are in
`generated/tile4_n5_frontend_linear_circuit_gate.json`; regenerate with
`make n5-frontend-linear-circuit-generate`.

### N5 Forward scale-edge survey (2026-08-13)

`N5-FORWARD-SCALE-EDGE-SURVEY-001` separates the Forward-boundary state into
mathematical value, Montgomery exponent, physical layout and representative
range, then enumerates the exponent equations of every actual KEM consumer.
It deliberately grants nonzero-scale coefficient producers for free before
using producer cost as a tie-break, so the gate is optimistic toward a changed
Forward scale ABI.

The first correction is structural: current N5 has no terminal normalization
that creates `e=0`.  Its twist and NTT tables store `e=1` constants and hence
preserve the input exponent, while the raw top split also preserves it.  The
current output is `e=0` because its producer is `e=0`; choosing another scale
cannot delete a nonexistent Forward finalizer.

The complete call graph then leaves no eligible exponent variant:

- Encap always needs at least one 48-vector conversion.  Current
  `r:e0, m:e0` pays it at the general-BM output.  `r:e1` removes that
  finalizer but pays the same pass when serializing `rhat`; `m:e-1` moves it
  to ciphertext serialization.
- Decap's first product already consumes native BM `e=-1` directly in the
  scale inverse.  Its second product always needs at least one conversion;
  scaling decoded `c` or `hinv` only moves the current output finalizer to a
  decoder edge.  The check-`r` Forward is already `e0 -> wire e0`.
- Keygen's BM-ready inverse of an `e=k` Forward has exponent `1-k`.  A common
  nonzero scale cancels in both quotients, but serialized `fhat` then needs a
  full normalization.  The existing P-J1 edge already captures the useful
  inverse scale with `F0:e0 x J1:e1 -> e0`.

A full polynomial scale change is 48 Montgomery chains, with a 192-instruction
floor at four instructions per chain.  No assignment deletes such a pass
without replacing it elsewhere, so no assembly or benchmark was emitted.
Keep the current Forward ABI at `e=0`.  Reopen only if a wire consumer
disappears, Q24 can absorb nonzero scale without a multiply chain, a producer
forms the scale for free and loses its serialization edge, or a new consumer
accepts the natural scaled result and deletes a complete pass.  Exact equations
and all enumerated assignments are in
`generated/tile4_n5_scale_edge_survey.json`; regenerate with
`make n5-scale-edge-survey-generate`.

### Scale conversion / Q24 consumer-fusion gate (2026-08-13)

`GT32-SCALE-CONSUMER-FUSION-001` follows the scale-edge survey with the
separate kernel-level question: an exponent conversion may be unavoidable in
the representation graph, but can it replace Q24's reduction instead of
running as `conversion + reduction`?

Two exact Encap closures were checked.  An `r:e1` wire value converts with
`Mont(x,1)`, while a ciphertext at `e=-1` converts with `Mont(x,R^2)`.  Both
four-instruction AVX2 chains return an already reduced `e=0` representative,
so the existing three-instruction `vpmulhrsw/vpmullw/vpsubw` Q24 lazy reducer
does disappear.  The fusion is therefore algebraically real; it is not merely
two functions in one symbol.  Exhaustive representative checks prove the
single-sign-correction Q24 tail for the `e1` Forward bound 18374 and the
`e=-1` post-add bound 32630.  The latter also adds a new exact feasibility
result: ternary input scaled by `R^-1=-682` survives N5 with bound 18610 and
the raw BM-plus-Forward add remains signed-i16 safe.

The whole-edge accounting nevertheless stops the experiment.  Scaled Q24 is
four instructions per vector versus three for the qualified lazy reducer, so
the wire edge adds 48 instructions.  Either scale assignment removes the
192-instruction BM `R^2` finalizer, but a concrete scaled ternary producer
costs 48 instructions and its mandatory Montgomery top split costs 72 more.
The net is only -24 instructions per Encap.  Even granting producer-side scale
formation for free leaves only -72.  All 48 Montgomery conversion chains are
still present, and the concrete gain is below the one-instruction-per-vector
continuation floor; no assembly or benchmark was emitted.

Reopen only if CBD/SOTP emits the scaled ternary values without a vector scale
pass, the scaled Forward avoids its Montgomery top premium, scaled Q24 reaches
three instructions per vector, a wire consumer disappears, or the ISA gains a
shorter packed fixed-factor reduction.  The exact bounds, congruence checks and
instruction accounting are in
`generated/tile4_scale_consumer_fusion_gate.json`; regenerate with
`make scale-consumer-fusion-generate`.
### Clean production export and SUPERcop closure (2026-08-13)

`tools/install_supercop_fastest_clean.sh` now exports the fastest validated
all-GT operation set as `crypto_kem/ntruplus768/avx2-gt-fastest-clean`:
P-J1 Keypair, current M/H1 Encap, and Q24/B3-M/global-inverse Decap.  The
export physically prunes unselected multi-variant assembly functions and the
benchmark uses function/data sections plus linker section GC for both GT and
Official.  The resulting measure ELF contains 18 selected GT symbols instead
of 68 and its `.text` is 0x10317 bytes instead of 0x1f3d7 for the linker-GC-only
experimental export.  Canonical KAT passes 100/100 byte-exact.

Four Official--CleanGT--CleanGT--Official SUPERcop blocks give pooled Q2
deltas (CleanGT minus Official): Keypair -51.224 cycles, Encap +38.047 cycles,
Decap -59.802 cycles.  The matched blocks are favorable in 3/4, 1/4, and 2/4
respectively, so only Keypair is directionally convincing; Encap and Decap
remain inside whole-image delivery variance.

The stricter `avx2-gt-decap-fastest-clean` control keeps Official Keypair and
Encap and replaces only Decap.  Its four pruned matched blocks all lose Decap
(+67.208, +68.604, +6.708, +121.250 cycles), pooled +84.172 cycles.  Even its
unchanged Official Keypair/Encap move by +29.464/+306.135 pooled cycles.  This
is direct evidence that previous GT Decap wins were not placement-stable and
that whole-image code geometry affects unrelated operations in the shared
SUPERcop measure ELF.  Official therefore remains the default.

Artifacts:

- `results/tile4-supercop-fastest-clean-pruned-abba-20260813.json`
- `results/tile4-supercop-decap-fastest-clean-pruned-abba-20260813.json`
- `results/kat-supercop-fastest-clean-pruned-20260813/`
- `results/supercop-fastest-clean-pruned-measure-20260813{,.nm,.sections}`
- `results/supercop-official-gc-measure-20260813`

### Operation-minimal SUPERcop image attribution (2026-08-13)

Three valid hybrid images now isolate one CleanGT operation at a time while
the other two operations use Official main.  All passed SUPERcop correctness
and constant-branch/index checks.  Two matched A-B-B-A blocks provide
diagnostic evidence that image composition or launch/runtime state is
comparable to the small GT margins: versus monolithic CleanGT,
Keypair-min changes GT Keypair by -241.0 pooled cycles, Encap-min changes GT
Encap by -124.1 cycles but with block deltas -170.1/+25.2, and Decap-min changes
GT Decap by +54.7 cycles with strongly inconsistent blocks.  Even the Official
operations not targeted by each hybrid move by tens to hundreds of cycles.

Against Official in separate matched blocks, Keypair-min wins Keypair by
234.5 cycles in both blocks, while Encap-min loses Encap by 216.8 cycles and
Decap-min loses Decap by 177.0 cycles.  Thus P-J1 Keypair has the strongest
intrinsic case; Encap still has caller/delivery debt; and the prior GT Decap
win is not yet placement-independent.  Two blocks are insufficient for a
causal or promotion claim.  Keep Official as default and do not reopen
N5/B3/I1 or Q24 arithmetic based on these image results.  Full methodology,
ELF sizes, addresses, and caveats are in
`results/tile4-supercop-operation-minimal-attribution-20260813.md`.

### Fixed-ELF formal SUPERcop comparison (2026-08-13)

The final Official and monolithic CleanGT `measure` ELFs were each linked once,
hashed, and executed in 16 balanced paired blocks (64 independent launches).
Odd blocks use Official--GT--GT--Official and even blocks reverse the order.
Every launch retains SUPERcop's native 96 core-cycle observations per KEM
operation; the analysis uses launch-level stabilized Q2 and paired block
deltas.  The backend is `default-perfevent/PERF_COUNT_HW_CPU_CYCLES`, not TSC.

CleanGT minus Official paired medians are: Keypair -33.760 cycles (-0.157%,
14/16 favorable, bootstrap 95% CI [-80.833,-13.417]); Encap +113.917 cycles
(+0.406%, 4/16 favorable, CI [+40.042,+154.833]); Decap +28.240 cycles
(+0.146%, 1/16 favorable, CI [+16.646,+50.333]).  ABBA and reversed BAAB
subsets agree in sign for all operations.  Thus only GT Keypair wins in the
fixed full image; GT Encap and Decap lose, and Official remains the default
complete backend.  See
`results/tile4-supercop-fixed-elf-serious-20260813.md` for the full method.

### P-J1 BaseInv stage PMU attribution (2026-08-13)

`GT32-KEYGEN-BASEINV-STAGE-PMU-001` splits the current intrinsic P-J1
BaseInv into exact prepare (quartic determinant plus pre-sign adjugate),
`batch_inverse`, and J1 finish boundaries. Batch and finish use matched-copy
controls, so their reset traffic is subtracted rather than attributed to the
stage. Each PMU event is run separately because simultaneous `cpu_core/*`
events multiplex on this hybrid host. The gate uses 100,000 calls per sample,
20 paired samples, and normal/reversed link placement. The staged path passes
1,000 random trials plus the zero/noninvertible check against direct P-J1
BaseInv.

| stage | normal core cycles | reversed core cycles | instructions normal/reversed |
| --- | ---: | ---: | ---: |
| prepare | 510.373 | 509.986 | 1408.3 / 1409.9 |
| batch inverse | 355.297 | 354.096 | 322.4 / 328.5 |
| J1 finish | 101.584 | 103.762 | 384.3 / 382.3 |
| direct full BaseInv | 1069.654 | 1069.774 | 2189.9 / 2187.5 |

Prepare is the largest absolute phase, so PMU does not support the literal
claim that `batch_inverse` consumes the most cycles. It does support
`batch_inverse` as the highest-priority hand-ASM probe: prepare has no stack
references, a compact 561-byte loop, and about 0.36 cycles/instruction, while
batch inverse is a 1609-byte body with a 648-byte stack frame, 57 static stack
references (36 vector moves), and about 1.08--1.10 cycles/instruction. Finish
is only about 102 cycles and is closed. The split-stage sum is about 102 core
cycles below the direct function; this is call/stack/code-shape closure debt,
not a fourth mathematical phase, so an isolated stage saving must be confirmed
again at the full BaseInv endpoint.

Artifact: `results/tile4-keygen-baseinv-stage-attribution-pmu.json`.

### Encap load-quality closure (2026-08-13)

The exact Encap `+763 retired loads` attribution was followed with cache,
load-stall, and blocking PMU events.  The accesses are warm-L1: L1/L2 misses,
store-forward blocks, address-alias blocks, and store-buffer stalls are all
effectively zero.  The two Forward calls' `+358` loads overlap with arithmetic
and do not own a positive load-bound signal.

Two compact executable probes tested the remaining plausible load mechanisms.
Fusing only the qualified B3 R-squared finalizer with `add(m)` removes about
131 instructions, 49 loads, and 49 stores, but its direct cycle result changes
sign across normal/reversed and PMU event runs.  Keeping the Q24 pair factor
and pack mask in YMM registers removes exactly 94 retired loads per serializer,
yet serialize-r-hat is about 3.6--4.2 core cycles slower and ciphertext
serialization about 0.4 cycle slower.  Neither probe is production-eligible.

The new closure is that retired memory-source operands cannot be valued as
recoverable load cycles on this CPU.  Future work must delete a critical
dependency or a complete arithmetic/reduction layer; reducing warm-L1 retired
load count alone is now a hard-stopped objective.  See
`results/tile4-encap-load-followup-20260813.md`.
# P-J1 product-tree batch inversion (2026-08-13)

`src/tile4_baseinv_p_j1_batch_asm.S` adds a hand-written AVX2 batch
inversion for the twelve P-J1 determinant vectors.  The selected implementation
uses a balanced product tree and batched `MONT2`/`MONT4` schedules rather than
the compiler-C linear prefix/backward scan.  The number of inter-vector field
products is unchanged, but independent nodes at each tree level execute in
parallel and the tree uses a 320-byte frame.

The 1,000-trial differential checks cover zero rejection, every determinant
lane modulo q, and the complete BaseInv output.  Paired 100k PMU measurements
against the matched split-C BaseInv show the complete BaseInv region improving
by 61.322 core cycles / 38.066 TSC (normal) and 62.389 core cycles / 38.749 TSC
(reversed), with 20/20 core-cycle wins in both placements.  The standalone
global-buffer batch microbenchmark is slower and is not the promotion endpoint;
the production-shaped stack-local BaseInv region is the selected gate.

The P-J1 instantiation now selects this external tree kernel.  The final
delivery gate exports matched independent SUPERcop control/candidate
implementations: both retain the compiler-C and product-tree sources and differ
only in the compile-time selector.  Both pass the canonical 100-vector KAT with
byte-identical request/response files.

The formal eight-block, 32-fresh-process matched A/B benchmark uses SUPERcop
`default-perfevent` core cycles, alternating ABBA/BAAB order and 96 observations
per operation per launch.  Product-tree minus compiler-C Keypair is
`-114.260` cycles (`-0.535%`), 7/8 favorable blocks, bootstrap 95% CI
`[-263.688,-70.500]`; both ABBA and BAAB medians are negative.  Encap
(`+25.021`, CI crossing zero) and Decap (`+9.490`, CI crossing zero) do not
execute the selected BaseInv and show no stable whole-image regression.
Therefore the hand-ASM product tree is whole-Keypair delivery-qualified.

A same-session four-block comparison against Official Main reports candidate
minus Official: Keypair `-139.990` cycles (`-0.653%`, 4/4 favorable, bootstrap
CI `[-331.479,-70.292]`), Encap `+411.802` cycles (`+1.471%`), and Decap
`+123.167` cycles (`+0.636%`).  Thus the Keypair operation is qualified, but
the complete GT backend must remain opt-in because its Encap and Decap still
lose to Official in this binary.  Artifacts are
`results/tile4-supercop-p-j1-batch-tree-ab-20260813.json` and
`results/tile4-supercop-p-j1-batch-tree-vs-official-20260813.json`.

### Encap four-poly island and B3 final-store add-m (2026-08-13)

`GT32-ENCAP-FOUR-POLY-B3-ADD-M-001` tests the bounded caller ABI proposed
after the retired-load audit.  It uses the already-proved in-place N5 core
contract so `r` and `m` each serve as their own frontend scratch, removes the
fifth `c` polynomial, and selects the existing B3 finalizer which adds the
private-SoA message before B3's sole final stores.  The ciphertext is then
packed from `work`; coefficient-domain `m` no longer remains in `work`.

The candidate is byte-exact and passes the canonical 100-vector KAT.  Static
compiler output reduces the Encap frame from 8,128 to 6,592 bytes, removes the
standalone `poly_add` call, and introduces no vector spill.  The isolated
B3-add edge retires about 131 fewer instructions, 49 fewer loads and 49 fewer
stores.  Its core-cycle result is not stable: normal is `-24.283` cycles
(13/20 favorable) while reversed is `+8.457` (10/20).

The decisive eight-block/32-process SUPERcop ABBA/BAAB gate reports candidate
minus matched control Encap `-2.698` core cycles, only 4/8 favorable blocks,
bootstrap 95% CI `[-85.729,+192.792]`; ABBA is `-29.885` while BAAB is
`+72.938`.  Keypair is a zero-effect control.  Decap, which never executes
the changed Encap function, moves `+119.063` cycles with CI
`[+14.021,+150.750]`, proving that whole-image placement perturbation is larger
than the intrinsic edge saving in this build.  The candidate therefore fails
the requested local and whole-Encap continuation thresholds and remains
default-off.  Artifact:
`results/tile4-supercop-encap-four-poly-ab-20260813.json`.

### Decap native-domain final verification (2026-08-13)

`GT32-DECAP-NATIVE-RCHECK-001` removes the non-protocol second serialization
from decapsulation.  The mandatory recovered-r Q24 bytes remain unchanged for
`hash_g`; its private-SoA source stays live in `scratch.aux`.  After SOTP
decode, `scratch.m` is reused for CBD coefficients, `work` for the N5
frontend, and `hinv` for the derived r-hat.  A compact 78-byte AVX2 leaf then
compares the recovered and derived private-SoA e=0 words modulo 3457 using the
already-proved v=9 reducer over the exact difference bound 12699.

This removes the second lazy10788 Q24 pack and byte verify, and reduces the
hash-g output buffer from 1,152 to 192 bytes.  Compiler output reduces the
decap frame by exactly 960 bytes (`0x2c40` to `0x2880`).  Exhaustive testing of
every integer difference in `[-12699,12699]`, the existing valid/malformed
decap differential, and both canonical 100-vector SUPERcop KATs pass.

The primary measurement calls control and candidate from the same ELF, so no
unrelated address can differ between A and B.  Across eight fresh SUPERcop
launches, the normal placement saves a median 165.833 core cycles with 8/8
favorable launches; an alternate 4-KiB candidate placement saves 219.417 with
8/8.  The local C5 deletion saves 211.333 and 208.208 cycles respectively,
also 8/8 in both placements.  Paired calls to the unchanged Encap and Keypair
functions remain centered near measurement noise and have no consistent
direction.  The gate therefore passes and the opt-in GT SUPERcop APIs now
select native-rcheck; Official Main remains the public/default backend.
Artifacts:
`results/tile4-supercop-native-rcheck-same-elf-c5-20260813.json` and
`results/tile4-supercop-native-rcheck-same-elf-alt-20260813.json`.

### Promoted native-rcheck versus Official Main (2026-08-13)

The promoted GT export and Official Main were each compiled once with the same
forced SUPERcop O3/section-GC flags, then run as fixed ELFs in 16 balanced
ABBA/BAAB blocks (64 fresh processes, 96 native observations per operation).
The primary metric is `default-perfevent` core cycles.  GT minus Official
paired medians are Keypair `+151.083` cycles (`+0.703%`, 0/16 favorable),
Encap `+181.469` (`+0.647%`, 0/16), and Decap `-159.708` (`-0.826%`, 16/16).
All bootstrap 95% intervals exclude zero and both order families agree in
sign.  Decap's complete-operation saving closely matches the preceding
same-ELF native-rcheck gate, so the structural deletion survives whole-image
delivery and the direct Official comparison.

The promoted export is still the full multi-variant GT image (`.text` 128983
bytes versus Official 42007), so this result is deliberately about the actual
promoted export rather than a specially pruned ideal image.  Promote GT Decap
as an opt-in/hybrid choice; current GT Keypair and Encap do not beat Official,
and Official remains the default complete backend.  Full methodology and
block data are in
`results/tile4-supercop-native-rcheck-vs-official-20260813.md`.

### Fastest clean GT32 composite closure (2026-08-14)

`avx2-gt-fastest-clean-native-rcheck` now combines the selected P-J1,
finalizer-free BaseMul and SP1 Keypair with the qualified Encap and promoted
native-rcheck Decap, while pruning unreachable assembly variants.  Its linked
`.text` is 66519 bytes versus 128983 for the preceding unpruned native-rcheck
export.  Canonical 100-vector KAT is request/response byte-exact and linked
symbol audit confirms all five intended typed components.

The formal fixed-ELF SUPERcop test uses 16 balanced ABBA/BAAB blocks and 64
fresh process launches.  GT minus Official paired medians are Keypair
`-388.240` core cycles (`-1.806%`, 16/16 favorable), Encap `+65.458`
(`+0.233%`, 3/16), and Decap `-222.781` (`-1.151%`, 16/16).  Both order
families agree in sign and all bootstrap intervals exclude zero.  The clean
composite therefore wins Keypair and Decap robustly; Encap remains the only
losing operation.  See
`results/tile4-supercop-fastest-clean-native-rcheck-vs-official-20260814.md`.

### PREPARED-P0 decoded-key ceiling (2026-08-14)

The first prepared-key gate caches only fixed key work: public `h` for Encap,
and secret `f`/`hinv` for Decap.  Required serialized/hash fields stay in the
context, and prepared operation bodies consume private SoA directly without a
per-call polynomial copy.  This preserves all arithmetic and wire semantics
and measures the maximum value of making key decode free.

A fixed same-ELF SUPERcop core-cycle test over 16 fresh processes reports
prepared-minus-normal medians of `-211.187` cycles (`-0.749%`, 14/16 favorable,
95% bootstrap CI `[-266.50,-129.75]`) for Encap and `-364.854` (`-1.898%`,
16/16, CI `[-406.63,-331.42]`) for Decap.  Prepare costs are 409.56 and
562.19 cycles, so both amortize by approximately the second operation.  The
gate supports a repeated-key prepared API, while proving that decoded-key
caching alone cannot approach a 10% one-shot KEM improvement.  See
`results/tile4-supercop-prepared-p0-20260814.md`.

### Slot-aligned VPBLENDD cross-lane gate (2026-08-14)

`GT32-VPBLENDD-CROSSLANE-001` selects one real Fastest-Clean production
boundary while freezing its mathematics and consumer: inverse S2 inside
`gt32_global_inverse_core_asm`, between the private-M input/S1 transitions and
the unchanged inverse S3/T9 suffix.  Q24-to-SoA and B3-entry transposes were
not selected because they contain no cross-128-bit permutation to delete.

The exact symbolic gate proves that slot-aligned `vpblendd` cannot reduce this
boundary.  It preserves each dword's 128-bit-half coordinate.  For one S2
pair, forming both low/high pair-packed operands requires two cross-half
outputs, and restoring both ordinary-layout outputs for the frozen S3
consumer requires another two.  Since one `vperm2i128` produces one YMM, the
lower bound is four cross-half instructions per pair, exactly the current
implementation.  With four pairs per tile and six tiles, both current cost
and lower bound are 16 per tile and 96 per inverse.

No assembly or benchmark is emitted: `vpblendd` can cheaply select same-slot
dwords, but it cannot perform the half movement that this boundary requires.
Keeping the two extracted pair-packed outputs would change the S3 ABI and is
therefore outside this bounded gate; that larger problem is already covered
by the global physical-layout search.  Reproduce the proof with
`make vpblendd-crosslane-generate`; the artifact is
`generated/tile4_vpblendd_crosslane_gate.json`.

### Inverse S2-to-S3 pair-packed gate (2026-08-14)

`INV-S2-S3-PAIRPACKED-001` tests the proposed consumer relaxation directly.
S2 arithmetic and input formation remain unchanged, while its output may stay
as pair-packed `S` and `D`; S3 register assignment and twiddle-table ordering
are free, but the mathematical S3 butterfly and post-S3 consumer state remain
fixed.

The exact DAG shows that the two current post-S2 `vperm2i128` instructions are
not an independent canonicalization pass.  They form precisely the two S3
arms: `L=[S.low,D.low]` and `H=[S.high,D.high]`.  Each arm is a distinct YMM
and contains one half that changed physical half, so two one-destination
cross-half instructions are the lower bound.  Reordering S3 twiddles can
relabel coefficient-wise constants, but cannot change which data values form
an add/sub butterfly.

Consequently the apparent deletion of 48 output permutes per inverse merely
reintroduces 48 S3 operand-forming permutes.  Net deletion is zero, so no ASM
or benchmark is emitted.  The remaining nonredundant question begins earlier:
a joint post-S1/dword-transition through S2/S3 physical search must determine
whether the producer can supply both arms without paying the same movement.
Reproduce this gate with `make inverse-s2-s3-pairpacked-generate`; see
`generated/tile4_inverse_s2_s3_pairpacked_gate.json`.

### Inverse post-S1 through S3 joint physical gate (2026-08-14)

`INV-S1-S2-S3-JOINT-PHYSICAL-001` expands the preceding gate to the machine
state after inverse S1 and its dword transition.  It searches all 5,040
physical states with the exact transition library already proved by the
global physical-layout generator, and minimizes lexicographically: true
cross-128-bit-half instructions, all shuffle instructions, then critical
depth.  Retained pair-packed stage output is covered by taking a one-way
transition before arithmetic and not restoring the previous state.

The minimum ties the current route at 16 cross-half instructions, 24 total
shuffles and 11 critical layers per tile.  A different optimal route can make
S2 cross-YMM, but then must pay a qword unpack and a `vpermq` half crossing to
restore the fixed post-S3 endpoint.  Thus it exchanges eight
`vperm2i128`-class operations for eight `vpermq`-class operations per tile;
over six tiles, both current and candidate remain at 96 true cross-half and
144 total shuffle instructions.

Because no metric improves, no tied ASM variant is emitted.  Reproduce with
`make inverse-s1-s3-joint-physical-generate`; the proof is
`generated/tile4_inverse_s1_s3_joint_physical_gate.json`.

### Inverse S2--S5 free-terminal gate (2026-08-14)

`INV-S1-S5-FREE-TERMINAL-001` removes the current inverse output ABI from the
search.  It starts at the qualified pre-S2 state, keeps the exact S2--S5
arithmetic/range/scale contract, and quotients terminal YMM renaming, twiddle
relabeling and whole-vector store-address permutation.  The objective is
lexicographic cross-half operations, total shuffles, then critical depth.

Unlike the fixed-terminal gates, this search finds real freedom.  Cross-half
work falls from 16 to 8 instructions per tile, hence from 96 to 48 per full
inverse.  The selected state executes q1/q2/q3 as cross-YMM stages and leaves
a noncanonical terminal after lane-local transitions place q4 on a vector
selector.  The trade is not a standalone win: shuffle count rises from 16 to
24 per tile and critical depth from 18 to 19.  Across six tiles this exchanges
48 true cross-half operations for 48 additional lane-local shuffles.

No standalone inverse ASM is emitted.  The candidate advances to a joint
`B3 -> inverse -> T9` physical gate, where B3 may absorb its input state and
T9 may consume the free terminal.  Reproduce with
`make inverse-s1-s5-free-terminal-generate`; see
`generated/tile4_inverse_s1_s5_free_terminal_gate.json`.

### Meteor Lake shuffle-class cost gate (2026-08-14)

`MTL-SHUFFLE-CLASS-COST-001` measures dependent and 2/4/8-independent-stream
forms of `vperm2i128` and `vpunpck{w,d,q}` on the target Core Ultra 7 155H.
The permanent benchmark uses grouped hardware core-cycle/instruction/reference
events with TSC corroboration, CPU-1 affinity, eight fresh launches, and both
normal/reversed link placements.  Each reported operation retires one
instruction after subtracting an identical loop control.

The 8-stream steady-state normal-placement costs are 0.98442 core cycles for
`vperm2i128` and 0.48442 for every unpack width; reversed results agree within
0.00001.  Thus `L/G` is 0.49208 in both placements, only narrowly below the
free-terminal break-even condition `L < G/2`.  Under a deliberately additive
contention model, `16G` versus `8G+16L` would save about 0.125 core cycles per
tile, or 0.75 per six-tile inverse.  This is a model bound, not a measured
mixed schedule: isolated reciprocal throughput does not reveal whether global
and local shuffle resources overlap.  MIX-002 supplies that measurement.

### Meteor Lake mixed shuffle schedule gate (2026-08-14)

`MTL-SHUFFLE-MIX-COST-002` measures interleaved routing ratios, the generated
free-terminal dependency shape, and both shapes under an identical finite
24-instruction Montgomery-like arithmetic background.  The pure 8-global plus
16-local mix costs 11.327 core cycles per tile versus 15.000 for 16 global,
so real resource overlap saves 3.673 cycles.  Preserving the proof-route
dependency layers still saves 2.507 cycles (12.493 versus 15.000).

Arithmetic contention reverses the result.  The current-like 16-global route
plus arithmetic costs 16.331 core cycles per tile; the interleaved free mix
costs 17.255 (`+0.923`), and the dependency-shaped free route costs 18.021
(`+1.690`).  Normal and reversed placements agree within about 0.002 cycles.
The arithmetic chains start with fresh destinations and consume routing
outputs, avoiding an artificial loop-carried arithmetic dependency.

This calibration gives the correct reason to reject a standalone
free-terminal variant: routing overlap is real, but disappears under the
relevant arithmetic background.  The joint Pareto gate remains active only
for candidates that additionally remove B3/inverse-entry or inverse/T9
boundary work.  Reproduce with `make bench-mtl-shuffle-class`; results are in
`results/tile4-mtl-shuffle-mix-cost.json`.

### Prepared fixed-operand B3 (2026-08-14)

`PREPARED-FIXED-B3-001` expands a fixed private-SoA operand at key-prepare
time into four pair-packed dot-product rows per quartic output.  The matrix is
6,144 bytes per fixed polynomial.  Runtime uses sixteen `vpmaddwd` operations
and eight REDC16 accumulators per 16-leaf block; lambda multiplication and the
fixed operand's pair formation have disappeared.  Rows are stored at `e=1`,
so the mandatory REDC16 directly emits general-product `e=0` and replaces the
current runtime R-squared finalizer.

The scale edge `c*f -> inverse` is not emitted: it cannot delete a finalizer,
and its 153-instruction fixed-dot shape is larger than the 127-instruction
scale B3.  The general `h*r` and `(c-mhat)*hinv` edge is executable.  It passes
1,000 randomized modulo-q trials, uses no stack/spill, and has 153 static
instructions versus 154 for general B3.  Eight 20-sample launches per link
placement save about 31--33 TSC normal and 27--37 TSC reversed before its
consumer.

REDC16's output is deliberately noncentered.  Conservative bounds are 4,594
for Encap and 4,796 for the second Decap product; Encap's subsequent add stays
within 15,382.  The already-qualified H1 Q24 reducer covers the complete
signed-int16 domain, so no new center pass is required.  Adding a standalone
three-instruction center per output makes the local candidate 3--9 TSC slower
and is rejected.

The independent SUPERcop prepared export passes deterministic Encap, valid
Decap, and 16 malformed-ciphertext differentials.  A first cross-binary view
against nonprepared CleanGT reported `-248.10` core cycles for Encap and
`-387.81` for Decap, but that number cannot attribute the matrix itself.

The decisive same-ELF gate contains both the original Prepared-P0 generic B3
and Prepared-Fixed-B3.  Sixteen launches leave Encap at only `-16.71` core
cycles (11/16 favorable, CI `[-85.63,+19.08]`) and make Decap `+41.21` cycles
slower (4/16, CI `[+5.21,+95.38]`).  Decap repays the local B3 saving because
the noncentered REDC16 output requires H1 rather than the centered recovered-r
pack.  Fixed preparation also costs an additional 3,560/3,651 cycles per
public/secret key; even the unstable Encap median would need about 213 calls
to amortize it.  Therefore the general fixed-dot primitive remains a useful
local oracle, but the prepared caller integration is hard-stopped and neither
the prepared API nor production selector changes.

Artifacts: `generated/tile4_prepared_fixed_b3_gate.json`,
`src/tile4_prepared_fixed_b3.{c,h}`, `src/tile4_prepared_fixed_b3_asm.S`, and
`results/tile4-supercop-prepared-fixed-b3-incremental-20260814.json`.

### Prepared fixed-f B3 to inverse-S1 composition (2026-08-14)

`PREPARED-F-B3-INVS1-STATIC-001` evaluates the remaining prepared-key
composition separately from the rejected standalone fixed-f scale B3.  A
production-code audit corrects an important premise: S1 in
`gt32_global_inverse_core_asm` is a raw add/sub butterfly and layout route.  It
has no S1 twiddle or Montgomery reduction to fold into prepared constants.

The current replaced region is 134 instructions per 16 leaves: one exact
114-instruction B3-scale loop plus 20 instructions, amortized, from the
40-instruction inverse-S1 prefix per 32 leaves.  A composed schedule can avoid
the intermediate B3 stores/loads, form the S1 sum/difference in int32, and do
eight terminal REDC16 representatives.  The eight-term accumulator bound is
47,775,744, leaving ample signed-int32 margin; the conservative REDC16 output
bound is 4,185.  A no-spill schedule fits in 14 YMM registers.

The known exact physical route still needs 20 instructions after compaction.
The complete executable accounting is therefore 117 instructions, only 17
fewer than control (12.69%).  It does not eliminate a fusion-specific
reduction layer and remains below the precommitted 15--20% local-cycle entry
gate.  No ASM is emitted.  Reopen only for an exact route of at most 12
instructions, producer-supplied pair-packed dwords, a wider ISA, or a later
consumer contract that deletes another complete route.  The generated proof
is `generated/tile4_prepared_f_b3_invs1_gate.json`.

### Encap typed final-representation architecture gate (2026-08-17)

`GT32-ENCAP-REPRESENTATION-ARCH-001` tests the bounded final-ciphertext
proposal, not another universal ABI.  It freezes `h` and `r` in production M
and enumerates all 120 coefficient-plane P-like Q-axis placements for:

```text
Forward(m) -> P
B3(M,M)    -> P
add(P,P)   -> P
Q24(P)     -> wire
```

The accounting is executable AVX2 routing: the exact Forward schedule, the
minimum physical-bit path from M-valued B3 lanes to P, and the residual Q24
qword route.  B3 arithmetic, `vpaddw`, Q24 reduction and 12-bit packet math
are common and excluded.

No distinct P beats the current M island.  The best distinct layout
`[q2,q1,q0,q3,q4]` saves 48 Forward instructions and 41 Q24 route
instructions, but B3 must pay a 96-instruction M-to-P transition, producing a
net **+7 instructions**.  Current Keygen P is net **+13 instructions** on this
Encap edge.  Neither candidate deletes a complete transition,
materialization, Montgomery chain, or checkpoint, so no assembly or `r_D`
search is emitted.

The search also identifies a smaller, different opportunity: retaining M and
absorbing symmetric Q24 qword swaps into the transpose tail has a static
ceiling of 25 instructions per pack, or 50 across the two Encap packs.  This
is recorded as a deferred local Q24 code-shape probe, not as a representation
architecture result; it remains below the required 50--80 core-cycle
mechanism.  Reproduce with `make encap-representation-architecture-generate`;
the proof is `generated/tile4_encap_representation_architecture_gate.json`.

### Encap serializer-side M-domain add gate (2026-08-17)

`GT32-ENCAP-Q24-SUM-M-001` keeps the production M representation and moves
the final `+m` to the Q24 load seam.  The candidate loads the B3 product,
uses 48 memory-source `vpaddw` operations for the M-domain message, and then
reuses the proven v=9 high-range reduction and exact packet route.  Relative
to the production control it removes the standalone 48-vector load/store
`poly_add` pass and shrinks the Encap stack from 8,128 to 6,592 bytes.

Correctness passes 1,000 high-range codec trials, the guarded final packet,
100 full deterministic Encaps, and all 768 single-slot noncanonical public
keys.  The local same-ELF edge is genuinely faster: Normal/Reversed launch
medians are -17.78/-16.12 TSC (8/8 favorable each), while single-event PMU
reports about -21.23/-25.68 core cycles.

The full caller does not preserve that result.  Normal improves by -52.25
TSC with 8/8 favorable launch medians, but Reversed is +14.26 TSC with only
2/8 favorable.  The candidate also adds a distinct 4,914-byte unrolled
serializer body.  Therefore the materialization deletion is locally
qualified but production promotion is hard-stopped: its gain is smaller than
the whole-image delivery perturbation.  No padding/alignment search is
opened.  See `generated/tile4_encap_q24_sum_gate.json` and
`results/tile4-encap-q24-sum-m-full-short.json`.

### CRT / wide-twist coordinate gate (2026-08-17)

`GT32-CRT-TWIST-COORDINATE-001` tests whether a different equivalent
CRT/leaf coordinate can simplify or eliminate the 48 wide-twist Montgomery
chains in one Forward.  The production table is highly structured, but the
structure is slightly subtler than a plain `k mod 3` split.  Reducing
`64*row+33*k` modulo 96 creates three cyclic row-ratio triplets separated by
one representative carry seam; each individual row ratio consequently has
only two values.

The first search enumerates 3,072 affine parameters

```text
k3'  = a*k3 + b*(k32 mod 3) mod 3
k32' = c*k32 + d*k3 mod 32
```

and finds 1,088 bijections.  None makes the twist multiplicatively
separable, DFT3-column-permutation absorbable, or turns even one four-qword
wide vector into a one- or two-constant vector.  In particular, the proposed
`k3 +/- k32 mod 3` shears retain ratio cardinalities `[2,2,2,2]` and create
240 NTT32 edges crossing the new row coordinate.  The only two candidates
that preserve both DFT3 locality and radix-2 NTT32 geometry are the current
coordinate and a global row inversion.

There is nevertheless an exact positive algebraic result outside that
affine family.  The carry-aware cyclic row rotations

```text
[0,2,0,1,2,0,1,2,...,0,1,2]
```

are common to both top-split branches and factor the table exactly as
`T[branch,row,k] = A[branch,row] * B[branch,k]`.  The two `A` ratios are
`[1,867,1520]` and `[1,1886,3200]`.  Away from the single CRT seam, `B` advances
by `2^-1=1729` or `22^-1=1100` on every k edge.

This separability does not accelerate the current N5 schedule.  The present
wide-twist plus one-multiply DFT3 region costs 64 vector Montgomery chains per
Forward.  Scaling the two nontrivial `A` rows and performing DFT3 costs 48;
applying the common `B` after DFT3 adds another 48, for 96 total.  Pushing `B`
into NTT32 instead makes the currently raw S1 nonidentity.  Its 96 scalar
butterflies are packed as four YMM Montgomery chains per tile across six
tiles: 24 vector chains.  The resulting total is therefore 72, not 144.
The coordinate change simplifies the table but still adds eight vector
chains in the current schedule.

No assembly or cycle benchmark is emitted.  Reopen only if a joint
DFT3/NTT32 factorization absorbs `B` without making S1 nonidentity, a
non-affine executable topology deletes a complete Montgomery chain, or a
wider ISA changes the cross-row economics.  Reproduce with
`make crt-twist-coordinate-generate`; the complete proof is
`generated/tile4_crt_twist_coordinate_gate.json`.

### Stage-gauged geometric twist absorption (2026-08-17)

`GT32-GEOMETRIC-TWIST-STAGE-GAUGE-001` follows the positive carry-aware
factorization with the narrower question: can an equivalent separable gauge
make the one raw radix-2 stage free, while the remaining four binary factors
are absorbed by replacing existing S2--S5 twiddle constants?

There are exactly three common cyclic-row gauges, differing by a global row
rotation.  All five possible raw-stage bits were checked for both branches
and all gauges (120 radix stage orders).  Every one of the sixteen edges in
every possible raw stage has a nontrivial `B[k xor 2^bit]/B[k]` ratio; none is
`1` or `-1`.  For distance 16 the two values are 2775 and 3310, with the
single seam exchanging which branch receives the exceptional value.  Moving
the seam or globally rotating rows cannot eliminate it.

An accounting correction is essential.  The contaminated S1 contains 96
quartic butterflies, but production packs them into four YMM Montgomery
chains per tile across six tiles: **24 vector chains**, not 96.  The current
wide twist plus DFT3 costs 64 vector chains.  The known separated schedule
costs 32 for the two nontrivial A-row scalings, 16 for DFT3, and 24 for the
new nonidentity raw stage, totaling 72; the lower four stages only replace
existing constants.  Thus the best known schedule is `+8` vector chains, not
the previously reported `+80`.

No assembly is emitted.  The precise reopen condition is now small: synthesize
`DFT3*diag(A)` in at most two YMM Montgomery chains per branch/group, find a
non-cyclic gauge with one complete identity/negative-identity radix bit, or
fold the raw-stage ratio into an independently required multiplication.
Reproduce with `make geometric-twist-stage-gauge-generate`; the proof is
`generated/tile4_geometric_twist_stage_gauge_gate.json`.

### Shifted DFT3 two-chain multiplicative-complexity gate (2026-08-17)

`GT32-SHIFTED-DFT3-TWO-CHAIN-001` tests the sole arithmetic continuation left
by the corrected `72 versus 64` stage-gauge accounting.  For both branches the
matrix is

```text
DFT3 * diag(1,a,a^2),
a = 867 or 1886,  867*1886 = 1 (mod 3457).
```

The exhaustive sequential circuit model permits

```text
m0 = C0 * (alpha dot x)
m1 = C1 * (b dot x + beta*m0)
y  = Gamma*x + u*m0 + v*m1
```

with arbitrary field constants `C0,C1`; thus the second Montgomery chain may
depend on the first.  G1 restricts all remaining coefficients to `0,+/-1`.
For each branch it checks 44,928 distinct first-chain results over 13 small
projective input lines and finds no solution.

G2 exhaustively expands every cheap coefficient to `0,+/-1,+/-2`.  It checks
all 1,953,125 small `Gamma` matrices per branch, 19,454/19,327 singular rank-2
residuals, and 953,040 compatible small-plane basis factorizations per branch.
There is no rank-at-most-one residual and no valid sequential two-chain
factorization for either `a`.

This is not an unrestricted theorem about field multiplicative complexity,
but it closes the AVX2-relevant pure add/sub and bounded-double circuit family
that motivated the gate.  No assembly or benchmark is emitted; the known
three-chain A-scale plus DFT3 schedule remains, so the stage-gauged path stays
at 72 versus the current 64 YMM chains.  Reopen only for a supplied symbolic
identity outside this circuit model, or if the nonidentity raw-stage factor
can be folded into an independently required producer multiplication.
Reproduce with `make shifted-dft3-two-chain-generate`; the proof is
`generated/tile4_shifted_dft3_two_chain_gate.json`.

### Frontend dependency/schedule gate (2026-08-17)

`GT32-FRONTEND-F1-F4-001` changes neither arithmetic, representation nor
materialization.  F1 computes `s=L+H` independently of `t=-722H`, then emits
`B0=L+t, B1=s-t`.  F4 routes branch 0 and launches its three Montgomery
chains before routing branch 1, using the independent blends to cover the
multiply latency.  F14 combines both changes.

All four frontend bodies are exactly 3,917 bytes with the same 858
disassembly lines, instruction multiset, register footprint and no spills.
The 1,000-trial exact frontend/Forward differential and the complete
`make check` pass.  Across two symbol orders and eight launches, F14 saves
5.81--7.32 TSC and 10.39--11.87 core cycles per Forward; the two-Forward
region saves 13.44--15.70 TSC and 20.96--23.10 core cycles, normally with
18--20/20 paired wins.

Whole Encap does not provide promotion evidence.  A same-ELF gate containing
four 3.9-KiB frontend variants is image-polluted, while clean control/F14
ELFs have identical section sizes and all relevant symbol addresses but
still show launch/runtime variance larger than the intrinsic ~14-TSC effect,
even as non-PIE binaries.  F14 is therefore retained as the default-off local
kernel champion; production remains unchanged pending fixed-ELF SUPERcop
corroboration.  See
`generated/tile4_frontend_dependency_schedule_gate.json`.

### Cross-unit wavefront scheduling closure (2026-08-17)

`GT32-WAVEFRONT-SCHEDULING-001` tested the three remaining non-fusion
software-pipeline boundaries with arithmetic, layouts, constants and range
contracts frozen.  F14-W2 moves the next packet's two high-vector loads into
the dead-register window between the current packet's two DFT3 tails.  It is
exactly the same 3,917 bytes and instruction multiset as F14, uses all 16 YMM
registers without spills, and passes 1,000 exact trials.  Across eight launches
in both symbol orders, a full Forward improves by about 1.21--1.56 TSC and
1.68--2.30 core cycles; two Forwards improve by about 2.39--2.65 TSC and
3.90--4.09 core cycles.  This is a real same-work scheduling micro-win, but is
too small for independent whole-image promotion.

The N5 tile wavefront reuses each just-stored output register for the matching
next-tile load.  It passes 1,000 trials and is negative in core cycles in all
eight launches, but saves only 1.04 core cycles over the complete six-tile N5
while growing the safely peeled symbol by 101 bytes.  The B3 block wavefront
can preload all four next-block B planes in `ymm9..ymm12` during the four R^2
chains with peak 13 YMM and no spill.  It also passes 1,000 trials and all eight
launches, but saves only 1.47 core cycles while adding 184 bytes.  N5 and B3
wavefronts are therefore hard-stopped; F14-W2 remains benchmark-only.  The
combined result is that cross-unit scheduling is measurable but already below
caller-significant scale on this AVX2 target.  See
`generated/tile4_wavefront_schedule_gate.json` and
`results/tile4-frontend-f14-wavefront.json`.

### M-domain Q24 transpose-tail orientation (2026-08-17)

`GT32-Q24-M-TF1-001` leaves the M layout, v=9 reducer, canonical correction,
packet order and stores unchanged.  Of the control's 48 qword permutations,
11 symmetric `0xb1` swaps are absorbed by reversing the corresponding final
`vpunpcklqdq/vpunpckhqdq` operands and 14 pre-existing identity permutations
are omitted.  The candidate therefore retires exactly 25 fewer instructions
per serialization and retains only 23 `vpermq` instructions.

Control and candidate occupy matched 5,120-byte cages.  Exhaustive scalar
testing over `[-12699,12699]` is Official-byte-exact, the safe final packet is
unchanged, and `make check` passes all 1,000 trials.  Across four launches in
both symbol orders, a single pack saves 8.3--9.3 core cycles and 5.0--5.9 TSC;
the mixed lazy10788/highrange12699 two-pack region saves 18.2--19.4 core cycles
and 9.7--12.3 TSC.

Full Encap is not promotion evidence: with identical relevant symbol
addresses, eight-launch medians show -124.3 TSC in Normal but +6.3 TSC in
Reversed.  This is consistent with whole-caller delivery variance exceeding
the intrinsic approximately 11-TSC two-pack effect.  TF1 is retained as a
default-off, locally qualified Q24 champion for later composition; production
remains unchanged.  See `generated/tile4_q24_m_tf1_gate.json`.

### Same-ELF Encap residual attribution (2026-08-17)

`SAME-ELF-ENCAP-RESIDUAL-ATTRIBUTION-001` places C00 (Clean), C10
(F14), C01 (TF1), and C11 (F14+TF1) in one ELF.  All four Encap wrappers are
611 bytes; the two frontends are matched 3,917-byte bodies and the two Q24
serializers are matched 5,120-byte cages.  The 100-case valid differential,
malformed-public-key checks, and the complete 1,000-trial test suite pass.

The full-call TSC factorial does not recover the known approximately -25-TSC
local signal, even with ASLR disabled.  Normal reports C11-C00 = +22.4 TSC
and Reversed -7.1 TSC, with large non-additive interactions.  A/A, A/B, B/A,
B/B and homogeneous/alternating/blocked sequences do not show a stable
predecessor or transition penalty.  This rejects a simple model in which one
implementation consistently pollutes the next.

Two interaction estimators are now reported separately.  The ordinary
factorial interaction computed from the four reported cell medians is
`C11-C10-C01+C00`: -9.4 TSC in Normal and -68.1 TSC in Reversed for the
recorded run.  The median of the per-sample paired interactions is a different
robust estimator (-17.7/-33.6 TSC in that run) and must not be labelled as the
cell-median factorial interaction.

Region-scoped PMU measurement changes the conclusion about the arithmetic
signal.  Counters are enabled only after warm-up and C00/C11 are paired inside
the same process.  C11 always retires exactly 51 fewer instructions and one
fewer branch.  Across 64 pairs per placement it has a median core-cycle delta
of -58.4 (50/64 negative, bootstrap median CI [-111.0,-17.4]) in Normal and
-21.8 (34/64 negative, CI [-100.9,39.8]) in Reversed.  The known local signal
is therefore visible in paired core work, but is not stable enough for
full-caller TSC promotion in Reversed.

L1I and iTLB miss deltas are effectively zero.  DSB/MITE delivery changes
substantially with link order, while the architectural instruction delta stays
fixed.  The remaining variance is classified as relative-code-geometry and
frontend/branch-delivery sensitivity, not a Q24/Forward arithmetic loss and
not an ASLR-base or cache-miss effect.  F14 and TF1 remain default-off local
champions.  Future Official-versus-Clean claims below 100 cycles must use
same-process paired region-scoped PMU, with TSC only as corroboration.  See
`generated/tile4_encap_same_elf_residual_gate.json`.

### Official versus Clean Encap polynomial island (2026-08-17)

`SAME-ELF-OFFICIAL-CLEAN-POLY-ISLAND-001` now measures four same-ELF semantic
regions: R1 Decodeq(h), R2 Forward(r)+Q24(rhat), R3
Forward(m)+BaseMul+add+Q24(ciphertext) with prepared h/r, and R4 the complete
island.  Hashes, CBD/SOTP production, and KEM copy/clear glue are outside the
measured regions.  Official, current production Clean, and Clean+F14+TF1 use
identical real producer outputs and produce exact R1--R4 endpoints over 100
trials.

With ASLR disabled, eight launches, explicit ABBA/BAAB pairing, and both link
orders, R4 current Clean beats Official by 57.3/64.0 TSC and 78.8/107.6
paired core cycles, while
retiring exactly 1,003 fewer instructions.  F14+TF1 extends the R4 win to
70.3/79.5 TSC and 108.8/143.6 core cycles, with 1,054 fewer instructions.
Every R4 candidate/placement has a strictly negative bootstrap upper bound.

The decomposition identifies the trade clearly.  Clean R1 costs +20.5/+20.6
TSC and +33.5/+33.8 core cycles, while R2 saves 43.6/44.8 TSC and R3 saves
37.2/43.4 TSC.  Retired-instruction closure is within 11--13 instructions:
R4 minus R1/R2/R3 has only -13 instructions for Clean and about -11 for
F14+TF1.  Core-cycle residual is placement-sensitive (+22.7/+6.3 Clean and
+20.4/approximately 0 F14+TF1), so arithmetic work closes but executable delivery does
not.  GT also retires 654 more loads but 179 fewer stores in R4; the load debt
is now a concrete next attribution target.

The result formally qualifies the GT32 Encap polynomial architecture as the
winner: current Clean is about 3.4--3.8% faster in TSC for this island, and the
local-champion composition is about 4.2--4.8% faster.  F14+TF1 contributes another
13.8/19.4 TSC over Clean in R4, below the prior 23--28 TSC local expectation,
so it remains unpromoted.  GT still shifts several
thousand delivered uops from DSB to MITE and pays about 20--23 DSB/MITE penalty
cycles, yet wins; L1I and iTLB deltas remain negligible.  Therefore the
remaining full-Encap problem is integration/front-end delivery and extra load
work, not NTT/B3 arithmetic.  NTT arithmetic remains frozen.  The next
experiment is load attribution outside/around the island, not another shuffle
or alignment search.  See `generated/tile4_encap_poly_island_gate.json`.

### Polynomial load closure and outside-island causal gate (2026-08-17)

`POLY-ISLAND-LOAD-CLOSURE-001` closes the apparently suspicious load count.
R1/R2/R3 contribute +105/+224/+329 retired loads, summing to +658 versus
R4's +654; the residual is only -4 loads.  Stores similarly sum to -175
versus -179, and instructions sum to -990 versus -1,003.  The +654 loads are
therefore not hidden benchmark glue.  They are the structural footprint of
the measured polynomial architecture.  Crucially, 553 of the 658 summed
extra loads are in R2/R3, which are faster by 44 and 37--43 TSC.  Aggregate
load reduction is not a valid objective; R1 Decode remains the only locally
demonstrated polynomial debt.

`SAME-ELF-ENCAP-OUTSIDE-ISLAND-RESIDUAL-001` initially exposed a measurement
trap.  Duplicating the same shared C source in Official and GT cumulative
prefixes let the compiler create different bodies, so the purported shared
stage no longer had identical machine code.  The corrected harness calls one
physical `noinline,noclone` prework symbol, one middle-glue symbol, and one
common-tail symbol from both predecessors.  Architectural closure is exact:
each shared stage has zero instruction/load/store delta, while the complete
wrapper reports -1,009 instructions, +654 loads, and -179 stores.

Adjacent cumulative-prefix latency subtraction is still not a component-cost
estimator.  It varies sharply with cut, event group, and link order even when
the incremental architectural work is exactly zero.  A stronger causal probe
therefore brackets only the identical shared consumer after preparing either
the Official or GT predecessor.  Middle glue differs by only +2.86 TSC in
Normal (4/8 GT-favorable pairs) and -8.44 TSC in Reversed (6/8); common tail
is -0.06/+1.28 TSC.  There is no stable 50--100-cycle intrinsic hash/SOTP or
tail penalty.  The large whole-caller residual is a whole-prefix/whole-image
delivery and code-geometry interaction, not missing polynomial work and not a
specific shared crypto component.

NTT/B3/Q24 arithmetic remains frozen.  The next valid gate is
`PRODUCTION-HOT-CODE-CLOSURE-001`: remove unreachable benchmark variants and
tables, verify the selected `.text`/`.rodata` reachability set, then benchmark
a fixed production-shaped ELF.  See
`generated/tile4_encap_poly_island_load_closure_gate.json` and
`generated/tile4_encap_outside_island_gate.json`.

### Production hot-code closure (2026-08-17)

`PRODUCTION-HOT-CODE-CLOSURE-001` compares the same selected CleanGT KEM as
an intentionally unpruned image (G0) and a physically pruned image (Gc).
The gate found and fixed a real closure bug: the pruner recognized only the
transpose-cut Forward emitter and missed other `FR_*FUNCTION` emitters, so two
unused wavefront Forward variants survived the clean export.

After the fix, linked `.text` falls from 128,919 to 64,407 bytes (-64,512,
50.04%), and named GT text symbols fall from 75 to 18.  `.rodata` falls only
from 57,576 to 56,808 bytes (-768, 1.33%); the remaining constants are mostly
shared or physically monolithic, so table closure is not the dominant result.
Normalized disassembly of every one of the 18 retained GT symbols is exactly
identical between G0 and Gc, including instruction count, operands modulo RIP
displacement, branches, and register allocation.  Thus the experiment changes
image closure, not hot arithmetic.

The formal SUPERcop matrix uses `BENCH_CPU=1`, O3 plus function/data sections
and linker GC, and four valid palindromic blocks in the order
Official/G0/Gc/Gc/G0/Official.  SUPERcop `try` and `constbranchindex` pass for
every image/run.  Pooled stabilized-Q2 cycle deltas are:

| operation | G0 - Official | Gc - Official | Gc - G0 |
|---|---:|---:|---:|
| keypair | -133.0 | -184.2 | -51.1 |
| encap | +293.2 | +99.6 | -193.6 |
| decap | -104.9 | -217.8 | -112.9 |

Closure improves Encap and Decap in all four blocks; Keypair improves in three
of four.  Encap's per-block Gc-G0 deltas are -100.8, -261.0, -296.2, and
-28.2 cycles.  Therefore executable closure is a real delivery mechanism and
recovers most of G0's Encap integration loss.  It does not finish Encap
promotion: Gc remains about +100 cycles behind Official in the pooled result.

A whole-process fixed-ELF PMU corroboration (16 samples/image) is diagnostic,
not per-operation attribution.  Gc shifts about 197k uops away from MITE and
373k toward DSB, reduces IDQ-not-delivered by about 103k, and reduces whole
measure core cycles by about 56k.  This is directionally consistent with the
closure hypothesis, although SUPERcop operation cycles remain the promotion
metric.  No padding or alignment sweep was performed.

Decision: physically pruned closure becomes the only valid CleanGT export
shape; the unpruned image is retained only as the causal control.  Arithmetic,
Q24 packet mathematics, and the selected hot instruction sequences remain
frozen.  Encap still needs a separate mechanism or hot semantic grouping to
close the remaining approximately 100-cycle gap.  See
`generated/tile4_production_hot_code_closure_gate.json`,
`results/tile4-production-hot-code-closure-supercop.json`, and
`results/tile4-production-hot-code-closure-frontend-pmu.json`.

### Production hot-function grouping (2026-08-17)

`PRODUCTION-HOT-FUNCTION-GROUPING-001` tests the one remaining geometry
hypothesis without changing arithmetic.  A direct-call/tail-jump reachability
audit finds 22,559 named function bytes (25 functions) reachable from Encap,
versus 64,407 linked `.text` bytes.  The classified unique named bytes are
16,669 shared, 5,890 Encap-only, 9,273 Keypair-only, 12,747 Decap-only, and
19,618 cold/unreachable.  This gave semantic clustering a legitimate static
rationale.

H0 is the pruned Gc default order.  H1 orders production sections by Encap
first dynamic use.  H2 groups the reusable Forward/BaseMul/Q24 and hash chains
using weighted transition rationale.  GNU ld's section-ordering-file performs
only input-section permutation.  All three images have exactly 64,407 bytes of
linked `.text`; normalized disassembly of all 105 common production functions
is identical, while hot function addresses change.  H1/H2's extra 224 rodata
bytes are only the longer compiler-identification string embedded by the
SUPERcop harness, not implementation constants.

Four fixed-core palindromic SUPERcop blocks use
H0/H1/H2/H2/H1/H0.  Both semantic orders are decisive regressions:

| operation | H1-H0 | H1 wins | H2-H0 | H2 wins |
|---|---:|---:|---:|---:|
| Keypair | -38.2 | 4/4 | +19.3 | 2/4 |
| Encap | +210.5 | 0/4 | +228.4 | 0/4 |
| Decap | +160.1 | 0/4 | +142.9 | 0/4 |

Encap's H1 per-block deltas are +217.3/+140.4/+200.5/+274.6 cycles;
H2 is +223.6/+200.2/+237.2/+262.6.  This is a cycle-level hard stop for
semantic linear grouping.  Function proximity does not model the relevant DSB
set/address interactions well enough, and concentrating Encap code damages the
other production paths.  H1's small Keypair win cannot justify Encap and Decap
regressions.

Per the predeclared stop rule, there is no H3/H4/H5 search, no padding sweep,
and F14/TF1 are not reintroduced.  H0/Gc remains the production baseline.
Physical dead-code closure remains promoted; further function-order search is
closed.  The next useful work must provide a non-layout structural mechanism,
or return to the measured Decode debt.  See
`generated/tile4_hot_function_reachability.json`,
`generated/tile4_hot_function_grouping_static.json`,
`generated/tile4_production_hot_function_grouping_gate.json`, and
`results/tile4-production-hot-function-grouping-supercop.json`.

### Production reachable-hot-text compaction (2026-08-17)

`PRODUCTION-REACHABLE-HOT-TEXT-COMPACTION-001` tests whether G0-to-Gc's
successful physical-closure mechanism continues inside the 25-function Encap
reachable set.  The static census accounts for all 22,559 named bytes.  The
only zero-cost intra-symbol candidate is the production lazy10788 Q24
serializer: its executed body ends after 4,543 bytes but a placement cage pads
the symbol to 5,120 bytes.  Decode, frontend, Forward and B3 have no comparable
post-return NOP suffix.

C0 removes only that cage.  The retained serializer instruction prefix has an
identical SHA-256 in Gc and C0, the canonical 100-vector KAT is byte-exact, the
symbol shrinks from 5,120 to 4,543 bytes, and linked `.text` shrinks from
64,407 to 63,831 bytes.  Nevertheless, the formal fixed-CPU SUPERcop matrix
`Official/Gc/C0/C0/Gc/Official` rejects it:

| operation | C0 - Gc | C0 wins | C0 - Official |
|---|---:|---:|---:|
| keypair | +8.2 | 2/4 | -314.1 |
| encap | +45.2 | 0/4 | +39.0 |
| decap | -49.7 | 2/4 | -288.4 |

Encap's four C0-Gc block deltas are +100.7/+62.1/+1.4/+21.4 cycles.  Thus a
576-byte whole-text reduction is too small to lower frontend demand
materially; its address remapping effect still dominates.  C0 is retained only
as a dormant causal control and is not production-promoted.

C1 then performs the one permitted code-density trade-off.  It groups the 12
M-to-Q24 blocks into six fixed route templates while preserving the production
transpose, v=9 reducer, canonicalization and packet format.  Exhaustive
`[-12699,12699]` and guard-page tests pass.  The symbol shrinks from 5,120 to
2,321 bytes (-2,799), but each pack retires 108 extra instructions and costs
about +35.5 core cycles; two Encap packs cost about +70 core cycles.  This is
far above the predeclared +2--4-cycle density budget, so C1 stops before a
whole-image SUPERcop run.  Route-class reordering also requires safe block
tails, and scalar table/loop dependencies destroy the unrolled schedule's
throughput.

The cheap call-boundary audit finds 21 static direct call sites in the GT
Encap parent versus 19 in Official, not a 20--30-transition excess.  Wrapper
closure is therefore closed as a primary mechanism.  Gc/H0 remains the clean
production baseline; function reordering, padding, C0, C1 and frontend
re-rolling are closed absent a new schedule-preserving compaction mechanism.
The next bounded fallback is the measured Decode debt.  See
`generated/tile4_reachable_hot_text_compaction_census.json`,
`generated/tile4_production_reachable_hot_text_compaction_gate.json`,
`results/tile4-q24-hotcompact-c1-local.json`, and
`results/tile4-production-reachable-hot-text-compaction-supercop.json`.

### R1 Decode debt closure (2026-08-17)

`R1-DECODE-DEBT-001` separates the remaining Encap input-boundary debt without
changing the production decoder.  D0 is the qualified Q24 bytes-to-private-M
decoder.  D1 emits the exact same M words but intentionally omits canonical
validation and is attribution-only.  D2 splits the operation into a
bytes-to-wire-order-int16 unpacker and a wire-order-to-M router; this split
materializes 1,536 bytes and is not a candidate ABI.

Four launches per link order, fixed CPU 1, give these launch-median results:

| region | Normal TSC | Normal core | Reversed TSC | Reversed core | instructions |
|---|---:|---:|---:|---:|---:|
| D0 full fused Decode | 116.1 | 183.9 | 115.3 | 184.9 | 609.5 |
| D1 no validation | 103.7 | 166.0 | 104.3 | 166.5 | 546.5 |
| D2 unpack only | 93.2 | 149.2 | 93.8 | 150.7 | 463.5 |
| D2 M routing only | 64.0 | 102.4 | 64.0 | 102.4 | 303.5 |
| D2 materialized split | 153.3 | 245.3 | 153.3 | 245.2 | 760.5 |

Validation plus return aggregation accounts for 63 retired instructions and
about 18 core cycles, but it is required by the public Decode contract.
More importantly, unpack and M routing are not additive removable debts: the
materialized D2 split costs about 60--61 more core cycles and 151 more
instructions than D0.  The current Q24 shuffle masks already combine unpack
with quartic placement; separately reconstructing wire order loses that
fusion.

D3 tests the only proposed large mechanism: replace each group's eight XMM
packet loads with three contiguous YMM loads.  Every 96-byte group contains
four 12-byte windows crossing a 128-bit boundary.  Each target register pairs
one crossing and one non-crossing window at a different byte alignment.  On
AVX2, the best packet-window factorization requires three source-lane gathers,
two aligned crossing-window vectors, and four final lane merges per group.
Against the current four `vinserti128`, that adds 60 route/shuffle operations
over the polynomial, exceeding the predeclared +36 limit even though loads
fall by 60.  The total instruction lower bound is therefore unchanged: load
uops are exchanged one-for-one for cross-lane work.  D3 stops before ASM.

Decision: retain the production Q24 decoder.  Validation cannot be removed,
the wire/M split is decisively worse, and contiguous-load consolidation has no
eligible AVX2 network under the gate.  Decode-local work is closed unless a
full-width byte permute, a wider ISA, or a consumer contract removes the M
transpose.  See `generated/tile4_decode_debt_static.json` and
`results/tile4-decode-debt-gate.json`.

### Encap Q24-native D01 x M TMVP gate (2026-08-17)

`ENCAP-H-D01-MIXED-TMVP-B3-001` reopens exactly one typed edge: public-key
Q24 Decode may emit pair-packed `h`, Forward still emits persistent M `r`, and
a `vpmaddwd`/unsigned-REDC16 BaseMul must return M.  The generator simulates
every word through the existing four-register Q24 transpose and the M
`vpunpcklwd/hwd` consumer view.

The natural eight-instruction Q24 endpoint is only *degree-blocked* D01.  It
saves the four final qword unpacks per 16-leaf block, or 48 instructions per
polynomial.  `vpmaddwd`, however, requires adjacent `(c0,c1)` and `(c2,c3)`
pairs; four lane-local `vpshufb` per block are then mandatory.  Consumer-ready
D01 therefore costs the same 12 routing instructions as current M.  The
producer/consumer representation saving is exactly zero.

The complete mixed arithmetic audit uses R1-U's actual four-instruction
unsigned REDC16, not a hypothetical `vpmulld` reducer.  It also includes both
8-leaf halves, six row vectors, four source reloads, eight dword
compact/order pairs, half merges, three lambda-plane scratch stores, and the
mandatory four full-width R-squared finalizers.  The disassembled current
general MxM-to-M loop is 134 instructions.  The blocked-D zero-stack-spill
schedule is 146; consumer-ready D is 142.  Including Decode routing over 12
blocks, both candidate forms are 96 instructions larger than the current
edge.

The all-resident ideal needs at least 19 YMM.  A 13-YMM schedule is possible
only by materializing three lambda-r planes in the public output block; it has
no stack spill, but that materialization is included in the losing count.
Range is not the blocker: the conservative four-term dot bound is
149,133,312, unsigned REDC16 is bounded by 5,732, and the R-squared output by
3,532.

Decision: static hard stop before ASM.  The candidate is algebraically valid
and its register problem can be scheduled around, but it does not make the
Q24-to-B3 edge smaller.  Reopen only if the decoder can emit adjacent pairs
before the eight-instruction blocked transpose, both halves can be reduced
without compact/order work, the e=-1 result becomes directly consumable, or a
wider ISA removes the half/register constraints.  See
`generated/tile4_encap_h_d01_mixed_tmvp_gate.json`.

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

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

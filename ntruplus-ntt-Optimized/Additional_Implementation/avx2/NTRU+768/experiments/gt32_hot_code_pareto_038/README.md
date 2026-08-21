# GT32-HOT-CODE-PARETO-AUDIT-038

038 starts only after 036R/037R separated executed work from relocation.  Its
performance baseline is the production-shaped GT reference with the 034
arithmetic contracts and fixed hot-symbol addresses.  Frontend 036 is retained
only as a Pareto/placement reference; it is not the selected performance
baseline.  The experiment does not change the `vzeroupper` policy.

## Static hot-body inventory

The fixed ELF is 037R-A: compact frontend 036, 034 canonicalizer, current
unrolled serializers, O3/PIE/section-GC.  Counts exclude NOP padding.  Memory
counts are static AT&T operand classifications, not dynamic PMU events.

| Body | Bytes | Instructions | Branches | Likely L/S | Calls K/E/D | Classification |
|---|---:|---:|---:|---:|---:|---|
| Frontend 036 | 2472 | 434 | 2 | 126/30 | 2/2/2 | placement reference; intrinsic neutral |
| NTT-P | 1046 | 192 | 2 | 45/8 | 2/0/0 | freeze; compact repeated loop |
| NTT-M | 1056 | 194 | 2 | 43/8 | 0/2/2 | freeze; compact repeated loop |
| Decode-M body | 3470 | 588 | 1 | 146/48 | 0/1/3 | prior compact search closed |
| M centered pack | 3815 | 580 | 1 | 145/97 | 0/1/1 | Q24 Pareto survey candidate |
| M lazy10788 pack | 5120 | 725 | 1 | 146/97 | 0/1/0 | Q24 Pareto survey candidate |
| P SP1 pack | 4364 | 738 | 1 | 159/97 | 3/0/0 | Keypair-only shape candidate |
| BaseInv leaf | 923 | 199 | 9 | 20/10 | 2/0/0 | freeze local DAG |
| BaseInv batch | 1787 | 347 | 3 | 52/32 | 2/0/0 | outside code-shape gate |
| B3 scale-M | 573 | 120 | 2 | 20/4 | 0/0/1 | freeze |
| B3 general-M | 684 | 140 | 2 | 30/7 | 0/1/1 | freeze |
| inverse core | 948 | 169 | 2 | 42/8 | 0/0/1 | freeze; compact loop |
| inverse tail | 5578 | 1006 | 1 | 204/48 | 0/0/1 | Decap shape candidate |

## Prior-coverage correction

Decode is large, but it is not an uncovered opportunity.  The earlier Q24
codec campaign already compared the 3,470-byte unrolled body with a 1,850-byte
fixed-pattern body and a 703-byte table-driven body.  Unrolled remained the
speed champion; compact variants did not stabilize full Decap.  038 therefore
classifies Decode as closed unless a new operation-class deletion appears.

P-pack is also not a blank slate: SP1's next-block preload is locally qualified
and must be preserved.  A future shape probe may change unroll granularity but
must not regress SP1 routing or redo P/P-prime layout searches.

## Pareto worklist

1. **M Q24 midpoint shapes.**  Current 5.1 KiB and 037's 1.8 KiB are extreme
   points.  Generate bounded U8/U4 or equivalent fixed-immediate midpoints,
   first in equal-size cages.  Track centered and lazy contracts separately.
2. **Inverse tail repetition audit.**  It is the largest active body and has no
   loop branch.  Classify repeated groups/immediates before emitting code.
3. **P-SP1 shape audit.**  Keypair calls it three times; preserve SP1 preload
   and compare only static/dynamic code shape.

Every candidate must first report `(static bytes, local core cycles, retired
instructions, branches, loads, stores)` under fixed downstream addresses.
Footprint release is a separate B-to-C gate, because 037R proved relocation can
cost 136--172 cycles even when the compact body itself is unchanged.

## 038A repeated-shape classification

The source-level classifier canonicalizes absolute input/output offsets but
retains register order, qword permutations, safe-tail handling, SP1 preload
semantics, and inverse register rotations.

- M-Q24 and P-SP1 both have the twelve-group sequence
  `A A B C D D E D A A B F`.  The class counts are `A=4`, `D=3`, `B=2`,
  and three singletons.  This is not a fixed-period loop.
- M-Q24 groups are independent, so sharing only A, A/D, or A/D/B is an exact
  midpoint mechanism.
- P-SP1 groups are not freely reorderable: each group preloads the next
  physical input group.  Sharing a routing class therefore also requires
  pointer/dispatch work.
- Inverse tail is exactly `A B C A B C A B`, with affine 32-byte input/output
  and 288-byte matrix strides.  Its natural candidate is `U3 x 2 + U2`.

The machine-readable classification is in
`generated/repeated_shape_classification.json`.

## 038B equal-size executable gates

All candidates reserve the original symbol size.  Negative deltas would mean
the candidate is faster.

### M-Q24 midpoint probes

| Shape | Active/reserved bytes | Static instructions | Dynamic instructions | Core cycles, on/off | TSC, on/off |
|---|---:|---:|---:|---:|---:|
| Control | 4303/5120 | 725 | baseline | baseline | baseline |
| share A | 3082/5120 | 565 | +23 | +9.793 / +9.862 | +5.942 / +6.167 |
| share A,D | 2444/5120 | 452 | +32 | +9.415 / +9.420 | +5.917 / +5.942 |
| share A,D,B | 2125/5120 | 397 | +38 | +10.325 / +11.114 | +6.553 / +7.056 |

Each figure is the median across eight fresh launches.  Every candidate is
slower in all eight core-cycle launches in both ASLR settings.  Reducing the
active body by 28--51% does not reveal a midpoint performance sweet spot.
M-Q24 midpoint compaction is closed without releasing its cage.

### Inverse-tail U3 x 2 + U2

| Shape | Active/reserved bytes | Static instructions | Dynamic instructions | Core cycles, on/off | TSC, on/off |
|---|---:|---:|---:|---:|---:|
| Control | 5578/5578 | 1006 | baseline | baseline | baseline |
| U3 x 2 + U2 | 3463/5578 | 652 | +35 | +2.865 / +6.614 | +2.376 / +2.067 |

The candidate is byte/word exact over 1,000 random trials and reduces active
code by 37.9%, but it is slower in all 16 fresh-launch core-cycle comparisons.
It is a legitimate code-size Pareto point, not a performance winner, and its
padding is not released.

### P-SP1 closure

P-SP1 has the same heterogeneous class sequence as M-Q24, plus the next-group
preload dependency.  The existing compact shared-group executable already
measured the relevant call/pointer-dispatch mechanism at +52.330/+62.058 core
cycles.  038A finds no new fixed-period or zero-dispatch midpoint mechanism.
The current SP1 body remains selected; this does not close future
operation-class deletion or a genuinely new preload-preserving schedule.

## 038 decision

No active-body candidate survives the equal-address performance gate.  No
footprint is released, no whole-KEM timing is used for promotion, and
production GT Clean remains unchanged.  The next allowed phase is 039's
fixed-size internal-ABI/`vzeroupper` audit; any later integrated release must
again separate stable-slot and compact-layout builds.

## Explicitly deferred

- No N5, B3, BaseInv, inverse-core, or Decode arithmetic changes.
- No stacking multiple compact bodies in one benchmark.
- No linker-padding search for a favorable address.
- No `vzeroupper` removal until 038 chooses the code shapes.

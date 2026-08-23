# GT32 HWA16 island probe (061)

This directory is an experiment-only architecture probe.  It does not modify
GT Clean and is not linked into any KEM caller.

## Question

For fixed `(branch=0,k3=0)`, compare the current native TILE4 island with a
persistent natural-Q coefficient-plane representation:

```text
H[c][g][lane] = A[branch][k3][Q=16*g+lane][c]
```

The measured semantic region is:

```text
Forward(a) + Forward(b) + quartic BaseMul + Inverse
```

Both sides start in their native representation.  No synthetic TILE4/HWA16
conversion is timed.  Algebra, roots, twiddles, Montgomery exponent, quartic
leaves, and reduction placement are identical.

## Implementations

- `ctl_tile4_*`: current TILE4 pair Forward, B3-late/c3-center, pair Inverse.
- `hwa16_*_v1`: direct per-vector natural-Q lane routing.
- `hwa16_*_v2`: the one mode-preserving mutation.  It packs two independent
  HWA16 vectors into each distance-8/4/2 butterfly route; distance-1 remains a
  lane-local `vpshufb`/blend route.
- `hwa16_basemul_asm`: consumes and emits natural-Q coefficient planes, so it
  has no TILE4/coefficient-plane transpose.

The fixed YMM semantic order is:

```text
ymm0=c0/Q0..15   ymm1=c0/Q16..31
ymm2=c1/Q0..15   ymm3=c1/Q16..31
ymm4=c2/Q0..15   ymm5=c2/Q16..31
ymm6=c3/Q0..15   ymm7=c3/Q16..31
```

### V3 physical-Q mapping probe

V3 removes the assumption that natural logical Q order must equal physical
SIMD order.  The generator enumerates all `5! = 120` assignments of logical
`q0..q4` to `YMM/half/qword/dword/word`.  All 120 tie at 72 static routing
instructions per transform, so static count is used only to describe the
space, not to reject a mapping or predict cycles.

Three executable schedules put the raw Forward stage `q4` in word position
and the final Forward Montgomery stage `q0` in the YMM selector, while spanning
three middle-bit orders:

| Name | YMM | half | qword | dword | word |
|---|---:|---:|---:|---:|---:|
| `m40a` | q0 | q3 | q2 | q1 | q4 |
| `m40b` | q0 | q1 | q2 | q3 | q4 |
| `m40c` | q0 | q2 | q3 | q1 | q4 |

Their coefficient-plane BaseMul is the same arithmetic body with
mapping-specific lambda tables.  This preserves the HWA16 thesis and changes
only physical Q-bit ownership and the resulting NTT32 schedule.

Forward and Inverse support `out == in`.  BaseMul uses the experiment's
control contract `out != a && out != b`; aliasing is deliberately not part of
this gate.  All measured assembly symbols have zero stack references/spills.

## Correctness

`make test` covers V1/V2 and each of the three V3 mappings:

- all 128 logical impulses;
- structured `0/±1/±1728` and canonical extremes;
- 1000 random centered cases;
- 200 random modulo-q cases supported by the control;
- exact Forward equality after logical remapping;
- modulo-q scalar BaseMul equality and exact TILE4/HWA16 BaseMul equality;
- exact Inverse and complete `2F+B+I` equality;
- Forward/Inverse in-place aliases.

Observed absolute representatives across the complete corpus were:

```text
Forward <= 11952, BaseMul <= 7478, Inverse <= 13716
```

These are observations, not widened production contracts.  No extra reduction
was inserted to pass the tests, and every observed representative remained
inside signed int16.

V3 independently passes the same 128 impulses, eight structured cases, 1000
random centered cases, 200 canonical modulo-q cases, exact logical remapping,
and Forward/Inverse aliases: 1336 cases for each of three mappings.

## Short paired result

Eight same-ELF launches, 41 alternating-order paired samples per launch:

| Candidate minus TILE4 | Forward | BaseMul | Inverse | 2F+B+I |
|---|---:|---:|---:|---:|
| HWA16 V1, median TSC | +38 | -22 | +36 | +68 |
| HWA16 V2, median TSC | +19 | -22 | +15 | **+7** |

V2's complete-island deltas were `+7,+7,+7,+7,+8,+7,+7,+7` TSC.

Region-scoped PMU medians (seven runs, `cpu_core` events):

| Region | TILE4 cycles | HWA16 V2 cycles | Delta cycles | Delta retired instructions |
|---|---:|---:|---:|---:|
| Forward | 64.40 | 91.77 | +27.36 | +55.62 |
| BaseMul | 109.13 | 72.88 | **-36.24** | **-96.66** |
| Inverse | 61.97 | 83.61 | +21.64 | +39.50 |
| 2F+B+I | 330.98 | 343.27 | **+12.29** | **+55.96** |

The component deltas are attribution measurements, not an additive prediction
of the complete caller.  The complete same-ELF island is the decision metric.

### V3 result

Eight same-ELF launches with the same paired method:

| Candidate minus TILE4 | Forward | BaseMul | Inverse | 2F+B+I |
|---|---:|---:|---:|---:|
| `m40a`, median TSC | +13 | -27 | +20 | **+18** |
| `m40b`, median TSC | +13 | -27 | +20 | **+22** |
| `m40c`, median TSC | +14 | -27 | +21 | **+21** |

`m40a`'s island delta was `+18` in every launch.  `m40b` was `+22` in every
launch and `m40c` was `+21` in every launch.  Region-scoped PMU corroborates
the direction:

| V3 minus TILE4 | Forward cycles | BaseMul cycles | Inverse cycles | Island cycles | Island instructions |
|---|---:|---:|---:|---:|---:|
| `m40a` | +20.45 | -36.36 | +30.41 | **+28.98** | +44.10 |
| `m40b` | +19.32 | -36.57 | +30.41 | **+28.44** | +44.28 |
| `m40c` | +21.13 | -36.51 | +32.20 | **+30.42** | +43.71 |

The V3 BaseMul result must not be compared directly with V2's BaseMul number
as an intrinsic mapping gain: V2 and V3 live in different benchmark ELFs and
V3 uses a shared body behind a five-instruction typed entry.  Within the V3
ELF, all three mappings use identical BaseMul arithmetic.

## Architectural attribution

V1's loss was largely implementation-specific.  Pair packing changes no HWA16
semantics or arithmetic, yet removes 96 static instructions from Forward and
95 from Inverse and reduces the complete loss from +68 to +7 TSC.

For V2, routing-family accounting is especially informative:

```text
TILE4 Forward route instructions: 32
HWA16 V2 Forward routes:           72   (+40)
TILE4 Inverse routes:              32
HWA16 V2 Inverse routes:           72   (+40)
TILE4 B3 transposes, dynamic:      72
HWA16 B3 transposes:                0   (-72)
------------------------------------------------
2F+B+I net movement floor:              about +48
```

The measured complete retired-instruction delta is +55.96/call, closely
matching this accounting.  The architectural trade therefore exists exactly
where expected: natural-Q planes remove the BaseMul transpose, but NTT32 must
route distance-8/4/2/1 butterflies inside lanes.  V2 makes distance-8/4/2
two-vector dense; distance-1 and possible cross-stage route absorption remain
implementation headroom, not a proved impossibility.

V3 gives a more specific result.  Moving `q4` to word and `q0` to YMM swaps the
V2 Forward/Inverse code shapes: V3 Forward is 210 instructions / 1218 bytes,
while V3 Inverse is 225 / 1322; natural-Q V2 is 225 / 1322 Forward and
210 / 1218 Inverse.  V3 therefore improves Forward TSC by about 6, but loses
about 5 in Inverse and makes the complete island 11--15 TSC worse than V2.
The three middle-bit schedules are nearly indistinguishable.  PMU also shows
that V3 retires fewer extra island instructions than V2 (`+44.1` versus
`+56.0`) while taking more cycles (`+29.0` versus `+12.3`), so instruction
count alone would select the wrong schedule.

## Decision

```text
candidate viability: VIABLE
campaign: PAUSED_AT_INTERNAL_ISLAND
best realization: V2 natural-Q
physical-Q mapping search: SEARCH_CLASS_EXHAUSTED
```

HWA16 V2 is only about +7 TSC / +11 core cycles for the complete fixed island,
so the architecture is not rejected.  V3 does not replace it: the best tested
physical-Q remapping is `m40a` at +18 TSC / +29.0 core cycles.  This does not
prove natural-Q is the global optimum among all 120 dynamic schedules; it does
show that the most plausible endpoint reassignment moves cost between Forward
and Inverse rather than deleting it, and that middle-bit order is not the
source of V2's remaining +7 TSC.

Per the probe stop rule, the experiment stops and reports here.  No
DFT3-to-HWA16 landing and no KEM integration are implemented.  If a separate
producer gate is authorized later, V2's repayment target remains more than
3.5 TSC per Forward (or about 6.1 core cycles per Forward) to cross island
parity.

`SEARCH_CLASS_EXHAUSTED` applies only to permutations assigning the five
logical Q bits to `YMM/half/qword/dword/word`.  HWA16 is not closed for the
NTRU+768/AVX2 scope; producer-native post-stage1 landing remains a separate
architecture question.

## Reproduce

```sh
make test
make audit
make bench-short
make pmu
```

Artifacts are in `generated/` and `results/`.

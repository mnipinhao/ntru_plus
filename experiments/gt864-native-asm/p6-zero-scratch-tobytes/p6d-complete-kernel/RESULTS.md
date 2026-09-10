# P6-D complete-kernel gate

## Outcome

P6-D1, D2 and D3 now pass.  P6-D3 is a complete, assembling, zero-coefficient-
scratch implementation of both 1,296-byte ToBytes entry points.  It is a
**timing candidate**, not yet eligible for production:

- **P6-D1 saved-pair producer:** both symbolic regions allocate `OPTIMAL`
  with spills disabled.  Pair 0 is 407 semantic instructions with vector
  peak 25 and 27 data GPRs; pair 1 is 475 instructions with vector peak 27
  and all 28 available data GPRs.
- **P6-D2 all-row layout:** the exact 13-Q plus 28-GPR state reconstructs all
  nine rows in physical store order.  The 648-byte top output is exactly 40
  `STR Q` plus one `STR D`; no lane `ST3` is part of the proposed boundary.
- **P6-D3 complete function:** all twelve allocation regions are Slothy
  `OPTIMAL` with spills disabled.  The composed two-top public function passes
  the complete full/small byte oracle and its physical ABI audit.

Production and Pi 5 timing remain intentionally unchanged.  The next hard
gate is P6-E: same-boundary Cortex-A76 timing against the current 432-byte
scratch implementation, followed by full-KEM timing only if ToBytes wins.

## D1 physical allocation

The pair-0 state is 27 consecutive 64-bit chunks.  During pair 1, the first
26 chunks of the combined row-major state become thirteen Q registers and the
remaining 28 chunks occupy every usable data GPR:

```text
dense D positions  0..25  -> saved_q0..saved_q12
dense D positions 26..53  -> 28 allocated data GPRs
```

`x18` is never used.  `x29` is the fixed coefficient base and `x30` is the
fixed combined public-table base.  Reusing `x30` is legal only after the outer
wrapper has saved the incoming link register.  The stores at the end of the
allocation slices are synthetic live-out observations for Slothy and the
oracle; they are not proposed coefficient scratch.

The physical audit checks every TBL source group, rejects non-consecutive
groups, unresolved symbolic registers, `x18`, and non-stack writes.  It reports
36 TBL instructions per producer, including 18 three-register TBLs, and no
failure.

The arm64 executable oracle compares the allocated regions to the production
`byte_pair_block`:

```text
PASS producer_cases=4107 pair0_bytes=216 pair1_dense_bytes=432
```

This includes signed-int16 edge patterns and 4,096 deterministic random
polynomials.

## D2 row schedule

The consumer must run in this order:

```text
physical row: 0 1 2 3 4 5 6 7 8
logical row:  0 3 6 1 4 7 2 5 8
```

Each physical row consumes six consecutive D chunks.  Rows 0--3 are entirely
Q-resident; row 4 consumes `saved_q12.d[0..1]` followed by the first four GPR
chunks; rows 5--8 are entirely GPR-resident.  `complete-model-results.json`
records every exact source, packed-A low/high source, B vector and output byte
range.  A 4,096-case model proves the reconstructed stream equals direct
three-pair packing.

## D3 complete-function result

At the pair-1 frontier there is no disposable scalar register.  The complete
function resolves this as follows:

- Q and reciprocal constants must be vector-loaded through `x30`, not created
  through a temporary `wN`;
- `x29` cannot become the final output pointer until the last pair-2
  coefficient load has completed;
- each consumed GPR chunk dies before it is reused for address or wrapper
  work;
- all TBL2/TBL3 source groups are consecutive in the physical allocation;
- A is routed, normalized and compressed before B is routed, so the third
  pair never requires both nine-row sets to be live simultaneously;
- even rows retain their final eight bytes in a cross-row carry; the next odd
  row emits five Q stores.  The last row emits four Q plus one D.  This changes
  the initially correct but undesirable `72 Q + 18 D` store shape into the
  required `80 Q + 2 D` for the two-top function.

The composed physical audit reports:

```text
semantic instructions including public wrapper  4029
coefficient Q loads                               108
final stores                                      80 Q + 2 D
TBL / TBL2 / TBL3                                 450 / 180 / 162
public AAPCS stack frame                           176 bytes
coefficient scratch                               0 bytes
lane ST3 / x18 / symbolic leaks                    none
arm64 object __TEXT                                16,752 bytes
```

The full executable oracle compares arbitrary signed-int16 inputs against
`gt864_tobytes_full_asm`; the small oracle uses inputs strictly in `(-q,q)` and
compares against `gt864_tobytes_small_asm`:

```text
PASS full_cases=4107 small_cases=4096 bytes_per_case=1296 canaries=PASS
```

The D3 small entry intentionally aliases the full-normalization DAG.  This is
byte-correct, but it does **not** yet exploit the small producer's conditional-
add-only contract.  P6-E must measure full and small separately.  If the small
alias loses, a small-specific D3 arithmetic DAG is required before promotion.

The generic symbolic checker has zero contract errors after per-region
live-in/live-out/range annotations were added.  Its remaining 264 warnings are
unsupported classification of legal `INS`, `MOV` and `TBL` forms; the actual
Slothy parser allocated all twelve regions and the arm64 assembler accepted
the composed result.

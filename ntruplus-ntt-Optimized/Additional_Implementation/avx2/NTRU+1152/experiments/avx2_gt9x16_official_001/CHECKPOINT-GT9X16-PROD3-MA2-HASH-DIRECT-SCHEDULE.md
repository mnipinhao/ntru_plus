# GT9X16-PROD3-MA2-HASH-DIRECT-SCHEDULE

## Scope

This checkpoint lowers the closed MA2-to-byte ownership map into one exact H1
register schedule and three exact-mask H2 tile schedules. It does not implement
assembly or run a benchmark. PROD3, MA2, scale, canonicalization, and the
1,728-byte output contract remain frozen.

## H1: lowerable production-shaped control

H1 processes the nine pinned 128-coefficient serializer blocks independently.
For each block it constructs the eight exact Official coefficient vectors in
`ymm0..ymm7`, normalizes scale 4 in registers, and enters the bit-packing part
of pinned `pack.s` after its now-proved-redundant Barrett/sign prefix.

The generated schedule contains all 136 source-half selections, their
`vperm2i128` immediates, and their exact `vpshufb` masks. Symbolic replay proves
that every destination word is the required Official coefficient.

The phase allocation is:

| Phase | Persistent registers | Scratch/constants | Peak YMM |
| --- | --- | --- | ---: |
| construct eight vectors | `ymm0..ymm7` | `ymm8..ymm10` | 11 |
| inv4 and sign-add-q | `ymm0..ymm7` | `ymm11`, constants `ymm13..ymm15` | 12 |
| pinned pack body | data `ymm0..ymm7` | `ymm8..ymm15` | 16 |

Constants are deliberately separated from data movement. The 136 shuffle
masks remain constant memory operands. The three inv4/q constants are loaded
once per serializer block, for 27 vector constant loads total. They are dead
before the pack phase reuses their registers.

The exact dynamic H1 ledger is:

| Class | Count |
| --- | ---: |
| MA2 data loads | 272 |
| vector constant loads | 27 |
| constant mask memory operands | 136 |
| coefficient reorder routes | 336 |
| coefficient register copies | 0; first shuffle writes its final output register |
| inv4 Montgomery instructions | 288 |
| sign canonicalization instructions | 216 |
| pack bit instructions | 144 |
| pack transpose routes | 324 |
| byte stores | 54 |
| intermediate coefficient stores/reloads | 0 / 0 |
| temporary bytes | 0 |

The H1 schedule is therefore directly lowerable to a `.p2align 5` AVX2 leaf
with no calls, frame, stack vector traffic, or internal `vzeroupper`.

## H2 correction from ASM0 raw-byte closure

The old H2-24/48/96 schedules were based on treating the Official physical NTT
cell index as the linear serialized coefficient index. ASM0's external-byte
differential exposed that `pack.s` transposes those physical cells. A basis
probe now records the pinned 1,152-cell physical-to-serialized permutation.
After applying it, `0/576` true adjacent serialized pairs remain within one
MA2 vector. The old H2 72-load bound and all three derived route/store ledgers
are therefore withdrawn. H2 is not an implementation candidate until a new
ownership and register schedule is derived from the probed order.

## Decision

H1 is authorized for ASM0. It is exact, spill-free, removes all full-array
materialization, and provides the highest-information machine test without
waiting for a speculative byte-oriented alternative.

H2 is not authorized for assembly. Its prior schedule is invalidated, not
merely deferred for pricing.

The next checkpoint implements only H1 ASM0, with `.p2align 5` entry and
aligned read-only constants. It must pass raw 1,728-byte differential tests,
range/alias/canary checks, and linked frame/spill/call/`vzeroupper`/instruction
audits. Those gates are completed in
`CHECKPOINT-GT9X16-PROD3-MA2-HASH-H1-ASM0.md`; benchmark pricing is the next
checkpoint, but was not run as part of ASM0.

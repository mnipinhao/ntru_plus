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

## H2: byte-oriented tile search

H2 never constructs ordered coefficient vectors. For each input YMM it creates
the low and high member of four serializer pairs in each 128-bit half, performs
the frozen inv4/sign operation, and produces two padded fragments:

```text
low128:  12 exact bytes + 4 zero bytes
high128: 12 exact bytes + 4 zero bytes
```

The pair masks are exact and symbolically replayed. Across all 72 vectors their
formation costs 144 `vperm2i128`, 192 `vpshufb`, and 48 `vpor`. The local
12-bit epilogue adds six instructions per vector: 216 bit instructions and 216
local pack routes in total.

Three store tiles were then generated and replayed byte-for-byte:

| Candidate | Data loads | Route/pack total | Byte stores | Peak YMM |
| --- | ---: | ---: | ---: | ---: |
| H1 direct block | 272 | 804 | 54 | 16 |
| H2-24 scattered fragments | 72 | 888 | 288 | 8 |
| H2-48 four-fragment tiles | 72 | 1,176 | 72 | 11 |
| H2-96 eight-fragment tiles | 72 | 1,086 | 54 | 15 |

All H2 variants use only three vector constant loads for the whole leaf, 288
inv4 Montgomery instructions, 216 sign-canonicalization instructions, and no
intermediate array. Counts are kept as separate resource classes; they are not
converted to cycle predictions.

H2-24 pays four scalar-width stores per input vector. H2-48 compacts four
consecutive 12-byte fragments into one 32-byte and one 16-byte store. H2-96
compacts eight fragments into three 32-byte stores, preserving the pinned total
of 54 stores. The generated compaction masks prove exact byte order for every
48- and 96-byte tile.

H2-48 is not useful on loads/routes/stores alone versus H2-96, but remains on
the recorded multi-resource frontier because its peak is 11 rather than 15
YMM. H2-24 similarly trades a much larger store count for the lowest peak and
only 84 more route/pack operations than H1. None is declared faster without a
machine measurement.

## Decision

H1 is authorized for ASM0. It is exact, spill-free, removes all full-array
materialization, and provides the highest-information machine test without
waiting for the 72-load lower-bound design.

H2-96 remains the primary optimized challenger because it combines 72 data
loads with the same 54-store geometry as H1. It is not yet authorized for
assembly: its 1,086 route/pack operations versus H1's 804 must first be judged
against the H1 machine result, and implementing both now would weaken
attribution.

The next checkpoint implements only H1 ASM0, with `.p2align 5` entry and
aligned read-only constants. It must pass raw 1,728-byte differential tests,
range/alias/canary checks, and linked frame/spill/call/`vzeroupper`/instruction
audits. Benchmarking remains blocked until those gates pass.

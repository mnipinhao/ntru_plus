# Checkpoint F0-MA-SCHED

## Outcome

This checkpoint converts the F0-MA semantic map into correctness-first
physical schedules. It authorizes MA1 and MA3 assembly prototypes; it does not
implement assembly or make a performance claim. MA0 remains the Official
adapter control, and MA2 is deferred rather than rejected.

The benchmark and output contract is the actual encapsulation boundary:

```text
F0(r) + F0(m) + resident-h projection
-> MulAdd
-> inverse-four finalizer
-> poly_tobytes
```

There is no inverse transform in this caller.

## Official chunk pairing

A single semantic `(branch,p)` tile is not an Official serializer block.
Offline ownership analysis proves nine 128-coefficient Official chunks, each
interleaving exactly two semantic tiles:

| Official chunk | Semantic tiles |
| ---: | --- |
| 0 | `(0,4)`, `(0,7)` |
| 1 | `(0,0)`, `(0,1)` |
| 2 | `(0,3)`, `(0,6)` |
| 3 | `(0,2)`, `(0,8)` |
| 4 | `(0,5)`, `(1,3)` |
| 5 | `(1,0)`, `(1,6)` |
| 6 | `(1,2)`, `(1,5)` |
| 7 | `(1,7)`, `(1,8)` |
| 8 | `(1,1)`, `(1,4)` |

Each chunk consumes eight aligned Official `h` vectors and produces eight
local coefficient planes using eight `vperm2i128` plus eight `vpshufb` routes.
The inverse projection into the existing serializer geometry has the same
16-route schedule. The generated artifact records every lane's F0 position,
Official `h` position, semantic q, lambda, and exact incoming F0 interval.

For one semantic tile, one F0 operand forms four coefficient planes using four
`vperm2i128`: the target lane order is even physical-q lanes followed by odd
physical-q lanes. This retains the current bit-reversed q identity; no natural
q permutation is introduced.

## Range schedule

The prototype schedules center `h`, `r`, and `m` when consumed. Official's
signed-high-half Montgomery sequence has the following proved conservative
integer bounds:

```text
centered x centered:        [-1774, 1774]
pair-sum x pair-sum:        [-1911, 1911]
```

MA2/MA1 weighted-schoolbook final pre-centering bounds are:

```text
c0: [-5371, 5371]
c1: [-7098, 7098]
c2: [-8825, 8825]
c3: [-8824, 8824]
```

MA3 centers each quadratic result and cross value before reuse. Its largest
proved pre-operation interval is `[-5459,5459]`; all final accumulators remain
within `[-5230,5230]`. Every scheduled pre-operation therefore fits signed
i16 without relying on empirical corpus behavior.

## Scale placement

Three role-aware placements were priced:

| ID | Placement | Full-1152 inverse-four vector chains |
| --- | --- | ---: |
| S0 | Normalize four output planes before inverse projection/serializer | 72 |
| S1 | Scale resident `h` and F0(`m`) independently | 144 |
| S2 | Scale product output and F0(`m`) independently | 144 |

S0 is selected. It can be scheduled with the serializer but is not called
free: all 72 chains remain in the price. Neither role-specific input scheme
has an already-required multiplication proven to absorb both uniform factors.
Changing a table counts as zero runtime cost only after such an identity is
proved.

## Candidate schedules

| Candidate | Montgomery chains/tile | Full routing schedule | Peak YMM | Decision |
| --- | ---: | ---: | ---: | --- |
| MA0 | Official control | 288 adapter routes plus materialization | Official | control |
| MA1 | 20 | 792 | 14 | first F0-native prototype |
| MA2 | 19 | 432 | 13 | deferred |
| MA3 | 13 | 432 | 15 | coefficient-plane challenger |

MA1 remains necessary even though its explicit pair-operand routing is larger:
it directly prices whether persistent F0-basis arithmetic has scheduling
credit not visible in the static route count.

MA2 and MA3 have the same proved external projection and serializer geometry.
MA3 is selected over MA2 for the first ASM round because it uses six fewer
Montgomery chains per tile while remaining spill-free. Its schedule is
streaming: EE, OO, and TT rank products are accumulated into four outputs and
killed immediately. Nine rank products never coexist.

These are prototype choices, not static performance winners. A measured MA1
or MA3 loss remains an ordinary research rejection.

## Assembly and alignment authorization

The next implementation order is MA1, then MA3. Both must:

- use `.p2align 5` at the leaf entry and for YMM constant tables;
- place constants in aligned read-only storage;
- preserve the proved 14/15-YMM spill-free schedules;
- retain unaligned byte stores at the serializer boundary;
- prove every `vmovdqa` caller-data address from the 32-byte-aligned `poly`
  type and a multiple-of-32 offset;
- record object and linked-ELF section alignment, symbol modulo 32/64,
  padding, and text/rodata size; and
- treat `.p2align 6` only as a paired placement variant.

Correctness, exact range, ABI, constant-time, alias/canary, and alignment audits
precede timing. The primary timing includes both F0 producers, all projection,
MulAdd, the 72-chain inverse-four finalizer, inverse projection, and
serialization. MulAdd-only timing is diagnostic and cannot select a winner.

## Artifacts

- `generated/f0-ma-schedule.json`
- `tools/generate_f0_ma_schedule.py`
- `tests/test_f0_ma_schedule.py`

# Checkpoint F0-MA2

F0-MA2 tests the Hwa-style hypothesis that coefficient planes are valuable
only when arithmetic, range policy, scratch lifetime, and serialization share
the same geometry. It is a real handwritten/generated AVX2 assembly path, not
a symbolic chain-count model.

## Machine contract

- One YMM holds one fixed quartic coefficient over 16 physical-q leaves.
- Each tile executes 19 weighted-schoolbook core Montgomery chains, four raw
  resident-h R2 lifts, and four `inv4` chains.
- The full path processes 18 semantic tiles as nine serializer chunks, keeps
  at most 14 YMM registers live, and reuses 128 `int16_t` scratch words only
  for eight semantic output planes.
- It never materializes an Official-vector intermediate. The proved
  post-`inv4` interval `[-2133,2133]` is inside `(-q,q)`, so serialization uses
  sign correction without a redundant Barrett pass.
- Every entry and the read-only constant section use `.p2align 5`.

The full linked object contains 4,681 straight-line instructions and 486
Montgomery chains, with no call, branch, stack reference, spill, or
`vzeroupper`. Object and linked symbol addresses are both zero modulo 32.

## Correctness and range

The independent scalar quartic oracle and pinned `poly_tobytes` comparison pass
1,003 random/boundary raw-input cases for ASM0, CHUNK0, and the complete
1,728-byte path. Input immutability, alignment, output/scratch canaries, strict
warnings, ASan/UBSan, generated-artifact checks, and the linked ABI audit are
required gates.

The formal interval proof retains raw F0 and resident-h inputs. All signed-i16
operations remain safe; the aggregate pre-`inv4` bound is
`[-29899,29901]`. It classifies the input centers, wrapped-sum centers, and
post-`inv4` Barrett as unnecessary in this schedule; final sign add-q remains
mandatory.

## SUPERCOP-derived results

The optimistic repeated-CHUNK0 diagnostic measured 2077.4421 cycles against
MA0 at 2822.0602, with a paired median delta of -745.8958 cycles in 9/9 fresh
launches. This diagnostic only authorized full expansion.

The complete, semantically distinct nine-chunk path then measured:

| path | pooled StQ2 | observations |
| --- | ---: | ---: |
| MA0 | 2826.4907 | 1728 |
| MA2 full | 2072.1435 | 1728 |

MA2 won all nine fresh launches; the paired-launch median delta was
-753.8333 cycles (about -26.7%). The run used pinned SUPERCOP 20260627,
CPU 1, performance governor, and turbo disabled. These numbers are labeled
`supercop-derived-poly-f0-ma2`; they are not native KEM or promotion evidence.

## Decision

MA2 replaces MA0 as the selected encapsulation MulAdd-to-serializer research
candidate. The next gate is caller integration with the real encapsulation
decode/input residency and then native SUPERCOP KEM plus fixed-ELF placement
controls. No clean-production promotion is made at this checkpoint.

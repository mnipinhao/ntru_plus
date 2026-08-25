# F0-MA1-ASM1

Status: complete research checkpoint. C1 is the selected MA1 schedule, but the
complete MA1 architecture is rejected against MA0. These are
`supercop-derived-poly` primitive results, not native KEM or production evidence.

## Implemented boundary

ASM1 consumes aligned persistent-F0 `r` and `m`, aligned resident Official
`h`, and a 512-byte aligned scratch area. It processes all 18 semantic tiles
as the nine exact Official serializer chunks and writes the 1,728 ciphertext
bytes directly. It does not construct a full normalized 1,152-coefficient
output ABI.

Two arithmetic-identical schedules are retained for attribution:

- C0 completes tile A and then tile B.
- C1 interleaves corresponding A/B Montgomery chains and materializes pair
  outputs only until both consumers are safe.

The full ledger for either schedule is 360 core-product, 72 resident-`h`
R-lift, and 72 inverse-four chains: 504 vector Montgomery chains total.
Resident `h`, `r`, and `m` are centered on consumption. Every proved
preoperation remains signed-i16, output scale is one, and no reassociation is
used.

## Correctness and machine gates

The independent scalar quartic oracle plus pinned Official `poly_tobytes`
passes 1,003 zero, boundary, and random cases byte-for-byte for C0, C1, and
MA0. Inputs remain immutable; output and scratch canaries pass; ASan and UBSan
pass.

Both MA1 symbols and the MA0 adapter use `.p2align 5` entries and aligned
read-only constants. Linked addresses remain 32-byte aligned. C0/C1 are
straight-line leaves with no call, branch, stack/frame reference, spill, or
`vzeroupper`; their proved peaks are 13 and 16 YMM. C1 has the same arithmetic
and routing multiset as C0 but 216 additional `vmovdqa` instructions from its
correctness-first pair materialization.

MA0 is a complete measured control:

```text
F0(r), F0(m)
  -> two direct F0-to-Official adapters
  -> centered Official operands
  -> pinned Official poly_basemul + poly_add
  -> inverse-four finalizer
  -> pinned Official poly_tobytes
```

One direct adapter is a 1,152-cell bijection and executes 136 `vperm2i128`,
136 `vpshufb`, and 64 `vpor` instructions. The earlier value 288 is retained
only as a semantic adapter estimate; it is not presented as an executed
instruction count.

## SUPERCOP-derived serious result

The pinned release is SUPERCOP 20260627. A disposable campaign installed the
candidate as `crypto_kem/ntruplus1152/avx2-gt9x16-exp001`; pristine SUPERCOP
and built-in `avx2` were not modified. CPU 1 passed the configured frequency
preflight. Each serious result uses nine fresh measure-ELF launches, 96
observations per operation/position per launch, and SUPERCOP stabilized
quartiles.

The balanced two-schedule result is:

| schedule | pooled StQ2 cycles |
| --- | ---: |
| C0 sequential | 4139.0486 |
| C1 interleaved | 3866.6875 |

C1 beats C0 in 9/9 launches; the median paired delta is -273.0625 cycles.
C1 is therefore the selected MA1 schedule despite its extra materialization.

The balanced three-way control result is:

| implementation | pooled StQ2 cycles |
| --- | ---: |
| MA0 complete Official-adapter control | 2827.9429 |
| MA1 C1 selected | 3867.8009 |
| MA1 C0 | 4139.8673 |

C1 loses to MA0 in 9/9 launches. The median paired `C1-MA0` delta is
+1039.4167 cycles; C1 is 36.77% slower. In the same ELF, C1 still beats C0 in
9/9 launches with median delta -271.4861 cycles.

## Decision

C1 validates the two-tile ILP hypothesis, but it does not rescue weighted
schoolbook MA1. Freeze MA1 as the F0-native architecture control; do not spend
another checkpoint micro-tuning it. The next implementation is MA3 using the
same resident-`h`, chunk traversal, finalizer, serializer, correctness, and
SUPERCOP-derived benchmark infrastructure.

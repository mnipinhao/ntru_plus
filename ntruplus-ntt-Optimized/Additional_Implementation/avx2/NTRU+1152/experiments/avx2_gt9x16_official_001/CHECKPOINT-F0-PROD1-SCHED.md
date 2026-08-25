# Checkpoint F0-PROD1-SCHED

## Outcome

This checkpoint closes the production-shaped schedule for the direct
coefficient-domain F0 producer. It deliberately does not implement assembly
or authorize a KEM benchmark. The existing 2,304-byte top split remains the
only live array; the scalar GT adapter and the 288-byte coefficient plus two
576-byte pair staging objects are removed from the planned boundary.

The selected realization is `P1-H`: a small set of aligned AVX2 leaf helpers
may remain while bringing up the producer, provided they have no frame,
spills, or internal `vzeroupper`. Full inlining (`P1-I`) remains a later
code-placement variant rather than a correctness requirement.

## Direct split loads

For each `branch x terminal-pair x GT-input-row`, four aligned YMM loads read
one 64-word split row. The source row is `h=(5*row) mod 9`; branch bases and
all row offsets are multiples of 32 bytes under the proved caller allocation.
The two terminal-pair choices use `vpshufd 0x88` and `0xdd` respectively.

After that selection, a fixed sequence of six `vpermq`, two `vperm2i128`, two
`vpshufb`, and one each of `vpunpcklqdq`/`vpunpckhqdq` produces the two
16-lane coefficient streams in the unchanged bit-reversed Q order. Together
with four `vpshufd`, this is 16 routing instructions per map. The generator
simulates every label through this sequence and proves the result equals
`component[0..15].coefficient[2*pair+stream]`.

There are 36 maps and 72 output vectors. Every transient/final F0 vector slot
is owned exactly once.

## Arithmetic and transient storage

Pre-twist constants and Montgomery q-inverses are emitted as 32-byte-aligned
YMM tables. No standalone factor-four pass is added: scale four remains an
inherent result of the already verified paper R2 schedule.

The arithmetic order is frozen to the selected F-R3D1 implementation:

1. R2 first-layer groups `(0,3,6)`, `(1,4,7)`, and `(8,2,5)`; the third group
   retains the existing address rotation to output rows `(2,5,8)`.
2. First-layer results are stored directly in their strided final-F0 slots.
3. R2 second-layer groups `(0,1,2)`, `(3,4,5)`, `(6,7,8)` consume and overwrite
   those slots, with the frozen `rho/rhoinv` pre-twist pattern.
4. D1 consumes physical-adjacent row pairs `(0,1)`, `(2,3)`, `(4,5)`, `(6,7)`
   plus tail row 8 and overwrites the same slots with final F0 values.

This is transient use of the destination buffer after top split has completed;
the split input remains untouched, so `output == input` remains implementable.

## Range, register, and alignment gates

The actual `r` and `m` domains `[-1,1]` are subsets of the existing exhaustive
KEM-small `[-3,4]` domain. Top split, pre-twist, R2, and D1 arithmetic and order
are unchanged, so every actual register state is a subset of the existing
signed-i16 proof. The generated schedule also requires MA2's proof that every
pre-operation is signed-i16 safe. No new reduction is authorized.

The planned local peaks are 13 YMM registers during formation, 15 in cached
R2, and 11 in D1. The spill target is zero. The required array storage is
2,304 bytes, with a 2,432-byte maximum frame target allowing alignment and
saved-GPR bookkeeping. Function entries and constants require `.p2align 5`;
aligned split loads are allowed only under the recorded 32-byte caller and row
alignment proof.

## Decision

`F0-PROD1-ASM P1-H` is authorized. Its gates are full PROD0 differential,
alias/canary, generated per-cell range checks, sanitizer, ABI/static linked
audit, exact stack bound, no vector spill, and no internal `vzeroupper`.

KEM timing is still forbidden. Only after the producer assembly passes those
gates may `F0-PROD1-MA2` install the R-only, M-only, and both-direct caller
variants and proceed to KAT, native SUPERCOP, and fixed-ELF attribution.

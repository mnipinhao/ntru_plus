# GT32 direct degree-8 packet schedule gate 019

018 proved the degree-8 algebra.  This gate reconciles it with the existing
GT16 quadratic executable and asks whether a direct degree-8 packet can avoid
that implementation's split/QBM/merge work.

## Existing executable coverage

GT16 does not persist a degree-8 array, but it computes exactly the same four
quadratic factors with a complete NTT16 Forward, `QBM-PREWEIGHT`, scale-2
merge, and lazy CT16 inverse.  Its materialized boundary costs 672 instructions
for two splits, 1056 for QBM, and 432 for merge: 2160 total.  The terminal wins
48.840 TSC, but inverse loses 214.364 TSC; the tracked best local `2F+B+I`
remains 181.486 TSC behind.  Fusing merge into the inverse first load was also
0.782% slower.

## Register-capacity result

One block of 16 degree-8 leaves has four quadratic factors, each with two
coefficient vectors: eight YMM per operand.

```text
persistent A+B:                       8 + 8 + one temporary >= 17 YMM
materialized A + live B at QBM peak:  11 + seven unconsumed B = 18 YMM
root stream from eight pre-S5 planes: 8 + QBM residual live set = 18 YMM
```

The selected QBM's generated peak is 11 YMM.  Consequently the only current
zero-spill schedule is the already measured materialized GT16 boundary.  A
direct ABI by itself changes where values are stored; it does not delete a
split, merge, or multiply class.

## Decision

No assembly is emitted.  The straightforward direct degree-8 packet family is
closed for the selected QBM.  It can reopen if QBM peak falls to at most nine
YMM, if a dynamic stage packet kills source planes before the first factor is
consumed, or if interleaved LHS/RHS Forward production emits and consumes one
factor without retaining the other seven.

That makes **streamed evaluation plus LHS/RHS-coupled production** the next
representation gate, rather than another persistent degree-8 layout.

## Reproduction

```sh
make check
```

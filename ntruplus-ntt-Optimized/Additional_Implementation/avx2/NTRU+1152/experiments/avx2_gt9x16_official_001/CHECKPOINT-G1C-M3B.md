# Checkpoint G1C-M3B: producer-correlated range search

M3B replaces the failed box abstraction with source-aware D2 classification
and a deterministic counterexample search over the qualified F1-B1 producer,
exact BMScale instruction semantics, and inverse D1/D2/D4/D8 maps. It asks how
much repair the persistent inverse state actually needs; it assumes neither a
fully lazy path nor a full reduction.

## Provenance contract

Every future symbolic node retains expression/provenance, source IDs, integer
range, mod-q class, representative rule, and producer instruction. Montgomery
multiplication is a correlation boundary: the oracle preserves modular identity
and source dependencies but introduces a new bounded symbol for the selected
signed representative. Exact reasoning is localized to nodes whose later
correlation matters.

At D2, each row has four post-Mont reduced+reduced pairs and four
shared-producer large+large pairs. Across nine rows this is 36/36 structural
pairs, or 288/288 after expanding two branches and four terminal coefficients.
The reduced pairs are safe from independent post-Mont bounds. The large pairs
share the same F1 row/coefficient producer state and cannot be proved by
independent boxes; their proof remains open despite the corpus result.

## Deterministic producer-real search

The fixed 10,003-case corpus includes zero, uniform extrema, alternating
extrema, lane-group extrema, and deterministic random inputs inside the proved
F-R3 producer envelope. Inputs pass through real F1-B1 assembly; BMScale and
inverse use exact signed-high, 16-bit-wrap, and Montgomery semantics. This is a
counterexample search, not a proof of safety.

| Stage | max input | max sum | max difference | max twisted | unsafe sum/diff |
|---|---:|---:|---:|---:|---:|
| D1 | 8,888 | 13,864 | 13,480 | 1,976 | 0 / 0 |
| D2 | 13,864 | 21,367 | 19,733 | 2,086 | 0 / 0 |
| D4 | 21,367 | 31,373 | 28,207 | 2,191 | 0 / 0 |
| D8 | 31,373 | 45,358 | 38,455 | 2,324 | 187 / 11 |

The first concrete failure is trial 3, branch 0, physical row 3, `c3`, D8
lanes `(0,8)`: `-19648 + -16636 = -36284`. Thus current-orientation,
zero-repair C2 is rejected. D2/D4 remain proof-open; absence of corpus failures
does not close their range gates.

## Decision

Do not insert a generic or full reduction. M3C searches in this order:

1. an equivalent D8 orientation/gauge pairing a large branch with a post-Mont
   reduced branch;
2. a correlated proof for one-sided D8 reduction;
3. lane- or row-selective D8 reduction;
4. explicit full reduction only as a control.

The objective is saved materialization/routing minus minimum repair cost.
M3-C0/C1/C2 assembly remains deferred until one arithmetic-correct full
inverse16 repair contract is fixed. This checkpoint is repository-local range
evidence and carries no performance or production claim.

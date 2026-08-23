# Checkpoint G1C-M3C0: zero-cost orientation/gauge search

M3C0 exhausts the representation freedoms that do not add a Montgomery chain,
runtime route, or standalone scale correction. It does not write assembly and
does not authorize a reduction.

## Search result

For each of the D1-to-D2, D2-to-D4, and D4-to-D8 boundaries, all 256 local
butterfly output-swap masks were enumerated. Sixteen masks preserve the
original next-stage factor partition and can therefore be implemented by
component relabeling plus root-table rekeying. A different set of sixteen
masks makes all eight next-stage edges mixed L/R. Their intersection is empty.

The reason is structural. The two producer butterflies feeding a next factor
must use equal orientations to keep both halves of one mathematical factor
together. A mixed L/R edge requires those orientations to be opposite. Joining
halves from different factors changes the inverse map and would need new
routing or a different factorization.

The sixteen `q -> q xor c` relabels preserve every fixed distance matching but
do not change this result. Permuting q-bit axes is excluded from the zero-route
domain because it changes the D1/D2/D4/D8 route sequence and the linked-D1
contract.

## Gauge and permanent regression

The M3B counterexample is now a permanent regression:

```text
trial 3, branch 0, row 3, c3, D8 lanes (0,8)
u = -19648, v = -16636, abs(u)+abs(v) = 36284
```

For every input sign choice,
`max(abs(u+v),abs(u-v)) = abs(u)+abs(v)`, so at least one pre-Montgomery
operation exceeds signed i16. A nontrivial root-power gauge is free only on an
existing Montgomery-reduced R output. The counterexample's all-L path has no
such slot; scaling it would add arithmetic or alter upstream arithmetic, both
outside M3C0.

## Decision

M3C0 closes with no zero-cost safe candidate. M3C1 is not entered because
there is no selected orientation to prove. The next checkpoint is M3C2:
compute the logical minimum one-sided/selective repair and then project it onto
AVX2 vector groups as a set-cover problem. Full reduction remains an M3C3
control, and M3 assembly remains forbidden until both repair contracts are
fixed.

The machine-readable source of truth is
`generated/g1c-m3c0-orientation-search.json`. This is a deterministic
repository-local algebra/range gate, not a performance result.

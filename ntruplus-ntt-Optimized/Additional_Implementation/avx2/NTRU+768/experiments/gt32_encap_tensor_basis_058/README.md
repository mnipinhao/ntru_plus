# GT32-ENCAP-TENSOR-BASIS-058

This is a generator-only coverage and lower-bound gate.  It asks whether the
quartic degree-basis search that was previously evaluated only around the
Forward/K2 seam becomes attractive when the complete Encap WIRE12 graph is
included.

It does **not** modify GT Clean and it does not claim to exhaust arbitrary
`GL(4,q)` bases or new bilinear multiplication tensors.

## Result

The existing structured search was reproduced exactly:

- 40 nonzero sign-normalized ternary rows;
- 72,780 rank-four bases;
- 979 bases capable of synthesizing the eight current K2 forms with integral
  unit coefficients;
- current monomial basis lower bound: 6;
- best nonmonomial lower bound: 9.

WIRE12 already carries the four monomial quartic coefficients.  A zero-
arithmetic invertible linear conversion can only select and permute those four
coordinates.  Any genuinely nonmonomial basis needs add/sub arithmetic; the
existing search also proves that none of the 978 eligible nonmonomial bases
reduces current K2 operand synthesis.

That cost occurs on a five-boundary Encap graph: Decode(h), CBD(r), SOTP(m),
and the two serializers.  Moving the transform between these boundaries is not
a credit.  A candidate must delete work from the complete graph.

Independent prior gates agree with this result:

- Q24-native D01 saves 48 decoder instructions but repays all 48 pair
  shuffles before `vpmaddwd`; its complete mixed-TMVP edge is +96
  instructions.
- the best distinct P-like Encap endpoint remains +7 instructions because the
  B3 output repair costs more than the Q24/Forward savings.
- 120 P-like Q-axis placements were already surveyed separately.

The scoped decision is therefore
`close-structured-current-tensor-basis-repack-space`.

## What remains open

The experiment deliberately leaves open:

- a genuinely different quartic bilinear tensor/decomposition;
- producer-native redundant forms that remove a complete consumer operation;
- a nonmonomial representation that survives through a later protocol
  boundary and therefore avoids conversion back to WIRE12;
- a different leaf degree or Good-Thomas factorization.

The next executable candidate must first show deletion of a vector multiply,
complete REDC/recombination class, or another operation class.  A new
permutation or basis transform alone is not a new premise.

## Reproduction

```sh
python3 tools/generate_gate.py
```

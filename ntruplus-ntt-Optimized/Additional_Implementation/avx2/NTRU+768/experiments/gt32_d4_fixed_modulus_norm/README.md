# GT32-D4-FIXED-MODULUS-NORM

This side gate tests a leaf-dependent diagonal algebra isomorphism that was
not covered by the structured ternary basis search.

For all 192 production leaves the generator proves

```text
lambda_i = 2*s_i^4
```

and therefore maps

```text
F_q[x]/(x^4-lambda_i) -> F_q[y]/(y^4-2)
```

with coordinates

```text
(a0, s_i*a1, s_i^2*a2, s_i^3*a3).
```

All 768 coordinate roundtrips and 3,072 quartic basis products pass exactly.
The representation remains 1,536 bytes.

The physical chain result needs one correction: the selected L01 chain-2
packet contains the ninth variable product in one qword and three lambda
forms in the other qwords.  Normalization cannot delete that packet outright.
Pooling the four ninth-product qwords across groups gives

```text
12 current Montgomery chains
 -> 8 dense variable chains
  + 1 pooled variable chain
  + three fixed-two linear vectors
```

so the genuine operation-class credit is three full-width Montgomery chains
per 16 quartics, subject to explicit pool/redeposit routing.

Standalone Decode/Forward/Q24 diagonal transforms are more expensive than
that credit.  The direction remains open only because absorbing the diagonal
into Forward twisting, Q24 reduction, or an asymmetric h/r B3 tensor has not
previously been tested.  This is not a production claim and GT Clean is
unchanged.

## Pooled ninth-product route (B)

The four chain-2 vectors have symbolic qwords

```text
[v_i, fixed_i1, fixed_i2, fixed_i3].
```

Two `vpunpcklqdq` plus one `vperm2i128 0x20` gather
`[v0,v1,v2,v3]`.  One Montgomery chain processes that vector; four `vpaddw`
form the fixed-times-two lanes, and four qword selects plus four `vpblendd`
redeposit the variable results.  This audited template is 19 instructions
versus 16 for four mixed Montgomery chains, but removes nine vector multiply
instructions and three full chains.  It therefore continues to matched ASM;
the `+3` retired-instruction estimate is not a rejection criterion.  The
15-instruction routing figure is a constructive template cost, not a claimed
global AVX2 circuit lower bound.

## Absorption matrix (C)

The current schedules contain no free constant relabeling:

| boundary | degree 1 | degree 2 | degree 3 |
| --- | ---: | ---: | ---: |
| Forward standalone | 12 chains | 12 | 12 |
| Q24 inverse standalone | 12 chains | 12 | 12 |
| direct reuse in current operation | no | no | no |

For Forward, low butterfly arms bypass the Montgomery operations, so changing
only terminal constants cannot apply the diagonal to every output.  A full
conjugated transform/physical trajectory remains open.  For Q24, the existing
`v=9` and multiply-by-q operations are reduction operations, not arbitrary
constant Montgomery products; a joint wide inverse-diagonal + REDC/pack exit
remains open.  If nothing absorbs, two Forward plus two Q24 transforms cost
144 chains against only 36 chains of B3 credit, so standalone normalization
is not viable.

## Reproduction

```sh
python3 tools/generate_gate.py
python3 tools/generate_pooled_routing.py
python3 tools/generate_absorption_matrix.py
```

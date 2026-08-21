# GT32-PERSISTENT-R7-LATE-RECOMBINATION-059C

This generator tests an Encap-private rank-seven ABI rather than forcing B3
back to four quartic coefficients.

Inputs use the seven symmetric evaluations

```text
P(0), P(+/-1), P(+/-2), P(+/-4).
```

After seven pointwise products, the terminal representation is

```text
P0, S1, D1, S2, D2, S4, D4,
```

where sums and differences are deliberately unnormalised.  Message Forward
produces the same linear representation, so message addition happens before
the lambda-dependent interpolation:

```text
K_lambda * (H*(E(h)*E(r)) + H*E(m)) = h*r + m.
```

The identity passes 3,072 product-basis and 768 message-basis checks over all
192 production lambdas.

## Late-exit lowering (A)

`generate_late_exit_lowering.py` now emits every lambda's centered 4x7
`K_lambda`, its e=1 Montgomery encoding, and the pair-packed constants used by
`vpmaddwd`.  The support is lambda-independent:

```text
c0,c2: (P0,S1) + (S2,S4)
c1,c3: (D1,D2) + (D4,zero)
```

For one 16-leaf block the constructive schedule uses eight source
interleaves, 16 `vpmaddwd`, eight `vpaddd`, and eight half-REDC32 exits.  It
then produces four e=0 coefficient planes, reuses the existing 12-instruction
Q24 transpose and omits the four wide v=9 reducers (12 instructions) that a
materialized high-range quartic would need.  Under the explicit centered-E7
contract the largest e=1 dot accumulator is 36,844,554, safely inside signed
32-bit, and the conservative peak is 12 YMM without spills.

The generator also emits the complete 192-vector/6,144-byte sparse e=1
constant table in block/output/pair/low-high order, plus all 48 existing Q24
packet permutations and safe-tail store metadata.  Thus the next gate does
not need to rediscover either constant layout or wire routing.

This is not yet a claim that current Forward emits centered E7 for free.  It
is a complete lowering target for a matched block-level assembly gate.  A
larger first-version instruction count is not a stop condition because the
candidate deletes quartic recombination/materialization and a distinct Q24
reduction layer.

This deletes B3-local quartic recombination, quartic output materialization,
and the standalone four-plane add pass.  It adds a seven-plane representation
and a late `K_lambda + Q24` exit.  The next gate must lower that exit with
pair-packed `vpmaddwd`/REDC32 and prove range/liveness; no production or cycle
claim is made here.  GT Clean is unchanged.

## Reproduction

```sh
python3 tools/generate_gate.py
python3 tools/generate_late_exit_lowering.py
```

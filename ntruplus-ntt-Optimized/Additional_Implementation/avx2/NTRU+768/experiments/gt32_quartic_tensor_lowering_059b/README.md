# GT32-QUARTIC-TENSOR-LOWERING-059B

This generator compares three non-production tensor architectures without
using a cycle or total-instruction threshold:

1. **R7-A** — the selected rank-seven points from experiment 059;
2. **R7-B** — `0, +/-1, +/-2, +/-4`, with explicit even/odd interpolation;
3. **R6-CRT** — factor every quartic leaf into two quadratic components and
   use two rank-three quadratic multiplications.

## Exact results

All three candidates pass all 192 effective lambda entries and all 16
monomial input products per lambda: 3,072 exact checks per architecture.

Every lambda is a square and not a fourth power in `F_3457`, so

```text
x^4 - lambda = (x^2 - mu)(x^2 + mu)
```

is valid for every production GT leaf, while both quadratic factors remain
the natural incomplete-transform endpoints.

## Operation-class result

```text
current quartic tensor:  9 variable products
R7-A / R7-B:             7 variable products
R6 quadratic CRT:        6 variable products
```

If R6 is paid locally at the current quartic B3 boundary, split and merge
constant multiplications can erase the credit.  That is deliberately not the
target architecture.  With native d2 producers and consumers, B3 needs six
variable-product chains plus two quadratic-mu chains, while quartic split and
merge disappear from B3.

R7-B also remains open: three sum pairs and three difference pairs expose
separate even and odd 3x3 systems, which is a different lowering mechanism
from the dense R7-A `W_lambda` map.

## Decision

- retain R7-A as a lowering control;
- continue R7-B to an explicit even/odd AVX2 DAG;
- promote R6-CRT to the `060` d2 / GT 3x64 architecture research gate.

This is not a production promotion, and GT Clean is unchanged.

## Reproduction

```sh
python3 tools/generate_gate.py
```

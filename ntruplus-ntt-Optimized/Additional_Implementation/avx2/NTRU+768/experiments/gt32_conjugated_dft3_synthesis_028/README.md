# GT32 conjugated DFT3 synthesis 028

This gate asks whether the exact unweighted-merge scale from 027 can be
consumed directly by a modified DFT3 rather than repaired afterward.  GT Clean
and production code are unchanged; no assembly is emitted.

For each difference-lane class it constructs

```text
G = F * diag(rho^-1)
```

and exhaustively searches signed-add circuits of the form

```text
signed base matrix
  + c0 * (signed output form) * (signed input form)
  + c1 * (signed output form) * (signed input form)
```

The rank-one updates model a Montgomery multiplication of a retained signed
linear form followed by signed distribution to outputs.  Unlike a plain
`A*diag(c)*B` model, this correctly permits retaining the unmultiplied source.

## Oracle calibration

The search rediscovers current DFT3 with one Montgomery chain:

```text
t  = Mont(x1 - x2, -722)
y0 = x0 + x1 + x2
y1 = x0 - x1 + t
y2 = x0 - x2 - t
```

Thus the model does not reject the current one-chain factorization by
construction.

## Result

For all four exact difference-lane scale classes and all four free k3 sign
choices, no zero-, one-, or two-Montgomery factorization exists in the complete
signed-base/rank-one-update search.  The conjugated DFT3 therefore needs at
least three chains per 16-vector DFT3 unit in this topology, versus one now.
This is optimistic: each lane class is allowed to choose its own signed
topology, and any SIMD routing needed to combine those topologies is ignored.

Exact conjugation before DFT3 has the following chain count:

| Region | Current | Candidate |
|---|---:|---:|
| merge | 48 | 0 |
| inverse size2 | 0 | 24 |
| inverse length 4 | 12 | 24 |
| inverse length 8 | 18 | 24 |
| inverse length 16 | 21 | 24 |
| 16 DFT3 units | 16 | at least 48 |
| **total through DFT3** | **115** | **at least 144** |

The direct conjugated DFT3 therefore changes the earlier three-chain credit
into a lower bound of **+29 Montgomery chains**.  This violates the requested
`candidate <= current` condition before range, register allocation, or ASM.

## Decision

Static stop for the one/two-rank-one-update AVX2 DFT3 family.  This is an
operation-class result, not an instruction-count heuristic.

Reopen only with an algebraically different DFT3 factorization outside the
searched signed-base plus two rank-one updates, and require it to prove fewer
than three chains before implementation.

Run `make check` to regenerate and validate the JSON result.

# FR-ISO2 preliminary range and scale obligations

This gate proves only the algebraic R0 relation.  It does not reuse M5C's old
`24438` operand proof: M5R-D has a new-node/output maximum of 26306, so the old
consumer proof is insufficient.

Assume the next Forward DAG leaves component 0 at the conservative M5R-D bound

```text
B0 = 26306
```

and produces component 1/2 through one valid Algorithm-10 multiplication by
the fused `tau`/`tau^2` constants.  Algorithm 10 gives the strict bound
`3q/2`; the integer proof conservatively uses

```text
B12 = floor(3q/2) = 5185.
```

For branch constant `z0`, the unreduced widening accumulators satisfy:

| Component | Bound |
|---|---:|
| `c0` | `B0^2 + 2*z0*B12^2` |
| `c1` | `2*B0*B12 + z0*B12^2` |
| `c2` | `2*B0*B12 + B12^2` |

The machine proof obtains:

| Branch | `c0` | `c1` | `c2` |
|---|---:|---:|---:|
| alpha, `z0=9` | 1,175,921,686 | 514,751,245 | 299,677,445 |
| beta, `z0=3` | 853,310,986 | 353,445,895 | 299,677,445 |

All fit signed int32.  This establishes feasibility of accumulating the small
ordinary constants before reduction; it does not select the final Montgomery
reduction sequence or its output bound.  The next gate must prove each actual
instruction-level scale transition and include BaseMulAdd's R0 addend.

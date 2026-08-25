# Checkpoint F0-PROD0

## Outcome

F0-PROD0 establishes the first complete coefficient-domain producer for the
exact materialized F0 ABI consumed by MA2.  It does not call Official
`poly_ntt`, does not form an Official transform result, and does not invoke the
Official-to-F0 adapter.  The pipeline is:

```text
KEM-small coefficients
-> existing top-split arithmetic
-> GT gather/relabel/pre-twist
-> paper R2 NTT9
-> persistent D1 NTT16
-> materialized F0 P/Q/coefficient-plane layout at scale four
```

This is a correctness-first producer.  It is not yet installed in the KEM and
has no performance claim.

## Role contracts

The pinned encapsulation caller creates `r` with `poly_cbd1` and `m` with
`poly_sotp_encode`; both produce coefficients in `[-1,1]`.  Their semantic
roles and lifetimes remain separate as `F0_R` and `F0_M`, but their input
range, 32-byte caller alignment, transform map, and output ABI are identical.
The shared `ntruplus1152_exp001_f0_forward_for_ma2` core is therefore
authorized for both roles.  In-place `output == input` is supported.

The output owner is `(branch,p,q,terminal_coefficient)`.  Physical P remains
`[0,3,6,1,4,7,8,2,5]`; physical Q remains the existing four-bit-reversed
order.  Transform scale is four and the Montgomery exponent is zero.  The
generated contract carries the exact per-cell raw signed-i16 bounds already
proved for the paper R2/D1 path.

## Correctness

The Official oracle runs pinned `poly_ntt` and maps its result into the F0
owner layout with an exact scale-four lift.  Direct producer values can differ
from that oracle by multiples of `q` because the paper path intentionally
retains lazy representatives; comparisons therefore canonicalize both sides.
No reduction is inserted merely to obtain prettier representatives.

The gate passes:

- all 1,152 positive and 1,152 negative coefficient impulses;
- zero and alternating-bound inputs;
- 1,003 deterministic random KEM-small polynomials;
- all 1,152 raw outputs against their generated per-cell ranges;
- in-place alias, input immutability, and output canaries; and
- ASan/UBSan with strict warnings.

The underlying R2/D1 arithmetic remains covered by its existing bit-exact
schedule differential and full-range proof.

## Linked-shape debt

The O3 object is 32-byte aligned and contains no Official representation call.
Its current correctness-first shape is deliberately recorded rather than
hidden:

| item | current value |
| --- | ---: |
| text bytes | 1,029 |
| stack reservation | 3,872 bytes |
| top-split calls per forward | 1 |
| scalar GT adapter calls per forward | 8 |
| R2+D1 pair calls per forward | 4 |
| static compiler `vzeroupper` | 6 |

The source-level live buffers are the 2,304-byte split, two 576-byte pair
buffers, and one 288-byte coefficient adapter.  These costs are real and must
remain inside every future end-to-end measurement.

## Decision

F0-PROD0 passes the algebra, map, scale, range, alias, canary, sanitizer, and
entry-alignment gates.  It closes the producer correctness question but is not
a production-shaped AVX2 leaf yet.

The next checkpoints are F0-PROD1-SCHED and F0-PROD1-ASM. They must replace
the scalar gather/pre-twist and four-call C composition with a caller-shaped
producer while preserving this contract. Only then does F0-PROD1-MA2 install
four attribution variants:
Official control, only-R direct F0, only-M direct F0, and both direct F0.  KAT
and encapsulation consistency precede timing; no KEM or SUPERCOP promotion is
authorized by F0-PROD0 alone.

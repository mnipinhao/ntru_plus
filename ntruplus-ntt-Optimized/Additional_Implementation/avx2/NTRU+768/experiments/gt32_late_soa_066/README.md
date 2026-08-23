# GT32-LATE-SOA-066 — Decap first-product closure

This gate tests the first real KEM caller affected by the Late-SoA seam proven
by 063–065.  It does not modify GT Clean production sources.

## Encap audit

The originally proposed Encap 066 was not run:

```text
NOT_RUN — caller graph incompatible with the 065 seam
```

GT Clean Encap already uses persistent M coefficient planes for both Forward
outputs and general B3, and it has no inverse.  Substituting the 065 Forward
would therefore compare the control with itself; using the fused B3/inverse
output would violate Encap's M/e=0 add-and-pack contract.

## Decap control and candidate

Only the first-product seam differs:

```text
Control:   decode M -> scale B3_M -> invntt_M -> common tail -> crepmod3
Candidate: decode M -> Late-SoA scale B3 + inverse I0/I1
                    -> inverse remainder -> common tail -> crepmod3
```

The caller's current M input is already the coefficient-plane representation
consumed by the Late-SoA B3.  The measured entry conversion cost is therefore
zero; no preformed 064/065 state is supplied to the candidate.

The complete Decap implementation is shared and receives either first-product
leaf through the same function-pointer seam.  Decode, second Forward, general
B3, recovered-r packing, hashes, final native-domain verification, cleanup,
failure behavior, and public API remain common.

## Decision methodology

- `primary_normal` and `primary_reversed` are lean decision ELFs containing
  only the required `post-I1`, `crepmod3`, and full-Decap gates.
- `bench_normal` and `bench_reversed` add diagnostic checkpoints and are used
  only for attribution, not for promotion.
- Every launch contains 41 alternating paired measurements on one pinned CPU.
- The primary gate uses 16 process launches per placement and a bootstrap CI
  over launch medians.
- PMU measurements use deterministic key/ciphertext setup and alternating
  process order.

See `RESULTS.md` and `STATUS.yml` for the decision and exact measurements.

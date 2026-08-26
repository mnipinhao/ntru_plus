# NTRU+864 9-by-32 Montgomery boundary reference

## Question

Can the row-major 9-by-32 GT reference preserve the current NTRU+864 scale and
legacy cubic-leaf consumer contract?

## Scale contract

Current transformed coefficients are not stored in Montgomery domain. They are
normal `R^0` field representatives. Public roots and inverse constants are
stored as `constant * R mod q`, where `R=2^16 mod 3457`.

Therefore:

```text
montgomery_reduce(normal_value * public_constant_R)
    = normal_value * public_constant mod q
```

The candidate keeps this contract through both 32- and 9-point stages.

## Boundaries checked

1. GT row-major forward output maps to the current 288-leaf order by matching
   decoded `X^3-zeta` labels.
2. Mapped forward output must equal current scalar `ntt()` exactly, including
   centered representatives.
3. GT-grid cubic basemul uses Montgomery-form leaf roots and must equal current
   scalar `basemul()` exactly after mapping.
4. Candidate inverse must equal current `invntt()` modulo q. Exact int16 equality
   is not required because current inverse returns a wider bounded
   representative while the candidate deliberately returns centered values.
5. Complete GT multiplication must equal the frozen canonical reference and
   independent schoolbook multiplication modulo q.

## Why inverse equality is modulo q

Current `invntt()` ends with Montgomery reductions but no final centered
Barrett pass. Its output can therefore use a different valid `R^0`
representative from the candidate. This experiment does not mistake an int16
representative difference for a mathematical scale difference.

## Run

```sh
make check
```

This is a scalar correctness reference. It is not a lazy-range proof, Neon
layout, constant-time production implementation, or benchmark candidate.

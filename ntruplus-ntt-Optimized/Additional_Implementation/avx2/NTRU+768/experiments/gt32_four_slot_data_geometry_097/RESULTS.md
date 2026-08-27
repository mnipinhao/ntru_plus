# 097 results — four-slot data geometry

## Decision

`SEARCHED_NO_PROMOTION`.

The 24 permutations are correct and statically isolated, but none of the three
short-sweep leaders retained a statistically stable Encap advantage in the
formal ASLR-on SUPERCOP campaign.  Production remains the `hrmc` order from
`b2a4bea`.

This is not a claim that stack geometry has no effect.  It is the narrower and
more useful result that a fixed four-slot order does not control enough of the
fresh-process ASLR geometry to create a reproducible winner under the declared
benchmark objective.

## Correctness and isolation

- All 24 layouts passed 1000 deterministic byte-exact Encapsulations, 768
  noncanonical-public-key cases, and input-immutability checks.
- Every frame remained 6592 bytes and every qualified caller reservation
  remained 611 bytes.
- 83 pre-existing symbols outside the Encap caller had identical addresses,
  sizes, and bytes.
- `.rodata` and the 4914-byte E0V RX-tail section were identical.
- The arithmetic, calls, number of slots, and E0V helper were unchanged.

## Directional sweep

Eight fresh-process blocks screened all 24 orders.  Each block used three
`hrmc` anchors and one launch of every candidate.  The top three by Encap
median were:

| Order | Median vs `hrmc` | 95% bootstrap CI | Negative blocks |
|---|---:|---:|---:|
| `rhcm` | -65.83 | [-149.67, +15.17] | 6/8 |
| `cmhr` | -47.25 | [-131.67, -2.67] | 7/8 |
| `mchr` | -40.92 | [-156.67, -7.17] | 7/8 |

The sweep selected candidates; it did not qualify them.

## Formal comparison

The formal campaign placed `hrmc`, `rhcm`, `cmhr`, and `mchr` in one fixed
image set and used 16 balanced palindrome blocks with two launches per profile
per block.  CPU 1 was pinned and ASLR remained enabled.

### Encap cycles

| Order | Median vs `hrmc` | 95% bootstrap CI | Negative blocks |
|---|---:|---:|---:|
| `rhcm` | -6.75 | [-95.00, +37.75] | 10/16 |
| `cmhr` | +12.25 | [-17.13, +29.75] | 4/16 |
| `mchr` | +0.75 | [-113.00, +29.25] | 8/16 |

No confidence interval excludes zero.  Individual block deltas reached
hundreds of cycles in both directions, including `rhcm` values from -259.5 to
+844 cycles.  The short-sweep ranking therefore did not reproduce.

### Unaffected-operation controls

Keypair and Decap also showed confidence intervals crossing zero for all three
candidates.  This is consistent with the static audit: those operations share
identical code and the experiment has not produced a stable collateral change.

## Interpretation

Data geometry remains a legal implementation variable, but selecting the best
order from one short run would fit transient ASLR phases rather than deliver a
reproducibly faster submitted implementation.  The four-slot permutation
search class is exhausted for the current production caller and canonical
ASLR-on SUPERCOP protocol.

The next geometry campaign, if pursued, should change an executable property
that remains deterministic across launches (for example linker-controlled hot
symbol relative placement), rather than adding more four-slot permutations.

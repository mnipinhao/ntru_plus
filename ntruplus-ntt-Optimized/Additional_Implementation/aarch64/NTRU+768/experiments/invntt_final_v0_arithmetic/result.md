# Inverse final V0 arithmetic result

## Scope

This model covers the active rminus1 inverse final path:

```text
Stage45 centered row outputs
-> inverse DFT3
-> branchfold Montgomery products
-> final Barrett reductions
-> signed time-domain stores
```

It models the exact signed 16-bit behavior of `sqrdmulh`, `sqdmulh`, `srshr`,
`mul`, and `mls`. The three inverse-DFT3 output sets are constructed from every
triple in `[-1728, 1728]^3`; the model then checks all 192 low/high
branchfold reduction chains and all production rminus1 constants. The
two-instruction quotient search covers all 65,536 signed 16-bit
`sqrdmulh` multipliers.

## Static cost

| Category | Dynamic V0 instructions per inverse |
|---|---:|
| inverse DFT3 multiply | 96 |
| branchfold Montgomery multiply | 576 |
| final Barrett reduction | 576 |
| total final region | 1248 |

Deleting every final Barrett would save at most
576 vector
instructions. Replacing each three-instruction quotient/reduction with one
`sqrdmulh` quotient plus `mls` would save at most
192.

## Proof result

```text
delete-safe chains: 0 / 192
two-instruction direct-quotient chains: 0 / 192
decision: stop_no_proof_backed_instruction_deletion
```

The first deletion counterexample is:

```json
{
  "raw": -3636,
  "left_input": 4847,
  "right_input": 5167,
  "left_fqmul": -1758,
  "right_fqmul": -1878,
  "reduced": -179
}
```

The direct `sqrdmulh` quotient candidates fail as well. Representative
counterexamples for multipliers 9 and 10 are:

```json
{
  "9": {
    "raw": -1820,
    "left_input": -5180,
    "right_input": -2567,
    "left_fqmul": -1631,
    "right_fqmul": -189,
    "wanted_quotient": -1,
    "direct_quotient": 0
  },
  "10": {
    "raw": -1728,
    "left_input": -5180,
    "right_input": -4683,
    "left_fqmul": -1631,
    "right_fqmul": -97,
    "wanted_quotient": 0,
    "direct_quotient": -1
  }
}
```

Consequently, the current three-instruction final Barrett is not removable or
replaceable by a two-instruction direct-quotient form under the active inverse
contract. No ASM candidate is emitted.

## Interpretation

The existing implementation has already removed the intermediate post-DFT3
reductions and folded normalization, untwist, branch merge, and the rminus1
correction into the branchfold constants. The remaining reductions are doing
real representative work. A modulo-q-only deletion is insufficient because
the following `poly_crepmod3` is sensitive to changes by `q`, and `q = 3457`
is congruent to one modulo 3.

The previously tested fused inverse-plus-crep3 path reused the Barrett
quotient and was correct, but its same-path PMU result was slower. Reopening it
would require a new arithmetic DAG with fewer instructions, not another
wrapper or store/load fusion.

# GT32 character-compatible producer gate 029

This gate checks the other narrow reopening condition from 027: can an
existing producer Montgomery chain be relabeled so the merge residual is a
DFT3 character and terminal correction becomes a permutation?

For a diagonal producer scaling `alpha`, both QBM bilinear products receive
the same scale.  Consequently:

```text
sum coordinate ratio         = alpha
difference coordinate ratio  = alpha / merge_weight
```

Both ratios are DFT3 characters exactly when the terminal merge-weight triple
is itself a character, because the three DFT3 characters form a group.

## Result

The four difference-lane classes give:

| lanes | normalized merge weight | character? |
|---|---|---|
| 2,3 | `(1,-723,722)` | yes |
| 6,7 | `(1,723,-722)` | no |
| 10,11 | `(1,-723,-722)` | no |
| 14,15 | `(1,723,-722)` | no |

Only one of four classes can use a free character relabel.  AVX2 lane-wise
constants allow the partial case, but the other six difference lanes still
require non-character correction, so there is no complete producer ABI.

## Provenance

- Forward has an existing `round4c_forward_preweight_mont` chain whose
  constants can be relabeled, but diagonal relabeling scales sum and
  difference together and fails three lane classes.
- Decode has no existing Montgomery chain to absorb nontrivial `alpha`.
- BaseInv may fold an output scale, but it has the same diagonal obstruction.
- Prepared-key precomputation is a separate time/memory API and is not a
  zero-cost standard-KEM producer.

Scaling only the difference coordinate requires a non-diagonal rank-two
output mix, which is precisely the producer obstruction already proved by
026A.  It cannot be obtained by merely replacing a constant.

## Decision

Static stop for the zero-new-chain diagonal producer-character family.  Reopen
only for a coupled producer that deletes another operation class, an existing
selective-difference chain, or an explicitly prepared-key representation.

Run `make check` to regenerate and validate the result.

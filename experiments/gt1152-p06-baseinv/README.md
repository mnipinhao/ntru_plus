# GT1152-P06 — degree-4 BaseInv and the R⁻¹ boundary

Transform-domain inversion over `Z_q[X]/(X⁴ − ζ)`, plus the `basemul_rinv`
multiplication boundary the inverse consumes. NEON intrinsics C.

```sh
make check
```

Built and run on the local arm64 host. Not Cortex-A76 — no performance claim.

## Result

All four checks pass over 10 cases, each also run with exact `out == in`
aliasing:

| check | result |
| --- | --- |
| `baseinv_matches_oracle` | matches the G1 oracle under the GT layout; 3 of the 10 inputs were genuinely non-invertible and returned 1 with a fully zeroed output |
| `basemul_rinv_scale` | `out · R` is congruent to the R0 `basemul` for every coefficient |
| `d7_normalization` | output observed in `[−1727, 1728]` |
| `noninvertible_rejected` | an all-zero transform-domain input returns 1 and clears the output |

## Degree 4 is simpler here, not harder

`X⁴ − ζ` is a **quadratic tower**. With `u = X²` and `u² = ζ`, an element
`a = (a₀+a₂u) + X(a₁+a₃u)` lives in `R[X]/(X²−u)` over `R = Z_q[u]/(u²−ζ)`, so
inversion is two nested quadratic conjugations. Degree 3 needs a genuine cubic
resultant.

```
t0 = a₂² − 2a₁a₃              t1 = a₃²
t0 = a₀² + ζ·t0               t1 = a₁² + ζ·t1 − 2a₀a₂
t2 = ζ·t1
norm = t0² − t1·t2            ← the scalar that gets batch-inverted
```

The `+,−,+,−` sign pattern on the four outputs — which appears in the stock
lane as `pden, mden, pden, mden` — **is that conjugation**, deferred to the
final scaling. 864 has no conjugation structure, so all three of its outputs
take the same denominator with no sign flip.

## The batch inversion, and the scale trap

288 leaf norms are inverted with one field inversion instead of 288, via
running prefix products. The subtlety is that the running multiply is `fqmul`,
which is Montgomery and introduces an `R⁻¹` per step — so the prefix at step *i*
carries `R^{−i}`.

Before writing any of it, this was checked in Python against the oracle: the
batch result is **exactly** elementwise `fqinv`, over random 36-lane inputs. The
`R` powers cancel between the prefix, the single inversion and the walk-back. A
separate check established that `fqinv(a) = a⁻¹` with **no** scale factor, so
there is nothing to compensate for.

Getting this wrong would produce a uniformly scaled, entirely plausible-looking
wrong answer, so it was worth settling before writing C.

## Phase decomposition

Written to mirror NTRU+864's phases so a later gate can swap in assembly piece
by piece: numerator → prefix → inverse → recover → finish.

864 splits the batch into 12 steps × 3 chains for instruction-level
parallelism. That is an optimization, not a correctness requirement, and is
left to a later gate; this implementation uses 36 sequential groups with one
8-lane inversion.

## D7 applied

`basemul_rinv` stops one Montgomery stage before R0, which is why it carries
the input magnitude through — G2 measured 2752 over the decapsulation domain,
above NTRU+864's documented 2497 inverse input contract. Per decision D7 a
`barrett_reduce` is applied, bringing the output to `[−1729, 1728]`, measured
here as `[−1727, 1728]`. The 864 inverse bound chain therefore holds a
fortiori.

## Not established

- **A targeted per-leaf failure suite.** The 3 naturally non-invertible cases
  and the all-zero input exercise the reject path, but NTRU+864 gates this with
  an 808-case failure/alias/wipe suite. An equivalent is still owed, and G8
  should not claim the failure path is covered without it.
- Constant-time review of the failure branch beyond the structural argument
  (`vminvq_u16` folds all lanes with no early exit; the single branch depends
  on public non-invertibility).
- No Pi 5 measurement and no performance claim.

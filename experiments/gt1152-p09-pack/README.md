# GT1152-P09 — the codec

Good-Thomas layout to the 12-bit wire format, and back with canonical
rejection. Plain C, per decision **D5**.

```sh
make check
```

Built and run on the local arm64 host. No performance claim.

## Result

All seven checks pass.

| check | detail |
| --- | --- |
| `full_exact_bytes` | 17 cases including every int16 extreme and the measured Forward bound |
| `full_model_agrees_with_oracle` | the mod-q model reproduces the oracle wherever the oracle is defined |
| `small_matches_full_on_its_domain` | 8 cases over `(−q, q)` |
| `round_trip` | 6 canonical polynomials survive `tobytes` then `frombytes` exactly |
| `canonical_rejection` | **3456 cases** — every one of the 1152 positions carrying each of `q`, `q+1`, `4095` |
| `canonical_accepted` | the unmodified canonical buffer decodes with 0 |
| `tobytes_compare` | equal returns 0; 256 sampled single-bit corruptions all return 1 |

## Why this is not a port of NTRU+864's pack

864's `pack_full` + `pack_small` + `pack_compare` are 7,751 lines with 111
Slothy windows. They exist because degree-3 leaves are **6 bytes stored and 4.5
bytes packed** — neither aligns, so the routing needs ST3 lane stores and TBL.
Degree 4 is **8 bytes stored (one `d` register) and 6 whole bytes packed**.

What does *not* improve: G3a measured one GT vector's eight leaves landing at
natural starts `0, 64, 128, …, 448` — **structurally identical to 864's scatter**,
only multiplied by the leaf degree. Only the granularity changes. Here the
scatter is a plain table lookup; G9's profile decides whether it needs more.

## Full and Small are genuinely different

`kem.c` calls **Full** on raw Forward output — `poly_tobytes(sk, f)` where
`f = poly_ntt(...)`, measured at ±14607 in G3b. So Full must reduce arbitrary
int16, which it does with a branch-free Barrett followed by a conditional add,
landing in `[0, q)`.

**Small** is called on `basemul` / `basemul_add` / `baseinv` outputs, bounded by
G2 and G4 at 1764 / 1768 / 1781, so it skips the Barrett and only folds the sign
bit.

### A correction the gate produced

`full_exact_bytes` failed on the first run, and the fault was in the **test**,
not the code. The G1 oracle's `poly_tobytes` is the *reference* serializer: it
only folds the sign bit, so it is defined on `(−q, q)`. Comparing Full against
it over arbitrary int16 was the wrong model. The right model is the canonical
representative of `x mod q`, with the oracle used to cross-check that the two
agree wherever the oracle is defined — which is now its own check.

## Not established

- No Pi 5 measurement, no performance claim, and no comparison against 864's
  routed pack.
- Plain C with a table-lookup scatter. A vectorized codec is later work, and
  should be sized from a profile rather than from the degree-4 argument.

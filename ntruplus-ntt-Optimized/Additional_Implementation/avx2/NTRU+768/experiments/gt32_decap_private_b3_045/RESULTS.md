# GT32-DECAP-PRIVATE-GENERAL-B3-PRELOAD-045 Results

All deltas are candidate minus control; negative is faster.

## Correctness and infrastructure

- Parser regression test passed: base `28000` plus deviations `-10,+5,+20`
  reconstructs `27990,28005,28020`.
- Both fixed-geometry images passed the canonical 100-vector byte-exact KAT.
- Control and candidate fixed-geometry images have identical selected symbol
  addresses and identical `.text`/`.rodata` sizes.

## Fixed-geometry causal gate

256 paired AB/BA blocks:

| Operation | Paired median delta | Favorable | Bootstrap 95% CI |
|---|---:|---:|---:|
| Keypair | +0.0625 | 128/256 | [-14.1667, +9.9167] |
| Encap | -1.6458 | 132/256 | [-5.0417, +4.5417] |
| Decap | **-16.1875** | **177/256** | **[-19.3333, -10.25]** |

This isolates and qualifies the Decap-private General-B3 qinv-preload
mechanism.  The two unrelated operations are neutral.

## Clean exact-image SUPERcop gate

Three independently built fixed ELFs were measured in 256 balanced mirrored
blocks: Official, GT Clean, and the GT private-clone export.

### Private-clone export minus GT Clean

| Operation | Aggregate delta | Paired median delta | Favorable | Bootstrap 95% CI |
|---|---:|---:|---:|---:|
| Keypair | -12.1887 | **-18.1354** | 158/256 | [-28.8958, -9.9583] |
| Encap | +164.5606 | **+220.5** | 34/256 | [+214.1042, +233.9583] |
| Decap | +105.3726 | **+125.9167** | 22/256 | [+120.7813, +133.2292] |

The export adds 704 bytes of `.text` (`64432 -> 65136`).  Existing callers and
the public General-B3 retain their own implementations, but later hot symbols
move.  The large Keypair and Encap changes, despite neither operation calling
the private symbol, prove that the exact-image result is dominated by delivery
geometry.  The local `-16.19` Decap mechanism is overwhelmed rather than
invalidated.

### Private-clone export minus Official

| Operation | Aggregate delta | Paired median delta | Favorable | Bootstrap 95% CI |
|---|---:|---:|---:|---:|
| Keypair | -406.5278 | **-427.6250** | 248/256 | [-436.8125, -417.7083] |
| Encap | +57.3151 | **+61.6563** | 26/256 | [+56.8438, +67.0] |
| Decap | -225.0242 | **-219.9896** | 238/256 | [-222.7292, -214.9583] |

The private-clone image still beats Official for Keypair and Decap, but this is
not sufficient for promotion because it materially regresses both Encap and
Decap relative to the selected GT Clean image.

## Final decision

`045` is **mechanism-qualified but exact-image rejected**.  Do not update GT
Clean production with the current export.  A retry is justified only with an
end-placed private object or an equal-size reserved cage that leaves every
existing hot symbol address unchanged.  That retry must again pass KAT,
fixed-geometry causality, and exact-image SUPERcop with neutral Keypair/Encap
and a negative Decap confidence interval.

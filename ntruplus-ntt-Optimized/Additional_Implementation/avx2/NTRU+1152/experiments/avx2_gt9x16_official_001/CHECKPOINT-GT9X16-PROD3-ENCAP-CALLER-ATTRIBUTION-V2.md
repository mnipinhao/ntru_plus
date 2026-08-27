# GT9x16 PROD3 Encap caller attribution V2

## Scope

This checkpoint does not change arithmetic or add candidate assembly. It
re-prices the exact cumulative Encap baseline after the native SUPERCOP rebase:

```text
persistent AoS + Natural-Q + T0-beta + scale-4 MA2 + Direct H1
```

The fixed-common O3GC, same-ELF measure splits the current native
`+992.0231`-cycle Encap gap into four production-shaped boundaries:

1. coefficient-domain `r` to the implementation-native transformed state;
2. coefficient-domain `m` to the implementation-native transformed state;
3. coefficient-domain `r` to both native state and exact 1728 hash bytes;
4. resident transformed `r/m/h` to exact ciphertext polynomial bytes.

Official runs `poly_ntt`, `poly_basemul`, `poly_add`, and `poly_tobytes` in its
native representation. GT runs the cumulative producer, Natural-Q scale-4 MA2,
and Direct H1. Official producers are in-place, matching the real caller; GT
uses the separate coefficient and plane buffers present in the cumulative
caller.

Untimed preflight requires Official `poly_tobytes(state)` to equal GT Direct
H1 bytes and requires exact equality of the final tail bytes. Linked-object
audit fixes every direct call target.

## Method

- pinned SUPERCOP: `20260627`;
- CPU: physical P-core 1, performance governor, turbo disabled;
- compiler: common O3GC SUPERCOP recipe;
- 9 fresh processes and 96 observations per label per process;
- balanced same-ELF order: Official, GT, GT, Official;
- normal/reversed source placement;
- ASLR on/off;
- headline placement selected independently by the lowest absolute GT StQ2 sum
  for `dual-r + m producer + tail`.

The result is `supercop-derived`, not a native SUPERCOP public number.

## Result

Normal placement was selected (`5510.4282` versus `5515.1736` modeled-path
absolute StQ2). Headline normal/ASLR-on component medians are:

| component | GT - Official cycles |
| --- | ---: |
| `r` producer | +78.8125 |
| `m` producer | +76.1042 |
| excess `r` hash fanout (`dual-r - r producer`) | +226.7083 |
| resident `h` + MA2 + ciphertext serializer tail | **+605.3958** |
| rough modeled debt | **+987.4167** |

All raw paired boundaries were GT-slower in 9/9 launches under every setting,
and every bootstrap interval was wholly positive:

| setting | r producer | m producer | dual-r | tail | rough modeled debt |
| --- | ---: | ---: | ---: | ---: | ---: |
| normal, ASLR on | +78.81 | +76.10 | +304.50 | +605.40 | +987.42 |
| normal, ASLR off | +79.52 | +76.75 | +307.75 | +606.98 | +991.04 |
| reversed, ASLR on | +74.50 | +73.94 | +301.42 | +608.56 | +981.31 |
| reversed, ASLR off | +75.83 | +75.02 | +301.27 | +604.06 | +981.25 |

The balance sheet uses:

```text
r producer
+ m producer
+ (dual-r - r producer)
+ tail
```

Its headline residual relative to the separate native campaign is only
`+4.6064` cycles. This close match is not an additive performance claim:
island cuts change cache state, placement, dependency overlap, and omit the
real `hash_g -> SOTP` chain. It is nevertheless strong decision evidence that
the three measured regions already explain the native gap's scale; a new
dependency-chain benchmark is not the first priority.

## Evidence correction

The older current-Q versus Natural-Q caller timing contained MA2 inv4 followed
by H1 inv4. Its `-160`-cycle production interpretation remains downgraded to
scoped evidence. A corrected single-inv4 sidecar was not added here because it
would require a new current-Q scale-4 machine object, violating this
checkpoint's cheap-sidecar/no-new-ASM boundary. Natural-Q structural evidence
and the frozen cumulative correctness result remain valid; Q-order search is
not reopened.

## Decision

The cumulative architecture is not promoted. The next checkpoint is
`ENCAP-TAIL-ATTRIBUTION-V1`, still without new ASM: split the approximately
`+605`-cycle tail into resident-`h` projection, MA2 arithmetic, and final H1
serialization debt using the exact cumulative representation. Producer and
dual-output work are deferred because their debts are materially smaller.

Evidence:

- `results/gt9x16-prod3-encap-attribution-v2-intel155h-20260827-001/summary.json`
- `bench/supercop/gt9x16_prod3_encap_attribution_v2_measure.c`
- `scripts/run_gt9x16_prod3_encap_attribution_v2.py`

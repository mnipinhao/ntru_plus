# ENCAP Lazy x H4 factorial pricing

## Question and boundary

This checkpoint prices two previously separate candidates in one fixed ELF:

- `L`: the proved `72 -> 40` Forward Barrett mask;
- `H`: the scale-1 producer plus H3 plus H4-M3B egress bundle.

Every cell starts with identical coefficient-domain small `r/m` and valid
public-key bytes and stops at exact 1728-byte ciphertext. The four cells are:

| cell | Forward | tail |
| --- | --- | --- |
| `C00` | current scale-4 | H3 scale-4 plus Natural-Q H1 |
| `C10` | lazy scale-4 | H3 scale-4 plus Natural-Q H1 |
| `C01` | current scale-1 | H4-M3B |
| `C11` | lazy scale-1 | H4-M3B |

The untimed hard gate compares all four ciphertexts byte-for-byte with the
pinned Official polynomial path. The benchmark deliberately excludes the
`r -> bytes -> hash_g -> SOTP(m)` fan-out, so it is a production-shaped
polynomial caller island, not a native Encapsulation result.

The combined scale-1/lazy object also passed 1003 random-small plus fixed-case
semantic and final-ciphertext differential, invalid decoder, overlap, canary,
immutability, ASan, and UBSan gates. Linked-object comparison corrects the
scale-1 estimate to 3685 -> 3557 instructions and 15489 -> 14945 `.text`
bytes; `vpmulhrsw` is 72 -> 40 and no output ABI changes.

## Method

- Pinned SUPERCOP 20260627 `cpucycles()` and O3GC compiler recipe.
- Same ELF for all four cells.
- Four cyclic execution orders, placing every cell once in every position.
- 384 observations per cell per fresh process.
- Nine fresh processes for normal/reversed placement and ASLR on/off.
- CPU 2, performance governor, turbo disabled.
- Headline placement predeclared as normal from the independent H4-M3B
  serious campaign; headline uses ASLR on.

## Result

Launch-level effects use a cell StQ2 pooled over all four positions. The table
reports the median of nine launch-local contrasts in cycles.

| setting | `L @ H=0` | `H @ L=0` | `L @ H=1` | `H @ L=1` | interaction | `C11-C00` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| normal, ASLR off | -82.04 | -35.57 | -81.84 | -35.33 | +0.78 | -117.61 |
| **normal, ASLR on** | **-79.61** | **-28.09** | **-86.79** | **-27.95** | **-1.84** | **-119.44** |
| reversed, ASLR off | -103.70 | -31.16 | -89.11 | -20.48 | +13.92 | -117.55 |
| reversed, ASLR on | -92.47 | -27.65 | -88.99 | -16.33 | +2.82 | -114.35 |

Every conditional Lazy and H4 contrast is negative in 9/9 launches in every
setting. `C11-C00` is also negative in all 36 launches. Interaction is small
relative to either main effect but is placement-sensitive: reversed/ASLR-off
has a positive median and confidence interval, while the normal headline
interval includes zero.

Do not arithmetically reconstruct `C11-C00` from the displayed medians. Each
column is the median of its own launch-local contrast, and medians are not
additive. The exact factorial identity holds within each launch before the
cross-launch median is taken.

## Decision

`C11` is the selected winner for this caller-island boundary. Lazy Forward is
independently robust under both tail contracts, and the complete H4 bundle is
independently favorable under both Forward contracts.

This result does **not** yet authorize native KEM integration. A scale-1 `r`
still has a second consumer: exact bytes for `hash_g`. The measured H4 island
does not price that fan-out edge. Native Rebase #2 therefore requires an
explicit scale-1 `r` hash contract (shared state, dual output, or a paid
consumer-side adapter); silently adding a second Forward or treating the old
scale-4 serializer as compatible is forbidden.

Raw evidence and ELF hashes are in
`results/encap-lazy-h4-factorial-price-intel155h-20260828-001/summary.json`.

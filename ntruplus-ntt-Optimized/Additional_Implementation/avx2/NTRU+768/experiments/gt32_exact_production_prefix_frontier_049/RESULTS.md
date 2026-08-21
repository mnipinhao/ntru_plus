# Results

Two independent formal runs each used 256 balanced blocks on CPU 1 with ASLR
enabled. Each block
launched the ten fixed ELF images in rotated, mirrored Official/GT order. Four
warm-up launches per image were discarded. The SUPERcop base-plus-deviation
format was decoded before computing the stabilized launch statistic.

## Cumulative Encap frontier

All values are paired `GT - Official` cycles. Positive means GT is slower.

| Checkpoint | Meaning | Run 1 median (95% CI) | Run 2 median (95% CI) |
|---|---|---:|---:|
| A | Decode, hashes, CBD(r) | +94.96 ([+81.77, +105.63]) | +98.40 ([+87.96, +106.40]) |
| B | r Forward, r pack, hash_g | +195.17 ([+179.96, +208.71]) | +183.00 ([+170.25, +194.46]) |
| C | SOTP(m), m Forward | +156.63 ([+145.08, +172.33]) | +154.92 ([+142.17, +174.25]) |
| D | general BaseMul, add(m) | +139.73 ([+126.00, +149.25]) | +137.13 ([+127.50, +151.54]) |
| E | complete exact-production Encap | +190.02 ([+177.33, +207.37]) | +198.96 ([+190.04, +211.17]) |

The byte-exact E images reproduce the motivating production reversal in both
campaigns. The
curve rules out a single hidden arithmetic-kernel debt:

- substantial debt already exists at A;
- the largest worsening is around the B frontier;
- C and D recover part of the gap rather than creating it;
- the final serializer/normal tail around E creates another clear worsening.

The numerical changes between rows locate movement of the cumulative frontier;
they are **not** standalone component costs and must not be added to isolated
kernel timings.

## Geometry control

Keypair runs before the patched Encap in every SUPERcop measurement process and
does not execute any patched bytes. Its paired GT-minus-Official median stayed
between `-279.10` and `-289.02` cycles over A-E in the first campaign. This
narrow spread supports the
frontier shape as an Encap effect rather than a campaign-wide frequency shift.
Decap is not used as a neutral control because A-D intentionally produce a
partial ciphertext before the subsequent Decap measurement.

## Decision

049 finds two coarse production divergence regions, not distributed monotonic
accumulation and not one 170-250-cycle hidden kernel:

1. entry through the r serialization/hash frontier (A/B), and
2. final ciphertext serialization plus the normal caller tail (D/E).

If attribution continues, only these two exact-production regions should be
split once more. N5 and B3 arithmetic remain closed: the C/D frontier shows
that they recover or preserve performance rather than explain the reversal.

# 099 results — current GT Clean versus Official

## Exact implementations

- GT Clean production source: `b2a4bea` (E0V, four-slot 6592-byte Encap
  frame, qualified 611-byte caller reservation, page-aligned RX helper tail).
- Official: frozen NTRU+768 `Additional_Implementation/avx2/NTRU+768`.

The later 097 and 098A commits contain experiments only and do not change the
selected production source.

## Method

- native SUPERcop `crypto_kem/measure.c` harness;
- identical GCC `-O3 -march=native` measurement build policy;
- CPU 1 pinned;
- Turbo disabled, performance governor, 1400 MHz maximum;
- ASLR enabled;
- 16 balanced `O/G/G/O` and `G/O/O/G` blocks;
- 32 fresh launches per implementation;
- 3072 observations per implementation and KEM operation;
- SUPERcop stabilized Q2 is the primary absolute estimate.

## Result

| Operation | Official StQ2 | GT Clean StQ2 | GT - Official | Relative |
|---|---:|---:|---:|---:|
| Keypair | 21,470.99 | 21,203.41 | **-267.58** | **-1.246%** |
| Encap | 28,106.01 | 28,358.48 | **+252.47** | **+0.898%** |
| Decap | 19,303.37 | 19,243.58 | **-59.78** | **-0.310%** |

Paired-block robustness:

| Operation | Paired median delta | Favorable blocks | Bootstrap 95% CI |
|---|---:|---:|---:|
| Keypair | **-283.41** | 16/16 | **[-314.71, -221.69]** |
| Encap | **+266.19** | 1/16 | **[+218.08, +318.38]** |
| Decap | **-48.46** | 14/16 | **[-94.02, -23.42]** |

Negative favors GT Clean.  The direction is statistically clear for all
three operations: GT wins Keypair, loses Encap, and wins Decap by a smaller
margin.

One block contained a common large launch disturbance.  Median-based paired
estimates and their confidence intervals remain unchanged in direction; the
absolute aggregate StQ2 uses all 3072 observations per implementation.

## Interpretation

The current fastest selected GT implementation is still `b2a4bea`.  Neither
097 nor 098A found a reproducible replacement.  It is not a strict replacement
for Official when each standard API operation must win independently, because
Encap remains about 252 cycles (0.90%) slower.

The older experiment 092 reported an E0V natural image that beat Official in
all three operations.  That image also caused large unrelated Keypair/Decap
movement and was not the geometry-preserving production integration.  Its
numbers must not be quoted as the current GT Clean result.

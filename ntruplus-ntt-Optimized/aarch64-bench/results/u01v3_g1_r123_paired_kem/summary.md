# G1R123+S2 Same-Binary Paired KEM PMU

Pi 5 Cortex-A76, core 3 pinned, 61 paired samples, 2000 calls per sample.
A is production; B is G1R123+S2. Negative delta means B is faster or uses fewer events.

## Cycles

| Scope | A p50 | B p50 | delta p10 | delta p50 | delta p90 | MAD | win rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| encap_total | 37718.332 | 37614.476 | -113.653 | -106.243 | -100.240 | 3.769 | 100.000% |
| decap_total | 33315.364 | 33225.502 | -101.116 | -88.853 | -82.876 | 3.893 | 100.000% |
| encap_ntt_r | 2692.752 | 2646.128 | -47.815 | -45.294 | -41.829 | 1.845 | 100.000% |
| encap_ntt_m | 2692.560 | 2645.751 | -50.520 | -45.767 | -43.005 | 1.851 | 100.000% |
| decap_ntt_m1 | 2690.608 | 2645.740 | -45.264 | -44.489 | -42.148 | 0.704 | 100.000% |
| decap_ntt_r1 | 2690.883 | 2645.751 | -47.832 | -44.977 | -42.916 | 1.145 | 100.000% |

## Instructions And CPI

| Scope | A instructions | B instructions | delta | A CPI | B CPI |
|---|---:|---:|---:|---:|---:|
| encap_total | 105607.019 | 105081.019 | -526.000 | 0.357157 | 0.357957 |
| decap_total | 75199.018 | 74673.018 | -526.000 | 0.443029 | 0.444947 |
| encap_ntt_r | 4008.018 | 3745.018 | -263.000 | 0.671841 | 0.706573 |
| encap_ntt_m | 4008.018 | 3745.018 | -263.000 | 0.671793 | 0.706472 |
| decap_ntt_m1 | 4008.018 | 3745.018 | -263.000 | 0.671306 | 0.706469 |
| decap_ntt_r1 | 4008.018 | 3745.018 | -263.000 | 0.671375 | 0.706472 |

## Frontend And Backend Diagnostics

Values are median paired deltas per KEM call.

| Event | encap delta | encap win rate | decap delta | decap win rate |
|---|---:|---:|---:|---:|
| branch_misses | 0.001 | 40.983% | 0.001 | 36.065% |
| l1i_refill | 0.147 | 6.557% | 0.172 | 9.836% |
| l1i_miss | 0.158 | 4.918% | 0.178 | 13.114% |
| stall_frontend | -0.080 | 54.098% | 0.426 | 8.196% |
| stall_backend | -53.314 | 100.000% | -16.203 | 96.721% |

## Layout And Gates

- Binary text size: 171491 bytes.
- Production poly_ntt: 48 bytes, address mod32/mod64 = 16/16.
- Candidate poly_ntt: 14904 bytes, address mod32/mod64 = 0/32.
- Paired correctness: 0 mismatches across 2562 checks.
- Same-binary measurement gate: **pass**.
- Keypair is intentionally not measured or claimed: the optimized triple path does not use generic poly_ntt.

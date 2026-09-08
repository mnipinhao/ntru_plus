# GT864 production component profiler

Six paired processes on Pi5 core 3; 41 samples each. Median of process medians.
Values are aggregate cycles per KEM operation across the listed call count,
with measured empty-profiler overhead subtracted. Inclusive hash costs include
internal SHAKE; the separate shake256 row counts only direct KEM calls.
Instrumentation alters cache/branch/layout state: do not force sums to match
uninstrumented whole-KEM cycles or interpret deltas as exact recoverable cycles.

GT kernel objects are the production objects; only kem.c is recompiled with
profiler aliases. Normal and instrumented outputs matched on valid/tampered
cases, and malformed ciphertext differences were zero. Baseline is the frozen
SUPERCOP 20260627 SHAKE256 snapshot, not verified upstream latest.
The scripts assume the existing Pi5 validation directory and sc[-prof].so links.
No production kernel was edited in this audit.

## keygen

| Component | SC calls | SC cycles | GT calls | GT cycles |
|---|---:|---:|---:|---:|
| poly_tobytes | 3 | 3293.0 | 3 | 5664.5 |
| poly_cbd1 | 2 | 806.0 | 2 | 767.0 |
| poly_ntt | 2 | 7534.0 | 2 | 6814.0 |
| poly_baseinv | 2 | 8352.5 | 2 | 17562.0 |
| poly_basemul | 2 | 4876.0 | 2 | 4358.0 |
| poly_triple | 2 | 484.0 | 2 | 488.0 |
| hash_f | 1 | 13284.0 | 1 | 13285.5 |
| shake256 | 2 | 5505.0 | 2 | 5613.0 |
| randombytes | 2 | 297.0 | 2 | 280.0 |

## encaps

| Component | SC calls | SC cycles | GT calls | GT cycles |
|---|---:|---:|---:|---:|
| poly_tobytes | 2 | 2208.0 | 2 | 3792.0 |
| poly_frombytes | 1 | 759.0 | 1 | 692.0 |
| poly_cbd1 | 1 | 400.5 | 1 | 391.5 |
| poly_sotp_encode | 1 | 415.0 | 1 | 418.5 |
| poly_ntt | 2 | 7535.0 | 2 | 6828.0 |
| poly_basemul_add | 1 | 2911.0 | 1 | 2180.0 |
| hash_f | 1 | 13302.0 | 1 | 13280.5 |
| hash_g | 1 | 14591.0 | 1 | 14532.5 |
| hash_h | 1 | 4082.0 | 1 | 4076.5 |
| randombytes | 1 | 401.0 | 1 | 398.5 |

## decaps

| Component | SC calls | SC cycles | GT calls | GT cycles |
|---|---:|---:|---:|---:|
| poly_tobytes | 2 | 2208.0 | 2 | 3805.0 |
| poly_frombytes | 3 | 2246.0 | 3 | 2050.5 |
| poly_cbd1 | 1 | 396.0 | 1 | 383.5 |
| poly_sotp_decode | 1 | 429.5 | 1 | 403.5 |
| poly_ntt | 2 | 7534.0 | 2 | 6815.5 |
| poly_basemul | 1 | 2440.0 | 2 | 4374.0 |
| poly_sub | 1 | 214.0 | 1 | 214.0 |
| poly_crepmod3 | 1 | 488.0 | 1 | 470.0 |
| hash_g | 1 | 14570.5 | 1 | 14534.5 |
| hash_h | 1 | 4074.0 | 1 | 4077.5 |
| poly_invntt_scale | 1 | 4128.0 | 0 | 0 |
| poly_basemul_scale | 1 | 1755.0 | 0 | 0 |
| poly_invntt | 0 | 0 | 1 | 7718.0 |

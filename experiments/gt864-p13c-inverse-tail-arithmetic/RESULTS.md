# P13-C — tail Inverse16 composite arithmetic (promoted)

## Decision

P13-C is promoted for the single `lazy_itail` call.  Unlike the P13-B main
layout, the tail vector is `[top0 component0..2 | top1 component0..2 | 0 | 0]`
for the final Good-Thomas row.  The candidate uses tail-specific composite
constants, `EXT #6`, and three-lane stores at the exact baseline addresses.

The old terminal map used one packed scale mulmod followed by high and low CRT
mulmods.  The replacement directly computes the low and high scaled CRT rows
with two Algorithm-10 products.  Low columns 0/12 and high columns 0/2/8/10
retain two-instruction `b=1` representative resets.  The exact tail bound is
5028 before these resets and 4303 after, below the unchanged P8 limit 4577.

## Static and Slothy result

| Tail call | P13-B production | P13-C | Delta |
|---|---:|---:|---:|
| Instructions | 669 | 603 | -66 |
| MUL | 65 | 49 | -16 |
| SQRDMULH / MLS | 66 / 66 | 56 / 56 | -10 / -10 |
| LDR | 54 | 86 | +32 |
| MOV / DUP | 33 / 33 | 2 / 2 | -31 / -31 |
| Same-mode expected cycles | 167 | 150 | -17 |

Functional RA is OPTIMAL in 61.118 seconds, uses `v0–v31`, and has no spill.
Both baseline and candidate timing use fixed allocation and the same bounded
Cortex-A76 windows.  This replaces the incomparable historical 633-cycle
estimate produced by the older whole-region performance-estimation mode.

## Correctness and Pi 5 timing

- Tail row 8 closes over all 16 columns and all three repeated components.
- All 8,607 values in the P8 consumer interval are exhausted.
- 544 symbolic cases preserve all 96 addresses and residues modulo 3457.
- Both packages pass `test_kem`, the identical 100-case KAT, identical
  417,216-byte malformed transcript, and 4,096 exact/alias/AAPCS/wipe cases.

| Pi 5 boundary | Baseline | P13-C | Independent median delta |
|---|---:|---:|---:|
| Inverse-to-ternary | 4961.414 | 4890.734 | -70.680 cycles |
| Complete Decaps | 40458.100 | 40378.750 | -79.350 cycles |

Paired medians are -71.586 Inverse-to-ternary cycles, IQR
[-72.469,-70.004] over 366 pairs, and -73.075 Decaps cycles, IQR
[-84.600,-66.350] over 186 pairs.  Both retire exactly 66 fewer instructions
and unchanged branches.  Keygen/Encaps retire identical instructions and their
cycle IQRs include zero.  The Pi 5 ran Cortex-A76 core 3, GCC 14.2, ondemand,
64.2 C, with `throttled=0x0`.

The selected Official tree remains `/home/pi/supercop-20260831`; this gate is a
paired P13-B production/P13-C comparison, not a fresh Official measurement.

## Next

P14 returns to ToBytes.  Its reopen condition remains a smaller common
route+normalization+packing DAG that attacks the measured aggregate gap; P6's
zero-scratch storage-only direction remains rejected.

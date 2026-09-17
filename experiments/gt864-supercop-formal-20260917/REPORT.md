# NTRU+864 formal SUPERCOP benchmark — 2026-09-17

## Identity and method

- Source branch: `neon-864`
- Source base commit: `6204d70d2d6a9f71b193ea1af77e0c2f4ff625f0`
- SUPERCOP tree: `/home/pi/supercop-20260831`
- Host: Raspberry Pi 5, Cortex-A76, Linux 6.18.33+rpt-rpi-2712
- Core: 3
- Frequency reported by SUPERCOP: 2,400,000,000 cycles/second
- Compiler selected for both leaves: GCC 14.2.0, `-march=native -mtune=native -O3`
- Throttle state after validation and measurement: `0x0`
- Command: `taskset -c 3 ./do-part crypto_kem ntruplus864`

The selected Official leaf remained
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`. The GT leaf was
temporarily placed at the same formal implementation path for its independent
run, then the Official leaf was restored. Both runs also evaluated `opt` and
`ref`; `avx2` was skipped on AArch64.

Before measurement, the production package passed its release manifest, 64 KEM
round trips with tampered-ciphertext rejection, ABI checks, 10,368 canonical
decode boundary cases, zeroization checks, KAT comparison, and deterministic
SUPERCOP export. The KAT response SHA-256 was
`0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.

## Results

The table reports the median of the three base cycle values emitted by the
selected SUPERCOP measurement binary.

| Operation | Official cycles | GT cycles | Difference | Change |
|---|---:|---:|---:|---:|
| Keygen | 43,988 | 38,968 | -5,020 | -11.41% |
| Encaps | 46,067 | 36,370 | -9,697 | -21.05% |
| Decaps | 40,761 | 35,439 | -5,322 | -13.06% |

Raw base samples:

| Operation | Official | GT |
|---|---|---|
| Keygen | 44,006 / 43,982 / 43,988 | 38,994 / 38,964 / 38,968 |
| Encaps | 46,093 / 46,067 / 46,063 | 36,412 / 36,370 / 36,350 |
| Decaps | 40,773 / 40,753 / 40,761 | 35,452 / 35,419 / 35,439 |

SUPERCOP object-size records for the selected O3 implementations were
`49,290 / 1,208 / 2,232` bytes for Official and
`90,626 / 1,224 / 2,232` bytes for GT. GT therefore trades a larger text image
for lower cycles across all three complete KEM operations.

## Export-contract corrections found by the formal run

The first formal attempt exposed two packaging defects that package-local tests
could not detect:

1. Exported `kem.c` did not include SUPERCOP's generated `crypto_kem.h`, so the
   public KEM entry points did not receive the implementation namespace.
2. The exported repository `randombytes.h` shadowed SUPERCOP's instrumented
   header, so `measure.c` could not access `randombytes_bytes` and
   `randombytes_calls`.

The deterministic exporter now prepends `crypto_kem.h` to exported `kem.c` and
omits `randombytes.h` from the leaf. These changes affect only SUPERCOP
materialization, not the production KEM algorithm.

## Evidence

- `supercop-official-selection-data.txt`: Official raw database,
  SHA-256 `a9727f69fbaf62b85801f91b786ef3311f5d649cc368fea765ff6112caafb529`
- `supercop-gt-data.txt`: GT raw database,
  SHA-256 `ba5367627389cbd032808c92ef8fd1346eb8d304482ee6ba22ed5895520d6496`
- `supercop-official-selection.log`: Official do-part log,
  SHA-256 `53b1a0fe8c2212efa94095362937972b1f72caa0929620f22ed4a7b73d505700`
- `supercop-gt.log`: GT do-part log,
  SHA-256 `3c342e1d51d3a0d7beba286d04c2e12fcb91fc5276f185953653658d59a169ff`

The installed selected Official snapshot is still not independently verified as
the latest upstream NTRU+ revision; this benchmark compares against the user-
selected SUPERCOP 20260831 tree.

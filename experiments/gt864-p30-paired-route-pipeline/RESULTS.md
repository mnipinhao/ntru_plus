# P30 — adjacent-record direct-ST3 pipeline

## Decision

P30 is **rejected**.  Slothy finds a much shorter modeled schedule, but the
same schedule reproducibly regresses complete Inverse and Decaps on Cortex-A76.
P29 remains rejected evidence and production remains P13-C/P8.

## What was changed

P29 schedules each route record independently:

```text
3 loads -> 3 normalizations -> 3 EXT -> 2 ST3 -> 6-byte skip
```

P30 presents two adjacent records to Slothy together.  The candidate loads all
six source vectors early and overlaps the two independent normalization DAGs,
while retaining the required ordered store cursor:

```text
record A: ST3, ST3, ADD x2,#6
record B: ST3, ST3, ADD x2,#6
```

The first solver run was discarded during post-Slothy review because it renamed
`x2` across post-index `ST3` instructions.  The current target model did not
provide a trustworthy writeback dependency for that transformation.  The final
run reserves every GPR, permits only vector allocation/scheduling, and preserves
the exact pointer sequence.

## Static and Slothy gates

- Local Slothy root: `/Users/chenpinhao/slothy`.
- Interpreter: `/Users/chenpinhao/slothy_and_ra/.venv/bin/python`.
- Target: Cortex-A76; 16 two-record windows; wall time 102.783 seconds.
- Spill/stack accesses: zero.
- P29/P30 instruction count: 873/873.
- Opcode multiset and all 96 scratch load offsets: exact parity.
- Store path: 64 full-vector `ST3.4h`, zero lane `ST3`, exact 32-record pointer sequence.
- Slothy expected route cycles: P29 928, P30 688, modeled delta **-240**.

## Correctness and security

- KEM: 64 round trips plus tampered-ciphertext rejection for production, P29, and P30.
- KAT SHA-256 for all three:
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Malformed transcript SHA-256 for all three:
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.
- 4,096 exact inverse-to-ternary, in-place alias, AAPCS, and full scratch-wipe cases pass.
- Pi object remains 3,492 bytes with 64 `ST3` and no `sp` reference.

## Raspberry Pi 5 PMU

Six alternating processes were pinned to Cortex-A76 CPU 3.  There are 366
paired complete-Inverse samples and 186 paired samples per KEM operation.

### P29 to P30

| Operation | P29 median | P30 median | paired cycle delta | instruction delta | P30 wins |
|---|---:|---:|---:|---:|---:|
| Complete Inverse-to-ternary | 4,970.859 | 4,980.836 | **+10.336** | 0 | 0/366 |
| Decaps | 40,167.900 | 40,172.675 | **+6.700** | 0 | 77/186 |
| Keygen control | 43,104.000 | 43,109.625 | +5.625 | 0 | 75/186 |
| Encaps control | 45,016.000 | 45,018.850 | -4.075 | 0 | 99/186 |

Complete-Inverse IPC falls from `1.3863` to `1.3835`.  The candidate loses all
366 paired Inverse samples, so the failure is not explained by median noise.

### Production to P30

| Operation | Production median | P30 median | paired cycle delta | instruction delta | P30 wins |
|---|---:|---:|---:|---:|---:|
| Complete Inverse-to-ternary | 4,895.047 | 4,968.328 | **+73.414** | -1,452 | 0/366 |
| Decaps | 40,093.225 | 40,180.900 | **+90.775** | -1,452 | 0/186 |
| Keygen control | 43,077.500 | 43,101.125 | +17.000 | 0 | 59/186 |
| Encaps control | 44,965.625 | 44,963.875 | -6.950 | 0 | 109/186 |

## Interpretation and next gate

The current Slothy A76 model substantially overvalues this cross-record
normalization/ST3 overlap.  Larger windows over the same P29 route are no
longer justified.  The next useful experiment must return to the producer DAG:
produce a store-ready subset earlier so normalization and full-vector output do
not wait for all three paired banks.  That is a DAG/layout experiment, not P30-S.

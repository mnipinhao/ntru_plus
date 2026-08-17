# Clean GT32 versus Official Main — formal SUPERcop benchmark (2026-08-16)

## Candidate and correctness

The standard-API GT candidate is
`crypto_kem/ntruplus768/avx2-gt-fastest-clean-native-rcheck`:

- Keypair: P-J1 BaseInv, finalizer-free F0xJ1 BaseMul, SP1 Q24 pack.
- Encap: Q24/M Forward, general B3, H1 high-range Q24 pack.
- Decap: Q24/M, global inverse, native-domain final verification.

The fresh export passes all 100 canonical KAT vectors byte-exactly.  Request
SHA-256 is `36c27b6089b8910733a01fea1136469769b3ca3c35f2b375cfcc592f2112cfaa`;
response SHA-256 is
`22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.

## Fixed benchmark ELFs

Both implementations were freshly compiled once with GCC 15.2.0 and the same
SUPERcop flags: `-O3 -march=native -mtune=native -fwrapv -fPIC -fPIE
-ffunction-sections -fdata-sections -Wl,--gc-sections`.

| implementation | ELF SHA-256 | `.text` | `.rodata` |
|---|---|---:|---:|
| Official `avx2` | `c7c1d482a0357fba85d14060196dccd08a616bbf1404ae5a72b24e86df91b217` | 42,007 B | 5,384 B |
| Clean GT32 | `471d94af9c18298042db857e01d3c210e7a983f9e565badebe9f34d73fe8fc66` | 66,519 B | 56,840 B |

Both are PIE (`ET_DYN`).  The cycle backend is SUPERcop
`default-perfevent`, i.e. `PERF_COUNT_HW_CPU_CYCLES`.  Every process is pinned
to CPU 1.  Each mode uses 16 balanced blocks and 64 fresh process launches;
odd blocks are Official–GT–GT–Official and even blocks reverse the order.
Each launch contributes 96 native observations per KEM operation.  The unit
of analysis is the launch-level stabilized Q2 and paired block delta, with a
100,000-resample bootstrap interval for the median.

## Primary: production-like PIE with ASLR enabled

Negative delta means GT is faster.

| operation | Official cycles | GT cycles | GT − Official | percent | favorable blocks | bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| Keypair | 21,502.48 | 21,136.48 | **−322.27** | **−1.499%** | 16/16 | [−381.60, −287.74] |
| Encap | 28,066.95 | 28,177.18 | **+102.27** | **+0.364%** | 3/16 | [+22.96, +175.29] |
| Decap | 19,366.85 | 19,160.04 | **−241.94** | **−1.249%** | 16/16 | [−283.29, −127.35] |

ABBA/BAAB medians agree in sign:

- Keypair: −347.46 / −292.53 cycles.
- Encap: +120.63 / +88.24 cycles.
- Decap: −249.95 / −218.77 cycles.

## Attribution control: the same PIE ELFs with ASLR disabled

The complete runner was invoked through `setarch x86_64 -R`; no system-wide
setting was changed.

| operation | Official cycles | GT cycles | GT − Official | percent | favorable blocks | bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| Keypair | 21,476.33 | 21,111.05 | **−365.29** | **−1.701%** | 15/16 | [−381.24, −310.04] |
| Encap | 28,020.42 | 28,143.39 | **+104.31** | **+0.372%** | 2/16 | [+83.75, +141.92] |
| Decap | 19,334.64 | 19,089.08 | **−250.51** | **−1.296%** | 16/16 | [−285.65, −217.96] |

ABBA/BAAB medians also agree in sign:

- Keypair: −382.13 / −304.50 cycles.
- Encap: +87.80 / +120.36 cycles.
- Decap: −233.75 / −260.51 cycles.

## Decision

ASLR changes the exact deltas but does not change any operation's direction.
Clean GT32 robustly beats Official for Keypair and Decap and robustly loses
for Encap.  It is therefore not a strict three-operation replacement.  The
fastest per-operation selector on this host remains:

```text
Keypair -> Clean GT32
Encap   -> Official Main
Decap   -> Clean GT32
```

For the artificial workload containing one Keypair, one Encap, and one Decap
with equal weight, the primary medians sum to approximately 68,473.70 cycles
for GT and 68,936.28 for Official, a 462.58-cycle (0.67%) aggregate GT win.
Real applications must weight operations according to their own call mix.

Artifacts:

- `results/tile4-supercop-gt-vs-official-aslr-on-20260816.json`
- `results/tile4-supercop-gt-vs-official-aslr-off-20260816.json`
- `results/tile4-supercop-gt-vs-official-aslr-on-raw-20260816/`
- `results/tile4-supercop-gt-vs-official-aslr-off-raw-20260816/`
- `results/kat-supercop-fastest-clean-native-rcheck-20260816/`

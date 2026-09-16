# D1-P3B11 evidence

Status: **isolated hard gate passed; keep experimental until full callers
close.**

## Exact contract and correctness

- Parameter set: NTRU+864, AArch64 Neon lane.
- Input: exactly 1296 serialized bytes, including arbitrary noncanonical
  twelve-bit values.
- Output: 864 signed-halfword slots in the current GT FR0 physical layout.
- Composed map SHA-256:
  `087b7193886e9f3e33ac457452642d64ae70ec780a0961d10036c8e5530da270`.
- The two 432-coefficient tops have identical relative maps.
- The generated input-once schedule has peak fourteen live partial outputs;
  this is a witnessed upper bound, not a minimum proof.
- Local: 256 complete arbitrary-byte cases and both guarded buffer edges pass.
- Pi 5: 128 complete arbitrary-byte cases pass for C1 and input-once.
- Every value in `[0,4095]` is preserved; no canonicalization was introduced.

## Target object audit

Host GCC 14.2.0 with `-O3 -march=armv8-a+simd` emits an 851-instruction
top-local core.  It uses all caller-saved vector registers `v0-v7,v16-v31`
and has no stack reference or coefficient spill.  Its main static operations
per top are:

| operation | count |
| --- | ---: |
| lane `mov` and other `mov` | 474 |
| serialized-group `ld1` lane-32 tail inserts | 54 |
| `tbl` / `ushl` / `bic` | 54 each |
| address `add` | 54 |
| q-vector output `stp` / `str` | 18 / 18 |

The 36 output store instructions cover all 54 output q-vectors because each
`stp q` writes two vectors.  Input loads are exact 8-byte plus 4-byte accesses;
the guarded last group passes.

## Paired Cortex-A76 PMU

The Pi 5 used core 3, 400 calls/sample, 41 samples per order, both execution
orders, and three complete repetitions.  Medians below include all 246 samples
per variant.  Every thermal check reported `throttled=0x0`.

| variant | cycles | instructions | branches |
| --- | ---: | ---: | ---: |
| P3B4 C1 control | 1181.090 | 3173.045 | 30.010 |
| P3B11 input-once | **935.717** | **1715.045** | **6.010** |
| candidate - control | **-245.373 (-20.78%)** | **-1458** | **-24** |

All three individual repetitions agree: candidate medians are
935.707/935.719/935.717 cycles versus 1181.110/1181.219/1180.910 for C1.

Using the existing P3B4 component ledger, the modeled one-call FromBytes gap
to Official falls from +386.597 to approximately +141.224 cycles.  This is a
cross-run model; the next gate must measure the real Encaps and Decaps callers.

## Decision

The hypothesis passes.  Input-once decode is the new isolated FromBytes
champion.  It does not modify Production and is not yet a full-KEM performance
claim.  The required next gate links only this FromBytes substitution against
the frozen P3B4 byte-boundary/full-KEM baseline; ToBytes remains unchanged so
the caller saving is attributable.

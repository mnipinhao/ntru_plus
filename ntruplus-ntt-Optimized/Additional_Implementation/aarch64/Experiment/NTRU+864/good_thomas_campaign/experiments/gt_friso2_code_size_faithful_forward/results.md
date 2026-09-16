# Results

Status: **code-size-faithful integration passed; FR-ISO2 operation route
rejected on measured Forward cost.**

## Structural and correctness gates

- The 345-instruction NTT16 producer has one static copy and four dynamic
  invocations.  Its normalized instruction SHA-256 is
  `a4d9e3a649b70c057281914b08c90060fb39dfdb7e67a93561781306d9c67c33`.
- The four inline consumers remain exactly 309, 309, 279, and 279
  instructions.  They contain zero boundary copies, spills, stack accesses, or
  coefficient-memory operations.
- Pass-2 has the same 108 final vector stores and the full Forward retains the
  two-load/two-store coefficient contract.
- CF5-A to CF5-B static executable instructions fall from 3283 to 2245.  The
  real Pi 5 object falls from 18,336 to 14,192 text bytes: **4,144 bytes saved**
  after alignment.
- Pi 5 oracle: 1126 cases, 972,864 non-alias and 972,864 exact-alias
  coefficient comparisons; zero mismatch.
- AAPCS64 outer-wrapper `d8-d15` preservation test passes.

## Five-way paired Cortex-A76 PMU

All values are overall p50 from three repetitions, both forward and reverse
orders, 61 samples/order, and 20,000 calls/sample on core 3.  The Pi remained
`throttled=0x0`.

| Forward | cycles | kernel instructions |
| --- | ---: | ---: |
| Official | 4395.892 | 4028 |
| M5R-D FR0 | 4230.940 | 4446 |
| CF0 FR-ISO2 | 4628.399 | 4738 |
| CF5-B FR-ISO2 | 4582.946 | 4726 |

Paired p50 deltas for CF5-B:

- versus CF0: **-45.807 cycles**, confirming the fused scaled-NTT9 path is a
  real improvement over explicit output scaling;
- versus Official: **+186.508 cycles**;
- versus retained M5R-D: **+351.936 cycles**.

The PMU observes the exact expected 4726 dynamic instructions, so neither an
old target object nor an accidental CF5-A binary was measured.  Source hashes
are recorded in the ignored reproducible `build/pi5-formal/summary.json`.

## Whole-operation early-rejection ledger

The measured two-constant FR-ISO2 BaseMul saves 334.194 cycles.  Two CF5-B
Forwards cost `2 * 351.936 = 703.873` cycles over the retained FR0 route.  The
pipeline is therefore already **369.679 cycles slower before any Inverse
correction**:

`2 * DeltaForward + DeltaBaseMul = 703.873 - 334.194 = +369.679 cycles`.

An Inverse implementation cannot rescue the gate unless it is itself at least
369.679 cycles faster than the retained FR0 Inverse.  The known direct FR-ISO2
Inverse instead adds correction work, so integrating it would only confirm a
strictly worse result.  Full KEM and SUPERCOP are consequently not run.

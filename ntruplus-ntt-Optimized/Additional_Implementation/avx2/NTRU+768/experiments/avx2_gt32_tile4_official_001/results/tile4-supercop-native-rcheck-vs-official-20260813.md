# Promoted native-rcheck GT32 versus Official Main (2026-08-13)

## Method

- Official Main implementation: `crypto_kem/ntruplus768/avx2`.
- GT implementation: `crypto_kem/ntruplus768/avx2-gt-native-rcheck-promoted`.
- Both `measure` ELFs were compiled once with the same forced SUPERcop
  `-O3`, function/data-section, and linker-GC flags.
- Cycle backend: SUPERcop `default-perfevent`, using
  `PERF_COUNT_HW_CPU_CYCLES` rather than TSC.
- CPU affinity: CPU 1.  CPU 2 is its SMT sibling and was not offlined.
- 16 balanced paired blocks and 64 independent process launches.
- Odd blocks use Official--GT--GT--Official; even blocks reverse the order.
- Every launch contributes SUPERcop's 96 observations per KEM operation.
- The statistical unit is the launch-level stabilized Q2, paired inside each
  block.  Confidence intervals use 100,000 bootstrap samples of the block
  median.

The fixed ELF SHA-256 hashes were checked again after all launches:

- Official: `c7c1d482a0357fba85d14060196dccd08a616bbf1404ae5a72b24e86df91b217`
- GT: `e58a20238f5de77502e01cbcae4887624a5ea1cc08676e7427ed59cdd2e76cb8`

The promoted export is deliberately the current full multi-variant image, not
the separately pruned CleanGT image.  Its `.text`/`.rodata` sizes are
128983/57544 bytes versus Official's 42007/5384 bytes, so this measurement
includes the promoted export's whole-image delivery cost.

## Results

Negative delta means GT is faster.

| Operation | Official Q2 | GT Q2 | GT - Official | Percent | GT wins | 95% bootstrap CI | ABBA / BAAB |
|---|---:|---:|---:|---:|---:|---:|---:|
| Keypair | 21491.01 | 21637.89 | **+151.08 cycles** | **+0.703%** | 0/16 | [+121.48, +224.19] | +151.08 / +166.58 |
| Encap | 28058.90 | 28239.51 | **+181.47 cycles** | **+0.647%** | 0/16 | [+147.93, +266.92] | +166.97 / +244.56 |
| Decap | 19331.59 | 19165.94 | **-159.71 cycles** | **-0.826%** | 16/16 | [-196.06, -129.00] | -158.11 / -159.71 |

The order families agree in sign for all three operations.  Decap's observed
159.7-cycle whole-operation saving also closely matches the preceding
same-ELF native-rcheck gate's normal-placement 165.8-cycle saving, so the
structural deletion survives the Official comparison with little composition
loss.

## Decision

- Native-domain final verification is confirmed at the complete SUPERcop
  Decap boundary: promoted GT Decap beats Official by about 160 core cycles
  (0.83%).
- The promoted export's current Keypair and Encap paths lose by about 151 and
  181 core cycles respectively.  They are not promoted over Official.
- The complete all-GT backend still does not beat Official on all three
  operations, so Official remains the public/default complete backend.
- A compile-time hybrid using Official Keypair/Encap and promoted GT Decap is
  now supported by stable formal benchmark evidence.

Artifacts:

- `results/tile4-supercop-native-rcheck-vs-official-20260813.json`
- `results/tile4-supercop-native-rcheck-vs-official-raw-20260813/`
- `results/supercop-native-rcheck-official-measure-20260813`
- `results/supercop-native-rcheck-promoted-measure-20260813`

# P17 result — selected-Official profiler checkpoint

P17 measures GT864 production revision
`912066b3529359a7b8752e52b9dae1a366db8a3c` against the user-selected
SUPERCOP tree at
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`. This fixed target
has not been independently proved to be the latest upstream revision.

## Provenance and correctness

- Official tree SHA-256: `40a284439eb5fe8dfef77f1a995ebc8dd16182835048d64e959fbcb6e3df0b59`.
- GT tree SHA-256: `4617302e0f64b41ccfc3bd1b49f414c3ec16018016a95745d495de6cb5f1170b`.
- GT KAT SHA-256: `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Fresh GT build, KEM test and KAT pass.
- Six cross-implementation processes each pass 100 exact transcripts and 100
  tampered-ciphertext rejections.
- Twelve instrumentation-equivalence processes pass.
- Pi 5 remained unthrottled (`0x0`); temperature was 58.2 to 61.5 C.

## Clean full-KEM result

Each cell is the median of 252 clean observations on Cortex-A76 CPU 3. A
negative delta means GT is faster or retires less work.

| Operation | Official cycles | GT cycles | GT cycle delta | Delta % | Instruction delta | Branch delta |
|---|---:|---:|---:|---:|---:|---:|
| Keygen | 44,309.500 | 43,582.250 | **-727.250** | **-1.641%** | +6,799.0 | +379.0 |
| Encaps | 46,425.975 | 45,277.525 | **-1,148.450** | **-2.474%** | +3,939.0 | -59.0 |
| Decaps | 40,759.325 | 40,324.775 | **-434.550** | **-1.066%** | +8,686.0 | +38.5 |

Current GT therefore wins all three complete operations against this fixed
Official target. It does so despite retiring more instructions, so instruction
count alone is not a promotion criterion.

## Same-boundary cycle profile

Call counts are already included in each operation-level value. `ToBytes` is
Official Full versus GT Full plus Small. The Decaps inverse boundary is
Official Inverse plus Crepmod3 versus GT Inverse-to-ternary.

| Operation / logical boundary | Calls | Official cycles | GT cycles | GT delta |
|---|---:|---:|---:|---:|
| Keygen / Forward | 2 | 7,534.000 | 6,787.500 | -746.500 |
| Keygen / BaseMul R0 | 2 | 4,881.000 | 4,358.000 | -523.000 |
| Keygen / BaseInv | 2 | 8,361.750 | 8,321.375 | -40.375 |
| Keygen / ToBytes | 3 | 3,327.000 | 3,825.000 | **+498.000** |
| Encaps / Forward | 2 | 7,535.525 | 6,785.000 | -750.525 |
| Encaps / BaseMulAdd | 1 | 2,900.075 | 2,170.000 | -730.075 |
| Encaps / FromBytes checked | 1 | 751.000 | 725.050 | -25.950 |
| Encaps / ToBytes | 2 | 2,218.000 | 2,637.000 | **+419.000** |
| Decaps / Forward | 2 | 7,533.675 | 6,789.125 | -744.550 |
| Decaps / BaseMul R0 | 1 | 2,439.000 | 2,174.000 | -265.000 |
| Decaps / BaseMul Rinv | 1 | 1,762.500 | 1,757.000 | -5.500 |
| Decaps / FromBytes checked | 3 | 2,279.925 | 2,165.600 | -114.325 |
| Decaps / Inverse to ternary | 1 | 4,619.875 | 4,909.600 | **+289.725** |
| Decaps / ToBytes | 2 | 2,214.000 | 2,639.475 | **+425.475** |

Medians from separately instrumented call sites are not additive with the
clean full-KEM median. They localize boundaries rather than reconstructing the
total cycle delta.

## Retired-work localization

- Keygen ToBytes retires 8,062 GT instructions versus 3,834 Official
  (`+4,228`); BaseInv is `+1,784`, and Forward is `+1,110`.
- Encaps ToBytes is `+2,886`, Forward `+1,110`, and FromBytes `+234`.
- Decaps Inverse-to-ternary is 8,345 instructions versus 4,605 for Official
  Inverse plus Crepmod3 (`+3,740`); ToBytes is `+2,886`, Forward `+1,110`,
  BaseMul Rinv `+770`, and FromBytes `+701`.

P16 improved Full ToBytes by scheduling without reducing those instruction
counts. P17 therefore does not justify another scheduling-only pass over the
same DAG.

## Decision and maintained work queue

1. **P18 — ToBytes joint DAG search (next).** Search a smaller FR0-coordinate
   to wire-byte network in which canonicalization, 12-bit packing and routing
   consume one another early. Full and Small remain separate DAGs. A candidate
   must reduce real routing/packing work relative to P5/P16 before Slothy or Pi
   timing; removing scratch by itself is not a success condition.
2. **Inverse-to-ternary arithmetic remains second.** Its cycle deficit is now
   about 290 cycles, although its retired-work deficit is the largest Decaps
   component. Reopen only with a new arithmetic/reduction hypothesis, not a
   terminal-routing-only rewrite already rejected by P11.
3. **BaseInv remains monitored, not immediate.** It is nearly cycle-neutral in
   this profile despite `+1,784` instructions. Fused-wide numerator and finish
   normalization remain known structural work, but are lower priority than the
   common ToBytes deficit.
4. **Forward remains retained.** It wins roughly 745--751 cycles in every
   two-call path. Its `+1,110` retired instructions are not the current cycle
   bottleneck.
5. **BaseMul Rinv and FromBytes remain monitored.** Their instruction gaps do
   not currently translate into positive cycle gaps; do not optimize them
   ahead of measured positive-cycle boundaries without a new hypothesis.

Production is unchanged by P17.

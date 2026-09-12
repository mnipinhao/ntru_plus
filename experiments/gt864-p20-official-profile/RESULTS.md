# P20 result — post-P19 selected-Official profiler checkpoint

P20 measures GT864 production revision
`126fb028fe9dfe640f37a391e9acb967896be234` against the user-selected
SUPERCOP tree at
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`. This fixed target
has not been independently proved to be the latest upstream revision.

## Provenance and correctness

- Official tree SHA-256: `40a284439eb5fe8dfef77f1a995ebc8dd16182835048d64e959fbcb6e3df0b59`.
- GT tree SHA-256: `657e6f12fa5075a4c391f1043826a2d8d71b2dcbd35663857f75fc87a11aa0ab`.
- GT KAT SHA-256: `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Fresh GT build, KEM test, and KAT pass.
- Six cross-implementation processes each pass 100 exact transcripts and 100
  tampered-ciphertext rejections.
- Twelve instrumentation-equivalence processes pass.
- The production profile links `gt864_p18_tobytes_full.o` and
  `gt864_p18_tobytes_small.o`.
- Pi 5 stayed unthrottled (`0x0`); temperature was 58.7 to 63.1 C.

## Clean full-KEM result

Each cell is the median of 252 clean observations on Cortex-A76 CPU 3. A
negative delta means GT is faster or retires less work.

| Operation | Official cycles | GT cycles | GT cycle delta | Delta % | Instruction delta | Branch delta |
|---|---:|---:|---:|---:|---:|---:|
| Keygen | 44,321.750 | 43,276.875 | **-1,044.875** | **-2.357%** | +5,372.0 | +374.0 |
| Encaps | 46,435.125 | 45,084.175 | **-1,350.950** | **-2.909%** | +2,997.0 | -61.5 |
| Decaps | 40,764.700 | 40,134.675 | **-630.025** | **-1.546%** | +7,744.0 | +36.0 |

GT therefore beats this fixed selected Official target in all three complete
operations. It still retires more instructions, especially in Decaps; cycle
measurements, rather than instruction count alone, remain the promotion gate.

## Same-boundary cycle and retired-work profile

Call counts are included in each operation-level value. `ToBytes aggregate`
compares all Official full calls with the corresponding GT full and small
calls. The Decaps inverse row compares Official `Inverse + Crepmod3` with the
fused GT `Inverse_to_ternary` boundary.

| Operation / logical boundary | Official cycles | GT cycles | GT cycle delta | Instruction delta | Branch delta |
|---|---:|---:|---:|---:|---:|
| Keygen / Forward (2 calls) | 7,533.000 | 6,786.000 | -747.000 | +1,110 | +22 |
| Keygen / BaseInv (2 calls) | 8,366.750 | 8,304.750 | -62.000 | +1,784 | +394 |
| Keygen / BaseMul R0 (2 calls) | 4,880.000 | 4,349.000 | -531.000 | -356 | +2 |
| Keygen / ToBytes aggregate (3 calls) | 3,342.000 | 3,495.250 | **+153.250** | +2,809 | -39 |
| Encaps / Forward (2 calls) | 7,537.000 | 6,787.000 | -750.000 | +1,110 | +22 |
| Encaps / BaseMulAdd | 2,900.000 | 2,170.000 | -730.000 | -100 | +1 |
| Encaps / FromBytes checked | 752.000 | 725.050 | -26.950 | +234 | -13 |
| Encaps / ToBytes aggregate (2 calls) | 2,220.000 | 2,457.150 | **+237.150** | +1,946 | -26 |
| Decaps / Forward (2 calls) | 7,533.050 | 6,789.950 | -743.100 | +1,110 | +22 |
| Decaps / BaseMul R0 | 2,439.000 | 2,174.000 | -265.000 | -178 | +1 |
| Decaps / BaseMul Rinv | 1,761.200 | 1,754.000 | -7.200 | +770 | +73 |
| Decaps / FromBytes checked (3 calls) | 2,266.050 | 2,165.450 | -100.600 | +701 | -39 |
| Decaps / Inverse to ternary | 4,620.550 | 4,904.750 | **+284.200** | +3,740 | +57 |
| Decaps / ToBytes aggregate (2 calls) | 2,215.000 | 2,458.125 | **+243.125** | +1,946 | -26 |

Medians from separately instrumented call sites are not additive with the
clean full-KEM median. They localize boundaries; they do not reconstruct the
whole-operation total.

## P19 effect and decision

Relative to the P17 selected-Official checkpoint, the positive ToBytes gap is
now much smaller: Keygen `+498.000 -> +153.250`, Encaps
`+419.000 -> +237.150`, and Decaps `+425.475 -> +243.125` cycles. The two
checkpoints are independent profiler runs, so these are diagnostic comparisons,
not paired P19 speedup claims; the paired promotion result remains P19's
authoritative evidence.

The fresh ranking is:

1. **P21 — current-production Inverse-to-ternary interior decomposition.**
   Re-profile the now-promoted P13-B/P13-C/P8 path as inverse9 aggregate, six
   main I16 calls, tail I16, route/materialization, direct ternary conversion,
   and wrapper/wipe residual. Select a new arithmetic or routing DAG only from
   the largest measured interior stage. Do not repeat P11's rejected
   terminal-only fusion.
2. **ToBytes remains second.** It is common to all KEM operations and still
   costs 153--243 cycles more at aggregate same boundaries, but P18 recovered
   most of the old cycle deficit. Reopen only with a smaller route/pack DAG,
   not another instruction-neutral schedule.
3. **BaseInv, Forward, and R0 BaseMul stay retained.** All are cycle winners at
   their current matched boundaries. BaseInv's instruction/branch excess and
   Rinv's retired-work excess remain monitored but do not outrank a positive
   cycle gap.
4. **Mechanical ELF metadata cleanup remains separate.** Adding `.type/.size`
   to the P18 assembly is useful packaging work but is not a performance gate.

P20 changes no production kernel.

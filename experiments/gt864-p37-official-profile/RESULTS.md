# P37 result — P35 selected-Official profiler

P37 measures exact GT864 P35 production revision
`88fb877ea5f22cdcd4c05ea6926e95e6ce0142eb` against the user-selected
SUPERCOP implementation at
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`. This fixed
SUPERCOP target is not independently verified as latest upstream.

## Provenance and correctness

- GT was extracted by `git archive`; unrelated working-tree changes could not
  enter the measured library.
- Official tree SHA-256:
  `40a284439eb5fe8dfef77f1a995ebc8dd16182835048d64e959fbcb6e3df0b59`.
- GT tree SHA-256:
  `ca0bf5b0daaf30e479ff204b372415eba98cce36f3099816e0015b7ec9ddf8b0`.
- Fresh GT manifest/build/KEM/KAT passed. KAT SHA-256:
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Six processes each passed 100 exact cross-implementation transcripts and
  100 tampered-ciphertext rejections.
- Twelve cycle-profiler and 24 event-profiler instrumentation-equivalence
  processes passed.
- Pi 5 CPU 3, GCC 14.2.0, ondemand governor; unthrottled (`0x0`) from
  57.6 to 62.6 C. No SUPERCOP `do-part` process was active.

## Clean full-KEM PMU

Each value is the median of 252 clean observations. Negative delta means GT is
faster or retires less work. IPC is retired instructions divided by cycles.

| Operation | Official cycles | GT cycles | Cycle delta | Delta % | Instruction delta | Branch delta | Official IPC | GT IPC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Keygen | 44313.250 | 43155.000 | **-1158.250** | -2.614% | +4790.0 | +374.0 | 2.016 | 2.181 |
| Encaps | 46443.750 | 45011.675 | **-1432.075** | -3.083% | +2607.0 | -62.0 | 2.602 | 2.742 |
| Decaps | 40771.025 | 39921.700 | **-849.325** | -2.083% | +7282.0 | +36.0 | 2.125 | 2.353 |

P35 therefore beats this selected Official target in all three complete KEM
operations. Relative to P25's same profiler, the Decaps advantage grows from
694.525 to 849.325 cycles; the other two margins are stable within roughly ten
cycles. This is consistent with P35 being Decaps-only.

## Complete matched component profile

Call counts are already aggregated per complete operation. Official
`Inverse + Crepmod3` is matched against GT's fused `Inverse_to_ternary`.
Official Full ToBytes calls are matched against GT's actual Full/Small call
mixture. Instrumented component medians are diagnostic and are not added to
reconstruct the clean full-KEM median.

| Operation / boundary | Official cycles | GT cycles | Cycle delta | Instruction delta | Branch delta |
|---|---:|---:|---:|---:|---:|
| Keygen / Forward x2 | 7533.000 | 6798.750 | -734.250 | +1110 | +22 |
| Keygen / BaseInv x2 | 8366.125 | 8318.750 | -47.375 | +1784 | +396 |
| Keygen / BaseMul R0 x2 | 4880.000 | 4349.000 | -531.000 | -356 | +2 |
| Keygen / CBD x2 | 815.000 | 763.750 | -51.250 | +20 | +4 |
| Keygen / Triple x2 | 488.000 | 470.375 | -17.625 | +24 | +4 |
| Keygen / SHAKE sampling x2 | 5526.125 | 5525.250 | -0.875 | +4 | -10 |
| Keygen / ToBytes aggregate | 3327.000 | 3375.000 | **+48.000** | +2227 | -39 |
| Encaps / Forward x2 | 7535.000 | 6825.000 | -710.000 | +1110 | +22 |
| Encaps / BaseMulAdd | 2900.000 | 2173.175 | -726.825 | -100 | +1 |
| Encaps / FromBytes checked | 751.500 | 723.925 | -27.575 | +234 | -13 |
| Encaps / ToBytes aggregate | 2216.000 | 2396.000 | **+180.000** | +1558 | -26 |
| Decaps / Forward x2 | 7533.000 | 6796.000 | -737.000 | +1110 | +22 |
| Decaps / BaseMul R0 | 2439.000 | 2174.000 | -265.000 | -178 | +1 |
| Decaps / BaseMul Rinv | 1761.000 | 1760.000 | -1.000 | +770 | +73 |
| Decaps / FromBytes checked x3 | 2261.000 | 2178.450 | -82.550 | +701 | -39 |
| Decaps / Inverse+Crepmod3 -> fused ternary | 4619.000 | 4766.075 | **+147.075** | +3666 | +57 |
| Decaps / ToBytes aggregate | 2214.000 | 2393.000 | **+179.000** | +1558 | -26 |

The remaining smaller common boundaries all favor GT: CBD by 24--28 cycles,
RNG by 31--41, SOTP by 20--27, cleanup by 63--83, and the shared SHAKE hashes
by 26--97 cycles at their operation-level call counts. Full machine-readable
distributions remain in `results.json` and `event-results.json`.

## Full versus Small ToBytes

The aggregate ToBytes row hides the useful signal. Every KEM operation makes
one GT Full call. Keygen additionally makes two Small calls; Encaps and Decaps
make one Small call. The selected Official uses the same Full serializer for
all corresponding calls.

| Operation | Official cycles/call | GT Full cycles | Full gap | GT Small cycles/call | Small delta vs Official/call |
|---|---:|---:|---:|---:|---:|
| Keygen | 1109.000 | 1410.000 | **+301.000** | 982.500 | -126.500 |
| Encaps | 1108.000 | 1413.000 | **+305.000** | 983.000 | -125.000 |
| Decaps | 1107.000 | 1411.000 | **+304.000** | 982.000 | -125.000 |

Small ToBytes is already faster than the Official per-call boundary. The
entire residual ToBytes deficit comes from Full. Full differs from Small by
108 `SQRDMULH+MLS` normalization pairs (216 vector instructions per complete
call) plus one constant setup, because every Full caller currently accepts the
wider direct-Forward representatives.

## Decision: P38

P38 is a direct-Forward terminal-representative plus Full-ToBytes
normalization co-DAG. It freezes Small ToBytes and P35 Inverse. The three Full
call sites are all serializations of direct Forward outputs: Keygen `f`,
Encaps `r`, and Decaps re-encryption `f`. This gives one common producer
contract to exploit and about 301--305 cycles of measured headroom in every
complete KEM operation.

P38 first computes exact per-output Forward bounds and quotient classes. It
then searches whether final Forward reductions/representative choices and the
Full route-normalize-pack consumers can share or eliminate normalization work.
Merely moving the same 216 instructions from ToBytes into Forward does not
pass. The gate requires:

1. exact equality of all wire bytes and unchanged FR0 values seen by BaseInv,
   BaseMul and BaseMulAdd, or a complete proof and cost ledger for any ABI
   change;
2. no added coefficient memory pass, scratch, input load, spill, or
   secret-dependent control/addressing;
3. removal of at least 108 of the 216 Full-only vector normalization
   instructions before scheduling;
4. a same-boundary Full improvement target of at least 150 cycles/call and no
   Small regression;
5. only after the static/range gate, bounded local Slothy and Pi 5 full-KEM
   confirmation.

The Decaps fused-Inverse gap is now second priority. Its 147-cycle measured
deficit is smaller, and P27--P33 already rejected several large routing
rewrites. BaseInv and BaseMul Rinv remain instruction-count cleanup candidates,
but they are not positive cycle gaps in this run.

# Post-P42 GT864 production versus selected Official

This measurement-only checkpoint compares exact GT production revision
`34d2c7584e52a78feb9f1ec89a53c8c769e35762` with the selected SUPERCOP tree at
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`.

The selected source uses SHAKE256. Its required `kem.c`, `symmetric.c` and
`api.h` hashes match `bench/aarch64/gt-production/OFFICIAL-BASELINE.json`. It
has not been independently verified as the latest upstream revision.

## Provenance and correctness

- Official tree hash: `40a284439eb5fe8dfef77f1a995ebc8dd16182835048d64e959fbcb6e3df0b59`.
- GT archive tree hash: `725a6eaf8b4728f8337880bd73e6bc223d0c343fc948f05cb45a91fb9f9ec1f1`.
- Fresh GT manifest, build, KEM test and KAT passed. KAT SHA-256 remains
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Six processes each passed 100 exact cross-implementation transcripts and 100
  tampered-ciphertext rejections.
- Twelve cycle-profiler and 24 event-profiler instrumentation-equivalence
  processes passed.
- Pi 5 CPU 3, GCC 14.2.0, ondemand governor, 252 clean observations per
  operation and implementation. Temperature was 58.2--62.6 C and
  `throttled=0x0` throughout.

The first archive attempt at `151ed540` was rejected before compilation because
the P42 roadmap edit had not refreshed the production manifest. Commit
`34d2c758` repairs only that manifest entry; no executable source changed.

## Clean full-KEM PMU

Negative delta means GT is faster. IPC is retired instructions divided by
cycles.

| Operation | Official cycles | GT cycles | Delta | Delta % | Instruction delta | Branch delta | Official IPC | GT IPC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Keygen | 44319.250 | 43148.750 | **-1170.500** | -2.641% | +4790 | +374 | 2.016 | 2.181 |
| Encaps | 46423.725 | 45012.650 | **-1411.075** | -3.040% | +2611 | -61 | 2.603 | 2.742 |
| Decaps | 40771.325 | 39919.225 | **-852.100** | -2.090% | +7274 | +34 | 2.125 | 2.353 |

GT therefore wins all three complete KEM operations despite retiring more
instructions. Its higher IPC plus the faster transform/multiplication kernels
more than compensate for the remaining instruction-count excess.

## Matched component profiler

Call counts are already aggregated per complete operation. The table lists the
large or decision-relevant boundaries; instrumented medians are diagnostic and
must not be summed to reconstruct the clean full-KEM median.

| Operation / boundary | Official cycles | GT cycles | Delta | Instruction delta | Branch delta |
|---|---:|---:|---:|---:|---:|
| Keygen / Forward x2 | 7533.000 | 6805.000 | **-728.000** | +1110 | +22 |
| Keygen / BaseInv x2 | 8360.750 | 8324.250 | -36.500 | +1800 | +394 |
| Keygen / BaseMul R0 x2 | 4880.000 | 4350.000 | **-530.000** | -356 | +2 |
| Keygen / ToBytes aggregate | 3327.000 | 3379.250 | **+52.250** | +2227 | -39 |
| Encaps / Forward x2 | 7535.000 | 6818.000 | **-717.000** | +1110 | +22 |
| Encaps / BaseMulAdd | 2900.000 | 2170.000 | **-730.000** | -100 | +1 |
| Encaps / FromBytes | 751.000 | 725.400 | -25.600 | +234 | -13 |
| Encaps / ToBytes aggregate | 2216.000 | 2397.950 | **+181.950** | +1558 | -26 |
| Decaps / Forward x2 | 7533.775 | 6801.850 | **-731.925** | +1110 | +22 |
| Decaps / BaseMul R0 | 2439.000 | 2174.000 | **-265.000** | -178 | +1 |
| Decaps / BaseMul Rinv | 1761.475 | 1760.000 | -1.475 | +770 | +73 |
| Decaps / FromBytes x3 | 2276.225 | 2167.800 | **-108.425** | +701 | -39 |
| Decaps / Inverse+Crepmod3 -> fused ternary | 4620.000 | 4762.000 | **+142.000** | +3666 | +57 |
| Decaps / ToBytes aggregate | 2214.000 | 2393.300 | **+179.300** | +1558 | -26 |

Smaller boundaries generally favor GT: CBD, SOTP, cleanup and SHAKE hashes.
Keygen SHAKE sampling is the small exception at +27.5 cycles.

## Full versus Small ToBytes

Every operation makes one GT Full call. Keygen also makes two Small calls;
Encaps and Decaps make one Small call. Official uses the same Full serializer
for every corresponding call.

| Operation | Official per call | GT Full | Full gap | GT Small per call | Small delta vs Official |
|---|---:|---:|---:|---:|---:|
| Keygen | 1109.000 | 1411.000 | **+302.000** | 984.125 | -124.875 |
| Encaps | 1108.000 | 1413.000 | **+305.000** | 984.950 | -123.050 |
| Decaps | 1107.000 | 1411.000 | **+304.000** | 982.300 | -124.700 |

Small is already faster. The ToBytes aggregate deficit remains entirely caused
by Full normalization. P42 established that replacing `SSHR+AND+ADD` with
`CMLT+MLS` is slower, so that lowering is closed.

## Decision

The current production ranking is stable relative to P37: GT wins full KEM;
the remaining positive component gaps are Full ToBytes and fused
Inverse-to-ternary. P43 is recorded as this profiler checkpoint. The deferred
P41 precedence-aware route-cache borrowing candidate moves to P44, but its
maximum target is the Full ToBytes gap and it must not repeat P42's multiply-
pipeline regression.

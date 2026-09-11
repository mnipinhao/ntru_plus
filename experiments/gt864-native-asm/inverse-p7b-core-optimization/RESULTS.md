# P7-B0 / P7-B1 results

## Outcome

P7-B0 identifies the twelve-call `packed_i9` aggregate as the largest isolated
Inverse stage.  P7-B1 is promoted: `v0/v5` keep one repeated Barrett-Shoup
constant pair, and Slothy reschedules that fixed all-32-register allocation.
The complete Inverse and Decaps improve without changing the mathematical ABI,
coefficient memory boundaries, branches, scratch, or any other KEM operation.

## P7-B0 decomposition

All numbers are net Pi 5 medians after the empty harness, across 258
observations per boundary.

| Boundary | Cycles | Instructions | IPC | Reads | Writes |
|---|---:|---:|---:|---:|---:|
| inverse9 x12 | 2958.406 | 3821 | 1.292 | 344.015 | 297.094 |
| main inverse16 x6 | 2555.812 | 4460 | 1.745 | 328.031 | 769.000 |
| tail inverse16 | 409.297 | 678 | 1.656 | 56.000 | 95.985 |
| center864 | 750.859 | 1169 | 1.557 | 109.000 | 107.985 |
| complete Inverse | 7021.336 | 10744 | 1.530 | 821.031 | 1398.953 |

Removing every terminal main/tail store in diagnostic-only kernels saves only
149.687 + 15.203 = 164.890 cycles.  That is an optimistic ceiling, not an
implementable result, because the output still has to reach its consumer.  It
rejects terminal scatter as the P7-B1 primary target.

## P7-B1 DAG

The old core has 305 instructions including `ret`; the candidate has 285.  For
each of 722 and 6844, six MOVs and six DUPs become one entry MOV+DUP pair.
Twelve uses of each constant are redirected to `v0` and `v5`.  Across twelve
inverse9 calls this is exactly 240 fewer retired instructions.  Text size falls
from 1220 to 1140 bytes.

The first generated candidate failed KEM correctness and exposed two generator
bugs: `ldr qN` must kill a `vN` live interval, and an instruction such as
`sqrdmulh vN,...,vN` consumes its old source before overwriting the destination.
Both rules are explicit in `generate_b1.py`; only the corrected candidate was
scheduled or promoted.

Slothy used the Cortex-A76 model from `/Users/chenpinhao/slothy`, with physical
renaming disabled, spills disabled, and split factor 8.  It preserved the exact
284-instruction body and reports 71 expected cycles per call.  The production
file assembles to SHA-256
`b88e0408e3144cba29031e2e06a25fd51b89ea15bc5fc8f344c8beeab201373f`,
byte-identical to the benchmarked object.

## Paired Pi 5 timing

The final comparison contains six balanced runs, 366 paired Inverse samples
and 186 paired samples per full-KEM operation.  Temperature stayed 57.6--59.3 C
and `get_throttled=0x0`.

| Boundary | Baseline median | P7-B1 median | Paired cycle delta | Instruction delta |
|---|---:|---:|---:|---:|
| complete Inverse | 7017.102 | 6997.172 | -18.782 | -240 |
| Keygen | 46407.500 | 46403.500 | +0.875 noise | 0 |
| Encaps | 45750.325 | 45736.050 | -10.475 noise | 0 |
| Decaps | 43361.850 | 43350.725 | -17.875 | -240 |

The attribution control is essential.  Baseline to raw-order B1 changes
Inverse by **+15.258** cycles and Decaps by **+10.225**, despite retiring 240
fewer instructions.  Raw B1 to Slothy B1 then changes Inverse by **-27.571**
and Decaps by **-25.700** with zero instruction change.  The accepted result is
therefore the combination of a smaller DAG and a new schedule.

Every paired run first passed 24 valid, 24 tampered, 256 exact Inverse and 256
exact in-place alias comparisons.  Fresh production checks passed 64 KEM
round trips/tamper rejection and the 100-case KAT with unchanged SHA-256
`0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.

## Next work

P8 is now active: test a raw-Inverse-to-ternary Decaps consumer that may remove
the independent `center864 -> poly_crepmod3` pass.  P9 remains the new ToBytes
routing search; P10 remains the Keygen-only BaseInv numerator/finish redesign.

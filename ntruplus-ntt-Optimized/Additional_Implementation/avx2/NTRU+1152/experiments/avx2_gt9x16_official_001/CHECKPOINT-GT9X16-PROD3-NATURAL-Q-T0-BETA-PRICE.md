# GT9X16-PROD3-NATURAL-Q-T0-BETA-PRICE

## Scope

This checkpoint prices the complete namespaced T0-beta ASM against the frozen
Natural-Q PROD3 control at two boundaries in one same-ELF SUPERCOP-derived
measure:

1. coefficient-domain input through one and two complete forwards to the
   Natural-Q scale-four MA2 plane ABI;
2. two forwards plus the unchanged resident-`h`, Natural-Q MA2, H1 ciphertext
   serializer, and H1 `r` hash serializer.

The producer preflight requires canonical equality modulo `q` and the proved
signed-i16 range, not raw representative equality.  The caller preflight
requires exact ciphertext and hash bytes.  No MA2, H1, top-split, layout,
scale, reduction, or caller change is included.

## Method

- pinned SUPERCOP `20260627` and its `cpucycles()` backend;
- fixed common O3GC compiler recipe;
- CPU 1, performance governor, turbo disabled;
- balanced same-ELF control/candidate ordering;
- 9 fresh launches and 96 observations per label per launch;
- normal/reversed placement with ASLR on/off;
- normal placement selected by an independent SUPERCOP build using absolute
  candidate caller StQ2; normal ASLR-on is the headline.

The metadata preserves both accounting vocabularies.  The earlier generic
schedule recorded constant operands `666 -> 650` and predicted `.rodata +448`
bytes; the frozen Natural-Q linked objects record `594 -> 578` and actual
`.rodata +416` bytes.  The absolute baseline differs because of schedule
taxonomy and the linker-retained set.  Both retain the important `-16`
constant-operand direction, and performance attribution uses the linked ELF.

## Results

Median candidate-minus-control cycles by setting:

| Setting | 1x forward | 2x forwards | Frozen caller |
|---|---:|---:|---:|
| normal, ASLR on | -16.125 | -38.354 | -36.417 |
| normal, ASLR off | -14.854 | -38.417 | -33.375 |
| reversed, ASLR on | -14.750 | -37.396 | -14.812 |
| reversed, ASLR off | -16.292 | -41.292 | -18.667 |

Every cell wins 9/9 launches.  All twelve bootstrap 95% confidence intervals
are wholly below zero.  The headline confidence intervals are:

- 1x: `[-18.083, -14.396]` cycles;
- 2x: `[-42.375, -35.396]` cycles;
- frozen caller: `[-38.604, -34.542]` cycles.

ASLR-on runs produce nine distinct runtime-address tuples; ASLR-off runs
produce exactly one.  The placement and ASLR controls therefore do not explain
the direction.

## Decision

The sixteen removed Encap-level Montgomery chains are real machine debt.
T0-beta is promoted to the frozen Natural-Q PROD3 **research baseline**.  The
old T0 placement remains the historical control.  This result is
SUPERCOP-derived caller-island evidence, not native-KEM evidence; no native KEM
run or production promotion is authorized by this checkpoint.

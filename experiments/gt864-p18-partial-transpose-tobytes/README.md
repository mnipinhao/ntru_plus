# P18 — class-local partial-transpose ToBytes

P18 keeps the production FR0 and wire-byte contracts but replaces P9's
per-coefficient lane insertion with class-local, pruned 8x8 transposes.

The exact 54-output map of one top has fifteen distinct eight-source
neighborhoods. Within each neighborhood, every required output is a column of
the same 8x8 matrix after two or four source rows receive fixed cyclic lane
rotations.
Only the required 2, 4, or 6 columns are materialized. Normalization and 12-bit
packing consume each completed column immediately.

Production is not modified by this experiment.

## Result

All P18 gates passed.  The generated source is checked against the exact byte
oracle locally, then scheduled in fifteen fixed-register Cortex-A76 windows
with `/Users/chenpinhao/slothy`.  The final real assembly (including restored
`STUR D/W`, which the selected parser models using same-address `STR D/W`)
passes the oracle again and has no vector spill in the Pi 5 target objects.

Against committed production at the same public ToBytes boundary:

| Mode | Production cycles | P18 cycles | Delta | Instruction delta |
| --- | ---: | ---: | ---: | ---: |
| full | 1441.008 | 1409.641 | -31.368 | -461 |
| small | 1173.750 | 1024.633 | -149.117 | -479 |

The isolated full-KEM package also passes KAT, malformed-ciphertext, exact and
tampered KEM tests.  Median paired deltas are -334.125 cycles for Keygen,
-194.400 for Encaps, and -182.825 for Decaps, with 252 observations per
operation.  The instruction deltas expose the call mix: Keygen uses one full
and two small paths (`461 + 2*479 = 1419`), while Encaps and Decaps each use one
of each (`461 + 479 = 940`).

See `RESULTS.md`, `static-results.json`, `slothy-results.json`, and
`pi-results.json` for the complete evidence.  Promotion is deliberately a
separate P19 action so this experiment does not silently modify production.

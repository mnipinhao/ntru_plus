# GT32-PREFIX-CHECKPOINT-AUDIT-052A

Static audit of experiment 050's B2/B3 checkpoint construction. Production is
not modified.

## Findings

The good news is that 050 did not relink or relocate either prefix variant.
Each B2/B3 image is an equal-sized in-place patch of its frozen 043 production
ELF. Within each implementation:

- all symbol addresses are identical in Base, B2, and B3;
- bytes before the selected patch point are the original production bytes;
- the stack frame and caller prologue are unchanged;
- all following symbols retain their addresses;
- both variants eventually use the same cleanup and return targets.

Therefore the B3 variant did **not** move the code executed before the
checkpoint. Broad variant-induced prefix relocation is rejected.

However, B2 and B3 are not a matched executable interval:

```text
B2: producer -> save pointer -> jump to cleanup
B3: producer -> call hash_g -> return at later site -> save pointer -> cleanup
```

The branch source, hash call/return history, live state at the exit, and amount
of executed code differ. Thus subtracting their two independent whole-prefix
medians is not an isolated `hash_g` measurement.

The cross-production address geometry also remains materially different:

| Symbol | Official VA | GT VA | Official page offset | GT page offset |
|---|---:|---:|---:|---:|
| `hash_g` | `0x5b20` | `0x9000` | `0xb20` | `0x000` |
| `fips202avx_shake256` | `0x72d0` | `0xaf80` | `0x2d0` | `0xf80` |

Experiment 052 rejected a producer-state penalty at one common hash address.
It did not test these two production address geometries.

## Decision

```text
050 checkpoint moved earlier prefix code: REJECTED
B3-B2 is standalone hash_g cost:         REJECTED
same hash bytes / different VA effect:    OPEN
```

If this frontier is pursued, 053 should be a fixed-slot identical-code address
gate. It should not change Q24, the producer, hash arithmetic, or production.


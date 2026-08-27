# GT9X16-PROD3-NATURAL-Q-T0-BETA-ASM

## Scope

This checkpoint directly realizes the complete namespaced Natural-Q forward
candidate.  It absorbs the lane gauge `beta_q` into the existing
branch-specific radix-2 twiddles while keeping the top split, paper-R2 DAG,
Natural-Q ownership, D-stage order, scale-four output, reductions, and MA2 ABI
frozen.  No tile or single-branch prototype was inserted because this is a
local arithmetic-placement change inside an already qualified architecture.

No timing or native-KEM benchmark is part of this checkpoint.

## Correctness

The full coefficient-domain harness runs the unchanged top split and compares
the Natural-Q control against the T0-beta candidate modulo `q`.  It covers:

- zero and alternating vectors;
- all `+1` and all `-1` vectors;
- every positive and negative coefficient impulse;
- 1,003 random-small inputs;
- unaligned and in-place output buffers, canaries, and input immutability.

Canonical equality passes for every cell.  Raw representatives intentionally
differ (`66,714` observed cells), demonstrating that the test is not merely
comparing identical code paths.  The observed candidate interval is
`[-15031,14962]`, inside the proved `[-21333,21333]` envelope.  ASan and UBSan
also pass.

## Linked machine audit

| Class | Natural-Q control | T0-beta | Delta |
|---|---:|---:|---:|
| instructions | 2,819 | 2,787 | -32 |
| Montgomery chains | 296 | 288 | -8 |
| `vpmullw` | 368 | 360 | -8 |
| `vpmulhw` | 592 | 576 | -16 |
| constant-memory operands | 594 | 578 | -16 |
| routing | 432 | 432 | 0 |
| data loads | 144 | 144 | 0 |
| data stores | 144 | 144 | 0 |
| Barrett reductions | 72 | 72 | 0 |

Both objects have zero calls, branches, stack references, vector spills, and
`vzeroupper`.  Function entries, `.text`, `.rodata`, and all candidate
constants are 32-byte aligned.  The linked object changes are:

- `.text`: `15,489 -> 15,297` bytes (`-192`);
- `.rodata`: `10,400 -> 10,816` bytes (`+416`, 13 YMM vectors).

The linked audit corrected two symbolic-accounting values that had inherited
the current-Q rather than Natural-Q baseline: constant operands are
`594 -> 578`, not `666 -> 650`, and linked `.rodata` grows by 416 rather than
448 bytes because the control retains one unused 32-byte current-Q mask.
The structural conclusion is unchanged: eight Montgomery chains disappear
without movement, reduction, spill, or stack debt.

## Decision

The full ASM candidate passes the cheap prototype gate and the strict
correctness/linked-audit gate.  Producer and frozen caller-island paired
pricing is authorized next.  Native KEM measurement and production promotion
remain unauthorized until that pricing establishes a stable machine-level
gain.

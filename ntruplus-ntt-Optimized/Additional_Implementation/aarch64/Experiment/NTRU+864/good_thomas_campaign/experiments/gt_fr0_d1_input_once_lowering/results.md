# D1-P3B7 results

Status: **reject the C inline-assembly form; retain the arithmetic operations
only as a future schedulable-assembly hypothesis.**

All 256 complete signed-int16 inputs match P3B6 byte-for-byte for both L1 and
L12.  The test set includes index tags, `INT16_MIN`, `INT16_MAX`, and random
values.

Apple clang's top-local emitted objects are:

| variant | instructions/top | lane `mov` | `dup` | old sign ops | new sign ops | stack refs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| P3B6 control | 1358 | 432 | 2 | 162 | 0 | 0 |
| L1 | 1304 | 432 | 1 | 0 | 108 | 0 |
| L12 | 1250 | 378 | 55 | 0 | 108 | 0 |

`old sign ops` counts `cmlt+and+add`; `new sign ops` counts `sshr+mls`.
Thus L1 removes exactly 54 instructions/top, and controlled first-lane `dup`
removes another 54.  Both preserve the zero-spill core.  Intrinsic-only forms
were rejected during construction because the compiler recreated the old
three-instruction correction and turned part of L2 into table lookups; the
retained candidates use narrow inline-assembly contracts for exact lowering.

## Pi 5 target result

GCC 14.2 preserved the requested operations and produced no coefficient
spill.  Stack references are only ABI preservation: control saves `d8-d15`,
L1 saves `d14-d15`, and L12 saves `d15`.

| variant | cycles | instructions | branches | IPC |
| --- | ---: | ---: | ---: | ---: |
| P3B6 | **1502.453** | 2769.057 | 6.010 | 1.843 |
| L1 | 1659.185 | 2696.057 | 6.010 | 1.625 |
| L12 | 1643.030 | **2614.057** | 6.010 | 1.591 |

L1 retires 73 fewer instructions but loses 156.732 cycles.  L12 retires 155
fewer instructions but loses 140.577 cycles.  Every one of the three complete
repetitions produced essentially the same medians, and the Pi remained
unthrottled.

The target objects explain the result.  Each two-instruction correction is one
opaque inline-assembly block, so GCC cannot interleave independent corrections
with routing and packing as aggressively as it does for P3B6.  The reduced
instruction count is outweighed by the loss of issue overlap: IPC falls from
1.843 to 1.625/1.591.  This is not a spill regression and does not disprove the
two-instruction identity; it disproves this compiler boundary as an efficient
implementation.

No full-KEM binding is permitted.  Reusing `sshr+mls` requires a larger
symbolic/assembly region whose independent corrections are visible to the
scheduler.  P3B6 remains the measured ToBytes champion at 1502.453 cycles.

# Y0/Y1/Y2 release static ledger

Counts for Y2 are dynamic counts after three row-loop iterations; its stored instruction
body contains one third of the row work.

| Item | Y0 SAFE | Y1 Yang | Y2 compact Yang |
| --- | ---: | ---: | ---: |
| Pass-A native loads | 96 | 48 | 48 |
| Pass-A state stores | 48 | 48 | 48 |
| Pass-B state loads | 48 | 48 | 48 |
| Pass-B final stores | 48 | 48 | 48 |
| table/constant memory operands | 170 | 230 | 230 dynamic |
| `vpmullw` | 96 | 192 | 192 dynamic |
| `vpmulhw` | 192 | 192 | 192 dynamic |
| `vpmulhrsw` | 0 | 96 | 96 dynamic |
| `vpaddw` | 528 | 240 | 240 dynamic |
| `vpsubw` | 624 | 336 | 336 dynamic |
| `vpermq` | 192 | 192 | 192 dynamic |
| `vpshufb` / `vperm2i128` | 0 / 0 | 0 / 0 | 0 / 0 |
| conditional branches | 0 | 0 | 6 dynamic |
| calls / spills / stack bytes | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| symbol bytes | 19643 | 11166 | 3780 |

Y1 removes 48 duplicate native loads and 576 add/sub correction instructions. It adds
96 `vpmulhrsw` plus 96 `vpmullw` for the two proved Barrett boundaries. Its higher
memory-constant count includes those 96 memory-source center10 operands; Pass-A
factor/qinv loads themselves fall from 72 to 36. Y2 adds only two static loop branches
and six dynamic branch executions while shrinking code by 7,386 bytes relative to Y1.

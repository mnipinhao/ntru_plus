# D1-P3B1 results

Status: **PASS — R9-A transpose/repair is the coordinate-route champion.**

All tagged and random cases pass in both directions, both R9-A and R9-B round
trip exactly, and the Pi 5 was unthrottled. Overall p50 results are:

| Direction / candidate | cycles | instructions | branches |
| --- | ---: | ---: | ---: |
| FR0→Official current | 1760.402 | 5193.036 | 867.008 |
| FR0→Official factorized scalar | 1658.391 | 4478.036 | 147.008 |
| FR0→Official R9-A | **392.238** | **1493.036** | **33.008** |
| FR0→Official R9-B | 595.208 | 1577.036 | 33.008 |
| Official→FR0 current | 1795.766 | 5193.036 | 867.008 |
| Official→FR0 factorized scalar | 1670.641 | 4622.036 | 147.008 |
| Official→FR0 R9-A | **417.285** | **1337.036** | **33.008** |
| Official→FR0 R9-B | 596.192 | 1577.036 | 33.008 |

R9-A saves 1368.164 cycles (77.719%) forward and 1378.481 cycles
(76.763%) reverse relative to current. It also beats R9-B by 202.970 and
178.907 cycles. Every individual repetition preserves `R9-A < R9-B < current`.

## Emitted machine shape

| Helper | bytes | instructions | structural lookup depth |
| --- | ---: | ---: | ---: |
| R9-A forward | 472 | 118 | 1 dependent TBL level |
| R9-A reverse | 420 | 105 | 1 dependent TBL level |
| R9-B forward | 500 | 125 | 1 dependent TBL level |
| R9-B reverse | 500 | 125 | 1 dependent TBL level |

R9-A forward contains 17 TBL instructions after GCC lowers cyclic rotations
and final lane reorder; reverse contains nine TBL plus seven EXT. R9-B has 27
independent lookup nodes feeding two ORR merge levels. No TBL result feeds a
second TBL in either family, so critical dependent TBL depth is one. R9-A's
longer conceptual shuffle chain is rotation, three transpose levels, diagonal
repair and final reorder; R9-B is lookup plus two merges. The emitted helpers
touch the 24 caller-saved registers `v0-v7,v16-v31`, with no `v8-v15`, vector
stack spill, or coefficient scratch. This is a physical-register footprint,
not a claim that all 24 values are simultaneously live.

The P3B0 87/90 counts were source-level conservative selection estimates, not
actual compiler instruction counts. The real Cortex-A76 result still strongly
selects R9-A, confirming that cycles and resource/dependency shape must rank
candidates rather than instruction count alone.

The Arm feature and secret-independence audits report zero warnings. The Neon
pattern checker flags the expected TBL/transpose/lane-insert sites; these are
accepted because every index and address is compile-time/public, their shuffle
cost is measured above, and the exhaustive tagged-position test validates the
coordinate map.

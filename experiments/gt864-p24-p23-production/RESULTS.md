# P24 result — P23 ToBytes schedules promoted

P24 is promoted.  Baseline and candidate were built from exact `git archive`
snapshots, not from the working tree:

- P18 production baseline: `32481d08aae9135803379499c68c12b20a3856d4`
- P24 production candidate: `4b7a3b83085045694f8861cea61660d3345816ac`
- Pi 5 workspace: `/home/pi/supercop-20260831/bench/pinhao/gt864-p24-20260913`

The public ABI and symbol names are unchanged.  Full and Small preserve the
FR0 input, exact 1,296-byte canonical wire output, input immutability,
disjoint-buffer contract, `d8-d15` preservation and SIMD cleanup.

## Promotion gates

- source manifest: pass;
- linked symbols: only the active P18-named public ToBytes symbols;
- exact bytes: 513 Full + 513 Small cases and two guarded-edge cases;
- AAPCS, SIMD cleanup, input immutability and output canaries: pass;
- KAT SHA-256:
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`;
- malformed transcript SHA-256:
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`;
- Pi 5 remained unthrottled (`0x0`), 57.1–60.9 C.

The complete linked objects have zero Q-register stack accesses.  Compared
with P18, each complete ToBytes call retires exactly 194 fewer instructions
and six fewer reads:

| Boundary | P18 cycles | P24 cycles | Delta | Instruction delta | Read delta |
|---|---:|---:|---:|---:|---:|
| Full | 1409.773 | 1393.867 | -15.906 | -194 | -6 |
| Small | 1024.633 | 984.973 | -39.660 | -194 | -6 |

The production KEM boundary also wins in all three operations across 252
observations per implementation/operation:

| Operation | P18 cycles | P24 cycles | Paired delta | Instruction delta |
|---|---:|---:|---:|---:|
| Keygen | 43242.375 | 43102.750 | -147.000 | -582 |
| Encaps | 45068.000 | 44996.800 | -67.325 | -388 |
| Decaps | 40127.225 | 40065.400 | -62.625 | -388 |

The isolated cycle deltas are not multiplied estimates: the KEM rows are
independently measured complete operation boundaries.  Full raw data and the
target-object audit are in `pi-results.json`.

# Results

## Hard-gate outcome

CF5-A passes the NTT16-producer to scaled-pair boundary gate.

- Producer RA: 345 instructions, `OPTIMAL`, self-check OK.
- Four consumer RAs: 309/309/279/279 instructions, all `OPTIMAL`, all
  self-check OK.
- All five schedules: split-heuristic full self-check OK.
- Boundary: eighteen distinct producer live-outs, including both `f8` tail
  values; zero copies, spills, stack accesses, or coefficient memory traffic.
- Cross-bank ABI: `v13=bitrev`, `v14=q`, and `v15=roots` remain unchanged.
- Assembler: all four concatenated producer/consumer functions assemble.
- CF1 exact matrix/root/scale/range proof passes.

## Linked execution

The correctness-only full Forward was compiled and run on Raspberry Pi 5
Cortex-A76.  It passed 1126 inputs: zero, five constant families, all 864 basis
vectors, and 256 random vectors.

Both ordinary output and in-place alias output were compared coefficient by
coefficient against `normalize(M5R-D Forward)`:

```text
comparisons=972864
alias_comparisons=972864
```

No mismatch occurred.

## Cost interpretation

The common packs and lane-dependent constants share one case table, so the
existing per-bank `adr x3` is reused.  The corrected dynamic estimate is:

```text
M5R-D                  4446
four CF3 replacements +280
CF5-A estimate         4726
CF0                    4738
```

This is a twelve-instruction advantage over CF0.  It is not yet a cycle win:
the linked correctness artifact duplicates the 345-instruction producer four
times and has not been measured with the Pi 5 PMU.

# P122 — frontend deduplication shrinks 768 by 6.5 KB but does not help a cold start

## What was changed (branch `gt768-frontend-dedupe`, on top of `gt768-cleanup`)

Each forward NTT has a frontend of 8 iterations.  Every iteration is five
base-pointer `add`s followed by a Slothy-scheduled body, and the body is
textually identical for all iterations of the same scheduling class.
`dedupe.py` turns every iteration of a class with two or more members into
`5 x add; bl <class body>`, and emits each body once after the function
with `ret`:

- `decap_ntt.S`: 8 of 8 iterations -> 3 bodies (classes {0,3,6}, {1,4,7}, {2,5}).
- `ntt.S`, keygen/core frontend: 7 of 8 -> 3 bodies (iter7 is unique and stays inline).
- `ntt.S`, Encap small frontend: 6 of 7 -> 3 bodies.
- x30 is saved at `[sp, #56]`.  `[sp, #0]` is the Slothy spill slot
  `STACK_LOC_0`: a first attempt that saved x30 there crashed.  A canary run
  showed the core writes `[sp, #0]` in all four modes and never touches `#56`,
  and a watchpoint found the spill (`str x16, [sp]`).

## Equivalence

- Every entry point is bit-identical to the pre-change objects on 20,000
  inputs: loose, keygen_cq, encap_small, encap_small_lazy (including in
  place), and decap.  Inputs are random int16 and ternary.
- `make check` passes on M2 and Pi 5, KAT unchanged.

## Size

| | before | after |
|---|---:|---:|
| linked text (Pi, gc-sections) | 91,112 B | 84,552 B (-7.2%) |
| keygen, code executed | 25.1 KB | 22.8 KB (-9.2%) |
| encaps | 24.6 KB | 23.2 KB (-5.7%) |
| decaps | 25.3 KB | 22.5 KB (-11.1%) |

## Speed (Pi 5 A76, cycles)

- Warm and L1I-cold: unchanged in three alternating rounds (±90 cycles).
- Fully cold (32 MiB read + 96 KiB executed nops before each operation), 12
  alternating process pairs, medians:

| | before | after | paired diff | after faster |
|---|---:|---:|---:|---:|
| keygen | 44,586 | 44,989 | +287 | 5 / 12 |
| encaps | 41,727 | 42,614 | **+1,340** | 3 / 12 |
| decaps | 40,991 | 41,226 | +6 | 6 / 12 |

- M2, warm: unchanged (within 2 ns).

## Conclusion

The cold-start estimate that motivated this (about 120-450 cycles per KB of
footprint) treated cold cost as proportional to bytes.  It is not.
Straight-line code is fetched ahead by the instruction prefetcher; calls into
bodies 20 KB away break that sequence, and the saving in bytes is lost to
serial misses at each call target.  Encaps, which makes the most calls
relative to the bytes saved, gets slower.

The deduplication is kept on its branch as a size-only option (-6.5 KB text,
behaviour-identical) and is **not proposed for production**.  Sharing the row
bodies would face the same fetch-pattern cost on top of its warm-path risk,
so item 4 (code size) is closed: code size is not the constraint in steady
state, and making the code smaller by calling shared bodies does not help a
cold start.

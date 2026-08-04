# Round 4 execution plan

## Frozen question

Can a horizontal weighted GT(3,16) representation reduce the complete native
forward/basemul/inverse consumer graph by at least 5% relative to the tracked
vertical GT(3,32) champion?

The complete transform contains 48 forward and 48 inverse NTT16 rows.  Every
cost report must cover a beta branch, a top branch, the complete transform,
and the caller-weighted KEM graph.

## Phase 1: pre-kernel contract

- Enumerate all 48 valid `F` roots for each of four beta branches.
- Select the four roots jointly using forward and inverse constant reuse.
- Generate full 3x16 pre/post-weight and CRT wrap-correction matrices.
- Track alpha, representation scale, Montgomery power, range, and layout per
  terminal component.
- Validate both transform orders, inverse, Official leaf mapping, and
  quotient-ring multiplication.

## Phase 2: static row DAG

Compare DFT3-first and NTT16-first for tile-by-row, tile-by-degree, and
tile-by-branch-pair.  Count shuffles, Montgomery products, lost reductions,
loads/stores, constant cache lines, code bytes, and in-place scratch.  Peak
steady-state data is at most 10 YMM; total live state is at most 15 YMM with
one emergency temporary and no spill.

Stop before AVX2 if the full-graph optimistic floor is not at least 5% below
the frozen vertical champion.

Result: this gate fails for the horizontal single-YMM design.  The 48 NTT16
rows alone have a 1,728-instruction optimistic floor; adding the minimum DFT3
and full-array I/O reaches 2,000 before either radix-2 or packing is counted.

## Phase 3: bounded AVX2 row prototype

Benchmark the complete `standard-R2 + weighted DFT3 + 48xNTT16 + native-store`
boundary and its paired inverse.  Forward, inverse, and the complete native
forward+basemul+inverse chain must each improve by at least 5%.

## Phase 4: consumer islands

Measure separately:

1. decryption: decode, multiply, inverse, message;
2. randomness recovery: forward message, subtract, multiply by `hinv`, encode
   recovered randomness, and equality/hash boundary.

Only a consumer-complete byte-exact result may enter a full KEM candidate.

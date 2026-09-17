# WIRE-MONOTONE-NATIVE-ATTRIBUTION-V3 / FORWARD REGISTER FLOW

## Native-gap attribution

The only scheme-level headline remains native SUPERCOP.  The current exp006
candidate has a native encapsulation deficit of `+672.27` cycles.  V3 is a
SUPERCOP-derived diagnostic using the same selected compiler,
`default-perfevent` `cpucycles()`, CPU 1, performance governor, disabled turbo,
9 fresh processes, and balanced Official/wire ordering in one ELF.

| boundary | Official StQ2 | wire StQ2 | wire - Official |
| --- | ---: | ---: | ---: |
| coefficient input -> forward state | 1495.13 | 1486.25 | -8.88 |
| forward + r serialization | 1806.55 | 1988.97 | +182.42 |
| forward + serialization + `hash_g` + SOTP | 19797.02 | 19948.36 | +151.34 |
| PK bytes + transformed r/m -> ciphertext | 1634.47 | 2064.81 | +430.34 |
| complete changed polynomial caller | 22464.76 | 23161.27 | +696.52 |

The complete diagnostic is within about 24 cycles of the native deficit.  It
therefore closes the gap well enough to guide work:

```text
latest forward arithmetic              small win (~ -9)
r dual-output / serializer boundary    main middle debt
PK ingress + MA2 + ciphertext tail     largest debt (~ +430)
complete changed caller                ~ +697
native SUPERCOP encapsulation          ~ +672
```

The forward remains worth optimizing as a reusable kernel, but it is not the
largest explanation of the current native loss.

## Measured forward boundary

The V3 candidate boundary includes both calls:

```text
coefficient-domain small polynomial
  -> ntruplus1152_exp001_top_split_small
  -> ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce
```

The register-flow below describes the second, handwritten AVX2 leaf.  Its
entry memory is the 2304-byte top-split state.  The leaf has 2,875 linked
instructions, 15,449 bytes of `.text`, 12,192 bytes of `.rodata`, no calls,
no branch, no frame, no vector spill, and no `vzeroupper`.

Linked opcode ledger:

| class | count |
| --- | ---: |
| Montgomery chains | 296 |
| Barrett vectors | 40 |
| `vpmullw` | 336 |
| `vpmulhw` | 592 |
| `vpmulhrsw` | 40 |
| routing | 488 |
| data loads | 144 |
| data stores | 144 |

The 296 Montgomery chains decompose as:

```text
72  scale-1 alpha normalization at input
48  two-layer radix-3 kappa chains
32  radix-3 inter-group zeta/rho adjustments
144 NTT16 D8/D4/D2/D1 twiddle chains
---
296
```

## Register-flow view

### Stage 0: leaf entry

**Register state before**

```text
rdi = 2304-byte top-split backing
YMM registers = caller-clobbered / no live contract
memory owner = (branch, GT row, q block, terminal coefficient AoS)
```

**Instructions**

No prologue.  The symbol is `.p2align 5` and immediately enters PASS A.

**State after / mathematics**

No arithmetic change yet.  The top split has already separated the two
branches without changing the forward's semantic coefficient values.

**Layout, scale, bound**

- Layout: branch-local AoS, nine GT rows, four 256-bit q blocks per row.
- Scale: coefficient-domain input gauge before the scale-1 transform.
- Bound: small-input contract inherited from top split.

**Why / next consumer**

Avoiding a frame and copies preserves the materialized top-split backing as
the transform workspace.  PASS A consumes one branch and q block at a time.

### Stage 1: `PROD3_LOAD_TWIST` / scale-1 alpha formation

**Register state before**

```text
ymm6      = q
ymm7..15  = free destinations for GT rows 0..8
ymm0      = temporary Montgomery low-half path
rdi       = current branch backing
```

**Instructions**

For each of nine rows:

```text
vmovdqu   row source -> ymm7..ymm15
vpmullw   x, alpha_qinv -> ymm0
vpmulhw   x, alpha      -> row register
vpmulhw   ymm0, q       -> ymm0
vpsubw    high - correction -> row register
```

This is repeated for four q blocks and two branches: 72 Montgomery chains.

**Register state after**

```text
ymm7..15 = nine alpha-normalized GT-row vectors for one q block
ymm6     = q
ymm0     = dead temporary
```

**Mathematics**

The branch/row `alpha_h` factor and caller-wide scale-1 gauge are applied.
The prior `beta_q` factor is not paid here; it has already been absorbed into
the radix-2 twiddle tables.

**Layout, scale, bound**

- AoS q/j lane ownership is unchanged.
- Scale changes to the scale-1 forward gauge expected by H4.
- Montgomery exponent returns to the consumer-visible exponent after each
  chain; no pending exponent is carried to the next macro.
- The complete proved forward envelope remains within `[-21333,21333]`.

**Why / next consumer**

Memory-form constants avoid holding alpha/qinv tables in additional YMMs.
The nine resident row vectors are exactly the inputs needed by the two-layer
radix-3 PASS A.

### Stage 2: first paper radix-3 layer

**Register state before**

```text
ymm7..15 = nine resident rows
ymm4     = kappa_qinv
ymm5     = kappa
ymm6     = q
ymm0..3  = arithmetic temporaries
```

**Instructions per `PROD3_R3(a,b,c)`**

```text
vpaddw / vpsubw       form b+c and b-c
vpmullw
vpmulhw ×2
vpsubw                Montgomery kappa*(b-c)
vpaddw / vpsubw       form the three radix-3 outputs
```

Three independent triples are executed.  The third uses the paper R2 address
rotation, so semantic rows `g8,g2,g5` occupy the physical `(15,9,12)` group.

**Register state after**

All nine outputs remain in `ymm7..15`; no transpose or materialization occurs.

**Mathematics**

First radix-3 dimension of NTT9, using the scaled paper identity.  Each R3
macro contains one vector Montgomery chain.

**Layout, scale, bound**

Physical row order changes to the paper-R2 rotated order.  q lanes and scale
do not change.  Values remain lazy signed-i16 representatives.

**Why / next consumer**

The formula avoids a general three-multiply DFT3 and keeps all nine rows live.
The next stage needs only a selected repair cover, not nine unconditional
reductions.

### Stage 3: localized Barrett repair

**Register state before**

```text
ymm7..15 = first-layer lazy outputs
ymm6     = q
ymm0     = temporary
```

**Instructions per repaired vector**

```text
vpmulhrsw value, v
vpmullw   quotient, q
vpsubw    value, product
```

The exact mask repairs physical registers `7,8,15,10,13`: five vectors per q
block, 40 vectors over the full forward.  The other 32 historical reductions
are absent.

**Register state after**

The nine vectors remain resident and in the same physical order; only selected
representatives are narrowed.

**Mathematics / layout / scale / bound**

Residues, ownership, scale, and Montgomery exponent are unchanged.  The
localized repair is exactly what keeps the following radix-3 and Montgomery
preconditions inside signed i16; the global proof peak is 21333.

**Why / next consumer**

`vpmulhrsw` implements the fixed-q Barrett quotient efficiently.  The second
radix-3 layer consumes the repaired/lazy mixture directly.

### Stage 4: second paper radix-3 layer and inter-group adjustments

**Register state before**

```text
ymm7..15 = repaired/lazy first-layer state
ymm0..3  = temporary arithmetic registers
ymm6     = q
```

**Instructions**

- Three more `PROD3_R3` macros.
- Four `PROD3_MONT6` chains applying fixed `zeta4`/`rhoinv` adjustments.

**Register state after**

```text
ymm7,8,15,10,11,9,13,14,12 = nine final NTT9 rows
```

They are stored to the branch backing in semantic paper-R2 row order.

**Mathematics**

Completes NTT9 while retaining the adjusted/paper gauge required by NTT16.

**Layout, scale, bound**

The output is still four contiguous AoS q blocks per row.  Scale remains 1;
no canonicalization is inserted.  PASS A then deliberately materializes all
72 vectors across both branches.

**Why / next consumer**

The materialization ends the nine-row live range and gives PASS B independent
row-sized work.  PASS B reloads one row at a time for NTT16.

### Stage 5: PASS B load, D8 and D4

**Register state before**

```text
ymm0..3  = four 256-bit AoS q blocks for one GT row
ymm15    = q
ymm4..7  = Montgomery temporaries
```

All four loads occur before the row's output overwrites the backing.

**Instructions**

Four `PROD3_BFLY` calls:

```text
D8: (ymm0,ymm2), (ymm1,ymm3)
D4: (ymm0,ymm1), (ymm2,ymm3)
```

Each butterfly performs one Montgomery twiddle chain followed by
`vpsubw/vpaddw`.

**Register state after**

`ymm0..3` still hold four contiguous AoS q blocks, now transformed through D8
and D4.  Temporaries are dead.

**Mathematics / layout / scale / bound**

Two NTT16 radix-2 layers complete with zero routing.  Twiddles include the
absorbed beta factor.  Layout and scale remain unchanged; values stay lazy.

**Why / next consumer**

Persistent AoS is ideal while butterfly partners already occupy matching
128-bit halves.  D2 is the first layer that needs cross-half regrouping.

### Stage 6: D2 regrouping and butterfly

**Register state before**

```text
ymm0..3  = D8/D4 AoS results
ymm15    = q
```

**Instructions**

```text
4 × vperm2i128 -> ymm4..7
2 × parallel Montgomery chains using ymm8..11
vpsubw/vpaddw -> ymm4..7
```

**Register state after**

`ymm4..7` hold D2 outputs, grouped as two four-q chains.  `ymm8..11` are dead.

**Mathematics / layout / scale / bound**

D2 completes without changing semantic leaf identity, scale, or exponent.
Physical halves are regrouped in preparation for adjacent-q D1 pairing.

**Why / next consumer**

`vperm2i128` is the minimum direct AVX2 operation for the required 128-bit
cross-lane selection.  D1 needs qword-interleaved partner pairs.

### Stage 7: D1 adjacent-q butterfly

**Register state before**

```text
ymm4..7  = D2 outputs
ymm15    = q
```

**Instructions**

```text
4 × vpunpckl/hqdq -> ymm0..3
2 × parallel Montgomery chains -> ymm4..7 temporaries
vpsubw/vpaddw -> ymm0..3
```

**Register state after**

`ymm0..3` are the four live D1 terminal vectors.  Their physical pairs are
adjacent physical-q butterfly states, not terminal-coefficient pairs.

**Mathematics / layout / scale / bound**

NTT16 is complete.  Semantic output is the same scale-1 GT9x16 transform;
physical ownership is deliberately non-canonical and ready for the final
consumer-specific transpose.

**Why / next consumer**

Qword unpack directly establishes D1 partners.  The next consumer needs four
coefficient planes in the frozen wire-monotone lane ABI.

### Stage 8: live transpose and wire-monotone redeposit

**Register state before**

```text
ymm0..3 = four live D1 terminal vectors
ymm4..7 = free output/transpose registers
```

**Instructions per row**

```text
4 word unpacks
4 dword unpacks
4 qword unpacks
4 vpermq
0..4 memory-form vpshufb, determined by the tile map
4 vmovdqu stores
```

Across 18 branch/row tiles, the direct D1 resynthesis requires 56 additional
`vpshufb`; four tiles require none.  The full linked routing count is 488.

**Register state after**

```text
memory owner = (branch, paper-R2 p row, terminal coefficient)
YMM lane     = wire-monotone physical q leaf
scale        = 1
Montgomery exponent = consumer-visible exponent 0
```

All live YMM values die after the four stores; the next row reloads independent
state.

**Mathematics / layout / scale / bound**

Only representation changes.  Residues and scale do not.  Raw lazy
representatives are retained within the proved signed-i16 envelope.

**Why / next consumers**

- For `r`, `direct_serializer_wire` consumes this exact lane geometry.
- For both `r` and `m`, H3/MA2/H4 consumes the same wire-monotone planes.

The chosen `vpshufb` tax is therefore a caller-ABI cost, not NTT arithmetic.

## Forward optimization opportunities

### 1. D1-to-wire orientation search

This is the lowest-risk meaningful target.  The final network still pays 56
memory-form `vpshufb` per forward.  Search equivalent D2/D1 output swaps,
twiddle sign conventions, and unpack orientations while keeping the exact
wire ABI fixed.  The goal is to absorb some masks into legal butterfly output
orientation, not to reopen Q-order.

### 2. PASS A / PASS B materialization pricing

The current two-pass shape stores 72 NTT9 vectors and reloads them for NTT16.
This is the largest explicit internal memory boundary.  A conservative
wavefront should retain one or two rows, not force whole-transform zero-copy.
It must be priced against the current OoO-friendly memory boundary because the
earlier D0 experiment showed that fewer loads/stores can still be slower.

### 3. Remaining 40 Barrett repairs

The 72-to-40 reduction already won.  Re-run exact interval propagation on the
scale-1 wire path to test whether a following Montgomery chain can absorb any
of the remaining five repairs per q block.  No reduction may be removed from
instruction count alone.

### 4. Montgomery-chain placement

The main arithmetic populations are 72 alpha, 80 NTT9, and 144 NTT16 chains.
Beta absorption is exhausted for the frozen DAG, but scale-1 alpha placement,
radix-3 orientation, and fixed adjustment constants can still be reconsidered.
This is higher risk because it changes representative ranges and gauge flow.

### 5. Scheduling and footprint

The two branches are emitted sequentially as one 15.4 KiB straight-line leaf.
Linked scheduling can investigate two-row interleaving, constant lifetime, and
selective helper/compact realizations.  Any compact version must beat the
current straight-line code under Native SUPERCOP; smaller `.text` alone is not
a performance result.

## Next checkpoint

Start `FORWARD-OPT-V3-D1-WIRE-ORIENTATION` as an exact-output-ABI search.  It is
more local and lower risk than reopening NTT9/NTT16 wavefront scheduling.  In
parallel, native encapsulation work should prioritize the independently larger
`PK bytes -> MA2 -> ciphertext` debt identified by V3.


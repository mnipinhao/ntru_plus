# P68 — the whole 1152 inverse in the (component, half) lane basis

P65 rebased the basemul output, P67 rebuilt the main 16-point kernel.  This gate
does the middle piece, `packed_i9`, and then wires the three together into a
complete inverse.  **Both hosts improve**, which no inverse gate before P61 had
achieved:

| | A76 cycles | M2 ns | dynamic instructions | dynamic mul-class |
|---|---:|---:|---:|---:|
| production | 5,944 | 562 | 8,919 | 2,485 |
| P68 | 5,827 | 484 | 7,078 | 2,485 |
| | **-1.97%** | **-13.9%** | -1,841 (-20.6%) | **unchanged** |

A76 median over 201 rounds of 200 calls, `taskset -c 2`, `PERF_COUNT_HW_CPU_CYCLES`,
`exclude_kernel`; M2 median of 64 rounds of 2,000, three repetitions each.  Both
variants live in one binary and alternate rounds.

## What the basis change is

Every stage of the inverse wants a different axis in the lanes, and the tree
paid for each disagreement with a transpose.  The observation that makes this
gate work is that **`inverse16_tail.S` was already right**.  `s=8` is a single
call, so its eight lanes could only ever be the four components and the two
halves — and that kernel, alone in the tree, stores its results with plain
`str d` and needs no `umov`/`strh` scatter at all.

P68 simply gives all nine `s` the layout the ninth already had:

```
rebased input   halfword(j,t,c,h) = j*128 + t*8 + (c + 4h)        (P65)
packed_i9 (t)   reads 9 Q at [x2 + j*256], writes 9 Q at [x0 + s*256]
invntt16  (s)   reads 16 consecutive Q at [x1 + s*256]            <- already its ABI
```

The scratch becomes a plain `[s][t]` array of 9x16 Q = 2,304 bytes, exactly the
size it was before.

## Recovering the register -> s map

The new stores had to know which pre-transpose register carries which radix-9
output.  The transpose network is Slothy-scheduled and its order is not the
textbook one, so this was measured, not derived: `probe_i9.S` tags each
transpose input with `(slot+1)*100 + lane` and `probe.c` dumps the scratch.

Reading the driver pins the axes the probe leaves ambiguous.  The `invntt16`
call bases are `x19 + c*2 + h*32`; `32` bytes is 16 halfwords is `4s`, so the
driver's "half" advances **s by 4**, and the tail at `+64` is **s=8**.  The i9
loop's "top" is therefore the real `half`, and

```
s = 4 * probe_block + lane_position
```

giving `s0..s8 = v24, v31, v9, v14, v22, v11, v20, v19, v28`.

The generator's own check is the strongest evidence this is right: taking each
output register's **last definition** after the transposes are deleted lands all
nine stores on `mls vX, v5.8H, v15.8H` — one per output, perfectly uniform, the
closing Montgomery reduction.  Nothing in the generator forced that.

Stores are emitted at the last definition rather than at the old store's
position for the reason `generate_tail.py` documents and P64's hand-made probe
fell into: the scheduler reuses these registers immediately after the
transposes consume them.

## What disappeared

- 16 output transposes and 24 split stores per `packed_i9` call, replaced by 9
  `str q`: **185 -> 150 instructions**, x16 calls.
- 128 `umov` + 128 `strh` -> 32 `str d` per `invntt16` call (P67): 658 -> 434, x8.
- The tail-padding clear.  `s=8` is now written by 16 full `str q` that cover all
  256 bytes, so there is nothing left to pre-zero.
- `x1`.  `packed_i9` took a second output pointer only for the lane scatter.

`inverse16_tail.S` is **unchanged** — and its input offsets are byte-identical
to what the new `str q28, [x0, #2048]` produces, which is an independent check
on the whole layout.

## Cost

The twiddle table is repacked from `[2][2][9][2][8]` keyed on `(half, block)` to
`[16][9][2][8]` keyed on `t`, each row `[A,A,A,A,B,B,B,B]` because the twiddle
depends on `(t, half)` and never on the component.  1,152 -> 4,608 bytes; the
number of loads per call is unchanged at 18.  `repack_tables.c` emits it and the
result is checked entry by entry against the source table.

The rebase pass costs 354 cycles on A76 (P65), which is most of why the A76 gain
is only 117 cycles despite 1,841 fewer instructions.

## Why A76 gains so little and M2 so much

The mul-class count is **identical**, 2,485, so the A76 floor stays at 4,970
cycles.  Production sits 974 cycles above it, P68 sits 857 above it.  On a
machine whose mul-class instructions are pinned to one pipe at 2 cycles, most of
the 1,841 removed instructions were filler that was already free — the campaign's
central finding, now confirmed from the other direction.  M2 has four
mul-capable pipes and no such slack, so it collects nearly the whole reduction.

## Verification

`verify.c` runs both chains in one binary and compares all 1,152 coefficients:
**5,000 trials on M2 and 2,000 on A76, zero mismatches**, including the all-zero
and unit-impulse inputs.

## Next

Neither new kernel has been scheduled.  `inverse9_lane.S` carries NTRU+864's
A76 schedule with 35 instructions deleted from it, and `invntt16_lane.S` the
same with 224 deleted; P36 already measured that 1152's kernels were never
scheduled for 1152 (inverse9 ~2,215 against 2,005 dependency-relaxed).  A Slothy
pass over the new shapes is the obvious follow-up, and it is now a much smaller
problem than it was.

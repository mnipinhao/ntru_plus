# P96 — 864's inverse is store-bound, and P95 only moves the stores

P95 proposed letting `invntt16`'s inner four lanes hold four consecutive output
positions `p = 3j + c`, so a group's four outputs become four contiguous
halfwords and its 4 UMOV + 4 STRH collapse to one STR D.  That part is real and
was built and proved here.  What the record did not price is the other side:
the transpose it removes from `invntt16` reappears in `packed_i9`, and costs
more there than it saved.

## The kernel side works exactly as designed

`gen16.py` rewrites `inverse16.S` mechanically.  The body and both tables are
untouched -- `invntt16_main_constants` is `[A,A,A,A,B,B,B,B]` in all 64 rows and
`invntt16_main_scale` in all 32, so the twiddles cannot see what the inner lanes
carry.  660 instructions become 439.

STR D scales its immediate by eight and a group is 54 bytes on from the last, so
`[x0, #54k]` does not encode.  Four bases -- `x0` and three more, one per
residue of `k mod 4` -- reach every group at `216m`, which does encode, and
leave the scheduler free to order the stores.

Two probes, both in this directory:

- `lanes.c` perturbs one scratch lane across all sixteen inputs and diffs the
  output, recovering each lane's support without assuming any index algebra.
  Current kernel: lane `l` lands at group offset `3l`.  New kernel: at `l`.
- `same.c`: over 2,000 random inputs, all 256,000 outputs satisfy
  `new[27g + l] == old[27g + 3l]`.  Values identical, placement moved.

## But the store budget is conserved

| `invntt16`, six calls | store/call | M2 Pro | Cortex-A76 |
|---|---:|---:|---:|
| current, 128 UMOV + 128 STRH | 128 | 199.1 ns | 845.4 ns |
| 128 `ST1 {v.H}[lane]` | 128 | 195.1 (-2.0%) | **1033.8 (+22.3%)** |
| 32 `STR D` (P95) | 32 | 125.7 (-36.9%) | 786.7 (-7.0%) |
| 16 `STR Q` (output layout free) | 16 | **112.3 (-43.6%)** | **768.1 (-9.1%)** |

| `packed_i9`, twelve calls | store/call | M2 Pro | Cortex-A76 |
|---|---:|---:|---:|
| current | 24 | 127.2 ns | 705.0 ns |
| the scatter P95 forces | 72 | 214.6 (+68.8%) | 1037.1 (+47.1%) |

P95 needs that scatter.  The new scratch mixes `c` across the four inner lanes,
a `packed_i9` call owns one `c`, so its eight main outputs can no longer leave
four-at-a-time; each register scatters eight lanes to eight slots sixteen bytes
apart.

**Total stores are unchanged: 768 + 192 before, 192 + 768 after.**  Removing 570
instructions from `invntt16` with the store count held fixed buys 4.0 ns on M2;
cutting the stores 128 -> 32 buys 73.4 ns.  A store µop costs ~0.5 cycles on
either side of the boundary, so relocating the transpose nets:

| | M2 Pro | Cortex-A76 |
|---|---:|---:|
| `invntt16` saves | -73.4 ns | -58.7 ns |
| `packed_i9` pays | +87.4 ns | +332.1 ns |
| **P95 net** | **+14.0 ns** | **+273.4 ns** |

P95 is a loss on both machines.  `ST1 {v.H}[lane]`, which needs no repacking at
all, is a 22% A76 regression on its own -- two µops there, and it blocks the
store pipe -- so it fails 兩台都不得退步 outright.

## What survives

Only cutting the *total* store count helps, and the one boundary with slack is
the final output, whose layout is fixed by matching Official.  Unconstrained,
`invntt16` dumps sixteen whole vectors per call and drops the 32 EXT
self-rotates that exist only to feed the UMOV: **-86.8 ns on M2, -77.2 ns on
A76, with `packed_i9` untouched.**

GT's inverse trails Official's by +106 ns on M2 (P92).  86.8 of that is this one
boundary.  The open question is whether the consumer -- `crepmod3_ternary_asm`
and the serializer behind it -- can absorb the permutation for free; that is the
question the store-budget result now makes worth asking.

This also explains the A76/M2 split the campaign keeps meeting.  Cutting stores
eightfold is worth 44% on M2 and 9% on A76: A76 is multiply-port bound, so the
stores sit in the shadow, and M2 has no shadow.

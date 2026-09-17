# P22 — `invntt16_tail` in assembly

Branch `neon-1152`, parent `30aa4e2f`.  Pi 5 core 3, GCC 14.2.0.

P21 ranked this first: the C tail measured **1,469 cycles** alone, more than the
whole inverse deficit of +1,134.  D8 always named assembly as the target and C
as the Milestone 1 stand-in.

**311 cycles, 4.7x faster.  `inverse` went from +1,134 to -14, decaps from
+3.11% to +0.90%, and the whole KEM from +0.65% to +0.00%.**

## 1. Why the port is two changes, not a rewrite

D6 established that this kernel could not be carried over by remapping
immediates — it is called once and covers every component, so its output count
grows from 96 to 128 — and that the tail's vector arithmetic is eight-lane and
element-wise, so the lanes 864 leaves as padding already hold correct results.

Reading the 864 kernel makes that exact.  Of its 589 instructions, only two
kinds are not element-wise:

**The fold over `top`.**  864 packs the tail scratch as `lane = 3*top + branch`,
six lanes of eight, and folds with

```
ext vD.16B, vA.16B, vA.16B, #6      ; rotate three halfwords
add vD.8H,  vA.8H,  vD.8H           ; vD[i] = vA[i] + vA[i+3]
```

1152 packs `lane = 4*top + branch`, all eight lanes used, so the rotation
becomes four halfwords: **`#6` -> `#8`**.  There are exactly 32 such `ext`, all
self-rotates, each paired with its `add`; the generator asserts all of it.

**The output extraction.**  864 writes `out[27k + branch]` for branch < 3 —
three halfwords, six bytes, never a clean store width — so it spends three
`umov` and three `strh` per output, 96 of each.  1152 writes `out[36k + branch]`
for branch < 4: four halfwords, **eight bytes, exactly one `str d`** of the
folded vector's low half.  192 instructions become 32.  That is the same
degree-4 alignment dividend P18 collected in the codec.

Result: 589 instructions become **430**.

## 2. One table had to be repacked, and the kernel says which

The tail reads two tables.  Counting how each is used settles it:

| table | loads | uses |
|---|---:|---|
| `x3` = `invntt16_constants` | 6 | 35, **all lane-indexed** |
| `x4` = `invntt16_tail_constants` | 64 | 64, **all full-vector** |

A lane-indexed table is a constant pool and carries unchanged.  A full-vector
table's lanes line up with the data lanes, so it is packed for 864:

```
[A, A, A, B, B, B, 0, 0]      ->      [A, A, A, A, B, B, B, B]
```

All 64 rows were asserted to have that shape before rewriting.  No value
changes.  `invntt16_main_constants` is left alone and verified byte-identical to
the package's copy: `invntt16_asm` packs its lanes by the 16-axis, not by
(top, branch).

## 3. Two defects the differential caught

Both were found by the unit differential against the C contract, not by the KAT.

**The table packing.**  First run: 4,352 mod-q mismatches out of 8,192, with
outputs equal to raw table values.  Cause as above.  After repacking: 511.

**Store placement.**  The remaining 511 were whole outputs reading back a table
row.  The generator had put each `str d` where the first `strh` was; Slothy
reuses these vector registers aggressively and several are overwritten between
an output's `umov` and its `strh`.  Moving the store to the **`umov` position**,
where the value is provably still live, fixed it.

## 4. Correctness

Unit differential against the C tail, which is the declared contract (its map
was measured from the 864 kernel by 128 delta probes):

```
4,000 trials x 128 outputs = 512,000 outputs
inputs uniform on [-2617, 2617] plus 200 trials at the +/-2617 extremes
mod-q mismatches: 0
max |output|:     3920      (864 declares the ternary consumer takes <= 5028)
```

Exact mismatches are expected and not a defect: the C version applies a final
Barrett to pick one representative, the assembly emits its own.  The consumer is
`crepmod3_ternary_asm`, which reduces mod q.

Package gates on the Pi, all green:

```
KAT sha256  2ddfc810c44f63f8d24086da7c33faf17d66c393f519a5b9cb76b0b7509464c3
test_kem            64 round trips + tampered rejection
test_canonical      cases=13824 failures=0
test_abi            11/11 sentinel masks 0x00000, inverse-ternary included
test_baseinv_fail   288/288 reject, clear, alias-clear
test_zeroization    clear_calls=26 clear_bytes=37526 nonzero_after=0
SOURCE-MANIFEST     43 files verify
```

## 5. Measured

| | cycles |
|---|---:|
| `invntt16_tail_asm`, C (P21) | 1,469 |
| **`invntt16_tail_asm`, assembly** | **311** |
| saving per call | **-1,158** |

| operation | official | GT | delta | was |
|---|---:|---:|---:|---:|
| keygen | 64,061 | 64,737 | +1.06% | +1.08% |
| **encaps** | 59,482 | **58,340** | **-1.92%** | -1.97% |
| decaps | 52,584 | 53,055 | **+0.90%** | +3.11% |
| **total** | **176,127** | **176,132** | **+0.00%** | +0.65% |

| category | official | GT | delta | was |
|---|---:|---:|---:|---:|
| inverse | 6,292 | 6,278 | **-14** | +1,134 |

**The KEM is at parity with the official**, five cycles apart on 176,000, with
the hash still the generic sponge.

## 6. Next

P21's order continues: `poly_sotp_decode` (+835, 144 horizontal reductions where
the official uses a bit-transpose), then `poly_basemul_rinv` (+834, M2-2).

The tail is now 430 unscheduled instructions carrying 864's schedule, which no
longer describes it.  Slothy on this kernel is a later question, not a blocker.

## Reproduce

```sh
python3 generate_tail.py        # emits inverse16_tail.S and inverse16_tables.h
gcc -O2 -march=native -I. diff.c ref_tail.c inverse16_tail.S -o diff && ./diff
```

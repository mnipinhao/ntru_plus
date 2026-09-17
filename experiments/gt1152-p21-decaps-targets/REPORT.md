# P21 — What to do next, after the codec and before the hash

Branch `neon-1152`, parent `645081a4`.  Analysis gate: no code changed.

P19's aggregate table ranked `baseinv` (+2,406) as the largest remaining item.
Per operation that is misleading.

## 1. Only decapsulation is still losing

| operation | attributed delta | the losses in it |
|---|---:|---|
| keygen | **+454** | `baseinv` +2,406 alone; everything else wins enough to nearly cancel it |
| encaps | **-1,271** | already ahead; only `hash` +1,110 |
| **decaps** | **+2,085** | four items, below |

SUPERCOP agrees: keygen +1.17% (q1), encaps -1.77%, decaps +3.29%.

`baseinv` is **keygen-only**, and keygen is the operation least behind.

## 2. Decapsulation, component by component

| GT | cycles | official counterpart | cycles | delta |
|---|---:|---|---:|---:|
| `poly_invntt_ternary` | 7,433 | `poly_invntt` 5,658 + `poly_crepmod3` 641 | 6,299 | **+1,134** |
| `poly_sotp_decode` | 1,343 | `poly_sotp_decode` | 508 | **+835** |
| `poly_basemul_rinv` | 3,385 | `poly_basemul_scale` | 2,551 | **+834** |
| `poly_frombytes` (3) | 2,187 | `poly_frombytes` (3) | 1,524 | +663 |
| `poly_tobytes_compare` + `_small` | 2,175 | `poly_tobytes` (2) | 2,302 | -127 |
| `poly_basemul` | 3,146 | `poly_basemul` | 3,409 | -263 |
| `poly_ntt` (2) | 8,760 | `poly_ntt` (2) | 9,629 | **-869** |

## 3. The three tractable targets, measured

**`invntt16_tail`, C -> assembly.**  Measured standalone this gate:
**1,469 cycles per call**, inside `poly_invntt_ternary`'s 7,433.  That single
function is larger than the whole inverse deficit.  NTRU+864's
`inverse16_tail.S` is **592 instructions with a Slothy estimate of 147 cycles**.
D6 already established the shape of the 1152 version: the tail's vector
arithmetic is already eight-lane and matches the main kernel's, so the two lanes
864 leaves as padding already hold correct results — **the gap is exactly 32
`umov`/`strh` pairs**, 96 outputs becoming 128.  So this is 592 + 64 = 656
instructions of known-correct arithmetic, not a re-derivation.  Expected saving
of order 1,200 cycles.  D8 always named assembly as the target and C as the
Milestone 1 stand-in.

**`poly_sotp_decode`.**  1,343 against the official's 508, 2.6x.  Cause found
this gate: P13's NEON version does a horizontal `vaddvq_u16` **per output byte**,
144 of them, because it packs eight 0/1 lanes into a byte by multiplying by
`{1,2,...,128}` and reducing.  The official has no horizontal reduction at all —
its `cbd.s` narrows with `sqxtn`, runs a **bit-transpose network** (`trn` at
.4s, .8h and .16b), then `add`/`shl`/`orr` to assemble the bytes.  That is the
same substitution P18 made in the codec: replace a reduction with a transpose.
No new mathematics, and the official's own source is the reference.

**`poly_basemul_rinv`.**  3,385 against 2,551.  Degree-4 intrinsics C, sixteen
products, never scheduled.  This is M2-2 exactly as planned.

## 4. What not to attack

`poly_frombytes` at +663 is **structural**.  P19 measured it at its issue floor:
the cost is the Good-Thomas permutation, which the official never performs.  It
is 729 cycles a call against 509 and there is no mechanism left.

## 5. Recommended order

1. **`invntt16_tail` in assembly** — largest, measured, already-shaped by D6, and
   the declared plan.  Should flip `inverse` from +1,134 to a win.
2. **`poly_sotp_decode`** — cheapest of the three, no new mathematics, the
   official's technique is readable in `cbd.s`.
3. **`poly_basemul_rinv`** — M2-2, the first Slothy gate.

If all three reach parity, decaps goes from +2,085 to roughly -900, and every
operation beats the official before the hash campaign starts.

`baseinv` (+2,406) comes after, to turn keygen's +454 into a clear win.

## Reproduce

```sh
gcc -O3 -march=native -D_DEFAULT_SOURCE -I<pkg> tailbench.c <pkg>/inverse16_tail.c -o tb
taskset -c 3 ./tb
```

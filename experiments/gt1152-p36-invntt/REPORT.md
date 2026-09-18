# P36 — the inverse transform: where its cycles go, and why its 12% is not cashing

Branch `neon-1152`, parent `075a32aa`.  Pi 5 core 3, GCC 14.2.0 `-march=native
-O3`, `taskset -c 3`.  Every figure below reproduced to the last printed digit
across consecutive runs.

P34 closed the forward: its 9.96% static multiply advantage cashed out as 9.04%
measured, and both sides sat the same distance above their issue floor.  **The
inverse does not behave that way.**  Static advantage is **11.95%** and the
measured advantage is **−0.29%**.  This gate finds out where it goes.

## 1. The static counts

Loop bounds read off the labels, not assumed — P34's lesson.

| official `poly_invntt_scale` + `poly_crepmod3` | body | ×iters | ops |
|---|---|---:|---:|
| `_looptop_6543` (l.633–801) | 20 mls + 16 mul + 20 sqrdmulh = 56 | 18 | 1,008 |
| `_looptop_210` (l.813–1295) | 69 + 63 + 69 = 201 | 8 | 1,608 |
| `poly_crepmod3` (`crepmod3.s`) | 4 mls + 4 sqrdmulh = 8 | 36 | 288 |
| | | | **2,904** |

| GT `invntt_ternary_asm` | per call | calls | ops |
|---|---|---:|---:|
| `packed_i9` | 19 × 3 = 57 | 16 | 912 |
| `invntt16_asm` | 51 + 49 + 51 = 151 | 8 | 1,208 |
| `invntt16_tail_asm` | 50 + 49 + 50 = 149 | 1 | 149 |
| `crepmod3_ternary_asm` | 8 | 36 | 288 |
| | | | **2,557** |

`2,557 × 2.000 = 5,114`, which is the multiply floor P25 recorded — independent
agreement that the count is right.

## 2. Measured, by stage

`generate_variants.py` emits seven copies of the driver with one stage removed
each; stage cost is the difference.  That attributes without re-deriving the
driver's own address arithmetic, which is part of what we are measuring.  Every
kernel here is straight-line and constant-time, so removing a `bl` changes the
data later stages see but not the cycle count — the same assumption the
package's constant-time claim already rests on.

```
  official invntt_scale + crepmod3       6237.9      (invntt 5617.0 + crepmod3 591.0)
  GT invntt_ternary_asm (whole)          6219.8

  packed_i9 x16            2215.3   (138.5 each)
  invntt16_asm x8          2702.8   (337.9 each)
  invntt16_tail_asm         306.8
  crepmod3_ternary_asm      576.8
  the 2304-byte wipe        139.0
  driver skeleton           275.0
  stages + skeleton        6215.7   vs whole 6219.8
```

## 3. The floors, and the correction that mattered

**First attempt was wrong and said so loudly.**  I built the mix floors by
grouping each kernel's instructions by opcode — 86 consecutive `ldr q`, then 128
consecutive `umov`/`strh` pairs — and they came back at **112.5%** and **153.5%**
of the kernels they were meant to bound.  A floor above the thing it bounds is
not a floor: clustering by opcode manufactures a serialization on one resource
that the real kernel avoids by interleaving.

The corrected probes keep each kernel's instruction sequence exactly as Slothy
emitted it — same opcodes, operand forms, order, and GPR names, so the same
`umov`/`strh` pairing distances — and rewrite only the vector **source**
operands to a pool the body never writes.  Dependencies that are inherent stay:
an `mls` still reads its own destination.

```
  floor: GT multiply multiset (2557 ops)        5111.0
  floor: official multiply multiset (2904 ops)  5805.0
  floor: packed_i9 instruction mix x16          2005.0
  floor: invntt16_asm instruction mix x8        2557.9
```

**Both mix floors are above the corresponding multiply floors** — 2,005 against
1,824, and 2,557.9 against 2,416.  So for neither kernel is the multiply pipe
the binding resource, and the "82% of floor" headline was measured against a
floor that does not bind.

| stage | measured | binding floor | of floor | headroom |
|---|---:|---:|---:|---:|
| `packed_i9` ×16 | 2,215.3 | 2,005.0 (mix) | **90.5%** | 210.3 |
| `invntt16_asm` ×8 | 2,702.8 | 2,557.9 (mix) | **94.6%** | 145.0 |
| `invntt16_tail_asm` | 306.8 | 298.0 (multiply) | 97.1% | 8.8 |
| `crepmod3_ternary_asm` | 576.8 | 576.0 (multiply) | **99.9%** | 0.8 |
| the wipe | 139.0 | ~144 (store pipe) | **at floor** | 0 |
| driver skeleton | 275.0 | — | — | **275.0** |

## 4. Why the 12% does not cash

Three separate reasons, and only one of them is a scheduling problem.

**(a) 414 cycles the official does not spend at all.**  The official is one
function with two loops.  GT is a driver over a 2,304-byte stack scratch, so it
pays a **275-cycle skeleton** (address arithmetic for 26 `bl`s) and a
**139-cycle wipe**.  The wipe is at the store pipe's floor — 2,304 bytes is 72
`stp q` is 144 128-bit stores is 144 cycles — so it is irreducible *given the
scratch*, not given the algorithm.

The skeleton is not irreducible.  Per `packed_i9` call the driver issues

```asm
    mov x8, #8      ; madd x1, x26, x8, x1
    mov x8, #1152   ; madd x2, x26, x8, x2
    mov x8, #64     ; madd x2, x28, x8, x2
    mov x8, #576    ; madd x3, x26, x8, x3
    mov x8, #288    ; madd x3, x28, x8, x3
```

— five loop-invariant constants reloaded on every one of 16 iterations, feeding
chained 3-cycle `madd`s, in a perfectly regular nest whose strides are fixed.
Hoisting the constants and advancing the pointers incrementally should recover
most of the 275.

**(b) GT's kernels carry more non-multiply work per multiply.**  Above their own
multiply floors: GT's four kernels 700 cycles over 2,557 multiplies (0.274
each); the official's two loops 433 over 2,904 (0.149).  That is the price of
the Good-Thomas decomposition on this side — `packed_i9` is 30% multiply by
instruction count and `invntt16_asm` 23%, against the official's loops which are
44% and 57%.  It is not a defect; it is what buys the 12% fewer multiplies.

**(c) Neither big kernel has ever been scheduled for 1152.**  Their own headers
say so:

> *Immediate remap of NTRU+864's inverse16.S (natural-order store pitch 6m →
> 8m). The instruction multiset is preserved, so NTRU+864's A76 schedule stays
> legal — **but no solver was run for 1152**, so Slothy's cycle annotations were
> stripped rather than carried over.*

G6 reused 864's schedule by immediate remapping and argued legality from the
unchanged multiset.  That argument is sound for **legality** and says nothing
about **optimality**: 864's schedule was solved against 864's strides.  The one
inverse kernel that *was* re-derived for 1152 — `invntt16_tail_asm`, where P22
turned 96 `umov`/`strh` pairs into 32 `str d` — is the one now at 97.1%.

## 5. What is available

| item | cycles | character |
|---|---:|---|
| driver skeleton | ~275 | plain waste; hoist constants, walk pointers |
| `packed_i9` schedule | ~210 | never solved for 1152; 90.5% |
| `invntt16_asm` schedule | ~145 | never solved for 1152; 94.6% |
| the wipe | 139 | at the store-pipe floor; structural only |
| tail, crepmod3 | ~10 | closed |

Realistically **~630 of 6,220, about 10%**, which would put the inverse at
roughly **−10% against the official** instead of level — close to what the
static multiply count promises.

Two caveats worth stating.  `packed_i9` at 90.5% is right at the line this
campaign has used to *reject* scheduling three times (P16 93%, P18 90%, P30
90%); what makes it different is that those three had been solved and this has
not.  And `invntt16_asm` at 94.6% is past that line — the 145 there is probably
not reachable by scheduling alone.

## Reproduce

```sh
python3 generate_variants.py && python3 generate_floors.py
G=<gt1152-p10-kem>; OFF=<supercop>/crypto_kem/ntruplus1152/aarch64
cp $OFF/ntt.s off_ntt.s; cp $OFF/crepmod3.s off_crepmod3.s
gcc -O3 -march=native -D_DEFAULT_SOURCE -I. bench_inv.c inv_variants.S \
    probes_inv.S inv_floors.S off_ntt.s off_crepmod3.s \
    $G/inverse9.S $G/inverse16.S $G/inverse16_tail.S $G/crepmod3_raw.S -o bench_inv
taskset -c 3 ./bench_inv
```

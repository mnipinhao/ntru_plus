# P16 — `ntt9.S`: where the forward NTT's cycles go, and what is left to take

Branch `neon-1152`, parent `a1d80dcd`.  All cycles are PMU cycles on Pi 5 core 3,
GCC 14.2.0 `-march=native`, 20,000 reps after 50 warm-ups, `taskset -c 3`.

Context: P11 found `poly_ntt` is GT's single biggest *win*, 2,592 cycles faster
than the official's.  The question this gate answers is whether there is more in
it, and by what mechanism.  **The answer is no, and the reason is structural
rather than a matter of scheduling.**

## 1. The forward NTT is `ntt9.S` and essentially nothing else

Reproducer: `stages.c`, linked against the package's `ntt.S ntt_top.S ntt_tail.S
ntt9.S`.

| stage | cycles/call | share |
|---|---:|---:|
| `ntt_top_asm` | 449 | 10.3% |
| `ntt_tail_asm` | 35 | 0.8% |
| **`ntt9_asm`** | **3,871** | **89.1%** |
| sum | 4,355 | |
| `ntt_asm` measured whole | 4,346 | (sum is within 0.2%) |

`ntt9_asm` runs 8 banks, so **484 cycles per bank**.

## 2. One bank is 512 instructions, and 225 of them are multiplies

`.Lntt_one_bank` is `ntt9.S:233-745`, 513 lines, 512 instructions:

| | count |
|---|---:|
| `sqrdmulh` / `mul` / `mls` | 75 / 75 / 75 |
| `add` / `sub` | 74 / 84 |
| `trn1` / `trn2` | 27 / 27 |
| `ldr` (q) | 66 |
| `orr` / `tbl` / `ret` / `ldp` | 5 / 2 / 1 / 1 |

The three multiply mnemonics appear in a fixed triple — the Barrett-Shoup
multiply by a twiddle:

```
mul      lo, a, z            ; z        = twiddle
sqrdmulh hi, a, z_shoup      ; z_shoup  = round(z * 2^15 / q)
mls      lo, hi, q           ; lo -= hi * q
```

So a bank performs exactly **75 twiddle multiplications**, 54 of them
lane-indexed (one twiddle broadcast over 8 lanes) and 21 full-vector (a
different twiddle per lane).  Every `mls` is full-vector, as it must be.

## 3. All three multiply forms are pinned to one pipe at 2 cycles each

The Slothy Cortex-A76 model says so:

- `slothy/targets/aarch64/cortex_a76.py:265` — `(Vmul, Vmla, Vqdmulh, Vmull,
  Vmlal): ExecutionUnit.V0()`, and `V0()` is `[VEC0]`, a single pipe.
- the `inverse_throughput` table — `(Vmul, Vmla, Vqdmulh): 2` against
  `(vadd, vsub, vumax, vmov, ASimdCompare, Transpose): 1` on `V()` = both pipes.
- `aarch64_neon.py` — `sqrdmulh` is `vqrdmulh`/`vqrdmulh_lane` under `Vqdmulh`,
  `mls` is `vmls`/`vmls_lane` under `Vmla`, `mul` is `vmul`/`vmul_lane` under
  `Vmul`.  All three are in the `V0()` set.

**Confirmed on the hardware itself**, not just in the model.  `pipe.c` runs
twelve independent chains so latency never binds:

| body | cycles per op |
|---|---:|
| `sqrdmulh` x12 | **2.000** |
| `mul` x12 | **2.000** |
| `add` x12 | 0.500 |
| `trn1` x12 | 0.500 |
| `sqrdmulh` x12 + `add` x12 | **2.000** per multiply |
| `sqrdmulh` x12 + `trn1` x12 | **2.000** per multiply |

The last two rows are the decisive ones: adding an equal number of adds or
transposes to the multiplies costs *nothing*.  Non-multiply vector work hides
completely in the multiply pipe's shadow.

## 4. The kernel is at 93% of the hardware floor

225 multiplies x 2 cycles on the one pipe that can run them:

```
floor       = 450 cycles per bank
measured    = 484 cycles per bank
utilisation = 93.0%
```

The other 219 vector ops (add, sub, trn, orr, tbl) and 66 loads fit entirely
inside those 450 cycles: 219 at one per cycle on VEC1 and 66 loads across two
load pipes are both well under the bound.  Nothing else can bind.

**Consequence for scheduling.**  The whole slack is 34 cycles per bank, 271 per
call, and `poly_ntt` is called 6 times across the three KEM operations:

```
1,626 cycles = 0.85% of 190,214
```

That is the *unreachable ceiling* on running Slothy over `ntt9.S` — the value of
a schedule that leaves the multiply pipe with zero idle cycles.  D4's decision to
run no solver in Milestone 1 costs at most this much, and this gate closes the
question rather than deferring it: **`ntt9.S` is not worth scheduling.**

## 5. The only lever is issuing fewer multiplies, and it is nearly exhausted too

Both known NEON int16 modular-multiply idioms cost the same 6 VEC0 cycles:

| idiom | VEC0 cycles |
|---|---:|
| Barrett-Shoup (what `ntt9.S` uses): `mul`(2) + `sqrdmulh`(2) + `mls`(2) | 6 |
| widening Montgomery: `smull`(1) + `smull2`(1) + `mul`(2) + `smlal`(1) + `smlal2`(1) | 6 |

The widening form looks cheaper per instruction — `(Vmull, Vmlal): 1` in the
throughput table — but it needs five multiply-class ops to cover 8 lanes instead
of three, and lands on exactly the same total.  The `uzp1`/`uzp2` it also needs
are free.  **There is no cheaper way to multiply by a twiddle on this core.**

So the count itself is the only remaining variable.  75 vector twiddle
multiplications is 600 lane-multiplications for a 144-point transform, against
roughly `(144/2)*log2(144) = 516` for an idealised radix-2 transform of that
size with perfect 8-lane packing.  The kernel is within ~16% of a bound that
already ignores the real obstacle — 9 rows do not fill 8 lanes, which is the same
odd-9 misalignment that forces `ntt_tail` and `inverse16_tail` to exist.
Recovering even that 16% means replacing the transform decomposition, not
editing the kernel.

## 6. What this gate settles

1. **`ntt9.S` is multiply-throughput bound at 93% of the hardware ceiling.**  It
   is hand-written and has never been Slothy-scheduled, and that turns out not to
   matter: the hand schedule is already close to optimal for this instruction
   mix.
2. **Slothy on `ntt9.S` is worth at most 0.85% of the KEM and realistically much
   less.**  Recorded so no later gate re-opens it on the assumption that an
   unscheduled 846-line kernel must contain headroom.
3. **P14's reopen condition is now void.**  P14 parked Option A (natural-order
   forward output, net -1,612 cycles) behind "worth revisiting only if `ntt9.S`
   is being restructured for some other reason, so the four-component grouping is
   paid for anyway."  No such reason exists: there is no performance case for
   restructuring `ntt9.S` at all.  Option A stays rejected on its own -1,612, and
   now with no path to becoming cheaper.
4. **The forward NTT is finished.**  It is 2,592 cycles ahead of the official and
   within 271 cycles per call of what the silicon permits.  Remaining effort
   belongs to the hash (M2-1, ~45% of total) and the items P11 already ranked.

## Reproduce

```sh
gcc -O2 -march=native -D_DEFAULT_SOURCE stages.c \
    <pkg>/ntt.S <pkg>/ntt_top.S <pkg>/ntt_tail.S <pkg>/ntt9.S -o stages
taskset -c 3 ./stages
gcc -O2 -march=native -D_DEFAULT_SOURCE pipe.c -o pipe
taskset -c 3 ./pipe
```

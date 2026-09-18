# P37 — flattening the inverse driver: 275 cycles of address arithmetic → 62

Branch `neon-1152`, parent `88860c76`.  Pi 5 core 3, GCC 14.2.0 `-march=native
-O3`, `taskset -c 3`.

P36 measured the inverse driver's skeleton at **275 of 6,220 cycles** and called
it the one item in that transform that is plain waste rather than a price paid
for the Good-Thomas decomposition.  This removes it.

**Skeleton 275.0 → 62.0.  The inverse 6,227 → 5,953 standalone, and against the
official 6,291 → 5,982, from −0.29% to −4.91%.  Decaps −13.96% → −14.40%; the
KEM −15.25% → −15.35%.**

## 1. What was there

Per `packed_i9` call, sixteen times:

```asm
    add x0, x25, x27, lsl #9
    add x0, x0, x28, lsl #7
    add x0, x0, x26, lsl #3
    add x1, x25, #2048
    add x1, x1, x28, lsl #7
    mov x8, #8      ; madd x1, x26, x8, x1
    add x1, x1, x27, lsl #1
    mov x8, #1152   ; madd x2, x26, x8, x20
    mov x8, #64     ; madd x2, x28, x8, x2
    add x2, x2, x27, lsl #4
    mov x8, #576    ; madd x3, x26, x8, x21
    mov x8, #288    ; madd x3, x28, x8, x3
```

Five loop-invariant constants reloaded into `x8` on every iteration, feeding
chained three-cycle `madd`s, in a nest whose trip counts and strides are all
fixed at assembly time.  Plus the same shape, smaller, for the eight
`invntt16_asm` calls.

## 2. What replaces it

The nests are 2 × 4 × 2 and 4 × 2, so there are only 16 + 8 call sites, and for
each one every pointer is a base register plus a **constant**:

| | expression | range over the 16 sites | fits `add #imm` (≤4095) |
|---|---|---|---|
| `x0` | scratch + 512c + 128b + 8t | 0 … 1672 | yes |
| `x1` | scratch + 2048 + 128b + 8t + 2c | 2048 … 2190 | yes |
| `x2` | in + 1152t + 64b + 16c | 0 … 1264 | yes |
| `x3` | tables + 576t + 288b | 0 … 864 | yes |

So each site becomes

```asm
    add x0, x25, #K0
    add x1, x25, #K1
    add x2, x20, #K2
    add x3, x21, #K3
    bl  C(packed_i9)
```

Loop order is preserved — (top, component, block), then (component, half) — so
the sequence of calls, and therefore every kernel's view of the scratch, is
unchanged.  The sites are independent anyway: their 128 tail-region halfword
slots are distinct and exactly fill scratch bytes 2048…2303.

Static size grows 137 → 218 instructions.  Dynamic address-and-bookkeeping work
falls from roughly 432 instructions to 128.

## 3. The constants are not transcribed

`generate_driver_flat.py` computes them from index algebra, and
`verify_constants.py` **symbolically executes the shipped nest's instructions**
— a small interpreter over `mov`/`add`/`add-shifted`/`madd`, which raises on
anything it does not recognise rather than skipping it — for every value of the
loop counters, and compares:

```
80/80 pointer constants agree with symbolic execution of the nest
```

That is the step worth not trusting, because it is where a hand-read index
formula would go wrong silently.

The generator also refuses to emit if any of `.Lp8inv_*` survives, if any `madd`
survives, if either nest's text is not found exactly once, or if any constant
exceeds the `add` immediate range.

## 4. Correctness

Differential against the shipped driver, both linked into one binary, over
every output coefficient — not a hash, so a mismatch would name the coefficient:

```
4000 trials x 1152 coefficients: 0 mismatches
```

The first four trials are the all-zero, all +2497, all −2497 and alternating
±2497 boundaries of the inherited input contract; the rest are uniform on
[−2497, 2497].

Package gate on the Pi, all green: KAT sha256 `2ddfc810c4…64c3`, 64 round trips
with tampered rejection, 13,824 canonical cases, 13/13 ABI sentinel masks zero,
288/288 baseinv leaves rejecting and clearing, `clear_calls=23
clear_bytes=32338 nonzero_after=0`.

## 5. Measured

Standalone, reproduced to the last digit across runs:

```
  driver: loop nest (shipped)           6227.4
  driver: flattened                     5952.5
    skeleton, loop nest                  275.0
    skeleton, flattened                   62.0

  skeleton  275.0 -> 62.0     (-213.0)
  whole     6227.4 -> 5952.5  (-274.8, -4.41%)
```

The whole saves 275 where the skeleton saves 213; the extra ~62 is the loop
branches no longer competing with the kernels for fetch.

In the KEM, component profiler, median of both directions:

| | official | GT | was |
|---|---:|---:|---:|
| `poly_invntt_scale` + `poly_crepmod3` vs `poly_invntt_ternary` | 6,290.9 | **5,982.0** | 6,272 |
| | | **−4.91%** | −0.29% |

| operation | official | GT | delta | was |
|---|---:|---:|---:|---:|
| keygen | 64,061 | 56,824 | −11.30% | −11.36% |
| encaps | 59,538 | 47,298 | −20.56% | −20.57% |
| **decaps** | 52,497 | **44,936** | **−14.40%** | −13.96% |
| **total** | **176,095** | **149,058** | **−15.35%** | −15.25% |

The inverse is one call, in decapsulation only, so the whole saving lands there.

## 6. What is left in the inverse

P36's table, updated:

| item | before | now | character |
|---|---:|---:|---|
| driver skeleton | 275 | **62** | done |
| `packed_i9` schedule | ~210 | ~210 | never solved for 1152; 90.5% of mix floor |
| `invntt16_asm` schedule | ~145 | ~145 | never solved for 1152; 94.6% |
| the 2,304-byte wipe | 139 | 139 | at the store-pipe floor; structural only |
| tail, crepmod3 | ~10 | ~10 | closed |

One crumb deliberately left: `x26`–`x28` are now unused in the driver body, so
`stp x27, x28` / `ldp x27, x28` in `SAVE_PUBLIC`/`RESTORE_PUBLIC` could go.  It
is worth about two cycles in 5,953 and would break the macro's pairing
symmetry, so it is recorded rather than taken.

**Also fixed:** `gt1152-p11-profile/build.sh` had drifted from the package
Makefile — it still listed `inverse16_tail.c` (a C file since replaced by P22's
assembly) and omitted `hash_fixed.c`, `keccakf1600.S` and the three
`basemul_rinv`/`baseinv` kernels, and it did not pass the three
`NTRUPLUS1152_ASM_*` defines, without which `inverse.c` compiles its C
fallbacks and the profile is of a different implementation.  Brought back in
step, with an assertion that fails if the lists drift again.

## Reproduce

```sh
python3 generate_driver_flat.py && python3 verify_constants.py
python3 generate_skeletons.py
G=<gt1152-p10-kem>
gcc -O2 -march=native -I. diff_test.c inverse_ntt.S inverse_ntt_ref.S \
    $G/inverse9.S $G/inverse16.S $G/inverse16_tail.S $G/crepmod3_raw.S -o diff_test
gcc -O3 -march=native -D_DEFAULT_SOURCE -I. bench_flat.c inverse_ntt.S \
    inverse_ntt_ref.S skeletons.S $G/inverse9.S $G/inverse16.S \
    $G/inverse16_tail.S $G/crepmod3_raw.S -o bench_flat
taskset -c 3 ./diff_test && taskset -c 3 ./bench_flat
```

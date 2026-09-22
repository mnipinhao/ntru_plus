# P97 — who consumes 864's inverse, and what freeing its layout would cost

P96 left one live lever: `invntt16` dumping sixteen whole vectors per call
instead of scattering 128 halfwords is **-86.8 ns on M2 and -77.2 ns on A76**,
with `packed_i9` untouched.  It needs the output layout freed from natural
order.  This prices that.

## The consumers are not the ones the roadmap named

`poly_invntt_ternary` has exactly one caller, `kem.c:283`, in decapsulation.
Its output `m` is read twice:

```c
poly_invntt_ternary(&m, &m);
poly_ntt(&f, &m);                      /* GT's own forward transform */
...
fail = poly_sotp_decode(msg, &m, buf2);
```

**The serializer is not in this path.**  `poly_tobytes` runs on `f`, the
re-encryption, never on `m`.

- `crepmod3_ternary_asm` is a streaming `ld1 {v2.8h-v5.8h}, [src], #64` ->
  `st1 ..., [dst], #64` loop, elementwise and position-blind.  **It absorbs any
  permutation for free.**  It was never the obstacle.
- `poly_ntt` gathers with `ld3 {v0.8h, v1.8h, v2.8h}` -- de-interleave by three,
  which is the `c` axis.  A free layout already has `c` in separate blocks, so
  this side is roughly neutral, not a cost.
- **`poly_sotp_decode` is the gatekeeper.**  It narrows with `sqxtn` and bit-packs
  coefficient `i` into bit `i` of `msg`.  That correspondence is fixed by the
  scheme, so it pins natural order.

## The cheapest materialisation, and why it still fails A76

The natural index is `27*(t + 16h) + 3j + c`, and the free layout puts `j` in
the lanes, `c` in the 128-halfword block and `h` in the lane halves.  So a
group's 24 main coefficients are one `ZIP .2D` per `c` followed by one `ST3` --
**`ST3`'s interleave-by-three is the `3j + c` axis exactly**, and `j = 8` rides
along as a single-lane `ST3` at offset 24.  Six loads and six zips per `t` serve
two groups.  284 instructions, 864/864 verified (`repack_check.c`).

| pass, 864 coefficients | M2 Pro | Cortex-A76 |
|---|---:|---:|
| `ZIP .2D` + `ST3` | **33.0 ns** | 93.7 ns |
| `TBL` interleave + `STR Q` | 32.6 | 113.8 |
| no interleave (floor: loads, zips, `STR Q`) | 29.8 | 69.3 |

| net against the -86.8 / -77.2 | M2 Pro | Cortex-A76 |
|---|---:|---:|
| free layout + repack pass | **-53.8 ns** | **+16.5 ns** |

On A76 the *floor* alone -- loading, zipping and storing 864 halfwords with no
interleave at all -- eats 90% of the saving.  **The stores P96 removes were free
on A76 because they hide in the multiply-port shadow; a separate movement pass
has nothing to hide behind and pays full price.**  That is the same asymmetry
the campaign keeps meeting, now in a form that kills the cheapest fix.

`TBL` is worse still on A76: three-source table lookup is several µops there,
while on M2 it ties `ST3`.

## What is left

Never materialise natural order: let both consumers read the free layout.

- `poly_ntt` is the easy half -- its `ld3` is undoing an interleave the free
  layout never applied.  Six `ldr q` + six `zip` per two groups against two
  `ld3` is roughly even on A76 and better on M2.
- `poly_sotp_decode` pays the three-way interleave once, in registers, feeding
  its existing `sqxtn` and bit-pack rather than memory.  The A76 bound on that
  work is the 93.7 - 69.3 = **24.4 ns** measured here, against 77.2 saved.

That is the only shape in which this clears 兩台都不得退步, and it is a rewrite
of `cbd.S`'s decode plus `ntt_top.S`'s front end -- not a store-addressing
change.

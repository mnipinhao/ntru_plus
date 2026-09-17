# GT1152-P14 — should the transform output natural order?

The proposal on the table was: have the inverse NTT output natural order so the
codec's permutation disappears. **Measured, and the answer is no.**

```sh
gcc -O3 -march=native -D_DEFAULT_SOURCE -I. micro.c -o micro && taskset -c 3 ./micro
```

## First, the proposal was aimed at the wrong end

`poly_invntt_ternary` **already** stores natural order — that is its documented
live-out — and its result goes to `poly_sotp_decode` and `poly_ntt`, never to
the codec. Tracing every codec call in `kem.c`:

| call | fed by | layout |
|---|---|---|
| `poly_tobytes(sk, f)` | `poly_ntt` | GT |
| `poly_tobytes_small(pk, &h)` | `poly_basemul` | GT |
| `poly_tobytes_small(ct, &c)` | `poly_basemul_add` | GT |
| `poly_tobytes_small(buf1, &f)` | `poly_basemul` | GT |
| `hash_g_fr0(ct, r.coeffs)` | `poly_ntt` | GT |
| `poly_tobytes_compare` | `poly_ntt` | GT |
| `poly_frombytes` × 4 | wire | must produce GT |

So the real question is whether the **forward** should store natural order.

## The measurements

Cycles per 1152-coefficient pass, Pi 5 core 3, 20,000 reps after 50 warm-ups:

| pass | cycles |
|---|---:|
| contiguous copy (the floor any pass pays) | 156 |
| permute GT → natural | 941 |
| permute natural → GT | 1,418 |
| 12-bit pack only | 461 |
| SoA pass with LD1×4 / ST1×4 | 160 |
| SoA pass with LD4 / ST4 | 472 |

So the **net permutation** is 780 writing and 1,265 reading, and **LD4/ST4 costs
312 more than LD1/ST1**.

## Option A — forward stores natural order

| | cycles |
|---|---:|
| save: codec loses its permutation (6 tobytes-family + 4 frombytes) | −9,741 |
| cost: basemul, basemul_add, basemul_rinv, baseinv × 2 move to LD4/ST4 | +2,183 |
| cost: forward's 144 `str q` become 288 lane-indexed ST4, × 6 calls | +4,682 |
| cost: `packed_i9` reads natural order | +1,265 |
| **net** | **−1,612** |

**1,612 cycles out of 190,214 — 0.85%.** And that is before the structural
problem: `ntt9.S` processes **one bank at a time**, and a bank is one component.
The natural-order interleave needs all four components of a group live
simultaneously, so the 846-line kernel would have to be restructured to produce
four banks together, at four times the live output registers. The basemul family
would also need a re-derived natural-order zeta table, and `packed_i9` new input
addressing.

Large, risky, contract-changing — for 0.85%.

## Option B — keep the layout, fuse the codec

The current codec runs the permutation, the reduction and the pack as separate
passes over a scratch array. Fusing them approaches the sum of their measured
parts:

| | now | floor | official |
|---|---:|---:|---:|
| `poly_tobytes` | 2,367 | 1,402 | 1,148 |
| `poly_frombytes` | 2,189 | 1,886 | 505 |
| serialize total | 21,024 | **15,958** | 10,086 |

**≈5,066 cycles recoverable**, with no contract change, no transform change, and
the existing byte oracle still applying unchanged.

## Conclusion

**Option B is roughly three times the payoff at a small fraction of the risk.**
Option A is rejected, and recorded as rejected rather than dropped.

The honest limit either way: at its floor GT's serialize is 15,958 against the
official's 10,086. That residual **+5,872 is the permutation**, and it is
structural — the official does no permutation at all, because its transform
already leaves coefficients in natural order. Option A is the only thing that
removes it, and it removes it by moving an equivalent cost into the forward, the
arithmetic and the inverse.

### Reopen condition

Option A becomes worth revisiting only if `ntt9.S` is being restructured for
some other reason, so the four-component grouping is paid for anyway. It should
not be undertaken on its own.

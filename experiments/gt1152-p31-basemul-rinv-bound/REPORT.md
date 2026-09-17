# P31 — D7's normalization was never needed

Branch `neon-1152`, parent `06c6c1da`.  Pi 5 core 3, GCC 14.2.0.

P24 found that the official's `poly_basemul_scale` issues an **identical**
multiply multiset to ours and differs only by having no reduction at the end,
and concluded the remaining gap was scheduling.  P27 scheduled it, leaving +227.

**The +227 was D7's normalization, and D7's premise was wrong.**  Removing it
takes `poly_basemul_rinv` from +227 to **-142** — faster than the official — and
the KEM from -2.51% to **-2.69%**.

## 1. Where 2752 came from

D7 added a normalization because `basemul_rinv`'s output was bounded at 2752,
above the inverse NTT's inherited input contract of 2497, and bringing it inside
let NTRU+864's bound chain hold a fortiori rather than needing re-derivation.

That 2752 assumes inputs on **[0,4095]**, which is what `inverse.h` declared.
The declaration was looser than the truth.  The only caller is decapsulation:

```c
if (poly_frombytes(&c,ct) || poly_frombytes(&f,sk) || poly_frombytes(&hinv,...))
    goto cleanup;
poly_basemul_rinv(m.coeffs, c.coeffs, f.coeffs);
```

`poly_frombytes` rejects any coefficient `>= q`, the `||` short-circuits, and any
failure aborts.  So both operands reaching `basemul_rinv` are **canonical**,
every coefficient in [0,q).

## 2. The bound on the real domain

With `|a|, |b| <= q-1` the widened accumulator over four products is at most
`4(q-1)^2 = 47,775,744`, and the signed Montgomery bound is

```
q/2 + 4(q-1)^2 / 2^16  =  1728.5 + 729.0  =  2458   <   2497
```

inside the contract with 39 to spare, so the 864 chain still holds a fortiori
and **nothing is re-derived**.

Probed over 20,000 trials on that domain, including the all-`q-1` case and
random extremes:

```
max |output|   2266      analytic bound 2458, contract 2497
```

`inverse.h` and `inverse_asm.h` now state the canonical precondition rather than
[0,4095], which is the actual change: a declaration corrected to match what the
caller already guarantees.

## 3. Measured

The kernel loses 24 operations a group — four vectors times
`cmgt, and, sub, cmgt, and, add` — so the clean source went from 126 to 98
instructions and SLOTHY re-solved in 191 seconds.

| | cycles |
|---|---:|
| with normalization, scheduled (P27) | 2,744 |
| intrinsics C, no normalization | 2,485 |
| **scheduled, no normalization** | **2,379** |
| official `poly_basemul_scale` | 2,551 |

Byte-identical to the C over 4,000 trials on the canonical domain, `max |out|`
2266.

## 4. Whole KEM

| operation | official | GT | delta | was |
|---|---:|---:|---:|---:|
| keygen | 64,044 | 62,046 | -3.12% | -3.19% |
| encaps | 59,547 | 58,248 | -2.18% | -2.05% |
| **decaps** | 52,496 | **51,051** | **-2.75%** | -2.21% |
| **total** | **176,087** | **171,345** | **-2.69%** | -2.51% |

`poly_basemul_rinv` is **-142** where it was +227.  Every package gate green,
`basemul-inverse` ABI sentinel included.

## 5. What this leaves

Of the three components that were still losing:

| | then | now |
|---|---:|---:|
| `hash_g_fr0` vs the official's second `hash_g` | +1,090 | +1,090 |
| `poly_frombytes` | +895 | +599 |
| `basemul_rinv` | +227 | **-142** |

`frombytes` has about 69 cycles a call of scheduling headroom left and then its
198-cycle transpose, which is minimal.  `hash_g_fr0` is M2-1's territory.

The lesson is worth recording separately: **a declared contract looser than the
caller's actual guarantee cost 227 cycles**, and three gates (D7, P24, P27)
reasoned from the declaration without checking it against the call site.

## Reproduce

```sh
# the bound, on the canonical domain
gcc -O2 -march=native -I. probe.c probe_impl.c ip.o -o probe && taskset -c 3 ./probe
# the kernel
cd dev/ntruplus1152_opt && python3 optimize.py basemul_rinv cortex_a76
```

# GT1152-P02 — degree-4 range and scale bounds

Second gate. Pure Python; no assembly, no hardware.

Every NTRU+864 bound is proved for degree-3 accumulators and does not transfer.
This gate derives the degree-4 chain, and resolves decision **D7** (whether
`basemul_rinv` needs a normalization to keep NTRU+864's inverse input contract).

```sh
make check      # bounds.py + instrument.py
```

| file | role |
| --- | --- |
| `bounds.py` | Exact interval derivation → `bounds-report.json`. **This is what proves.** |
| `instrument.py` | Instruments the G1 oracle over real KEM runs → `empirical-report.json`. Necessary, not sufficient; it catches a derivation written down wrong. |

## Method

`montgomery_reduce` is modelled exactly rather than with the usual loose
`|a|/2¹⁶ + q/2`:

```
t   = (int16_t)a * QINV        -> any value in [-2^15, 2^15-1]
out = (a - t*Q) >> 16          -> arithmetic (floor) shift
out in [ (lo - 32767*Q) >> 16 , (hi + 32768*Q) >> 16 ]
```

Taking the worst case over `t` independently of `a` is sound, and the
self-validation below shows it is tight to within one unit.

The leaf zeta interval is taken from the real table (`zetas[144..287]` and their
negations), not assumed: **[−1727, 1727]**.

### Self-validation

Running the *degree-3* model over the decapsulation input domain reproduces
NTRU+864's documented bound:

> `inverse.h`: *"Decaps FIRST product only: R0 inputs in [0,4095], FR0 R^-1 output"*
> and *"Decapsulation consumer: FR0 R^-1 abs<=2497"*

| | model | documented |
|---|---:|---:|
| degree-3 `basemul_rinv` over `[0,4095]²` | **2496** | 2497 |

Within one unit, so the method is sound before it is applied to degree 4.

## Results

Zero int32 overflows and zero int16 storage violations across all four domains.

| input domain | `basemul_rinv` | `basemul` | `basemul_add` | `baseinv` |
|---|---:|---:|---:|---:|
| `frombytes × frombytes` = `[0,4095]²` | **2752** | 1764 | 1768 | 1781 |
| `reference_ntt` = `[−1729,1729]²` | 1913 | 1754 | 1758 | 1777 |
| `decaps_sub × frombytes` = `[−1729,5824] × [0,4095]` | 3184 | 1770 | 1774 | 1784 |
| `gt_forward` = `[−15951,15951]²` (measured, see correction below) | 17258 | 1957 | 1961 | 1826 |

`basemul` / `basemul_add` / `baseinv` all land near 1750–1790 regardless of
input domain, because their final Montgomery rescale re-reduces. Only
`basemul_rinv` — which stops at the R⁻¹ boundary precisely so the inverse can
consume it without a rescale — carries the input magnitude through.

Per-coefficient `basemul_rinv` over `[0,4095]²`:

```
r0 [-1795, 2050]   r1 [-1788, 2299]   r2 [-1781, 2548]   r3 [-1729, 2752]
```

The maximum is `r3 = a0b3+a1b2+a2b1+a3b0`, the only coefficient with four direct
products and no ζ fold. Degree 3's widest is the corresponding three-product
`r2`, which is exactly why 864 gets 2497 and 1152 gets 2752.

### Correction: the forward domain was mislabelled

The first version of this gate used `[−4577, 4577]` for the GT forward and
called it "NTRU+864 lazy forward". **That was wrong.** 4577 is the raw
ternary-consumer limit in NTRU+864's *inverse* chain (`2497/2617/21397/4577`),
not a forward bound.

G3b measured the real value by building and running both GT forwards over the
`[−3,4]` input contract: **NTRU+864 reaches 15951, NTRU+1152 reaches 14607**
(`gt1152-p04-forward-8bank/forward-bound.json`). Same magnitude, as the
byte-identical core predicts. The table above now uses the measured envelope.

This is observed, not proved. A proof needs an interval model of
`.Lntt_one_bank`'s 617 instructions, which no gate has built.

### Headroom: degree 4 has measurably less

Largest symmetric input magnitude for which `basemul` raises no int32 or int16
violation, found by bisection over the same model:

| | max input |
|---|---:|
| degree 3 | 26039 |
| **degree 4** | **22551** |

Degree 4 accumulates one more product in both the ζ fold and the final sum, so
it has **13% less headroom**. The measured forward output of 15951 uses 71% of
it — a margin of **1.41×**. That margin is the budget any future lazier forward
has to spend, and it is not large.

### The empirical run caught a missing domain

The first version of `bounds.py` listed only `frombytes`, `reference_ntt` and
the 864 comparison. `instrument.py` then observed a `basemul` input of **5108**,
outside all of them. Source: `crypto_kem_dec` computes
`poly_sub(c, m2)` with `c` straight from `poly_frombytes` and
`m2 = ntt(crepmod3(...))`, giving `[0,4095] − [−1729,1729] = [−1729, 5824]`,
and feeds that to `poly_basemul(·, hinv)`. `decaps_sub_x_frombytes` was added.

This is the whole point of running both halves: the analytic model proves, the
instrumentation catches what the model forgot to include.

### D7 resolved

**1152 `basemul_rinv` output is ≤ 2752; NTRU+864's inverse input contract is
≤ 2497.** Ratio 1.102. The contract is exceeded, so a decision is required.

An earlier estimate of ~3008 in the campaign plan was computed over the wrong
domain — it assumed forward-NTT outputs, but `inverse.h` states the inputs are
raw 12-bit `poly_frombytes` values. 3008 was what the model gives over the
`[−4577, 4577]` domain that the correction above removed.

**Recommendation: add one `barrett_reduce` at the `basemul_rinv` output.**

- It brings the output to `[−1729, 1728]`, which is *tighter* than 2497, so
  NTRU+864's entire inverse bound chain (I9 ≤ 2617, I16 ≤ 21397, ternary
  consumer ≤ 5143) holds a fortiori rather than needing re-derivation.
- The inverse NTT operates on the 288-point transform. Leaf degree changes how
  many banks and components there are, but every coefficient still passes
  through the same butterfly network, so its bound chain depends only on the
  input coefficient magnitude — not on leaf degree. That is what makes
  inheriting sound.
- Cost is roughly 3–4 instructions per vector over 36 tiles, on a
  Decaps-only path.

The alternative — re-deriving the inverse chain at 2752 — is recorded as an M2
optimization. It is not worth the correctness risk during bring-up.

## What this gate does not establish

- **A proof of the forward output bound.** G3b measured it (15951 for 864,
  14607 for 1152) and `bounds.py` now reads that value from
  `gt1152-p04-forward-8bank/forward-bound.json`, but measurement is not proof.
  Proving it needs an interval model of `.Lntt_one_bank`.
- Nothing about the inverse NTT's *internal* bounds. Those are inherited from
  864 under the normalization above and must be re-verified in G6.
- No hardware ran.

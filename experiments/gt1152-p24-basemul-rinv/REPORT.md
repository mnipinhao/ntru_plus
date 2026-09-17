# P24 — `poly_basemul_rinv`: the normalization, not the schedule

Branch `neon-1152`, parent `7793ca96`.  Pi 5 core 3, GCC 14.2.0.

P21's third target.  **The gap turned out not to be the degree-4 arithmetic at
all** — the official issues exactly the same multiplies — but D7's Barrett
normalization on top of them.

## 1. The official's instruction mix is identical

Compiled loop body, one Good-Thomas group:

| | GT | official `poly_basemul_scale` |
|---|---:|---:|
| `smlal` / `smlal2` | 19 / 19 | 19 / 19 |
| `smull` / `smull2` | 7 / 7 | 7 / 7 |
| `mul` | 7 | 7 |
| `uzp1` / `uzp2` | 7 / 7 | 7 / 7 |
| `sqdmulh` / `srshr` / `mls` | **4 / 4 / 4** | **0 / 0 / 0** |

The 16-product schoolbook and its seven Montgomery reductions are the same on
both sides.  The only difference is four centered Barretts per group — and on
the measured A76 costs those are the expensive kind: `sqdmulh` and `mls` are
2 cycles each on the single multiply pipe.

| | VEC0 cycles per group | x36 |
|---|---:|---:|
| widening (52 ops at 1) | 52 | |
| `mul` (7 at 2) | 14 | |
| **official floor** | **66** | **2,376** |
| Barrett (4 `sqdmulh` + 4 `mls`, at 2) | +16 | |
| **GT floor** | **82** | **2,952** |

The official measures 2,551, 93% of its floor.  GT measured 3,378 against a
floor of 2,952 that was **already above the official's measurement** — so no
amount of scheduling could have closed it.

## 2. D7 does not need a Barrett

D7 added the normalization for one reason: `basemul_rinv`'s output reaches 2752,
above NTRU+864's documented inverse input contract of 2497, and bringing it to
[-1729, 1729] lets the 864 bound chain hold a fortiori.

A single conditional subtract does that with **no multiply at all**.  With
|x| <= 2752 < 1728 + q exactly one case applies:

```
x >  1728  ->  x - q  in (-1729, -705]
x < -1728  ->  x + q  in [705, 1729)
otherwise  ->  |x| <= 1728
```

The output lands in **[-1728, 1728]**, one tighter than the Barrett's, so D7's
contract is honoured exactly and **no bound is re-derived** — the change rests
on G2's already-proved 2752, not on new analysis.

Probed over 20,000 trials with inputs on the declared [0,4095], including the
all-4095 and random-extreme cases:

```
max |pre-normalization|   2536     G2's proved bound 2752; the single
                                   conditional subtract is valid to 5185
max |post-normalization|  1728     exactly as derived
```

## 3. A dependency-structure rewrite, at no instruction cost

Pre-multiplying zeta into b once per group turns

```
cross -> reduce -> x zeta -> accumulate -> reduce      (serial, per output)
```

into three shared `bz` values and four independent four-term accumulations.
Algebraically identical: `zeta*cross*R^-2` expands to
`a1*(zeta*b3*R^-1)*R^-1 + ...`.  The instruction multiset is unchanged — which
is why the official's histogram matches this form.

## 4. Measured

| | cycles |
|---|---:|
| P21 baseline (Barrett) | 3,378 |
| conditional subtract | 3,118 |
| **+ zeta pre-multiply** | **3,054** |
| official `poly_basemul_scale` | 2,551 |
| issue floor | 2,376 |

`poly_basemul_rinv` went from +827 to **+634**.  GCC's `unroll` pragma has no
effect at 1, 2, 3 or 4 — identical to the cycle.

**What is left here is genuinely a scheduling problem**, and the first one this
campaign has found: 3,054 against a 2,376 floor is 78%, and the official proves
2,551 is reachable with the same instructions.  That is M2-2, a Slothy gate,
worth about 500 cycles.

## 5. Where the campaign stands

| operation | official | GT | delta |
|---|---:|---:|---:|
| keygen | 64,053 | 64,748 | +1.09% |
| **encaps** | 59,531 | **58,319** | **-2.03%** |
| **decaps** | 52,508 | **52,087** | **-0.80%** |
| **total** | **176,092** | **175,155** | **-0.53%** |

| category | official | GT | delta | at P21 |
|---|---:|---:|---:|---:|
| **baseinv** | 10,599 | 12,996 | **+2,397** | +2,405 |
| hash | 84,801 | 85,703 | +902 | +985 |
| inverse | 6,292 | 6,309 | +18 | +1,134 |
| basemul | 16,131 | 15,781 | **-350** | -160 |
| serialize | 10,075 | 9,039 | **-1,036** | -1,034 |
| sample | 3,893 | 3,622 | **-270** | +556 |
| forward | 28,884 | 26,294 | **-2,590** | -2,618 |

All three of P21's targets are done.  Two of three operations beat the official
and so does the total, with the hash still the generic sponge.

**`baseinv` at +2,397 is now larger than every other loss combined, and it is
what keeps keygen positive** — it is keygen-only, and keygen is the one
operation still behind.  Its cause is on record from G5/P11: no ILP split, where
NTRU+864 uses a 12x3 decomposition.

## Reproduce

```sh
gcc -O3 -march=native -D_DEFAULT_SOURCE -I. bench.c inverse.c -o bb && ./bb
gcc -O2 -march=native -I. probe.c probe_impl.c ip.c -o probe && ./probe
```

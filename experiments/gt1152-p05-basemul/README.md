# GT1152-P05 — degree-4 basemul and basemul_add

Transform-domain multiplication over `Z_q[X]/(X⁴ − ζ)`, as NEON intrinsics C,
following NTRU+864's `base.c` structure.

```sh
make check      # bounds_barrett.py + verify.py
```

Built and run on the local arm64 host. Not Cortex-A76 — no performance claim.

## Result

**14 cases × 6 modes × 1152 coefficients match the G1 declared oracle.**

Modes: `basemul`, `basemul_add`, and four aliasing patterns — output aliased
with `a`, with `b`, with `c` in the add form, and `a` aliased with itself (a
square). Cases: contract extremes, a zero operand, 6 ternary and 6
full-contract random inputs, each first pushed through the real G3b GT forward
so the operands are genuine transform-domain values.

Observed output range `[−1765, 1778]`, against a Barrett bound of 2343.

## The algebra

```
r0 = a0b0                     + ζ(a1b3 + a2b2 + a3b1)
r1 = a0b1 + a1b0              + ζ(a2b3 + a3b2)
r2 = a0b2 + a1b1 + a2b0       + ζ(a3b3)
r3 = a0b3 + a1b2 + a2b1 + a3b0
```

Degree 3 folds two wrap groups; degree 4 folds three, and its widest direct sum
has four terms instead of three. That extra product in both places is what
costs 13% of the input headroom relative to degree 3 (G2).

Group stride is 32 int16 against 864's 24 — 36 groups either way, because both
parameter sets have 288 leaves. `basemul_zetas` is copied verbatim; G3a
verified it transfers.

## Does NTRU+864's Barrett reciprocal still work at degree 4?

864's `base.c` documents `SQRDMULH(x, 621199)` then `x − qhat·3457` as landing
in `[−2911, 2911]`, **proved over the degree-3 accumulator union**. Degree 4
widens that union, so the claim needed re-checking.

`621199 · 3457 = 2³¹ + 1295`, so the quotient estimate carries a relative error
of `1295/2³¹ ≈ 6.03e−7` and

```
|out| ≤ q/2 + |x| · 1295/2³¹
```

| accumulator width | widest \|x\| | bound |
|---|---:|---:|
| `frombytes [0,4095]` | 67,076,100 | 1769 |
| measured GT forward ±15951 | 1,017,737,604 | **2342** |
| degree-4 headroom 22551 | 2,034,190,404 | 2955 |
| full int32 | 2,147,483,647 | 3024 |

**The constant transfers.** It holds across the entire int32 range; only the
resulting bound changes, from 864's documented 2911 to 2342 over the domain
1152 actually reaches.

### One real constraint the check found

`VMLS` computes `value − qhat·q` in int32, so `qhat·q` must itself fit. That is
**not** true across all of int32: at `x = −2³¹` the estimate is `qhat = −621199`
and `|qhat·q| = 2,147,484,943 > 2³¹`.

Bisecting for the exact threshold: `|qhat·q| < 2³¹` holds for
**`|x| ≤ 2,147,481,919`**, which is all but the last 1729 values of int32. The
widest reachable degree-4 accumulator is 2,034,190,404, inside it with
113,291,515 to spare.

So the path is safe here, but it is not unconditionally safe — a lazier forward
would eat into that margin along with the 1.41× headroom margin from G2.

Also checked: congruence mod q over 160,015 samples spanning every reachable
domain and both ends of the accumulator limit, and that the largest sampled
output (3019) sits under the analytic bound (3023.5).

## Not established

- No Pi 5 measurement and no performance claim.
- The Barrett bound is derived analytically and sampled, not exhausted over
  int32.
- Nothing downstream: `basemul_rinv`, BaseInv, the inverse and pack are later
  gates.

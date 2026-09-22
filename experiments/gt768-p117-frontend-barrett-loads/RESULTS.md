# P117 — E3 could overflow on Official's product range; E4 fixes it with a third of the Barretts

Three items were left after P116: the 5 ns between E3's and E2b's inverse, the
stage45 Barretts, and the `st4` front-end.  The Barrett work turned up a
correctness bug in E3.

## E3 is not correct for every input, and E4 is

`range_interp.py` is an interval interpreter that runs the inverse's
disassembly.  Integer registers and control flow are concrete.  Vector data
is tracked as per-lane intervals, and constants are read from the object's
own tables.  Each fqmul is bounded by its constant pair's exact rounding error
and each Barrett by the exhaustive int16 result.  An instruction it does not
recognise counts as an error.

- **P116's E3 (reference arithmetic) is overflow-free only for |input| ≤ 1,846.**
  At 1,847, stage45's opening lazy butterflies reach 16x the input plus an
  fqmul: 32,774.
- **Official's first product reaches |x| = 2,420** (`prod_bound.c`, 200k skewed
  canonical ct), and its analytic bound is
  (4·3456² + 32768·q) / 2¹⁶ ≤ **2,458**.
- On synthetic inputs with |x| ≤ 2,458 (`check_e4.c`), E3 disagrees with
  Official's inverse applied to the same values on **2,000 coefficients (500 of
  2,000 polys)**.  E4 disagrees on **0**.

So E3 computes wrong ternary coefficients for some products Official's front-end
can produce.  P116's 3,000 random trials never lined the signs up.  It was never
integrated.  Whether an attacker who does not know `f` can steer a ciphertext
into such a pattern was not studied; correctness for every input is the bar.

## E4 — Barretts moved from stage45's outputs onto chosen stage123 outputs

Stage45 opens each stripe with unreduced `s0 ± s1` and `s2 ± s3` on stage123
outputs that reach 8x the input, and reduced only its 32 outputs per row.  E4
removes all 96 stage45 Barretts and reduces chosen stage123 outputs before the
scratch store (`make_e4.py`).

A greedy search (`search_e4.py`) starts from a hand-bounded placement and
removes Barretts while the interpreter still proves |x| ≤ 2,458 safe:

| stripe | blocks reduced |
|---|---|
| 0 | 0, 1, 2 |
| 1–7 | 0 |

**10 Barretts per row, 30 in total, against 96: −198 SIMD ops.**  The worst
value anywhere is 21,503 (stage45).  Post's inputs stay small enough for
its DFT3.

The E2 fused tail ends in an exactly centered Barrett, so the output is the
unique centered representative whatever representatives flow through.
Moving reductions cannot change a single output bit; only overflow could, and
the interpreter rules that out.

## Results: the first-product chain

| | M2 ns | A76 cycles |
|---|---:|---:|
| Official | 464.2 | 6,122.8 |
| E3 (P116, **unsafe**) | 450.5 | 5,909.1 |
| **E4** | **436.0 (−6.1%)** | **5,640.8 (−7.9%)** |
| E4 inverse + crepmod3 alone (copy-corrected) | 208.9 vs 254.0 | 3,337 vs 3,959 |

Correctness: output, `decoded_ct` and the fail flag are identical to Official's
chain over 3,000 trials, 10% of them malformed.  Also 3,000 skewed ciphertexts,
and 2,000 synthetic worst-case products checked against Official's inverse.

M2: three runs within 0.1 ns.  A76: three runs within 7 cycles,
`throttled=0x0`.

## The 5 ns between E3 and E2b: store-to-load proximity, not compute

Same binary (`bench_same.c`):

| | E2b | E3 |
|---|---:|---:|
| out of place | 224.0 | **223.6** |
| in place after a copy (copy-corrected) | 222.0 | **232.5** |

The kernels compute at the same speed.  E3's first loads hit the end of the
buffer (branch-1 elements in groups 20–23), which the preceding stores wrote
last.  E2b reads roughly in store order.

In the real chain, the inverse costs 450.5 − 224.1 = 226.4 ns, about 3 ns above
out-of-place.  Every row needs branch-1 elements from high groups first, so no
block order avoids this.  Not pursued.

## The `st4` front-end is near its floor on M2

Cost of adding each op to a SIMD-saturated loop (`perm_cost.c`):

| | M2 | A76 |
|---|---:|---:|
| `st4 {4}.8h` | +2.05 | +6.00 |
| `st1 {4}.8h` | +0.77 | +2.00 |
| 4 x `zip` / `uzp2` / `tbl` 1-reg / `tbl` 2-reg | +1.05 | +2.00 |
| 4 x `tbl` 4-reg | +3.62 | +6.00 |

Only v28 is free across the front-end loop.  The one cheaper route is to
re-pair the Montgomery `uzp2`s so each pairs two coefficients of the same
lanes, then 4 two-register `tbl` + `st1`.  It writes byte-identical memory,
so the inverse is unchanged.  Estimated gain: 1–2 ns on M2, ~48 cycles on
A76 (0.8% of the chain).  It moves accumulator lifetimes inside a Slothy
schedule, so it needs a Slothy re-run on the Pi.  **Deferred.**

## Files

- `range_interp.py`: the interval interpreter,
  `range_interp.py OBJ SYMBOL B_IN`.
- `make_e4.py` → `invntt_e4.S`; `search_e4.py`: the greedy placement.
- `check_e4.c`: E4 vs Official's chain, and E3/E4 on synthetic worst cases
  against Official's inverse.
- `prod_bound.c`: reachable size of Official's product.
- `bench_same.c`: E2b vs E3 in one binary.
- `bench_chain4.c`: the chain on M2 or the Pi.
- `perm_cost.c`: permute and store costs on both machines.

The E4 chain builds like P116's `bench_chain.c`, with `invntt_e4.S` in place of
`invntt_e3.S`.

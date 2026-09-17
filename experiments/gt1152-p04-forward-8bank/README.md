# GT1152-P04 — eight-bank GT forward NTT

Tier 2's first assembly. Ports NTRU+864's Good-Thomas forward to NTRU+1152:
six banks become eight, three cubic branches become four quartic ones.

```sh
make check      # generate, assemble, differential, bound measurement
```

The local host is arm64, so this gate **builds and runs the kernel**. It is
Apple silicon, not Cortex-A76 — nothing here is a performance statement.

## Result

**24 cases × 1152 coefficients match the G1 declared oracle**, under the layout
predicted in `gt1152-p03-gt-layout`. That single check establishes three things
at once:

1. the transform is correct — values agree mod q with the reference NTT;
2. the predicted 1152 layout formula is what the kernel actually produces;
3. the GT leaf permutation equals the one measured from NTRU+864.

Cases: the `[-3,4]` contract extremes (`all −3`, `all +4`, zero), deltas at
positions 0, 1, 575, 576, 1151 (both CRT halves and both boundaries), 8 ternary
inputs (the domain the KEM feeds after `poly_triple`), and 8 full-contract
random inputs.

## Files

| file | change from NTRU+864 |
| --- | --- |
| `ntt_top.S` | hand-written. `LD3`→`LD4`; 6→8 banks; `+864`→`+1152`; per-`t` stride `54`→`72`; tail offset `48`→`64` |
| `ntt_tail.S` | hand-written. Same transpose network, 12→16 stores |
| `ntt9.S` | **generated** by `generate_ntt9.py`. Core and tables copied verbatim |
| `ntt.S` | scratch `1792`→`2304`, tail region `+1536`→`+2048` |

### `ntt9.S` is generated, and the core is copied under a hard gate

`generate_ntt9.py` emits only the bank driver — 8 blocks and 144 stores. It
copies `.Lntt_one_bank` and all four twiddle tables byte-identically from the
864 source and **asserts** they appear unaltered in the output. That is sound
because the tables are selected by the alpha/beta half alone and never by
component, and the leaf ordering is fixed by the core rather than the component
count — both established in `gt1152-p03-gt-layout`.

Store addressing:

```
864 : top*864  + component*16 + row*96  + halfcol*48
1152: top*1152 + component*16 + row*128 + halfcol*64
```

### Where 1152 is simpler than 864

The `s=8` tail exists because 9 is odd — eight of the nine `s` values fill a
vector and one is left over. That does **not** go away at 1152. What improves:

- Four halfwords is exactly one `LDR d`, so 864's three-part load
  (`LDR s` + `LD1 {v.h}[2]`) becomes one instruction per half.
- 2 tops × 4 branches fills all eight lanes with no padding, so 864's
  `MOVI` + six `INS` becomes two `MOV`. (864 comments this as "two lanes are
  padding".)

Also dropped: NTRU+864's `ntt_top.S` dups `q` into `v29` and another constant
into `v31` and never uses either.

## Forward output bound, and a correction to G2

`bound.py` measures the forward's output range over the `[-3,4]` contract, and
G2's `bounds.py` reads it from `forward-bound.json`.

| | observed range | abs max |
|---|---|---:|
| NTRU+864 | `[−14298, 15951]` | 15951 |
| NTRU+1152 | `[−14607, 14602]` | 14607 |

Same magnitude, as the byte-identical core predicts.

**This corrects G2.** That gate used `[−4577, 4577]` for the GT forward and
labelled it "NTRU+864 lazy forward". 4577 is not a forward bound — it is the raw
ternary-consumer limit in NTRU+864's *inverse* chain (`2497/2617/21397/4577`).
The real value is over three times larger.

The bound is **observed, not proved**. Proving it needs an interval model of
`.Lntt_one_bank`'s 617 instructions, which no gate has built. What is argued is
narrower and sound: the core is byte-identical and sees the same input
contract, so the per-coefficient range is the same — and both were measured to
check exactly that.

The correction also produced a quantified headroom result in G2: degree-4
`basemul` tolerates inputs up to 22551 against degree-3's 26039, so the measured
forward output of 15951 leaves a margin of only **1.41×**.

## Not established

- No Pi 5 measurement, and no performance claim of any kind.
- No proof of the forward bound, only measurement.
- Nothing downstream: basemul, baseinv, the inverse and pack are later gates.

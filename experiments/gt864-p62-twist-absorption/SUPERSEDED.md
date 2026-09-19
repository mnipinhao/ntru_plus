# P62 is superseded by P40 and its arithmetic was wrong

P62 derived the inverse9 terminal closed form

    k(top, column, s) = -384 * lambda(top,0)^s * r^(column*s),  r = -594, ord(r) = 144

and concluded that absorbing the geometric part into the inverse16 butterflies
is net-negative at **+144 instructions**, because 14 of the 32 butterflies
currently carry twiddle 1 and the twist destroys that sparsity.

**`gt864-p40-inverse9-i16-phase-abi` had already built and measured exactly
this.**  P40 derives the same closed form (its 2863 is -594 mod 3457, also of
order 144), deletes all nine terminal products rather than reducing them to a
Barrett step, and absorbs the column factor into a twisted radix-2 I16 table.

P62's instruction estimate is wrong in sign.  Two mistakes:

- P62 assumed each terminal output still needs a reduction, so it costed the
  deletion at 3 instructions -> 2.  P40 proved the range holds after absorption
  (signed int16 peaks 28135 / 21889 / 19268; only tail column 6 low needs a
  `b=1` reset), so all three go.
- P62 costed the I16 side at +14 modmuls per call.  P40's ledger is +66
  instructions per main call, but the inverse9 side saves 540 rather than 108.

P40's measured ledger is **-136 instructions per complete inverse**, and Pi PMU
confirmed -137 retired.  It is still rejected, but for the campaign's usual
reason rather than P62's:

| boundary | P35 | P40 | delta |
|---|---:|---:|---:|
| inverse-to-ternary | 4,753.9 | 4,975.4 | **+221.5 (+4.66%)** |
| decaps | 39,917.5 | 40,137.1 | +219.5 (+0.55%) |

IPC falls from 1.739 to 1.634: nine products per inverse9 block become products
on every I16 butterfly right branch, with deeper multiply chains and more varied
table loads.

## What P62 still adds

One direction P40 did not test: moving the twist **backwards** into
`basemul_rinv`'s constants.  `premul.py` shows that is algebraically impossible
--- `D_in = T^-1 . D_out . T` is dense in all 32 (top, column) contexts, 72 of
72 off-diagonal entries non-zero.  That closes the remaining relocation
direction, and it is the only part of P62 that should be cited.

P62 should not be used to argue anything about forward absorption.  P40 is the
measured record.

# P125 — range proof of the 864/1152 decapsulation inverse

`range_interp2.py` generalises P117's interpreter to a linked executable: it
starts at the C wrapper `poly_invntt_ternary(m, m, scratch)`, follows the real
table addresses, `bl`/`ret` and every kernel, and keeps per-lane intervals.
Multiplications use the exact error of each constant pair; the mod-3 step is
bounded exhaustively over its input interval.  Anything unrecognised is an
error.  `prove.sh` builds both and runs it.

Two further checks were added:
- **poison**: scratch the transform reads before writing propagates as poison;
  overflow is not checked in poisoned lanes, and a poisoned output is an error;
- **q-centering**: `x - (x > 1728) + (x < -1728)` then `r - 3*sqrdmulh(r,10923)`
  is the centered mod-3 residue exactly for |x| <= q + 1728 = 5185 (exhaustive),
  so the largest value entering every such compare is checked against 5185.

| | input bound | peak | centering input | proven up to | limit |
|---|---:|---:|---:|---:|---|
| 864 | 2497 (contract) | 22,473 `packed_i9` | 4,482 | 3,640 | int16 overflow in `packed_i9` |
| 1152 | 2458 (canonical product) | 22,122 `packed_i9` | 5,178 | 2,501 | `crepmod3`'s single correction |

Both outputs are in {-1,0,1}.  864 reads 32 never-written scratch halfwords
(scratch + 0x60c..0x6fe, the old tail padding); none reaches an output, which
closes the roadmap's open question: the padding needs no clearing.  1152 reads
none.

Interpreter bugs found on the way: an `add ..., #0x1, lsl #12` (t=15's table
pointer in 1152's driver) lost its shift, and `dup` from a negative W register
lost its sign.  The first produced wrong tables and absurd bounds; the second
made `cmgt` against -1728 constant-false, which is unsound.  768's P117 proof is
unaffected: its only `dup` is of +10923 and it has no shifted immediates.

# M5D inverse range proof

Target is `Z_3457[x]/(x^864-x^432+1)`. Secret-derived values are signed int16
normal-domain representatives. Public fixed constants are Montgomery `R1` and
use the Neon `-qinv/add` widening reduction.

The input bound is M5C's widest real inverse predecessor under the G0 closure:
BaseMulAdd output `[-2205,2205]`. This gate does not claim that arbitrary wider FR-0 forward
representatives can enter the same lazy schedule without normalization.

| Step | Expression | Storage | Proved maximum absolute value |
| --- | --- | --- | ---: |
| input | FR-0 BaseMulAdd tiles | int16 | 2205 |
| inverse NTT9 lazy arithmetic | two inverse radix-3 layers | int16 | 19845 |
| pass-1 output | `inv9*lambda^-s` reduced P8 | int16 | 2048 |
| inverse NTT16 lazy arithmetic | four inverse radix-2 layers | int16 | included in 19845 global maximum |
| scaled top values | `inv16*zeta_top^-t` | int16 | 1948 |
| final output | alpha/beta recombination | int16 | 3696 |
| widest known-constant product | before Montgomery reduction | int32 | 22543920 |

`prove_ranges.py` exhausts every integer in every propagated interval for each
fixed Montgomery multiplication, checks every halfword add/sub before allowing
the next step, and evaluates all top/block/column/row table variants. The
widest int32 product is far below `2^31`; no signed C overflow or int16 wrap is
required by the proved contract.

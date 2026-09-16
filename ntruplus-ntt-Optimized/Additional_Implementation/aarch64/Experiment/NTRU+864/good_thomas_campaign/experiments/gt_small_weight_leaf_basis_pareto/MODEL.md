# Model

For each top, row `r`, and column `t`, choose

`u = kappa * theta^(2*t + H*r)`

and store the geometric degree-3 basis

`D_u(a0,a1,a2) = (a0,u*a1,u^2*a2)`.

The legacy leaf modulus `X^3-z` becomes `Y^3-z'`, with

`z'=z/u^3` and row exponent `K=96-3H mod 864`.

The Pareto points are:

| H | K | alpha weights | beta weights |
| ---: | ---: | --- | --- |
| 32 | 0 | `+9` | `+3` |
| 176 | 432 | `+9,-9` | `+3,-3` |
| 464 | 432 | `+9,-9` | `+3,-3` |
| 752 | 432 | `+9,-9` | `+3,-3` |

The three signed candidates share BaseMul weights but not Forward/Inverse basis
scales, because their `H` values differ by 288 rather than 864.

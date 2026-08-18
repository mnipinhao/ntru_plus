# F32X3 CT register plan

The L3/L4 macro uses:

- `ymm0..ymm3`: four live data blocks;
- `ymm4`: short-lived Montgomery factor;
- `ymm5`: matching factor-qinv vector;
- `ymm6`: Montgomery low/correction temporary;
- `ymm7`: Montgomery high/reduced product;
- `ymm8/ymm9`: destructive sum/difference outputs;
- `ymm10`: canonicalization mask;
- `ymm12/ymm13/ymm14`: q, q-1 and zero;
- `ymm11/ymm15`: free.

Peak allocation is 13 YMM registers. Factors are reloaded for each unrelated pair.
There are no calls, stack slots, scalar loops, or semantic stores between L3 and L4.

# Compact DFT3 range

Input is the exact canonical post-L4 R^0 state. `delta=Y2-Y1` lies in
`[-3456,3456]`. The signed Montgomery omega chain preserves R^0 scale.

- raw D0: `[0,10368]`
- raw D1/D2 conservative bound: `[-5368,5368]`
- packed signed-Barrett output: `[0,3457]`

The inclusive q endpoint is intentional. Test random case 8 produced scalar canonical
zero versus packed representative 3457, proving that `%q` was not a byte-exact boundary.
The scalar checkpoint now models the exact signed Montgomery and packed Barrett steps.

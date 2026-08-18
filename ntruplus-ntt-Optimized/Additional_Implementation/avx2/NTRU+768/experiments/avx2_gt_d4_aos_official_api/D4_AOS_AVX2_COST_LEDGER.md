# AVX2 cost ledger

| stage | GT/Official | d4AoS prototype | result |
| --- | --- | --- | --- |
| Forward | factorized kernels | 4,608 direct vector evaluations | prohibitive tax |
| Basemul | compact SoA | 1,392 Montgomery chains, 1,536 shuffles | likely tax |
| Inverse | SoA DFT3 scratch and terminal transpose | direct AoS terminal has neither, but 4,608 evaluations | benefit hidden by arithmetic |
| 2F+B+I | current champion is outside this island | at least 13,824 evaluation iterations | not promising |

All counts are static, not performance claims. Native adapters are zero: prototypes use typed d4AoS domains directly. No same-binary Official/GT timing is recorded because the prototype fails the pre-measurement practicality gate; no shadow KEM exists.

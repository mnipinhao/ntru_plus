# Experiment 141 generated result

| cut | decoder routes | B3 routes | total | reductions deleted | peak YMM |
|---|---:|---:|---:|---:|---:|
| RAW_PACKET | 0 | 144 | 144 | 0 | 16 |
| P1_WORD | 48 | 96 | 144 | 0 | 16 |
| P2_DWORD | 96 | 48 | 144 | 0 | 16 |
| M_SOA | 144 | 0 | 144 | 0 | 16 |

Result: **STATIC_NO_OPERATION_CLASS_DELETION**.

The current decoder already preserves canonical raw h residues; it does not center or reduce them. Moving the three transpose layers merely transfers 144 dynamic routes from decode to B3.

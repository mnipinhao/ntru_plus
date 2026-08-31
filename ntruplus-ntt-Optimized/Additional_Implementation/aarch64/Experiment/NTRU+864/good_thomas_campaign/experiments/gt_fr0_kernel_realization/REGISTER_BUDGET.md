# Register-flow and budget

The leaf ABI is `x0=out`, `x1=main s0..s7`, `x2=tail s8`, and `x3=public
twist table`. All addresses and loop selection are public.

| Stage | Entry | Instructions and exit | Meaning / next consumer |
| --- | --- | --- | --- |
| Constants and load | four public pointers | `dup v30=q`, `dup v31=-qinv`; four `ldp` place columns 0..7 in `v0..v7` | Eight lanes in each register initially mean `s=0..7` for one column. |
| Transpose | `v0..v7=column vectors` | `trn1/trn2` at 16-, 32-, then 64-bit granularity; `v0..v7=row vectors` | Register `vs` now contains fixed `s`, lanes contain eight columns. Scale and bounds do not change. |
| Exact tail | `x2` points at first public-stride tail | eight lane `ld1`; `v16={U8(c0)..U8(c7)}` | Reads exactly eight halfwords. It never reads the two padding lanes adjacent to a six-value tail group. |
| Twist | `v0..v7,v16=U_s` | eight constant loads and widening Montgomery `FQMUL`; `v_s=U_s*lambda_c^s` | Coefficients remain R0 because each public factor is Montgomery R1. |
| Oriented NTT9 | nine twisted vectors | six `B3`; four extra `eta/eta^-1` FQMUL; transformed values remain in `v0..v7,v16` | Lanes are independent columns; registers are physical output rows. |
| Store | row registers | nine `str q`; 96-byte row stride | Direct BaseMul SoA component vectors; no 864-value scratch or serializer. |

Register classes are fixed: coefficients `v0-v7,v16`; current constant `v17`;
widening Montgomery scratch `v18-v21`; transpose/B3 scratch `v22-v29`; modulus
vectors `v30-v31`. `v8-v15` are untouched, so no callee-saved Neon register
needs saving. Disassembly proves no `sp` reference and no coefficient spill.

The wrapper repeats this leaf 12 times. Hoisting modulus and repeated B3
constants across blocks is intentionally left to a later scheduling experiment.

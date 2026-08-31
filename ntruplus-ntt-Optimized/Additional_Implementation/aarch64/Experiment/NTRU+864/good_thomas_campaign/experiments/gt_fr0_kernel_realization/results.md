# Results

`make check` passes 106 exact-representative differential cases against M4
FR-0, including centered, non-centered, boundary, and randomized inputs. There
are zero mismatches. Static disassembly reports 430 instructions, no `sp`, no
`v8-v15`, and no coefficient spill.

The field-operation ledger for the full 864-coefficient boundary is:

| Class | Per block | 12 blocks |
| --- | ---: | ---: |
| branch-specific lambda twist | 8 | 96 |
| rho/rho2 inside six B3 | 24 | 288 |
| eta/eta-inverse orientation | 4 | 48 |
| total field mulmods | 36 | 432 |

Thus “96 mulmods” describes only the lambda twist, not the whole NTT9. The
widening multiply/reduction instructions are the realization of each field
mulmod, not additional field multiplications.

The generated FR-0 physical leaf map is bijective and `P^-1 P = I`. Its root
set equals the official BaseMul leaf set. In the official table,
`zetas[0..143]` are internal NTT twiddles; the BaseMul set is formed by
`zetas[144..287]` and their negatives. Mapping SHA-256 is
`7ff4ba4eea02e78a1cbe83c4dd15e042bbcf7b43e5173d639e1e1f391ce3c65f`;
FR-0 BaseMul-table SHA-256 is
`1c4d61e3a906acec0c44a3f3e88ef047ec7c0e45ed3e3ed8f3b38030092c4d92`.

Three native Apple-arm64 diagnostic batches (41 samples, 5000 calls/sample,
sample-rotated order) produced medians `371.725/376.908/371.192 ns` for M4 and
`323.617/323.592/322.617 ns` for M5A. Their median-of-medians is 371.725 ns
versus 323.592 ns, a 12.95% reduction. This is local attribution, not SUPERCOP
and not a full-Forward or full-KEM result.

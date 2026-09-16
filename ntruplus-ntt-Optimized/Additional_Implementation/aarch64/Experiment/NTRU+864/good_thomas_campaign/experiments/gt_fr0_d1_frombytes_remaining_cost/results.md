# D1-P3B17 evidence

Status: **pass; the current native-FR0 FromBytes gap is directly measured.**

The first diagnostic measured only Official's raw unpack core (555.200
cycles) and was discarded because the public `poly_frombytes()` also performs
`poly_shuffle_asm`.  The authoritative paired control below includes both
operations through ABI-preserving wrappers.

All 256 arbitrary-byte cases satisfy the exact raw-serialized-to-FR0 composed
map.  Pi 5 Cortex-A76 PMU uses one binary, core 3, 400 calls/sample, 41 samples
per order, both orders and three repetitions; throttling is zero.

| native boundary | cycles | instructions | branches |
| --- | ---: | ---: | ---: |
| Official unpack + shuffle | 794.375 | 1631.050 | 41.010 |
| P3B11 direct FR0 | 938.967 | 1715.050 | 6.010 |
| P3B11 - Official | **+144.592 (+18.20%)** | **+84** | **-35** |

The small instruction delta but substantial cycle delta points to dependency
and execution-port cost in P3B11's routing, not branch count.  Per top its
851-instruction core contains 432 lane-routing moves plus 54 each of
`tbl`/`ushl`/`bic`/`add`; the core is called twice per polynomial.

At the KEM call ledger, the isolated remaining contribution is approximately
+144.592 cycles for Encaps (one call) and +433.776 cycles for Decaps (three
calls), before caller-context effects.

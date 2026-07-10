# U01v3 Track H Semantic Lifetime Model

Status: mechanically extracted from the current G1 assembly and the production Phase123 symbolic source. Production default unchanged.

The important lifetime is per Stage12 stripe:

```text
Phase123 scratch: A, B, C, D
Stage12:           t0/t1/t2/t3
outputs:           Q0, Q8, Q16, Q24
Q24 formula:       (A-C) - twisted_reduce(B-D)
```

The physical D register stops being recoverable when it is reused for `t3=A-C`. The raw D scratch slot survives longer, but G1 then stores Q24 over that same slot. A/B/C raw scratch slots are not overwritten by the compact F012 producer.

This gives three reconstruction contracts:

```text
raw basis per stripe:          A, B, C, D       (4 vectors)
intermediate basis per stripe: t1_reduced, t3   (2 vectors)
final basis per stripe:        Q24+s            (1 vector)
final basis for all 3 rows:                       24 vectors
```

G1 already stores the smallest final basis: one vector for every block3 stripe. A proposed 1-4-vector global H3 basis therefore cannot represent all 24 independent block3 vectors unless it exploits a new algebraic dependency not present in this def-use graph.

Stage345 block3 is not the main blocker: 8/8 same-destination handoffs are safe before first consumer. The difficult boundary is keeping or producing the 24 independent Q24..Q31 row values at the right time.

Machine-readable details:

- `u01v3_track_h_semantic_ir.json`
- `u01v3_track_h_overwrite_map.json`

# Results

Status: passed locally on 2026-08-31.

```text
gt864_transform_domain_tile_abi_search=pass
candidate_count=5
shortlist=fixed_row_column_batch,lane_dependent_row_rotation,fixed_column_row_lanes
phase_claim=none; all candidates are pure leaf permutations
serializer_claim=none; structural obligations only
production_linked=0
```

Mapping anchors:

| Candidate | Mapping SHA-256 | Decision |
| --- | --- | --- |
| fixed-row natural | `a4cc60acbd3da82e7c1cd7b5f076cc6213296452634a9bfc7efca3498c8f9250` | primary family |
| fixed-row oriented `P9`, example bit-reversed `P16` | `fe81cfdcccd8134cd679ccff7221550d1d55775a6bad0684a468dbdf0b307589` | primary family |
| lane-dependent row rotation | `31d3f5870ae357b61dc7ae15d8c663cc91fcce621917bc2c703ae4848822d65e` | conditional on twist-table cost |
| fixed-column plus row-8 tail tiles | `ae40535d20da1a54bdf6ae2cd9c44b79190cb7bcf919e4f550f7461cbb6b9ecd` | secondary; microkernel cost required |
| oriented column stream chunked by eight | `3019baaa7c2ee0179600cd7d149365e3d8d7448b7f53e07abb17e2057c7302bd` | rejected structurally |

The gate requires every candidate to contain each of the 288 leaves exactly
once, preserve all three SoA component slots, generate 288 distinct matching
BaseMul roots, and possess a total inverse permutation.

No cycle, serializer, phase-carry, or Production result is claimed.

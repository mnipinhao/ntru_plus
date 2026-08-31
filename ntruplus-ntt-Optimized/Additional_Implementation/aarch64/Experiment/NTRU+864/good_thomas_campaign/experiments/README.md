# NTRU+864 Good-Thomas experiment registry

This directory follows the experiment discipline used by the NTRU+768 work on
`main`, while remaining completely outside the NTRU+864 Production Makefile.

Rules:

1. One directory answers one bounded question.
2. Every experiment declares a baseline contract and candidate contract.
3. Static and correctness gates run before implementation or timing.
4. Failed or incomplete experiments remain default-off and are not hidden.
5. Production promotion is a separate change with source-closure, KAT, ABI,
   full-KEM, and SUPERCOP evidence.

Current experiments:

| Experiment | Question | Status | Production linked? |
| --- | --- | --- | --- |
| `gt_9x32_root_gate` | Does the NTRU+864 cubic-leaf root set admit the proposed 9-by-32 algebraic grid? | passed | no |
| `gt_9x32_scalar_reference` | Does the 9-by-32 factorization implement the exact quotient-ring product? | passed | no |
| `gt_9x32_montgomery_reference` | Can GT preserve the current normal-coefficient/Montgomery-public-factor and legacy leaf contract? | passed | no |
| `gt_9x32_radix3_orientation_reference` | Does the paper-style oriented radix-3 NTT9 preserve the frozen canonical GT representation? | passed | no |
| `gt_2x9x16_ld3_top_split` | Can LD3 fuse the top split into a layout that directly feeds lane-wise NTT16? | passed | no |
| `gt_layout_consumer_abi_gate` | What exact stock Forward leaf layout do BaseMul and BaseMulAdd consume? | passed | no |
| `gt_transform_domain_tile_abi_search` | Which GT tile ABI gives NTT9 the cheapest producer shape while preserving SoA BaseMul? | passed | no |
| `gt_boundary_cost_campaign` | Across the same P8+tail to BaseMul-SoA boundary, which M3 survivor has the lowest measured Neon cost? | passed; FR-0 retained | no |

See `optimization_scoreboard.md` for decisions and reopen conditions.

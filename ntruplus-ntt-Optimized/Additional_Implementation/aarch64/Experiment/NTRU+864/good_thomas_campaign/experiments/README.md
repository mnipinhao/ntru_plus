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
| `gt_fr0_kernel_realization` | Can FR-0 be exact, stackless handwritten Neon with proved range and leaf maps? | passed; assembly baseline retained | no |
| `gt_ntt16_producer_range` | Does the real twisted radix-2 NTT16 schedule satisfy M5A without an extra reduction? | passed; maximum 8874 | no |
| `gt_fr0_basemul_arithmetic` | Does FR-0 zeta ordering support safe BaseMul/BaseMulAdd arithmetic directly on SoA tiles? | passed | no |
| `gt_fr0_inverse_consumer` | Can FR-0 BaseMul output return to natural coefficients in two load/store passes without a top-branch scratch? | passed | no |
| `gt_fr0_inverse_asm_realization` | Can handwritten Neon realize M5D exactly without coefficient spills, and what do component stores cost? | passed; inverse assembly baseline retained | no |
| `gt_forward_composition_barrett` | Can Algorithm-10 NTT16 and NTT9 compose directly from P8+tail to FR-0 with one pass-2 load/store and no coefficient spill requirement? | passed; assembly schedule frozen | no |
| `gt_forward_barrett_reduction_search` | How many identity reductions does the exact 276-constant Forward schedule require, and where should they be placed? | passed; zero-reduction R0 selected | no |
| `gt_forward_symbolic_dag` | Does the two-product B3 exact DAG fit signed halfwords and have a clean Slothy symbolic-register form under full NTT9 pressure? | passed; OPTIMAL 24-cycle N1-proxy allocation | no |
| `gt_forward_ntt9_level1_slothy` | Can the three complete level-1 B3s fit while the other nine-vector block stays live? | passed; OPTIMAL 48-cycle N1-proxy allocation uses all 15 allowed registers | no |

See `optimization_scoreboard.md` for decisions and reopen conditions.

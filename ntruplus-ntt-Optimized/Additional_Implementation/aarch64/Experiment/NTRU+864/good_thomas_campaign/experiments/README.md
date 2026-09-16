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
| `gt_forward_ntt9_core_slothy` | Can the complete two-level NTT9 plus eta corrections fit while the other nine-vector block stays live? | passed; RA OPTIMAL and split-window full OK with all 15 allowed registers | no |
| `gt_forward_ntt16_ntt9_handoff_slothy` | Can the real NTT16 column output transpose, twist, and enter one complete NTT9 while preserving the other block without coefficient traffic? | passed; RA OPTIMAL and split-window full OK with fixed held-tail `v16` | no |
| `gt_forward_two_ntt9_blocks_slothy` | Can both eight-column NTT9 blocks complete while the first nine outputs and fixed second tail have their real long lifetimes? | passed; 333 instructions, RA OPTIMAL and split-window full OK using all 24 caller-saved vectors | no |
| `gt_forward_full_register_pass2_dag` | Can opening v8-v15 remove copies and repeated constants after paying one outer ABI save/restore? | passed; 91 full-path instructions and 25.90 Pi5 cycles removed; still slower than Official | no |
| `gt_friso2_ntt16_producer_pair_link` | Can the frozen NTT16 producer feed each fused scaled-NTT9 pair directly with no boundary copy, spill, or coefficient traffic? | passed Forward boundary/correctness gate; CF5-A not yet code-size-faithful or timed | no |
| `gt_pipeline_structural_audits` | Which of axis order, twist absorption, inverse liveness, weighted BaseMul, layout/serializer co-design, and reduction placement are actually closed end to end? | audit executes; 2 open and 4 partial; no principle yet passes its end-to-end condition | no |
| `gt_ntt9_first_axis_layout_model` | Can NTT9-first preserve the exact CF5-A transform and beat NTT16-first without another coefficient pass? | rejected; layout fits, but 15/16 cross-phases are dense rather than free row rotations and canonical CRT packing misses the static/memory gate | no |
| `gt_friso2_code_size_faithful_forward` | Can one shared producer plus four inline scaled consumers preserve CF5-A while shrinking its real text footprint and making the FR-ISO2 operation viable? | integration passed; 4,144 object-text bytes saved and CF0 beaten by 45.807 cycles, but operation route rejected at +369.679 cycles before Inverse | no |
| `gt_friso2_scaled_consumer_cost_decomposition` | Under a frozen FR-ISO2 ABI, which scaled NTT9 bank costs explain CF5-B's Forward regression? | passed; four isolated deltas sum to 355.036 cycles versus 351.936 full-path, rejecting constant-load-only work and identifying shared extra mulmods plus top1 dependency loss | no |
| `gt_friso2_scaled_ntt9_arithmetic_dag_gate` | Can affine rescaling of the fixed M5R-D NTT9 topology reach the performance-screening budget of at most 21 mulmods per FR-ISO2 block? | hard gate not passed; bounded MILP and lazy-SAT searches found no witness but did not prove infeasibility; no assembly or Slothy run | no |
| `gt_b3_basemul_leaf_basis_codesign` | Can zero-post-add common-scale B3 islands feed a geometric degree-3 basis that retains FR-ISO2's BaseMul advantage? | algebra proof passes, candidate rejected; all 61 scale nodes collapse to one island, forcing 18 large weights and preserving both widening reductions | no |
| `gt_small_weight_leaf_basis_pareto` | Can four signed-small BaseMul weights preserve direct-wide arithmetic while a different row slope reduces Forward scale-cut cost? | FR-SIGN4 algebra/range passes; exact post-add minimum is eight, but H176 only ties the known 26-mulmod Forward upper bound and no sign4 case meets the 21-mulmod gate | no |
| `gt_m5rd_fr0_range_chain_closure` | Does the latest `9342` M5R-D one-product Forward remain range/scale-safe through M5C and M5E without another reduction? | passed; current chain is `9342 -> 25569 -> 2148/2205 -> 17220`, with linked full-product differential | no |
| `gt_tail_architecture_shootout` | Which current, bank-major, or six-bank-SIMD NTT16 tail architecture wins at equal tail, bank, and full-Forward boundaries? | passed; T1 bank-major selected at 4165.076 versus 4231.714 T0 cycles | no |
| `gt_inverse_st1_lane_store` | Does replacing inverse `UMOV+STRH` scatter with direct `ST1 lane` improve I16-only and complete inverse? | rejected; 634 fewer instructions but 477.866/484.157 more cycles | no |
| `gt_t1_slothy_scheduling` | How much scheduling headroom remains in the fixed T1 one-bank Stage16-to-NTT9 DAG? | promotion rejected; RA+schedule loses 43.306 cycles, while original-RA schedule-only reproducibly gains 8.462 but misses the 20-cycle gate | no |
| `gt_fr0_handwritten_basemul` | Can a same-DAG handwritten FR0 BaseMul and two-group software pipeline beat the exact Pi 5 GCC object? | D1 promoted experimental arithmetic baseline; old 78-instruction H1/H2 deferred | no |
| `gt_fr0_d1_consumer_closure` | Does direct R0 Barrett survive complete polynomial and real Encapsulation serialization consumers? | passed; C1 saves 547.594 cycles and C2 is byte-exact | no |
| `gt_fr0_d1_production_shaped` | Does D1 survive the unchanged stock KEM caller graph and compete with Official? | D1 beats GT-old at every boundary; complete GT remains slower than Official | no |
| `gt_fr0_d1_boundary_cost_decomposition` | Which boundaries explain GT-D1's remaining complete-KEM deficit? | passed; exact instruction/branch ledger identifies byte bridges and Inverse | no |
| `gt_fr0_d1_byte_abi_architecture` | Is the exact FR0/Official/protocol-byte map structured enough for a direct Neon boundary kernel? | passed; route9 selected, naïve tile-local rejected | no |
| `gt_fr0_d1_route9_network_search` | Are exact route9 lane labels regular enough for bounded transpose and TBL Neon networks? | passed; cyclic labels, R9-A/R9-B retained | no |
| `gt_fr0_d1_route9_pmu` | Do reusable route9 Neon bodies beat current and factorized scalar coordinate bridges in both directions? | passed; R9-A wins at 392.238/417.285 cycles | no |
| `gt_fr0_d1_composed_byte_routing_search` | What direct networks implement the composed FR0/pre-post-shuffle maps without Official[864]? | passed; C1 lane-load and C2 two-TBL4 retained | no |
| `gt_fr0_d1_input_once_frombytes` | Can each packed twelve-byte group be decoded once and routed into FR0 without coefficient scratch? | passed isolated; 935.717 versus 1181.090 C1 cycles, pending full callers | no |
| `gt_fr0_d1_input_once_frombytes_full_kem` | Does input-once FromBytes retain its saving in real Encaps and Decaps callers? | passed; -242.063/-817.050 cycles with exact call-ledger closure | no |

See `optimization_scoreboard.md` for decisions and reopen conditions.

D1-P3B11/P3B12 close the reverse input-once route: the peak-14 spill-free
kernel takes 935.717 cycles, and its full callers save 242.063 cycles in Encaps
and 817.050 in Decaps.  It is the experimental FromBytes champion; Production
remains unchanged while ToBytes moves to a separate structured-routing gate.

D1-P3B13/P3B14 reject two tempting boundary fusions before assembly.  Direct
ToBytes pair waiting still needs 28 live output vectors, and atomic adjacent
FromBytes `LD3` reaches 32 live partial outputs before decoder temporaries.
P3B6 and P3B11 therefore remain the experimental direction champions.  The
next work is a changed structured-routing DAG, not scratch or scheduling-only
work.

At the user's request, D1-P3B15 implemented the saturated pair-wait case.  It
is correct and only 5.033 cycles slower than P3B6, but GCC emits 67 non-ABI
vector stack accesses and +113 dynamic instructions.  D1-P3B16 then proves
that completing whole route9 stream pairs makes the no-scratch frontier worse:
six streams fan out to 54 block outputs; even ideal dense packing retains 27
vectors after two pairs, before the next route's nine inputs.  The next
ToBytes search therefore remains partial-output scheduling.

D1-P3B17 directly measures the remaining FromBytes gap in one Pi 5 binary:
P3B11 takes 938.967 cycles versus 794.375 for complete Official unpack plus
shuffle, a +144.592-cycle gap.  With only +84 instructions and 35 fewer
branches, structured lane-routing/dependency cost is now the precise target.

D1-P3B20 tests that structured-routing hypothesis directly.  Fifteen exact
destination-set clusters replace repeated scalar lane moves with TBL2/TBL4
subgraphs without additional input loads or coefficient scratch.  The bytes
are correct, but target lowering spills heavily (180 non-ABI stack accesses)
and regresses P3B11 by 362.787 cycles.  Whole-cluster TBL is rejected.

D1-P3B21 lowers ToBytes' pair frontier from 28 to an exact-DP 26.  It remains
correct, but normalization/packing overlap still produces 69 non-ABI vector
stack accesses and loses 6.750 cycles to P3B6.  P3B6 and P3B11 therefore
remain the independent experimental byte-boundary champions.

D1-P3B22 proves why immediate pair-local ToBytes cannot repair that result:
all 27 adjacent output-pair input neighborhoods are disjoint, so no input-once
order can co-complete a pair.  Retention, rereads or scratch are unavoidable;
the first and third have already failed object/Pi5 gates.

D1-P3B23 succeeds on the reverse boundary by using aligned local structure
instead of P3B20's mask-heavy TBL graph.  Eight four-source clusters use TRN,
four two-source clusters use ZIP, and the irregular remainder keeps lane
moves.  It is spill-free and takes 657.225 versus 938.935 P3B11 cycles,
becoming the isolated experimental FromBytes champion pending full callers.

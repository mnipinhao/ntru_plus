.text
.align 2

/*
 * Candidate A redesigned-TMVP ABI skeleton.
 *
 * This is intentionally only an AAPCS trampoline to the C adapter.  It gives
 * tests and benchmarks a stable assembly boundary that a later Slothy
 * candidate can replace without changing the caller contract.
 */

#ifdef __APPLE__
#define GT_TMVP_CANDIDATE_A_MUL_C _gt_tmvp_quartic_tmvp_incomplete_materialized_stage5_adapter_c
#define GT_TMVP_CANDIDATE_A_ADD_C _gt_tmvp_quartic_tmvp_add_incomplete_materialized_stage5_adapter_c
#else
#define GT_TMVP_CANDIDATE_A_MUL_C gt_tmvp_quartic_tmvp_incomplete_materialized_stage5_adapter_c
#define GT_TMVP_CANDIDATE_A_ADD_C gt_tmvp_quartic_tmvp_add_incomplete_materialized_stage5_adapter_c
#endif

.global gt_tmvp_quartic_tmvp_incomplete_candidate_a_asm
.global _gt_tmvp_quartic_tmvp_incomplete_candidate_a_asm
gt_tmvp_quartic_tmvp_incomplete_candidate_a_asm:
_gt_tmvp_quartic_tmvp_incomplete_candidate_a_asm:
	b GT_TMVP_CANDIDATE_A_MUL_C

.global gt_tmvp_quartic_tmvp_add_incomplete_candidate_a_asm
.global _gt_tmvp_quartic_tmvp_add_incomplete_candidate_a_asm
gt_tmvp_quartic_tmvp_add_incomplete_candidate_a_asm:
_gt_tmvp_quartic_tmvp_add_incomplete_candidate_a_asm:
	b GT_TMVP_CANDIDATE_A_ADD_C

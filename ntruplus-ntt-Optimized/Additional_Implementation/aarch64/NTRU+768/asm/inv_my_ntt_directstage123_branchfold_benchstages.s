/*
 * Benchmark-only wrapper for the legacy direct-stage123 branchfold inverse
 * path.  Use this only when a stage breakdown needs to compare against the
 * production stripe-scratch wrapper.
 */
.equ INVNTT_USE_DIRECT_STAGE123, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.equ INVNTT_BENCH_STAGES, 1
.include "asm/slothy/invntt_opt.s"

/*
 * Opt-in wrapper for the Slothy-generated full GT basemul_add32 pipeline.
 *
 * ABI:
 *   x0 = dst block-major output, 32 int16 coefficients
 *   x1 = a block-major input, 32 int16 coefficients
 *   x2 = b block-major input, 32 int16 coefficients
 *   x3 = c block-major addend, 32 int16 coefficients
 *   x4 = lambda vector, 8 int16 coefficients
 *
 * The generated function also expects x5 to point to Lgt_base_consts.
 * This wrapper supplies that pointer and tail-calls the generated prototype.
 * It is not production-wired.
 */

.text
.align 2

.global base_gt_add32_full_pipeline8_n1_opt
.global _base_gt_add32_full_pipeline8_n1_opt
base_gt_add32_full_pipeline8_n1_opt:
_base_gt_add32_full_pipeline8_n1_opt:
	adr x5, Ladd32_full_pipeline_consts
	b base_gt_add32_full_pipeline_slothy_prototype

.align 4
Ladd32_full_pipeline_consts:
	.hword 0x0d81, 0x4bd4, 0xcd7f, 0xff6d
	.hword 0xfa8f, 0xf9dd, 0xc5d5, 0x0363

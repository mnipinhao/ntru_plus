/*
 * Inline-loop wrapper for the Slothy-generated full GT basemul_add32 pipeline.
 *
 * Unlike asm/base_gt_add32_full_pipeline_wrapper.S, this does not call the
 * generated one-stripe routine 24 times.  It includes the scheduled body inside
 * the loop so the measured production path does not pay per-stripe bl/ret.
 */

.text
.align 2

#ifdef __APPLE__
#define C_SYM_1(sym) _##sym
#define C_SYM(sym) C_SYM_1(sym)
#define LOAD_ADDR_PAGE(reg, sym) adrp reg, C_SYM(sym)@PAGE
#define LOAD_ADDR_OFF(reg, sym) add reg, reg, C_SYM(sym)@PAGEOFF
#else
#define C_SYM(sym) sym
#define LOAD_ADDR_PAGE(reg, sym) adrp reg, C_SYM(sym)
#define LOAD_ADDR_OFF(reg, sym) add reg, reg, :lo12:C_SYM(sym)
#endif

.global poly_basemul_add
.global _poly_basemul_add
.global poly_basemul_add32
.global _poly_basemul_add32
poly_basemul_add:
_poly_basemul_add:
poly_basemul_add32:
_poly_basemul_add32:
	LOAD_ADDR_PAGE(x4, gt_rowbitrev_lambda)
	LOAD_ADDR_OFF(x4, gt_rowbitrev_lambda)
	adr x5, Ladd32_full_pipeline_inline_consts
	ldr q11, [x5]
	mov x6, #24

Ladd32_full_pipeline_inline_loop:
#define BASE_GT_ADD32_FULL_PIPELINE_BODY_ONLY 1
#define BASE_GT_ADD32_FULL_PIPELINE_CONST_PRELOADED 1
#include "../slothy/production/base_gt_add32_full_pipeline.n1.opt.S"
#undef BASE_GT_ADD32_FULL_PIPELINE_CONST_PRELOADED
#undef BASE_GT_ADD32_FULL_PIPELINE_BODY_ONLY
	subs x6, x6, #1
	b.ne Ladd32_full_pipeline_inline_loop

	ret

.align 4
Ladd32_full_pipeline_inline_consts:
	.hword 0x0d81, 0x4bd4, 0xcd7f, 0xff6d
	.hword 0xfa8f, 0xf9dd, 0xc5d5, 0x0363

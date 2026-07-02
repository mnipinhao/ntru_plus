/*
 * Opt-in wrapper for the Slothy-generated baseinv finish microkernel.
 *
 * This is not production-wired.  It loads the fixed Montgomery constants into
 * v0 and tail-calls baseinv_batch_finish8_slothy_prototype from
 * baseinv_batch_finish.n1.opt.S.
 */

.text
.align 2

.global baseinv_batch_finish8_n1_opt
.global _baseinv_batch_finish8_n1_opt
baseinv_batch_finish8_n1_opt:
_baseinv_batch_finish8_n1_opt:
	adr x2, Lbaseinv_finish_consts
	ld1 {v0.8h}, [x2]
	b baseinv_batch_finish8_slothy_prototype

.align 4
Lbaseinv_finish_consts:
	.hword 0x0d81, 0x0000, 0xcd7f, 0x0000
	.hword 0x0000, 0x0000, 0x0000, 0x0000

# Source-of-truth for files linked by the NTRU+768 GT production KEM.
#
# Consumers set GT_SOURCE_ROOT before including this file.  The scheme-local
# Makefile uses "." while aarch64-bench uses its "ntruplus" symlink.
GT_SOURCE_ROOT ?= .

GT_PRODUCTION_SUPPORT_SOURCES = \
	$(GT_SOURCE_ROOT)/asm/gt/support/poly_support.n1.opt.S \
	$(GT_SOURCE_ROOT)/asm/gt/support/poly_cbd_sotp.S

GT_PRODUCTION_NTT_SOURCES = \
	$(GT_SOURCE_ROOT)/asm/gt/ntt/poly_ntt.n1.opt.S \
	$(GT_SOURCE_ROOT)/asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S

GT_PRODUCTION_SAMPLE_NTT_MUL3_SOURCES = \
	$(GT_SOURCE_ROOT)/asm/gt/ntt/poly_ntt_mul3.S \
	$(GT_SOURCE_ROOT)/asm/gt/ntt/poly_ntt_mul3_add1.S

GT_PRODUCTION_INVNTT_SOURCE = \
	$(GT_SOURCE_ROOT)/asm/gt/invntt/poly_invntt.S
GT_PRODUCTION_INVNTT_RMINUS1_SOURCE = \
	$(GT_SOURCE_ROOT)/asm/gt/invntt/poly_invntt_rminus1.S

GT_PRODUCTION_BASEINV_FINISH_SOURCE = \
	$(GT_SOURCE_ROOT)/asm/gt/baseinv/poly_baseinv_batch_finish.n1.opt.S
GT_PRODUCTION_BASEINV_FQINV_SOURCE = \
	$(GT_SOURCE_ROOT)/asm/gt/baseinv/poly_baseinv_fqinv15.S

GT_PRODUCTION_BASE_SOURCES = \
	$(GT_SOURCE_ROOT)/asm/gt/basemul/poly_basemul.S \
	$(GT_SOURCE_ROOT)/asm/gt/basemul/poly_basemul_add.S \
	$(GT_SOURCE_ROOT)/asm/gt/basemul/poly_basemul_scaled_r_input.S \
	$(GT_SOURCE_ROOT)/asm/gt/basemul/poly_basemul_rminus1.S

GT_PRODUCTION_Q31_ENCAP_SOURCE = \
	$(GT_SOURCE_ROOT)/asm/gt/basemul/poly_basemul_add_encap_tobytes_q31.S

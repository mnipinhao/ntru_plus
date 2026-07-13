# Source-of-truth for files linked by the NTRU+768 GT production KEM.
#
# Consumers set GT_SOURCE_ROOT before including this file.  The scheme-local
# Makefile uses "." while aarch64-bench uses its "ntruplus" symlink.
GT_SOURCE_ROOT ?= .

GT_PRODUCTION_SUPPORT_SOURCES = \
	$(GT_SOURCE_ROOT)/asm/gt/support/poly_support_n1.S \
	$(GT_SOURCE_ROOT)/asm/gt/poly_cbd_sotp.s

GT_PRODUCTION_NTT_SOURCES = \
	$(GT_SOURCE_ROOT)/asm/gt/poly_ntt_g1_r123_s2.S \
	$(GT_SOURCE_ROOT)/asm/slothy/production/my_32ntt.opt.s

GT_PRODUCTION_SAMPLE_NTT_SOURCES = \
	$(GT_SOURCE_ROOT)/asm/gt/poly_ntt_triple_scheduled.S \
	$(GT_SOURCE_ROOT)/asm/gt/poly_ntt_triple_add1_scheduled.S

GT_PRODUCTION_INVNTT_SOURCE = \
	$(GT_SOURCE_ROOT)/asm/gt/poly_invntt.s
GT_PRODUCTION_INVNTT_RMINUS1_SOURCE = \
	$(GT_SOURCE_ROOT)/asm/gt/poly_invntt_rminus1.S

GT_PRODUCTION_BASEINV_FINISH_SOURCE = \
	$(GT_SOURCE_ROOT)/asm/slothy/production/baseinv_batch_finish_loop_n1.S
GT_PRODUCTION_BASEINV_FQINV_SOURCE = \
	$(GT_SOURCE_ROOT)/asm/gt/poly_baseinv_fqinv15.S

GT_PRODUCTION_BASE_SOURCES = \
	$(GT_SOURCE_ROOT)/asm/gt/poly_basemul.S \
	$(GT_SOURCE_ROOT)/asm/gt/poly_basemul_add.S \
	$(GT_SOURCE_ROOT)/asm/gt/poly_basemul_scaled_r_input.S \
	$(GT_SOURCE_ROOT)/asm/gt/poly_basemul_rminus1.S

GT_PRODUCTION_Q31_ENCAP_SOURCE = \
	$(GT_SOURCE_ROOT)/asm/gt/poly_basemul_add_encap_tobytes_q31.S

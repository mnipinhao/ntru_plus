# Source-of-truth for files linked by the NTRU+768 GT production KEM.
#
# Consumers set GT_SOURCE_ROOT before including this file.  The scheme-local
# Makefile uses "." while aarch64-bench uses its "ntruplus" symlink.
GT_SOURCE_ROOT ?= .

GT_PRODUCTION_SUPPORT_SOURCES = \
	$(GT_SOURCE_ROOT)/poly_gt_canonical.c \
	$(GT_SOURCE_ROOT)/asm/gt/support/poly_canonical_pack.S \
	$(GT_SOURCE_ROOT)/asm/gt/support/poly_canonical_pack_p1.S \
	$(GT_SOURCE_ROOT)/asm/gt/support/poly_canonical_unpack_u1.S \
	$(GT_SOURCE_ROOT)/asm/gt/support/poly_support.n1.opt.S \
	$(GT_SOURCE_ROOT)/asm/gt/support/poly_cbd_sotp.S

GT_PRODUCTION_NTT_SOURCES = \
	$(GT_SOURCE_ROOT)/asm/gt/ntt/poly_ntt.n1.opt.S \
	$(GT_SOURCE_ROOT)/asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S

GT_PRODUCTION_SAMPLE_NTT_MUL3_SOURCES = \
	$(GT_SOURCE_ROOT)/asm/gt/ntt/poly_ntt_mul3.S \
	$(GT_SOURCE_ROOT)/asm/gt/ntt/poly_ntt_mul3_add1.S

GT_PRODUCTION_BPQ_CQ_KEYGEN_SOURCES = \
	$(GT_SOURCE_ROOT)/gt/keygen_bpq_cq.c \
	$(GT_SOURCE_ROOT)/asm/gt/keygen_bpq_cq/ntt_mul3.S \
	$(GT_SOURCE_ROOT)/asm/gt/keygen_bpq_cq/ntt_mul3_add1.S \
	$(GT_SOURCE_ROOT)/asm/gt/keygen_bpq_cq/ntt32_to_bpq.S \
	$(GT_SOURCE_ROOT)/asm/gt/keygen_bpq_cq/baseinv_prepare.S \
	$(GT_SOURCE_ROOT)/asm/gt/keygen_bpq_cq/baseinv_tree.S \
	$(GT_SOURCE_ROOT)/asm/gt/keygen_bpq_cq/baseinv_finish.S \
	$(GT_SOURCE_ROOT)/asm/gt/keygen_bpq_cq/basemul.S \
	$(GT_SOURCE_ROOT)/asm/gt/keygen_bpq_cq/pack_cq.S \
	$(GT_SOURCE_ROOT)/asm/gt/keygen_bpq_cq/pack_bpq_p1.S

GT_PRODUCTION_INVNTT_SOURCE = \
	$(GT_SOURCE_ROOT)/asm/gt/invntt/poly_invntt.S
GT_PRODUCTION_INVNTT_RMINUS1_SOURCE = \
	$(GT_SOURCE_ROOT)/asm/gt/invntt/poly_invntt_rminus1.S

GT_PRODUCTION_BASEINV_FINISH_SOURCE = \
	$(GT_SOURCE_ROOT)/asm/gt/baseinv/poly_baseinv_batch_finish.n1.opt.S
GT_PRODUCTION_BASEINV_FQINV_SOURCE = \
	$(GT_SOURCE_ROOT)/asm/gt/baseinv/poly_baseinv_fqinv15.S

GT_PRODUCTION_BPQ_CQ_KEYGEN_RUNTIME_SOURCES = \
	$(GT_PRODUCTION_BPQ_CQ_KEYGEN_SOURCES) \
	$(GT_PRODUCTION_BASEINV_FQINV_SOURCE)

GT_PRODUCTION_BASEINV_TREE_SOURCE = \
	$(GT_SOURCE_ROOT)/poly_gt_baseinv_hier_k8_tree.c
GT_PRODUCTION_BASEINV_PAPER_HIER_K8_SOURCE = \
	$(GT_SOURCE_ROOT)/experiments/baseinv_hier_paper_neon/paper_hier_neon.c

GT_PRODUCTION_BASE_SOURCES = \
	$(GT_SOURCE_ROOT)/asm/gt/basemul/poly_basemul.S \
	$(GT_SOURCE_ROOT)/asm/gt/basemul/poly_basemul_add.S \
	$(GT_SOURCE_ROOT)/asm/gt/basemul/poly_basemul_scaled_r_input.S \
	$(GT_SOURCE_ROOT)/asm/gt/basemul/poly_basemul_rminus1.S

GT_PRODUCTION_Q31_ENCAP_SOURCE = \
	$(GT_SOURCE_ROOT)/asm/gt/basemul/poly_basemul_add_encap_tobytes_q31.n1.opt.S

# Decapsulation-only canonical pointwise production backend.
GT_PRODUCTION_DECAP_CANONICAL_POINTWISE_SOURCES = \
	$(GT_SOURCE_ROOT)/gt/decap_verify.c \
	$(GT_SOURCE_ROOT)/asm/gt/decap/verify_pointwise.S

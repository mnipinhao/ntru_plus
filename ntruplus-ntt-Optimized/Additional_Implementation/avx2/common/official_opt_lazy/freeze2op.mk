# Shared rules for the 2-op-freeze poly_tobytes candidates of Official
# NTRU+768 / NTRU+1152 AVX2, stacked on the caller-lazy Forward.  Included by
#   NTRU+768/experiments/avx2_official_opt_freeze_001/Makefile
#   NTRU+1152/experiments/avx2_official_opt_001/Makefile
# after lazy.mk (whose variables it reuses).
#   candidate  avx2-officialopt-lazy-freeze-$(PARAM)-exp001 = lazy Forward + freeze2op tobytes
#   control    freeze-only                                   = Official Forward + freeze2op tobytes
# The lazy-only candidate and its rules are untouched.  Phase A + same-ELF
# diagnostic build only; no host-control rule, no SUPERCOP campaign.
# Optional: LAZY_REFERENCE = a reference lazy Forward .s (read only) whose
# instruction stream the generated $(LAZY_ASM) must equal (NTRU+768 qual001).

ifeq ($(filter $(PARAM),768 1152),)
$(error freeze2op.mk: PARAM must be 768 or 1152)
endif

FREEZE := ntruplus$(PARAM)_officialopt_tobytes_freeze2op
FREEZE_ASM := asm/$(FREEZE).s
FREEZE_GEN := $(COMMON)/tools/generate_tobytes_freeze2op.py
FREEZE_KEM_SRC := $(COMMON)/tests/test_kem_lazy.c $(COMMON)/tests/support/crypto_declassify.c \
	$(LAZY_ASM) $(FREEZE_ASM) $(COMMON_C) $(COMMON_ASM)
FREEZE_UNIT_SRC := $(COMMON)/tests/test_tobytes_freeze2op.c $(COMMON)/tests/support/crypto_declassify.c \
	$(LAZY_ASM) $(FREEZE_ASM) $(COMMON_C) $(COMMON_ASM)
FREEZE_TWIN_SRC := $(COMMON)/tests/test_freeze_2op.c $(OFFICIAL)/consts.c
FREEZE_DEFS := -DFREEZE_TOBYTES=$(FREEZE) -DLAZY_NTT=$(LAZY)

.PHONY: generate-freeze check-freeze-generate freeze-prove lazy-stream-equal freeze-check \
	freeze-sanitize freeze-audit freeze-mutate freeze-phase-a freeze-record freeze-bench freeze-bench-keypair

generate-freeze:
	$(PYTHON) $(FREEZE_GEN) --param $(PARAM) --experiment .

check-freeze-generate: | $(EVIDENCE)
	$(PYTHON) $(FREEZE_GEN) --param $(PARAM) --experiment . --check --meta $(EVIDENCE)/freeze2op-generation.json

freeze-prove: | $(EVIDENCE)
	$(PYTHON) $(COMMON)/tools/prove_freeze_2op.py --experiment . --output $(EVIDENCE)/freeze-2op-proof.json

ifdef LAZY_REFERENCE
lazy-stream-equal: | $(EVIDENCE)
	$(PYTHON) $(COMMON)/tools/check_lazy_stream_equal.py --candidate $(LAZY_ASM) \
		--reference $(LAZY_REFERENCE) --output $(EVIDENCE)/lazy-stream-equality.json
else
lazy-stream-equal:
	@echo "lazy-stream-equal: no LAZY_REFERENCE for NTRU+$(PARAM); skipped"
endif

# test_kem_lazy.c drives whichever object is renamed to official_lazy_*.
define freeze_variant # $(1)=build dir, $(2)=flags, $(3)=name (kem_lazy_freeze2op|kem_freeze2op)
$(1)/$(3).o: src/$(3).c src/kem_lazy.c | $(1)
	$(CC) $(2) $(INCLUDES) $(LAZY_RENAME) -c -o $$@ $$<
$(1)/test_$(3): $(FREEZE_KEM_SRC) $(1)/kem_ref.o $(1)/$(3).o $(1)/kat_aes.o $(1)/kat_rng.o | $(1)
	$(CC) $(2) -maes -I$(KAT) $(INCLUDES) $(KEM_WRAP) -o $$@ $$^
$(1)/test_$(3)_fretry: $(FREEZE_KEM_SRC) $(1)/kem_ref.o $(1)/$(3).o $(1)/kat_aes.o $(1)/kat_rng.o | $(1)
	$(CC) $(2) -maes -I$(KAT) $(INCLUDES) $(KEM_WRAP) $(FRETRY) -o $$@ $$^
endef
define freeze_unit # $(1)=build dir, $(2)=flags
$(1)/test_tobytes_freeze2op: $(FREEZE_UNIT_SRC) | $(1)
	$(CC) $(2) $(INCLUDES) $(FREEZE_DEFS) -o $$@ $$^
$(1)/test_freeze_2op: $(FREEZE_TWIN_SRC) | $(1)
	$(CC) $(2) $(INCLUDES) -o $$@ $$^
endef
$(eval $(call freeze_variant,$(BUILD),$(CFLAGS),kem_lazy_freeze2op))
$(eval $(call freeze_variant,$(BUILD),$(CFLAGS),kem_freeze2op))
$(eval $(call freeze_variant,$(BUILD_SAN),$(SANFLAGS),kem_lazy_freeze2op))
$(eval $(call freeze_variant,$(BUILD_SAN),$(SANFLAGS),kem_freeze2op))
$(eval $(call freeze_unit,$(BUILD),$(CFLAGS)))
$(eval $(call freeze_unit,$(BUILD_SAN),$(SANFLAGS)))

FREEZE_TESTS := test_freeze_2op test_tobytes_freeze2op test_kem_lazy_freeze2op test_kem_lazy_freeze2op_fretry \
	test_kem_freeze2op test_kem_freeze2op_fretry

freeze-check: check-upstream check-generate check-freeze-generate freeze-prove lazy-stream-equal \
		$(addprefix $(BUILD)/,$(FREEZE_TESTS))
	$(foreach t,$(FREEZE_TESTS),$(BUILD)/$(t) &&) true

freeze-sanitize: $(addprefix $(BUILD_SAN)/,$(FREEZE_TESTS))
	$(foreach t,$(FREEZE_TESTS),$(SAN_ENV) $(BUILD_SAN)/$(t) &&) true

freeze-audit: $(BUILD)/test_kem_lazy_freeze2op $(BUILD)/kem_freeze2op.o $(BUILD)/kem_lazy.o | $(EVIDENCE)
	$(PYTHON) $(COMMON)/tools/audit_tobytes_freeze2op.py --param $(PARAM) --experiment . \
		--elf $(BUILD)/test_kem_lazy_freeze2op --output $(EVIDENCE)/freeze2op-linked-summary.json

# Mutation check: the tobytes differential must reject 5 one-line mutants.
freeze-mutate: $(BUILD)/test_tobytes_freeze2op | $(EVIDENCE)
	$(PYTHON) $(COMMON)/tools/mutate_tobytes_freeze2op.py --param $(PARAM) --experiment . \
		--output $(EVIDENCE)/freeze2op-mutation-check.json

freeze-phase-a: freeze-check freeze-sanitize freeze-audit freeze-mutate

# Curated, deterministic-shape evidence into the tracked results dir.
freeze-record: freeze-phase-a
	mkdir -p results/freeze2op-phase-a
	cp $(EVIDENCE)/freeze2op-linked-summary.json $(EVIDENCE)/freeze-2op-proof.json \
		$(EVIDENCE)/freeze2op-generation.json $(EVIDENCE)/freeze2op-mutation-check.json results/freeze2op-phase-a/
	$(if $(LAZY_REFERENCE),cp $(EVIDENCE)/lazy-stream-equality.json results/freeze2op-phase-a/)

# ------------------------------------------------ same-ELF component/caller diagnostic
# Official (v0), lazy (v1), lazy+freeze2op (v2) and freeze-only (v3) KEM
# translation units plus Official / freeze2op tobytes in one ELF; common O3GC
# recipe, cpucycles from the disposable SUPERCOP campaign (read only).
# supercop-derived, not Native.  The _swapped ELF links the same objects and
# asm in reverse order (placement control).
FZ_RENAME = -Dcrypto_kem_keypair=$(1)_keypair -Dcrypto_kem_enc=$(1)_enc -Dcrypto_kem_dec=$(1)_dec
define fz_bench_obj # $(1)=vN $(2)=source
$(BUILD)/fzbench_$(1).o: $(COMMON)/bench/kem_diag.c $(2) src/kem_lazy.c | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I. $(INCLUDES) $(call FZ_RENAME,$(1)) '-DKEM_SOURCE="$(2)"' \
		-DDERAND_NAME=$(1)_enc_derand -c -o $$@ $$<
endef
$(eval $(call fz_bench_obj,v0,$(OFFICIAL)/kem.c))
$(eval $(call fz_bench_obj,v1,src/kem_lazy.c))
$(eval $(call fz_bench_obj,v2,src/kem_lazy_freeze2op.c))
$(eval $(call fz_bench_obj,v3,src/kem_freeze2op.c))

FZ_OBJS := $(BUILD)/fzbench_v0.o $(BUILD)/fzbench_v1.o $(BUILD)/fzbench_v2.o $(BUILD)/fzbench_v3.o
FZ_OBJS_REV := $(BUILD)/fzbench_v3.o $(BUILD)/fzbench_v2.o $(BUILD)/fzbench_v1.o $(BUILD)/fzbench_v0.o
FZ_COMMON := $(COMMON)/bench/bench_freeze2op.c $(COMMON)/tests/support/crypto_declassify.c
$(BUILD)/bench_freeze2op: $(FZ_COMMON) $(FZ_OBJS) $(LAZY_ASM) $(FREEZE_ASM) $(COMMON_C) $(COMMON_ASM) \
		$(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -maes -I$(KAT) -I$(CPU_INCLUDE) $(INCLUDES) $(FREEZE_DEFS) -o $@ $^ $(CPU_LIB)
$(BUILD)/bench_freeze2op_swapped: $(FZ_COMMON) $(FZ_OBJS_REV) $(FREEZE_ASM) $(LAZY_ASM) $(COMMON_C) $(COMMON_ASM) \
		$(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -maes -I$(KAT) -I$(CPU_INCLUDE) $(INCLUDES) $(FREEZE_DEFS) -o $@ $^ $(CPU_LIB)

freeze-bench: $(BUILD)/bench_freeze2op $(BUILD)/bench_freeze2op_swapped

# ------------------------------------------------ seed-matched paired Keypair
# Shared unchanged harness (bench/bench_keypair_seedmatched.c): A = official_ref_*
# role bound to the lazy-only KEM, B = official_lazy_* role bound to the
# lazy+freeze2op KEM; _swapped links B before A.  supercop-derived, not Native.
define fz_kp_obj # $(1)=name $(2)=source $(3)=rename
$(BUILD)/fzkp_$(1).o: $(COMMON)/bench/kem_diag.c $(2) src/kem_lazy.c | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I. $(INCLUDES) $(3) '-DKEM_SOURCE="$(2)"' -DDERAND_NAME=fzkp_$(1)_derand -c -o $$@ $$<
endef
$(eval $(call fz_kp_obj,A_lazy,src/kem_lazy.c,$(REF_RENAME)))
$(eval $(call fz_kp_obj,B_lazy_freeze2op,src/kem_lazy_freeze2op.c,$(LAZY_RENAME)))
FZKP_DEPS := $(KP_SRC) $(LAZY_ASM) $(FREEZE_ASM) $(COMMON_C) $(COMMON_ASM)
$(BUILD)/kp_lazyfreeze_vs_lazy: $(BUILD)/fzkp_A_lazy.o $(BUILD)/fzkp_B_lazy_freeze2op.o $(FZKP_DEPS) | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I$(CPU_INCLUDE) $(INCLUDES) -o $@ $^ $(CPU_LIB)
$(BUILD)/kp_lazyfreeze_vs_lazy_swapped: $(BUILD)/fzkp_B_lazy_freeze2op.o $(BUILD)/fzkp_A_lazy.o $(FZKP_DEPS) | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I$(CPU_INCLUDE) $(INCLUDES) -o $@ $^ $(CPU_LIB)

freeze-bench-keypair: $(BUILD)/kp_lazyfreeze_vs_lazy $(BUILD)/kp_lazyfreeze_vs_lazy_swapped

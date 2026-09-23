# NTRU+864 only: direct 12-bit codec (exp002) candidates, Phase A + diagnostic.
# Included by ./Makefile after lazy.mk and codec.mk (whose variables it reuses).
#   candidate  avx2-officialopt-lazy-codec-864-exp002 = lazy Forward + direct codec
#   control    direct-codec-only                       = Official Forward + direct codec
#   control    tobytes_fused_min                       = exp001 tobytes + 2-op freeze only
# exp001 (codec.mk) and the lazy-only candidate are untouched.  No host-control rule.

DIRECT_ASM := asm/ntruplus864_officialopt_codec_direct.s
MIN_ASM := asm/ntruplus864_officialopt_codec_fused_min.s
DIRECT_GEN := tools/generate_codec_direct.py
DIRECT_KEM_SRC := $(COMMON)/tests/test_kem_lazy.c $(COMMON)/tests/support/crypto_declassify.c \
	$(LAZY_ASM) $(DIRECT_ASM) $(COMMON_C) $(COMMON_ASM)
DIRECT_TEST_SRC := tests/test_codec_direct.c $(COMMON)/tests/support/crypto_declassify.c \
	$(DIRECT_ASM) $(COMMON_C) $(COMMON_ASM)
MIN_TEST_SRC := tests/test_codec_fused_min.c $(COMMON)/tests/support/crypto_declassify.c \
	$(MIN_ASM) $(CODEC_ASM) $(COMMON_C) $(COMMON_ASM)
FREEZE_TEST_SRC := tests/test_freeze_2op.c $(OFFICIAL)/consts.c

.PHONY: generate-codec-direct check-codec-direct-generate direct-prove direct-check direct-sanitize \
	direct-audit direct-phase-a direct-record direct-bench direct-bench-keypair

generate-codec-direct:
	$(PYTHON) $(DIRECT_GEN) --experiment .

check-codec-direct-generate:
	$(PYTHON) $(DIRECT_GEN) --experiment . --check

# Exhaustive 2-op freeze record (NTRU+864 pinned sources; add the read-only
# NTRU+768/1152 pristine avx2 dirs for the portability record).
PRISTINE_KEM := $(SUPERCOP_PRISTINE)/crypto_kem
direct-prove: | $(EVIDENCE)
	$(PYTHON) tools/prove_freeze_2op.py --experiment . \
		--pack-dir $(PRISTINE_KEM)/ntruplus768/avx2 --pack-dir $(PRISTINE_KEM)/ntruplus1152/avx2 \
		--output $(EVIDENCE)/freeze-2op-proof.json

define direct_variant # $(1)=build dir, $(2)=flags, $(3)=name (kem_codec_direct|kem_lazy_codec_direct)
$(1)/$(3).o: src/$(3).c src/kem_lazy.c | $(1)
	$(CC) $(2) $(INCLUDES) $(LAZY_RENAME) -c -o $$@ $$<
$(1)/test_$(3): $(DIRECT_KEM_SRC) $(1)/kem_ref.o $(1)/$(3).o $(1)/kat_aes.o $(1)/kat_rng.o | $(1)
	$(CC) $(2) -maes -I$(KAT) $(INCLUDES) $(KEM_WRAP) -o $$@ $$^
$(1)/test_$(3)_fretry: $(DIRECT_KEM_SRC) $(1)/kem_ref.o $(1)/$(3).o $(1)/kat_aes.o $(1)/kat_rng.o | $(1)
	$(CC) $(2) -maes -I$(KAT) $(INCLUDES) $(KEM_WRAP) $(FRETRY) -o $$@ $$^
endef
$(eval $(call direct_variant,$(BUILD),$(CFLAGS),kem_codec_direct))
$(eval $(call direct_variant,$(BUILD),$(CFLAGS),kem_lazy_codec_direct))
$(eval $(call direct_variant,$(BUILD_SAN),$(SANFLAGS),kem_codec_direct))
$(eval $(call direct_variant,$(BUILD_SAN),$(SANFLAGS),kem_lazy_codec_direct))

define direct_unit # $(1)=build dir, $(2)=flags, $(3)=binary, $(4)=sources
$(1)/$(3): $(4) | $(1)
	$(CC) $(2) $(INCLUDES) -o $$@ $$^
endef
$(eval $(call direct_unit,$(BUILD),$(CFLAGS),test_codec_direct,$(DIRECT_TEST_SRC)))
$(eval $(call direct_unit,$(BUILD),$(CFLAGS),test_codec_fused_min,$(MIN_TEST_SRC)))
$(eval $(call direct_unit,$(BUILD),$(CFLAGS),test_freeze_2op,$(FREEZE_TEST_SRC)))
$(eval $(call direct_unit,$(BUILD_SAN),$(SANFLAGS),test_codec_direct,$(DIRECT_TEST_SRC)))
$(eval $(call direct_unit,$(BUILD_SAN),$(SANFLAGS),test_codec_fused_min,$(MIN_TEST_SRC)))
$(eval $(call direct_unit,$(BUILD_SAN),$(SANFLAGS),test_freeze_2op,$(FREEZE_TEST_SRC)))

DIRECT_TESTS := test_freeze_2op test_codec_direct test_codec_fused_min test_kem_lazy_codec_direct \
	test_kem_lazy_codec_direct_fretry test_kem_codec_direct test_kem_codec_direct_fretry

direct-check: check-upstream check-generate check-codec-generate check-codec-direct-generate direct-prove \
		$(addprefix $(BUILD)/,$(DIRECT_TESTS))
	$(foreach t,$(DIRECT_TESTS),$(BUILD)/$(t) &&) true

direct-sanitize: $(addprefix $(BUILD_SAN)/,$(DIRECT_TESTS))
	$(foreach t,$(DIRECT_TESTS),$(SAN_ENV) $(BUILD_SAN)/$(t) &&) true

direct-audit: $(BUILD)/test_kem_lazy_codec_direct $(BUILD)/test_kem_codec_direct $(BUILD)/test_codec_fused_min \
		$(BUILD)/test_kem_lazy_codec | $(EVIDENCE)
	$(PYTHON) tools/audit_codec_direct.py --experiment . --elf $(BUILD)/test_kem_lazy_codec_direct \
		--min-elf $(BUILD)/test_codec_fused_min --exp001-elf $(BUILD)/test_kem_lazy_codec \
		--output $(EVIDENCE)/codec-direct-linked-summary.json

direct-phase-a: direct-check direct-sanitize direct-audit

direct-record: direct-phase-a
	mkdir -p results/codec-direct-phase-a
	cp $(EVIDENCE)/codec-direct-linked-summary.json $(EVIDENCE)/freeze-2op-proof.json results/codec-direct-phase-a/

# ------------------------------------------------ same-ELF component/caller diagnostic
# Official, lazy, exp001 (lazy+fused codec) and exp002 (lazy+direct codec) KEM
# translation units plus Official / exp001 / fused_min / direct codec kernels in
# one ELF; common O3GC recipe, cpucycles from the disposable SUPERCOP campaign
# (read only).  supercop-derived, not Native.  The _swapped ELF links the same
# objects and asm in reverse order (placement control).
$(BUILD)/dbench_lazy_codec_direct.o: $(COMMON)/bench/kem_diag.c src/kem_lazy_codec_direct.c src/kem_lazy.c | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I. $(INCLUDES) $(call CODEC_RENAME,v4) '-DKEM_SOURCE="src/kem_lazy_codec_direct.c"' \
		-DDERAND_NAME=v4_enc_derand -c -o $@ $<

DBENCH_OBJS := $(BUILD)/cbench_ref.o $(BUILD)/cbench_lazy.o $(BUILD)/cbench_lazy_codec.o $(BUILD)/dbench_lazy_codec_direct.o
DBENCH_OBJS_REV := $(BUILD)/dbench_lazy_codec_direct.o $(BUILD)/cbench_lazy_codec.o $(BUILD)/cbench_lazy.o $(BUILD)/cbench_ref.o
$(BUILD)/bench_codec_direct: bench/bench_codec_direct.c $(COMMON)/tests/support/crypto_declassify.c \
		$(DBENCH_OBJS) $(LAZY_ASM) $(CODEC_ASM) $(MIN_ASM) $(DIRECT_ASM) $(COMMON_C) $(COMMON_ASM) \
		$(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -maes -I$(KAT) -I$(CPU_INCLUDE) $(INCLUDES) -o $@ $^ $(CPU_LIB)
$(BUILD)/bench_codec_direct_swapped: bench/bench_codec_direct.c $(COMMON)/tests/support/crypto_declassify.c \
		$(DBENCH_OBJS_REV) $(DIRECT_ASM) $(MIN_ASM) $(CODEC_ASM) $(LAZY_ASM) $(COMMON_C) $(COMMON_ASM) \
		$(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -maes -I$(KAT) -I$(CPU_INCLUDE) $(INCLUDES) -o $@ $^ $(CPU_LIB)

direct-bench: $(BUILD)/bench_codec_direct $(BUILD)/bench_codec_direct_swapped

# ------------------------------------------------ seed-matched paired Keypair
# Shared unchanged harness; A = official_ref_* role, B = official_lazy_* role.
$(eval $(call kp_obj,A_lazy_codec,src/kem_lazy_codec.c,$(REF_RENAME)))
$(eval $(call kp_obj,B_lazy_codec_direct,src/kem_lazy_codec_direct.c,$(LAZY_RENAME)))
KPD_DEPS := $(KP_SRC) $(LAZY_ASM) $(CODEC_ASM) $(DIRECT_ASM) $(COMMON_C) $(COMMON_ASM)
$(BUILD)/kp_direct_vs_official: $(BUILD)/kp_A_official.o $(BUILD)/kp_B_lazy_codec_direct.o $(KPD_DEPS) | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I$(CPU_INCLUDE) $(INCLUDES) -o $@ $^ $(CPU_LIB)
$(BUILD)/kp_direct_vs_exp001: $(BUILD)/kp_A_lazy_codec.o $(BUILD)/kp_B_lazy_codec_direct.o $(KPD_DEPS) | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I$(CPU_INCLUDE) $(INCLUDES) -o $@ $^ $(CPU_LIB)
$(BUILD)/kp_direct_vs_lazy: $(BUILD)/kp_A_lazy.o $(BUILD)/kp_B_lazy_codec_direct.o $(KPD_DEPS) | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I$(CPU_INCLUDE) $(INCLUDES) -o $@ $^ $(CPU_LIB)
direct-bench-keypair: $(BUILD)/kp_direct_vs_official $(BUILD)/kp_direct_vs_exp001 $(BUILD)/kp_direct_vs_lazy

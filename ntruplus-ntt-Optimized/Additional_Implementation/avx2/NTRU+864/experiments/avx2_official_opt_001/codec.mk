# NTRU+864 only: layout-fused codec (Option A) candidates, Phase A.
# Included by ./Makefile after the shared lazy.mk (whose variables it reuses).
#   candidate  avx2-officialopt-lazy-codec-864-exp001 = lazy Forward + fused codec
#   control    codec-only                             = Official Forward + fused codec
# The lazy-only candidate and its rules are untouched.  No host-control rule.

CODEC_ASM := asm/ntruplus864_officialopt_codec_fused.s
CODEC_GEN := tools/generate_codec_fused.py
CODEC_KEM_SRC := $(COMMON)/tests/test_kem_lazy.c $(COMMON)/tests/support/crypto_declassify.c \
	$(LAZY_ASM) $(CODEC_ASM) $(COMMON_C) $(COMMON_ASM)
CODEC_TEST_SRC := tests/test_codec_fused.c $(COMMON)/tests/support/crypto_declassify.c \
	$(CODEC_ASM) $(COMMON_C) $(COMMON_ASM)

.PHONY: generate-codec check-codec-generate codec-check codec-sanitize codec-audit codec-phase-a codec-record codec-bench

generate-codec:
	$(PYTHON) $(CODEC_GEN) --experiment .

check-codec-generate:
	$(PYTHON) $(CODEC_GEN) --experiment . --check

# test_kem_lazy.c drives whichever object is renamed to official_lazy_*.
define codec_variant # $(1)=build dir, $(2)=flags, $(3)=name (kem_codec|kem_lazy_codec)
$(1)/$(3).o: src/$(3).c src/kem_lazy.c | $(1)
	$(CC) $(2) $(INCLUDES) $(LAZY_RENAME) -c -o $$@ $$<
$(1)/test_$(3): $(CODEC_KEM_SRC) $(1)/kem_ref.o $(1)/$(3).o $(1)/kat_aes.o $(1)/kat_rng.o | $(1)
	$(CC) $(2) -maes -I$(KAT) $(INCLUDES) $(KEM_WRAP) -o $$@ $$^
$(1)/test_$(3)_fretry: $(CODEC_KEM_SRC) $(1)/kem_ref.o $(1)/$(3).o $(1)/kat_aes.o $(1)/kat_rng.o | $(1)
	$(CC) $(2) -maes -I$(KAT) $(INCLUDES) $(KEM_WRAP) $(FRETRY) -o $$@ $$^
endef
$(eval $(call codec_variant,$(BUILD),$(CFLAGS),kem_codec))
$(eval $(call codec_variant,$(BUILD),$(CFLAGS),kem_lazy_codec))
$(eval $(call codec_variant,$(BUILD_SAN),$(SANFLAGS),kem_codec))
$(eval $(call codec_variant,$(BUILD_SAN),$(SANFLAGS),kem_lazy_codec))

$(BUILD)/test_codec_fused: $(CODEC_TEST_SRC) | $(BUILD)
	$(CC) $(CFLAGS) $(INCLUDES) -o $@ $^

$(BUILD_SAN)/test_codec_fused: $(CODEC_TEST_SRC) | $(BUILD_SAN)
	$(CC) $(SANFLAGS) $(INCLUDES) -o $@ $^

CODEC_TESTS := test_codec_fused test_kem_lazy_codec test_kem_lazy_codec_fretry test_kem_codec test_kem_codec_fretry

codec-check: check-upstream check-generate check-codec-generate $(addprefix $(BUILD)/,$(CODEC_TESTS))
	$(foreach t,$(CODEC_TESTS),$(BUILD)/$(t) &&) true

codec-sanitize: $(addprefix $(BUILD_SAN)/,$(CODEC_TESTS))
	$(foreach t,$(CODEC_TESTS),$(SAN_ENV) $(BUILD_SAN)/$(t) &&) true

codec-audit: $(BUILD)/test_kem_lazy_codec $(BUILD)/test_kem_codec | $(EVIDENCE)
	$(PYTHON) tools/audit_codec_fused.py --experiment . --elf $(BUILD)/test_kem_lazy_codec \
		--output $(EVIDENCE)/codec-linked-summary.json

codec-phase-a: codec-check codec-sanitize codec-audit

codec-record: codec-phase-a
	mkdir -p results/codec-phase-a
	cp $(EVIDENCE)/codec-linked-summary.json results/codec-phase-a/

# ------------------------------------------------ same-ELF component/caller diagnostic
# Four KEM translation units in one ELF (Official, lazy, codec, lazy+codec)
# plus the component kernels; common O3GC recipe, cpucycles from the
# disposable SUPERCOP campaign (read only).  supercop-derived, not Native.
CODEC_RENAME = -Dcrypto_kem_keypair=$(1)_keypair -Dcrypto_kem_enc=$(1)_enc -Dcrypto_kem_dec=$(1)_dec
$(BUILD)/cbench_ref.o: $(COMMON)/bench/kem_diag.c $(OFFICIAL)/kem.c | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I. $(INCLUDES) $(call CODEC_RENAME,v0) '-DKEM_SOURCE="$(OFFICIAL)/kem.c"' \
		-DDERAND_NAME=v0_enc_derand -c -o $@ $<
$(BUILD)/cbench_lazy.o: $(COMMON)/bench/kem_diag.c src/kem_lazy.c | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I. $(INCLUDES) $(call CODEC_RENAME,v1) '-DKEM_SOURCE="src/kem_lazy.c"' \
		-DDERAND_NAME=v1_enc_derand -c -o $@ $<
$(BUILD)/cbench_codec.o: $(COMMON)/bench/kem_diag.c src/kem_codec.c | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I. $(INCLUDES) $(call CODEC_RENAME,v2) '-DKEM_SOURCE="src/kem_codec.c"' \
		-DDERAND_NAME=v2_enc_derand -c -o $@ $<
$(BUILD)/cbench_lazy_codec.o: $(COMMON)/bench/kem_diag.c src/kem_lazy_codec.c src/kem_lazy.c | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I. $(INCLUDES) $(call CODEC_RENAME,v3) '-DKEM_SOURCE="src/kem_lazy_codec.c"' \
		-DDERAND_NAME=v3_enc_derand -c -o $@ $<

CBENCH_OBJS := $(BUILD)/cbench_ref.o $(BUILD)/cbench_lazy.o $(BUILD)/cbench_codec.o $(BUILD)/cbench_lazy_codec.o
$(BUILD)/bench_codec_fused: bench/bench_codec_fused.c $(COMMON)/tests/support/crypto_declassify.c \
		$(CBENCH_OBJS) $(LAZY_ASM) $(CODEC_ASM) $(COMMON_C) $(COMMON_ASM) \
		$(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -maes -I$(KAT) -I$(CPU_INCLUDE) $(INCLUDES) -o $@ $^ $(CPU_LIB)

codec-bench: $(BUILD)/bench_codec_fused

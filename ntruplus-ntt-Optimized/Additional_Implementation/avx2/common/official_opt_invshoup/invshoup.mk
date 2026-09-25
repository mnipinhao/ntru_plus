# Shared rules for the NTRU+768 / 864 / 1152 fused inverse ("Inverse D": invntt_scale +
# crepmod3 in one call) and Shoup BaseMul (Encap BaseMul + second Decap BaseMul) candidates,
# stacked on each parameter's current best (the HT candidate).  Included last by
#   NTRU+768/experiments/avx2_official_opt_freeze_001/Makefile
#   NTRU+864/experiments/avx2_official_opt_001/Makefile
#   NTRU+1152/experiments/avx2_official_opt_001/Makefile
# after lazy.mk, the base .mk files, keccak.mk and ht.mk (whose variables it reuses).
# Every variable and target of this file is prefixed IS_ / invshoup- so nothing of the
# included files changes.  Variants (KEM overlays of src/, generate_invshoup_kems.py):
#   NTRU+864 / 1152 (S = codec_direct / freeze2op):
#     candidate  src/kem_lazy_r2fold_invcrep_shoup_S_keccak_ht.c  current best + Inverse D + Shoup
#     control    src/kem_lazy_r2fold_invcrep_S_keccak_ht.c        invd_only
#     control    src/kem_lazy_r2fold_shoup_S_keccak_ht.c          shoup_only
#   NTRU+768 (the current best keeps the HT inverse):
#     src/kem_lazy_r2fold_shoup_freeze2op_keccak_ht_htinv.c        current best + Shoup (HT inverse kept)
#     src/kem_lazy_r2fold_invcrep_freeze2op_keccak_ht.c            current best with the fused inverse
#                                                                  (HT block pass + sigma/8-op/crep5)
#     src/kem_lazy_r2fold_invcrep_shoup_freeze2op_keccak_ht.c      both
# Phase A + same-ELF diagnostic + flat export checks; no host-control rule, no SUPERCOP campaign.

ifeq ($(filter $(PARAM),768 864 1152),)
$(error invshoup.mk: PARAM must be 768, 864 or 1152)
endif

IS_COMMON := ../../../common/official_opt_invshoup
IS_TOOLS := $(IS_COMMON)/tools
IS_P := --param $(PARAM)
IS_INV := ntruplus$(PARAM)_officialopt_invntt_crep
IS_INV_ASM := asm/$(IS_INV).s
IS_SHOUP := ntruplus$(PARAM)_officialopt_basemul_shoup
IS_SHOUP_ASM := asm/$(IS_SHOUP).s
IS_STEM := $(if $(filter 864,$(PARAM)),codec_direct,freeze2op)
IS_ASM_ALL = $(HT_ASM_ALL) $(IS_INV_ASM) $(IS_SHOUP_ASM)
ifeq ($(PARAM),768)
IS_CAND := kem_lazy_r2fold_shoup_$(IS_STEM)_keccak_ht_htinv
IS_VARIANTS := $(IS_CAND) kem_lazy_r2fold_invcrep_$(IS_STEM)_keccak_ht kem_lazy_r2fold_invcrep_shoup_$(IS_STEM)_keccak_ht
else
IS_CAND := kem_lazy_r2fold_invcrep_shoup_$(IS_STEM)_keccak_ht
IS_VARIANTS := $(IS_CAND) kem_lazy_r2fold_invcrep_$(IS_STEM)_keccak_ht kem_lazy_r2fold_shoup_$(IS_STEM)_keccak_ht
endif
IS_HDR := $(BUILD)/invshoup_hdr
IS_PROOF := $(BUILD)/invshoup_proof
IS_BASEINV_WRAP := -Wl,--wrap=$(R2INV) -DCANDIDATE_BASEINV=$(R2INV)

.PHONY: generate-invshoup check-invshoup-generate invshoup-prove invshoup-check invshoup-sanitize \
	invshoup-audit invshoup-mutate invshoup-phase-a invshoup-record

generate-invshoup:
	$(PYTHON) $(IS_TOOLS)/generate_invntt_crep.py $(IS_P) --experiment .
	$(PYTHON) $(IS_TOOLS)/generate_basemul_shoup.py $(IS_P) --experiment .
	$(PYTHON) $(IS_TOOLS)/generate_invshoup_kems.py $(IS_P) --experiment .

# Every existing generator stays --check clean underneath (check-ht-generate runs them all).
check-invshoup-generate: check-ht-generate | $(EVIDENCE)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(IS_TOOLS)/generate_invntt_crep.py $(IS_P) --experiment . --check \
		--meta $(EVIDENCE)/invcrep-generation.json
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(IS_TOOLS)/generate_basemul_shoup.py $(IS_P) --experiment . --check \
		--meta $(EVIDENCE)/shoup-generation.json
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(IS_TOOLS)/generate_invshoup_kems.py $(IS_P) --experiment . --check \
		--meta $(EVIDENCE)/invshoup-kems-generation.json

$(IS_HDR) $(IS_PROOF):
	mkdir -p $@

# The proofs also write the headers the C differentials read (proven Decap box, Shoup envelopes).
$(EVIDENCE)/invcrep-proof.json: $(IS_INV_ASM) | $(EVIDENCE) $(IS_PROOF)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(IS_TOOLS)/prove_invntt_crep.py $(IS_P) --experiment . \
		--build $(IS_PROOF)/inv --output $@
$(IS_HDR)/invcrep_box.h: $(IS_INV_ASM) | $(IS_HDR) $(IS_PROOF)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(IS_TOOLS)/prove_invntt_crep.py $(IS_P) --experiment . \
		--build $(IS_PROOF)/box --output $(IS_PROOF)/box.json --emit-box $@
$(IS_HDR)/shoup_env.h $(EVIDENCE)/shoup-proof.json &: $(IS_SHOUP_ASM) $(HT_ASM) | $(EVIDENCE) $(IS_HDR) $(IS_PROOF)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(IS_TOOLS)/prove_basemul_shoup.py $(IS_P) --experiment . \
		--build $(IS_PROOF)/shoup --output $(EVIDENCE)/shoup-proof.json --emit-env $(IS_HDR)/shoup_env.h

invshoup-prove: $(EVIDENCE)/invcrep-proof.json $(EVIDENCE)/shoup-proof.json

# $(1)=build dir, $(2)=flags
define is_units
$(1)/test_invntt_crep: $(IS_COMMON)/tests/test_invntt_crep.c $(COMMON)/tests/support/crypto_declassify.c \
		$(IS_INV_ASM) $(COMMON_C) $(COMMON_ASM) $(IS_HDR)/invcrep_box.h | $(1)
	$(CC) $(2) $(INCLUDES) -I$(IS_HDR) -o $$@ $$(filter-out %.h,$$^)
$(1)/test_basemul_shoup: $(IS_COMMON)/tests/test_basemul_shoup.c $(COMMON)/tests/support/crypto_declassify.c \
		$(HT_ASM) $(IS_SHOUP_ASM) $(COMMON_C) $(COMMON_ASM) $(IS_HDR)/shoup_env.h | $(1)
	$(CC) $(2) $(INCLUDES) -I$(IS_HDR) -o $$@ $$(filter-out %.h,$$^)
endef
$(eval $(call is_units,$(BUILD),$(CFLAGS)))
$(eval $(call is_units,$(BUILD_SAN),$(SANFLAGS)))

# test_kem_lazy.c drives whichever object is renamed to official_lazy_*.
define is_variant # $(1)=build dir, $(2)=flags, $(3)=kem overlay name
$(1)/$(3).o: src/$(3).c src/kem_lazy.c src/kem_lazy_r2fold.c $(wildcard src/kem_lazy_r2fold_*.c) | $(1)
	$(CC) $(2) $(KECCAK_INCLUDES) $(LAZY_RENAME) -c -o $$@ $$<
$(1)/test_$(3): $(COMMON)/tests/test_kem_lazy.c $(COMMON)/tests/support/crypto_declassify.c \
		$(IS_ASM_ALL) $(COMMON_C) $(COMMON_ASM) $(call KECCAK_OBJS,$(1)) $(1)/$(R2INV).o \
		$(1)/kem_ref.o $(1)/$(3).o $(1)/kat_aes.o $(1)/kat_rng.o | $(1)
	$(CC) $(2) -maes -I$(KAT) $(INCLUDES) $(KECCAK_WRAP) -o $$@ $$^
$(1)/test_$(3)_fretry: $(COMMON)/tests/test_kem_lazy.c $(COMMON)/tests/support/crypto_declassify.c \
		$(IS_ASM_ALL) $(COMMON_C) $(COMMON_ASM) $(call KECCAK_OBJS,$(1)) $(1)/$(R2INV).o \
		$(1)/kem_ref.o $(1)/$(3).o $(1)/kat_aes.o $(1)/kat_rng.o | $(1)
	$(CC) $(2) -maes -I$(KAT) $(INCLUDES) $(KECCAK_WRAP) $(FRETRY) $(IS_BASEINV_WRAP) -o $$@ $$^
endef
$(foreach v,$(IS_VARIANTS),$(eval $(call is_variant,$(BUILD),$(CFLAGS),$(v))))
$(foreach v,$(IS_VARIANTS),$(eval $(call is_variant,$(BUILD_SAN),$(SANFLAGS),$(v))))

IS_TESTS := test_invntt_crep test_basemul_shoup $(foreach v,$(IS_VARIANTS),test_$(v) test_$(v)_fretry)
is_run = $(foreach t,$(IS_TESTS),$(2) $(1)/$(t) &&) true

invshoup-check: check-upstream check-invshoup-generate $(addprefix $(BUILD)/,$(IS_TESTS))
	$(call is_run,$(BUILD),)

invshoup-sanitize: $(addprefix $(BUILD_SAN)/,$(IS_TESTS))
	$(call is_run,$(BUILD_SAN),$(SAN_ENV))

invshoup-audit: $(BUILD)/test_$(IS_CAND) $(foreach v,$(IS_VARIANTS),$(BUILD)/$(v).o) | $(EVIDENCE)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(IS_TOOLS)/audit_invshoup_linked.py $(IS_P) --experiment . \
		--elf $(BUILD)/test_$(IS_CAND) --output $(EVIDENCE)/invshoup-linked-summary.json

# Mutation check: one-line mutants of the generated asm must be rejected by the generator's
# symbolic proof and by the C differential.
IS_INV_CMD = $(CC) $(CFLAGS) $(INCLUDES) -I$(IS_HDR) -o {OUT} $(IS_COMMON)/tests/test_invntt_crep.c \
	$(COMMON)/tests/support/crypto_declassify.c {ASM} $(COMMON_C) $(COMMON_ASM)
IS_SHOUP_CMD = $(CC) $(CFLAGS) $(INCLUDES) -I$(IS_HDR) -o {OUT} $(IS_COMMON)/tests/test_basemul_shoup.c \
	$(COMMON)/tests/support/crypto_declassify.c $(HT_ASM) {ASM} $(COMMON_C) $(COMMON_ASM)
invshoup-mutate: $(IS_HDR)/invcrep_box.h $(IS_HDR)/shoup_env.h | $(EVIDENCE)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(IS_TOOLS)/mutate_invshoup.py $(IS_P) --experiment . \
		--inv-cmd "$(IS_INV_CMD)" --shoup-cmd "$(IS_SHOUP_CMD)" --output $(EVIDENCE)/invshoup-mutation-check.json

invshoup-phase-a: invshoup-check invshoup-sanitize invshoup-prove invshoup-audit invshoup-mutate

# Curated, deterministic-shape evidence into the tracked results dir.
invshoup-record: invshoup-phase-a
	mkdir -p results/invshoup-phase-a
	{ echo "== release ($(CFLAGS))" && $(call is_run,$(BUILD),) && \
	  echo "== sanitizer ($(SANFLAGS); $(SAN_ENV))" && $(call is_run,$(BUILD_SAN),$(SAN_ENV)); } \
		> $(EVIDENCE)/invshoup-closure-tests.log 2>&1
	cp $(EVIDENCE)/invshoup-closure-tests.log results/invshoup-phase-a/closure-tests.log
	cp $(EVIDENCE)/invcrep-generation.json $(EVIDENCE)/shoup-generation.json \
		$(EVIDENCE)/invshoup-kems-generation.json $(EVIDENCE)/invcrep-proof.json $(EVIDENCE)/shoup-proof.json \
		$(EVIDENCE)/invshoup-linked-summary.json $(EVIDENCE)/invshoup-mutation-check.json results/invshoup-phase-a/

# ------------------------------------------------ same-ELF component/caller diagnostic
# bench/bench_invshoup_diag.c: regions inverse (current best vs fused), Encap BaseMul and second
# Decap BaseMul (Official vs Shoup), keypair (seed-matched) / encap / decap for
#   v0 Official, v1 base (the current best, src/$(HT_CAND).c), v2..v4 = IS_VARIANTS in order
#   (864/1152: candidate, invd_only, shoup_only; 768: shoup, invcrep_only, invcrep+shoup).
# Common O3GC recipe; the _swapped ELF links every object and asm file in reverse order.
# supercop-derived, not Native.
IS_B := $(BUILD)/isbench
$(IS_B):
	mkdir -p $@
$(eval $(call keccak_objs,$(IS_B),$(BENCH_CFLAGS),,))
define is_bench_obj # $(1)=vN $(2)=source $(3)=includes
$(IS_B)/kem_$(1).o: $(COMMON)/bench/kem_diag.c $(2) src/kem_lazy.c src/kem_lazy_r2fold.c $(wildcard src/kem_lazy_r2fold_*.c) | $(IS_B)
	$(CC) $(BENCH_CFLAGS) -I. $(3) $(call KB_RENAME,$(1)) '-DKEM_SOURCE="$(2)"' \
		-DDERAND_NAME=$(1)_enc_derand -c -o $$@ $$<
endef
$(eval $(call is_bench_obj,v0,$(OFFICIAL)/kem.c,$(INCLUDES)))
$(eval $(call is_bench_obj,v1,src/$(HT_CAND).c,$(KECCAK_INCLUDES)))
$(eval $(call is_bench_obj,v2,src/$(word 1,$(IS_VARIANTS)).c,$(KECCAK_INCLUDES)))
$(eval $(call is_bench_obj,v3,src/$(word 2,$(IS_VARIANTS)).c,$(KECCAK_INCLUDES)))
$(eval $(call is_bench_obj,v4,src/$(word 3,$(IS_VARIANTS)).c,$(KECCAK_INCLUDES)))
$(IS_B)/$(R2INV).o: $(R2INV_C) | $(IS_B)
	$(CC) $(BENCH_CFLAGS) $(INCLUDES) -c -o $@ $<
IS_B_OBJS := $(IS_B)/kem_v0.o $(IS_B)/kem_v1.o $(IS_B)/kem_v2.o $(IS_B)/kem_v3.o $(IS_B)/kem_v4.o \
	$(IS_B)/mlk_fips202.o $(IS_B)/mlk_keccakf1600.o $(IS_B)/symmetric_keccak.o $(IS_B)/$(R2INV).o
IS_B_SRC := $(IS_COMMON)/bench/bench_invshoup_diag.c $(COMMON)/tests/support/crypto_declassify.c
$(BUILD)/bench_invshoup_diag: $(IS_B_SRC) $(IS_B_OBJS) $(IS_ASM_ALL) $(COMMON_C) $(COMMON_ASM) \
		$(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -maes $(INCLUDES) -I$(KAT) -I$(CPU_INCLUDE) -o $@ $^ $(CPU_LIB)
$(BUILD)/bench_invshoup_diag_swapped: $(IS_B_SRC) $(IS_B_OBJS) $(IS_ASM_ALL) $(COMMON_C) $(COMMON_ASM) \
		$(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -maes $(INCLUDES) -I$(KAT) -I$(CPU_INCLUDE) -o $@ \
		$(IS_B_SRC) $(call reverse,$(IS_B_OBJS)) $(call reverse,$(COMMON_ASM)) $(call reverse,$(COMMON_C)) \
		$(call reverse,$(IS_ASM_ALL)) $(BUILD)/kat_rng.o $(BUILD)/kat_aes.o $(CPU_LIB)

.PHONY: invshoup-bench
invshoup-bench: $(BUILD)/bench_invshoup_diag $(BUILD)/bench_invshoup_diag_swapped

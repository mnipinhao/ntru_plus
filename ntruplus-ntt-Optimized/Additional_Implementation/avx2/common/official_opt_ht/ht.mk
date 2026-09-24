# Shared rules for the NTRU+768 / 864 / 1152 HT Forward + keygen R^2-fold candidates,
# stacked on each parameter's mlkem-native Keccak candidate.  Included last by
#   NTRU+768/experiments/avx2_official_opt_freeze_001/Makefile
#   NTRU+864/experiments/avx2_official_opt_001/Makefile
#   NTRU+1152/experiments/avx2_official_opt_001/Makefile
# after lazy.mk, the base candidate's .mk and keccak.mk (whose variables it reuses).
# NTRU+768 (base avx2-officialopt-lazy-freeze-keccak-768-exp001):
#   candidate  src/kem_lazy_r2fold_freeze2op_keccak_ht_htinv.c  avx2-officialopt-lazy-freeze-keccak-ht-768-exp001
#                                                             (base + HT Forward + R^2 fold + HT inverse)
#   control    src/kem_lazy_freeze2op_keccak_ht.c         ht_only     (base + HT Forward)
#   control    src/kem_lazy_r2fold_freeze2op_keccak.c     r2fold_only (base + keygen R^2 fold)
#   control    src/kem_lazy_freeze2op_keccak_htinv.c      htinv_only  (base + HT inverse)
#   control    src/kem_lazy_r2fold_freeze2op_keccak_ht.c  ht_r2fold   (base + HT Forward + R^2 fold)
# NTRU+864 / 1152 (no HT inverse; S = codec_direct / freeze2op, base src/kem_lazy_S_keccak.c):
#   candidate  src/kem_lazy_r2fold_S_keccak_ht.c  avx2-officialopt-lazy-{codec,freeze}-keccak-ht-{864,1152}-exp001
#                                                 (base + HT Forward + R^2 fold)
#   control    src/kem_lazy_S_keccak_ht.c         ht_only     (base + HT Forward)
#   control    src/kem_lazy_r2fold_S_keccak.c     r2fold_only (base + keygen R^2 fold)
# Every generator gets --param N except for NTRU+768, whose commands are unchanged.
# Phase A + same-ELF diagnostic build only; no host-control rule, no SUPERCOP campaign.

empty :=
space := $(empty) $(empty)
ifeq ($(filter $(PARAM),768 864 1152),)
$(error ht.mk: PARAM must be 768, 864 or 1152)
endif

HCOMMON := ../../../common/official_opt_ht
HT := ntruplus$(PARAM)_officialopt_ntt_ht
HT_ASM := asm/$(HT).s
NOR2 := ntruplus$(PARAM)_officialopt_basemul_nor2
NOR2_ASM := asm/$(NOR2).s
R2INV := ntruplus$(PARAM)_officialopt_baseinv_r2fold
R2INV_C := src/$(R2INV).c
ifeq ($(PARAM),768)
HT_P :=
HTINV := ntruplus768_officialopt_invntt_ht
HTINV_ASM := asm/$(HTINV).s
HT_ASM_ALL := $(LAZY_ASM) $(FREEZE_ASM) $(HT_ASM) $(NOR2_ASM) $(HTINV_ASM)
HT_KG_ASM = $(LAZY_ASM) $(FREEZE_ASM) $(HT_ASM) $(HTINV_ASM)
HT_CAND := kem_lazy_r2fold_freeze2op_keccak_ht_htinv
HT_ONLY := kem_lazy_freeze2op_keccak_ht
HT_R2ONLY := kem_lazy_r2fold_freeze2op_keccak
HT_VARIANTS := $(HT_CAND) kem_lazy_freeze2op_keccak_ht kem_lazy_r2fold_freeze2op_keccak \
	kem_lazy_freeze2op_keccak_htinv kem_lazy_r2fold_freeze2op_keccak_ht
HT_CAND_CHAIN := src/$(HT_CAND).c src/kem_lazy_r2fold_freeze2op_keccak_ht.c src/kem_lazy_r2fold_freeze2op_keccak.c
else
HT_P := $(space)--param $(PARAM)
HT_STEM := $(if $(filter 864,$(PARAM)),codec_direct,freeze2op)
HT_ASM_ALL := $(KECCAK_BASE_ASM) $(HT_ASM) $(NOR2_ASM)
HT_KG_ASM = $(KECCAK_BASE_ASM) $(HT_ASM)
HT_CAND := kem_lazy_r2fold_$(HT_STEM)_keccak_ht
HT_ONLY := kem_lazy_$(HT_STEM)_keccak_ht
HT_R2ONLY := kem_lazy_r2fold_$(HT_STEM)_keccak
HT_VARIANTS := $(HT_CAND) $(HT_ONLY) $(HT_R2ONLY)
HT_CAND_CHAIN := src/$(HT_CAND).c src/$(HT_R2ONLY).c
endif
HT_BASEINV_WRAP := -Wl,--wrap=$(R2INV) -DCANDIDATE_BASEINV=$(R2INV)
HT_GEN := $(HCOMMON)/tools

.PHONY: generate-ht check-ht-generate ht-check ht-sanitize ht-range-proof ht-r2fold-prove ht-audit \
	ht-mutate ht-phase-a ht-record ht-bench

generate-ht:
	$(PYTHON) $(HT_GEN)/generate_forward_ht.py$(HT_P) --experiment .
ifdef HTINV
	$(PYTHON) $(HT_GEN)/generate_inverse_ht.py --experiment .
endif
	$(PYTHON) $(HT_GEN)/generate_keygen_r2fold.py$(HT_P) --experiment .
	$(PYTHON) $(HT_GEN)/generate_ht_overlays.py$(HT_P) --experiment .

# Every existing generator stays --check clean underneath.
check-ht-generate: $(KECCAK_BASE_CHECKS) check-keccak-generate | $(EVIDENCE)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(HT_GEN)/generate_forward_ht.py$(HT_P) --experiment . --check \
		--meta $(EVIDENCE)/ht-forward-generation.json
ifdef HTINV
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(HT_GEN)/generate_inverse_ht.py --experiment . --check \
		--meta $(EVIDENCE)/ht-inverse-generation.json
endif
	$(PYTHON) $(HT_GEN)/generate_keygen_r2fold.py$(HT_P) --experiment . --check \
		--meta $(EVIDENCE)/r2fold-generation.json
	$(PYTHON) $(HT_GEN)/generate_ht_overlays.py$(HT_P) --experiment . --check

ht-range-proof: | $(EVIDENCE)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(HCOMMON)/range_proof_ht/prove_ht.py$(HT_P) --experiment . \
		--build $(BUILD)/range_proof_ht --output $(EVIDENCE)/ht-range-proof-summary.json

ht-r2fold-prove: | $(EVIDENCE)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(HT_GEN)/prove_keygen_r2fold.py$(HT_P) --experiment . \
		--output $(EVIDENCE)/r2fold-proof.json

# $(1)=build dir, $(2)=flags
define ht_objs
$(1)/$(R2INV).o: $(R2INV_C) | $(1)
	$(CC) $(2) $(INCLUDES) -c -o $$@ $$<
$(1)/test_forward_ht: $(HCOMMON)/tests/test_forward_ht.c $(COMMON)/tests/support/crypto_declassify.c \
		$(LAZY_ASM) $(HT_ASM) $(COMMON_C) $(COMMON_ASM) | $(1)
	$(CC) $(2) $(INCLUDES) -DHT_NTT=$(HT) -DLAZY_NTT=$(LAZY) -o $$@ $$^
$(if $(HTINV),$(1)/test_invntt_ht: $(HCOMMON)/tests/test_invntt_ht.c $(COMMON)/tests/support/crypto_declassify.c \
		$(LAZY_ASM) $(HTINV_ASM) $(COMMON_C) $(COMMON_ASM) | $(1)
	$(CC) $(2) $(INCLUDES) -o $$@ $$^)
$(1)/htkg_v0.o: $(OFFICIAL)/kem.c | $(1)
	$(CC) $(2) $(INCLUDES) $(call KB_RENAME,v0) -c -o $$@ $$<
$(1)/htkg_v1.o: src/kem_lazy_r2fold.c | $(1)
	$(CC) $(2) $(INCLUDES) $(call KB_RENAME,v1) -c -o $$@ $$<
$(1)/htkg_v2.o: src/$(HT_R2ONLY).c src/kem_lazy_r2fold.c | $(1)
	$(CC) $(2) $(KECCAK_INCLUDES) $(call KB_RENAME,v2) -c -o $$@ $$<
$(1)/htkg_v3.o: $(HT_CAND_CHAIN) \
		src/kem_lazy_r2fold.c | $(1)
	$(CC) $(2) $(KECCAK_INCLUDES) $(call KB_RENAME,v3) -c -o $$@ $$<
$(1)/test_keygen_r2fold: $(HCOMMON)/tests/test_keygen_r2fold.c $(COMMON)/tests/support/crypto_declassify.c \
		$(HT_ASM_ALL) $(COMMON_C) $(COMMON_ASM) $(call KECCAK_OBJS,$(1)) $(1)/$(R2INV).o \
		$(1)/htkg_v0.o $(1)/htkg_v1.o $(1)/htkg_v2.o $(1)/htkg_v3.o $(1)/kat_aes.o $(1)/kat_rng.o | $(1)
	$(CC) $(2) -maes $(INCLUDES) -I$(KAT) -DFWD_NTT=$(LAZY) -Wl,--wrap=poly_baseinv -Wl,--wrap=$(R2INV) \
		-Wl,--wrap=fips202avx_shake256 -Wl,--wrap=$(CAND_SHAKE) -Wl,--wrap=randombytes -o $$@ $$^
endef
$(eval $(call ht_objs,$(BUILD),$(CFLAGS)))
$(eval $(call ht_objs,$(BUILD_SAN),$(SANFLAGS)))

# test_kem_lazy.c drives whichever object is renamed to official_lazy_*.
define ht_variant # $(1)=build dir, $(2)=flags, $(3)=kem overlay name
$(1)/$(3).o: src/$(3).c src/kem_lazy.c src/kem_lazy_r2fold.c | $(1)
	$(CC) $(2) $(KECCAK_INCLUDES) $(LAZY_RENAME) -c -o $$@ $$<
$(1)/test_$(3): $(COMMON)/tests/test_kem_lazy.c $(COMMON)/tests/support/crypto_declassify.c \
		$(HT_ASM_ALL) $(COMMON_C) $(COMMON_ASM) $(call KECCAK_OBJS,$(1)) $(1)/$(R2INV).o \
		$(1)/kem_ref.o $(1)/$(3).o $(1)/kat_aes.o $(1)/kat_rng.o | $(1)
	$(CC) $(2) -maes -I$(KAT) $(INCLUDES) $(KECCAK_WRAP) -o $$@ $$^
$(1)/test_$(3)_fretry: $(COMMON)/tests/test_kem_lazy.c $(COMMON)/tests/support/crypto_declassify.c \
		$(HT_ASM_ALL) $(COMMON_C) $(COMMON_ASM) $(call KECCAK_OBJS,$(1)) $(1)/$(R2INV).o \
		$(1)/kem_ref.o $(1)/$(3).o $(1)/kat_aes.o $(1)/kat_rng.o | $(1)
	$(CC) $(2) -maes -I$(KAT) $(INCLUDES) $(KECCAK_WRAP) $(FRETRY) $(HT_BASEINV_WRAP) -o $$@ $$^
endef
$(foreach v,$(HT_VARIANTS),$(eval $(call ht_variant,$(BUILD),$(CFLAGS),$(v))))
$(foreach v,$(HT_VARIANTS),$(eval $(call ht_variant,$(BUILD_SAN),$(SANFLAGS),$(v))))

HT_TESTS := test_forward_ht $(if $(HTINV),test_invntt_ht) test_keygen_r2fold \
	$(foreach v,$(HT_VARIANTS),test_$(v) test_$(v)_fretry)
ht_run = $(foreach t,$(HT_TESTS),$(2) $(1)/$(t) &&) true

ht-check: check-upstream check-ht-generate $(addprefix $(BUILD)/,$(HT_TESTS))
	$(call ht_run,$(BUILD),)

ht-sanitize: $(addprefix $(BUILD_SAN)/,$(HT_TESTS))
	$(call ht_run,$(BUILD_SAN),$(SAN_ENV))

ht-audit: $(BUILD)/test_$(HT_CAND) $(foreach v,$(HT_VARIANTS),$(BUILD)/$(v).o) | $(EVIDENCE)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(HT_GEN)/audit_ht_linked.py$(HT_P) --experiment . \
		--elf $(BUILD)/test_$(HT_CAND) --output $(EVIDENCE)/ht-linked-summary.json

# Mutation check: one-line mutants of the generated files must be rejected.
HT_KG_WRAPS := -Wl,--wrap=poly_baseinv -Wl,--wrap=$(R2INV) -Wl,--wrap=fips202avx_shake256 \
	-Wl,--wrap=$(CAND_SHAKE) -Wl,--wrap=randombytes
HT_FWD_CMD = $(CC) $(CFLAGS) $(INCLUDES) -DHT_NTT=$(HT) -DLAZY_NTT=$(LAZY) -o {OUT} \
	$(HCOMMON)/tests/test_forward_ht.c $(COMMON)/tests/support/crypto_declassify.c $(LAZY_ASM) {HT} \
	$(COMMON_C) $(COMMON_ASM)
HT_KG_CMD = $(CC) $(CFLAGS) -maes $(INCLUDES) -I$(KAT) -DFWD_NTT=$(LAZY) $(HT_KG_WRAPS) -o {OUT} \
	$(HCOMMON)/tests/test_keygen_r2fold.c $(COMMON)/tests/support/crypto_declassify.c \
	$(HT_KG_ASM) {NOR2} $(COMMON_C) $(COMMON_ASM) $(call KECCAK_OBJS,$(BUILD)) {R2INV} \
	$(BUILD)/htkg_v0.o $(BUILD)/htkg_v1.o $(BUILD)/htkg_v2.o $(BUILD)/htkg_v3.o $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o
HT_INV_CMD = $(CC) $(CFLAGS) $(INCLUDES) -o {OUT} $(HCOMMON)/tests/test_invntt_ht.c \
	$(COMMON)/tests/support/crypto_declassify.c $(LAZY_ASM) {HTINV} $(COMMON_C) $(COMMON_ASM)
ht-mutate: $(BUILD)/test_keygen_r2fold | $(EVIDENCE)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(HT_GEN)/mutate_ht.py$(HT_P) --experiment . --fwd-cmd "$(HT_FWD_CMD)" \
		--kg-cmd "$(HT_KG_CMD)"$(if $(HTINV), --inv-cmd "$(HT_INV_CMD)") --output $(EVIDENCE)/ht-mutation-check.json

ht-phase-a: ht-check ht-sanitize ht-range-proof ht-r2fold-prove ht-audit ht-mutate

# Curated, deterministic-shape evidence into the tracked results dir.
ht-record: ht-phase-a
	mkdir -p results/ht-phase-a
	{ echo "== release ($(CFLAGS))" && $(call ht_run,$(BUILD),) && \
	  echo "== sanitizer ($(SANFLAGS); $(SAN_ENV))" && $(call ht_run,$(BUILD_SAN),$(SAN_ENV)); } \
		> $(EVIDENCE)/ht-closure-tests.log 2>&1
	cp $(EVIDENCE)/ht-closure-tests.log results/ht-phase-a/closure-tests.log
	cp $(EVIDENCE)/ht-forward-generation.json $(if $(HTINV),$(EVIDENCE)/ht-inverse-generation.json )$(EVIDENCE)/r2fold-generation.json \
		$(EVIDENCE)/ht-range-proof-summary.json $(EVIDENCE)/r2fold-proof.json \
		$(EVIDENCE)/ht-linked-summary.json $(EVIDENCE)/ht-mutation-check.json results/ht-phase-a/

# ------------------------------------------------ same-ELF component/caller diagnostic
# KEM variants: v0 Official, v1 base (lazy+freeze+keccak), v2 candidate, v3 ht_only,
# v4 r2fold_only, v5 htinv_only, v6 ht_r2fold; components: lazy vs HT Forward,
# Official BaseMul vs no-R^2 core, Official vs fold BaseInv, Official vs HT inverse.  Common O3GC recipe; the _swapped ELF links
# every object and asm file in reverse order.  supercop-derived, not Native.
# NTRU+864 / 1152: v0 Official, v1 base (the Keccak candidate), v2 candidate, v3 ht_only, v4 r2fold_only;
# no inverse region (bench_ht_diag.c without HT_INV).
HB := $(BUILD)/htbench
$(HB):
	mkdir -p $@
$(eval $(call keccak_objs,$(HB),$(BENCH_CFLAGS),,))
define htbench_obj # $(1)=vN $(2)=source $(3)=includes
$(HB)/kem_$(1).o: $(COMMON)/bench/kem_diag.c $(2) src/kem_lazy.c src/kem_lazy_r2fold.c | $(HB)
	$(CC) $(BENCH_CFLAGS) -I. $(3) $(call KB_RENAME,$(1)) '-DKEM_SOURCE="$(2)"' \
		-DDERAND_NAME=$(1)_enc_derand -c -o $$@ $$<
endef
$(eval $(call htbench_obj,v0,$(OFFICIAL)/kem.c,$(INCLUDES)))
$(eval $(call htbench_obj,v1,src/$(KECCAK_CAND).c,$(KECCAK_INCLUDES)))
$(eval $(call htbench_obj,v2,src/$(HT_CAND).c,$(KECCAK_INCLUDES)))
$(eval $(call htbench_obj,v3,src/$(HT_ONLY).c,$(KECCAK_INCLUDES)))
$(eval $(call htbench_obj,v4,src/$(HT_R2ONLY).c,$(KECCAK_INCLUDES)))
ifdef HTINV
$(eval $(call htbench_obj,v5,src/kem_lazy_freeze2op_keccak_htinv.c,$(KECCAK_INCLUDES)))
$(eval $(call htbench_obj,v6,src/kem_lazy_r2fold_freeze2op_keccak_ht.c,$(KECCAK_INCLUDES)))
endif
$(HB)/$(R2INV).o: $(R2INV_C) | $(HB)
	$(CC) $(BENCH_CFLAGS) $(INCLUDES) -c -o $@ $<
HB_OBJS := $(HB)/kem_v0.o $(HB)/kem_v1.o $(HB)/kem_v2.o $(HB)/kem_v3.o $(HB)/kem_v4.o \
	$(if $(HTINV),$(HB)/kem_v5.o $(HB)/kem_v6.o )$(HB)/mlk_fips202.o $(HB)/mlk_keccakf1600.o $(HB)/symmetric_keccak.o \
	$(HB)/$(R2INV).o
HB_SRC := $(HCOMMON)/bench/bench_ht_diag.c $(COMMON)/tests/support/crypto_declassify.c
$(BUILD)/bench_ht_diag: $(HB_SRC) $(HB_OBJS) $(HT_ASM_ALL) $(COMMON_C) $(COMMON_ASM) \
		$(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -maes $(INCLUDES) -I$(KAT) -I$(CPU_INCLUDE) -o $@ $^ $(CPU_LIB)
$(BUILD)/bench_ht_diag_swapped: $(HB_SRC) $(HB_OBJS) $(HT_ASM_ALL) $(COMMON_C) $(COMMON_ASM) \
		$(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -maes $(INCLUDES) -I$(KAT) -I$(CPU_INCLUDE) -o $@ \
		$(HB_SRC) $(call reverse,$(HB_OBJS)) $(call reverse,$(COMMON_ASM)) $(call reverse,$(COMMON_C)) \
		$(call reverse,$(HT_ASM_ALL)) $(BUILD)/kat_rng.o $(BUILD)/kat_aes.o $(CPU_LIB)

ht-bench: $(BUILD)/bench_ht_diag $(BUILD)/bench_ht_diag_swapped

# ------------------------------------------------ Phase B: SUPERCOP-flat qualification export
# avx2-officialopt-lazy-freeze-keccak-ht-qual001 = the Keccak base export + ntt_ht.s, invntt_ht.s,
# basemul_nor2.s, baseinv_r2fold.c (exact Phase-A bytes) + a kem.c rebinding what the Phase-A
# overlay chain rebinds (tools/export_ht_flat.py).  ht-qualification refuses to overwrite;
# ht-qualification-check regenerates in a temp dir and requires identity.
# NTRU+864: avx2-officialopt-lazy-codec-keccak-ht-qual001, NTRU+1152:
# avx2-officialopt-lazy-freeze-keccak-ht-qual001 (tools/export_ht_flat_param.py; no invntt_ht.s).
ifeq ($(PARAM),768)
HT_QUAL_NAME := avx2-officialopt-lazy-freeze-keccak-ht-qual001
HT_EXPORT := $(HT_GEN)/export_ht_flat.py
else
HT_QUAL_NAME := avx2-officialopt-lazy-$(if $(filter 864,$(PARAM)),codec,freeze)-keccak-ht-qual001
HT_EXPORT := $(HT_GEN)/export_ht_flat_param.py
endif
HT_QUAL := qualification/$(HT_QUAL_NAME)
ht-qualification:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(HT_EXPORT)$(HT_P) --experiment . --qualification-root qualification
ht-qualification-check:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(HT_EXPORT)$(HT_P) --experiment . --qualification-root qualification --check

# Flat-tree KEM test: every file of the export compiled from the export directory (its own
# fips202.h = mlkem-native adapter, Official hash_f/g/h names), kem.c renamed to official_lazy_*,
# against the pinned Official kem.c (official_ref_*; its symmetric.c hash_f/g/h renamed
# official_ref_hash_* so both copies link).  Byte-identical shared files (poly.c, consts.c, the
# Official .s) are linked once, from the export.  Same shared test_kem_lazy.c and wraps as Phase A.
HT_FLAT_INCLUDES := -I$(COMMON)/tests/support -I$(HT_QUAL) -I$(SUPERCOP_PRISTINE)/cryptoint \
	-I$(SUPERCOP_PRISTINE)/include
HT_FLAT_C := $(filter-out kem.c symmetric.c,$(notdir $(wildcard $(HT_QUAL)/*.c)))
HT_FLAT_S := $(addprefix $(HT_QUAL)/,$(notdir $(wildcard $(HT_QUAL)/*.s)))
REF_HASH_RENAME := -Dhash_f=official_ref_hash_f -Dhash_g=official_ref_hash_g -Dhash_h=official_ref_hash_h
define ht_flat # $(1)=build dir, $(2)=flags
$(1)/htflat:
	mkdir -p $$@
$(1)/htflat/%.o: $(HT_QUAL)/%.c | $(1)/htflat
	$(CC) $(2) $(HT_FLAT_INCLUDES) -c -o $$@ $$<
$(1)/htflat/kem.o: $(HT_QUAL)/kem.c | $(1)/htflat
	$(CC) $(2) $(HT_FLAT_INCLUDES) $(LAZY_RENAME) -c -o $$@ $$<
$(1)/htflat/ref_kem.o: $(OFFICIAL)/kem.c | $(1)/htflat
	$(CC) $(2) $(INCLUDES) $(REF_RENAME) $(REF_HASH_RENAME) -c -o $$@ $$<
$(1)/htflat/ref_symmetric.o: $(OFFICIAL)/symmetric.c | $(1)/htflat
	$(CC) $(2) $(INCLUDES) $(REF_HASH_RENAME) -c -o $$@ $$<
$(1)/htflat/ref_fips202.o: $(OFFICIAL)/fips202.c | $(1)/htflat
	$(CC) $(2) $(INCLUDES) -c -o $$@ $$<
HT_FLAT_OBJS_$(1) := $(addprefix $(1)/htflat/,$(HT_FLAT_C:.c=.o) symmetric.o kem.o ref_kem.o ref_symmetric.o ref_fips202.o)
$(1)/test_ht_flat: $(COMMON)/tests/test_kem_lazy.c $(COMMON)/tests/support/crypto_declassify.c \
		$(OFFICIAL)/KeccakP-1600-AVX2.s $(HT_FLAT_S) $$(HT_FLAT_OBJS_$(1)) $(1)/kat_aes.o $(1)/kat_rng.o | $(1)
	$(CC) $(2) -maes -I$(KAT) $(INCLUDES) $(KECCAK_WRAP) -o $$@ $$^
$(1)/test_ht_flat_fretry: $(COMMON)/tests/test_kem_lazy.c $(COMMON)/tests/support/crypto_declassify.c \
		$(OFFICIAL)/KeccakP-1600-AVX2.s $(HT_FLAT_S) $$(HT_FLAT_OBJS_$(1)) $(1)/kat_aes.o $(1)/kat_rng.o | $(1)
	$(CC) $(2) -maes -I$(KAT) $(INCLUDES) $(KECCAK_WRAP) $(FRETRY) $(HT_BASEINV_WRAP) -o $$@ $$^
endef
$(eval $(call ht_flat,$(BUILD),$(CFLAGS)))
$(eval $(call ht_flat,$(BUILD_SAN),$(SANFLAGS)))

.PHONY: ht-qualification ht-qualification-check ht-flat-check ht-flat-audit ht-flat ht-flat-record
ht-flat-check: ht-qualification-check $(BUILD)/test_ht_flat $(BUILD)/test_ht_flat_fretry \
		$(BUILD_SAN)/test_ht_flat $(BUILD_SAN)/test_ht_flat_fretry | $(EVIDENCE)
	{ echo "== release ($(CFLAGS))" && $(BUILD)/test_ht_flat && $(BUILD)/test_ht_flat_fretry && \
	  echo "== sanitizer ($(SANFLAGS); $(SAN_ENV))" && $(SAN_ENV) $(BUILD_SAN)/test_ht_flat && \
	  $(SAN_ENV) $(BUILD_SAN)/test_ht_flat_fretry; } > $(EVIDENCE)/ht-flat-tests.log 2>&1 || \
		{ cat $(EVIDENCE)/ht-flat-tests.log; false; }
	cat $(EVIDENCE)/ht-flat-tests.log

# Linked audit of the flat ELF + object identity with the Phase-A build (make ht-phase-a first).
ht-flat-audit: $(BUILD)/test_ht_flat $(BUILD)/test_$(HT_CAND) | $(EVIDENCE)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(HT_GEN)/audit_ht_linked.py$(HT_P) --experiment . \
		--elf $(BUILD)/test_ht_flat --flat-root $(HT_QUAL) --flat-kem-obj $(BUILD)/htflat/kem.o \
		--phase-a-obj $(BUILD)/htflat/kem.o=$(BUILD)/$(HT_CAND).o \
		--phase-a-obj $(BUILD)/htflat/baseinv_r2fold.o=$(BUILD)/$(R2INV).o \
		--phase-a-obj $(BUILD)/htflat/symmetric.o=$(BUILD)/symmetric_keccak.o \
		--phase-a-obj $(BUILD)/htflat/mlk_fips202.o=$(BUILD)/mlk_fips202.o \
		--phase-a-obj $(BUILD)/htflat/mlk_keccakf1600.o=$(BUILD)/mlk_keccakf1600.o \
		--output $(EVIDENCE)/ht-flat-linked-summary.json

ht-flat: ht-flat-check ht-flat-audit

# Curated Phase-B flat-export evidence into the tracked results dir.
ht-flat-record: ht-flat
	mkdir -p results/ht-phase-b
	cp $(EVIDENCE)/ht-flat-tests.log results/ht-phase-b/closure-tests.log
	cp $(EVIDENCE)/ht-flat-linked-summary.json results/ht-phase-b/flat-linked-summary.json

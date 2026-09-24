# Shared rules for the NTRU+768 HT Forward + keygen R^2-fold candidates, stacked
# on avx2-officialopt-lazy-freeze-keccak-768-exp001.  Included last by
#   NTRU+768/experiments/avx2_official_opt_freeze_001/Makefile
# after lazy.mk, freeze2op.mk and keccak.mk (whose variables it reuses).
#   candidate  src/kem_lazy_r2fold_freeze2op_keccak_ht_htinv.c  avx2-officialopt-lazy-freeze-keccak-ht-768-exp001
#                                                             (base + HT Forward + R^2 fold + HT inverse)
#   control    src/kem_lazy_freeze2op_keccak_ht.c         ht_only     (base + HT Forward)
#   control    src/kem_lazy_r2fold_freeze2op_keccak.c     r2fold_only (base + keygen R^2 fold)
#   control    src/kem_lazy_freeze2op_keccak_htinv.c      htinv_only  (base + HT inverse)
#   control    src/kem_lazy_r2fold_freeze2op_keccak_ht.c  ht_r2fold   (base + HT Forward + R^2 fold)
# Phase A + same-ELF diagnostic build only; no host-control rule, no SUPERCOP campaign.

ifneq ($(PARAM),768)
$(error ht.mk: NTRU+768 only)
endif

HCOMMON := ../../../common/official_opt_ht
HT := ntruplus768_officialopt_ntt_ht
HT_ASM := asm/$(HT).s
NOR2 := ntruplus768_officialopt_basemul_nor2
NOR2_ASM := asm/$(NOR2).s
R2INV := ntruplus768_officialopt_baseinv_r2fold
R2INV_C := src/$(R2INV).c
HTINV := ntruplus768_officialopt_invntt_ht
HTINV_ASM := asm/$(HTINV).s
HT_ASM_ALL := $(LAZY_ASM) $(FREEZE_ASM) $(HT_ASM) $(NOR2_ASM) $(HTINV_ASM)
HT_CAND := kem_lazy_r2fold_freeze2op_keccak_ht_htinv
HT_VARIANTS := $(HT_CAND) kem_lazy_freeze2op_keccak_ht kem_lazy_r2fold_freeze2op_keccak \
	kem_lazy_freeze2op_keccak_htinv kem_lazy_r2fold_freeze2op_keccak_ht
HT_BASEINV_WRAP := -Wl,--wrap=$(R2INV) -DCANDIDATE_BASEINV=$(R2INV)
HT_GEN := $(HCOMMON)/tools

.PHONY: generate-ht check-ht-generate ht-check ht-sanitize ht-range-proof ht-r2fold-prove ht-audit \
	ht-mutate ht-phase-a ht-record ht-bench

generate-ht:
	$(PYTHON) $(HT_GEN)/generate_forward_ht.py --experiment .
	$(PYTHON) $(HT_GEN)/generate_inverse_ht.py --experiment .
	$(PYTHON) $(HT_GEN)/generate_keygen_r2fold.py --experiment .
	$(PYTHON) $(HT_GEN)/generate_ht_overlays.py --experiment .

# Every existing generator stays --check clean underneath.
check-ht-generate: check-generate check-freeze-generate check-keccak-generate | $(EVIDENCE)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(HT_GEN)/generate_forward_ht.py --experiment . --check \
		--meta $(EVIDENCE)/ht-forward-generation.json
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(HT_GEN)/generate_inverse_ht.py --experiment . --check \
		--meta $(EVIDENCE)/ht-inverse-generation.json
	$(PYTHON) $(HT_GEN)/generate_keygen_r2fold.py --experiment . --check \
		--meta $(EVIDENCE)/r2fold-generation.json
	$(PYTHON) $(HT_GEN)/generate_ht_overlays.py --experiment . --check

ht-range-proof: | $(EVIDENCE)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(HCOMMON)/range_proof_ht/prove_ht.py --experiment . \
		--build $(BUILD)/range_proof_ht --output $(EVIDENCE)/ht-range-proof-summary.json

ht-r2fold-prove: | $(EVIDENCE)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(HT_GEN)/prove_keygen_r2fold.py --experiment . \
		--output $(EVIDENCE)/r2fold-proof.json

# $(1)=build dir, $(2)=flags
define ht_objs
$(1)/$(R2INV).o: $(R2INV_C) | $(1)
	$(CC) $(2) $(INCLUDES) -c -o $$@ $$<
$(1)/test_forward_ht: $(HCOMMON)/tests/test_forward_ht.c $(COMMON)/tests/support/crypto_declassify.c \
		$(LAZY_ASM) $(HT_ASM) $(COMMON_C) $(COMMON_ASM) | $(1)
	$(CC) $(2) $(INCLUDES) -DHT_NTT=$(HT) -DLAZY_NTT=$(LAZY) -o $$@ $$^
$(1)/test_invntt_ht: $(HCOMMON)/tests/test_invntt_ht.c $(COMMON)/tests/support/crypto_declassify.c \
		$(LAZY_ASM) $(HTINV_ASM) $(COMMON_C) $(COMMON_ASM) | $(1)
	$(CC) $(2) $(INCLUDES) -o $$@ $$^
$(1)/htkg_v0.o: $(OFFICIAL)/kem.c | $(1)
	$(CC) $(2) $(INCLUDES) $(call KB_RENAME,v0) -c -o $$@ $$<
$(1)/htkg_v1.o: src/kem_lazy_r2fold.c | $(1)
	$(CC) $(2) $(INCLUDES) $(call KB_RENAME,v1) -c -o $$@ $$<
$(1)/htkg_v2.o: src/kem_lazy_r2fold_freeze2op_keccak.c src/kem_lazy_r2fold.c | $(1)
	$(CC) $(2) $(KECCAK_INCLUDES) $(call KB_RENAME,v2) -c -o $$@ $$<
$(1)/htkg_v3.o: src/$(HT_CAND).c src/kem_lazy_r2fold_freeze2op_keccak_ht.c src/kem_lazy_r2fold_freeze2op_keccak.c \
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

HT_TESTS := test_forward_ht test_invntt_ht test_keygen_r2fold $(foreach v,$(HT_VARIANTS),test_$(v) test_$(v)_fretry)
ht_run = $(foreach t,$(HT_TESTS),$(2) $(1)/$(t) &&) true

ht-check: check-upstream check-ht-generate $(addprefix $(BUILD)/,$(HT_TESTS))
	$(call ht_run,$(BUILD),)

ht-sanitize: $(addprefix $(BUILD_SAN)/,$(HT_TESTS))
	$(call ht_run,$(BUILD_SAN),$(SAN_ENV))

ht-audit: $(BUILD)/test_$(HT_CAND) $(foreach v,$(HT_VARIANTS),$(BUILD)/$(v).o) | $(EVIDENCE)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(HT_GEN)/audit_ht_linked.py --experiment . \
		--elf $(BUILD)/test_$(HT_CAND) --output $(EVIDENCE)/ht-linked-summary.json

# Mutation check: one-line mutants of the generated files must be rejected.
HT_KG_WRAPS := -Wl,--wrap=poly_baseinv -Wl,--wrap=$(R2INV) -Wl,--wrap=fips202avx_shake256 \
	-Wl,--wrap=$(CAND_SHAKE) -Wl,--wrap=randombytes
HT_FWD_CMD = $(CC) $(CFLAGS) $(INCLUDES) -DHT_NTT=$(HT) -DLAZY_NTT=$(LAZY) -o {OUT} \
	$(HCOMMON)/tests/test_forward_ht.c $(COMMON)/tests/support/crypto_declassify.c $(LAZY_ASM) {HT} \
	$(COMMON_C) $(COMMON_ASM)
HT_KG_CMD = $(CC) $(CFLAGS) -maes $(INCLUDES) -I$(KAT) -DFWD_NTT=$(LAZY) $(HT_KG_WRAPS) -o {OUT} \
	$(HCOMMON)/tests/test_keygen_r2fold.c $(COMMON)/tests/support/crypto_declassify.c \
	$(LAZY_ASM) $(FREEZE_ASM) $(HT_ASM) $(HTINV_ASM) {NOR2} $(COMMON_C) $(COMMON_ASM) $(call KECCAK_OBJS,$(BUILD)) {R2INV} \
	$(BUILD)/htkg_v0.o $(BUILD)/htkg_v1.o $(BUILD)/htkg_v2.o $(BUILD)/htkg_v3.o $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o
HT_INV_CMD = $(CC) $(CFLAGS) $(INCLUDES) -o {OUT} $(HCOMMON)/tests/test_invntt_ht.c \
	$(COMMON)/tests/support/crypto_declassify.c $(LAZY_ASM) {HTINV} $(COMMON_C) $(COMMON_ASM)
ht-mutate: $(BUILD)/test_keygen_r2fold | $(EVIDENCE)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(HT_GEN)/mutate_ht.py --experiment . --fwd-cmd "$(HT_FWD_CMD)" \
		--kg-cmd "$(HT_KG_CMD)" --inv-cmd "$(HT_INV_CMD)" --output $(EVIDENCE)/ht-mutation-check.json

ht-phase-a: ht-check ht-sanitize ht-range-proof ht-r2fold-prove ht-audit ht-mutate

# Curated, deterministic-shape evidence into the tracked results dir.
ht-record: ht-phase-a
	mkdir -p results/ht-phase-a
	{ echo "== release ($(CFLAGS))" && $(call ht_run,$(BUILD),) && \
	  echo "== sanitizer ($(SANFLAGS); $(SAN_ENV))" && $(call ht_run,$(BUILD_SAN),$(SAN_ENV)); } \
		> $(EVIDENCE)/ht-closure-tests.log 2>&1
	cp $(EVIDENCE)/ht-closure-tests.log results/ht-phase-a/closure-tests.log
	cp $(EVIDENCE)/ht-forward-generation.json $(EVIDENCE)/ht-inverse-generation.json $(EVIDENCE)/r2fold-generation.json \
		$(EVIDENCE)/ht-range-proof-summary.json $(EVIDENCE)/r2fold-proof.json \
		$(EVIDENCE)/ht-linked-summary.json $(EVIDENCE)/ht-mutation-check.json results/ht-phase-a/

# ------------------------------------------------ same-ELF component/caller diagnostic
# KEM variants: v0 Official, v1 base (lazy+freeze+keccak), v2 candidate, v3 ht_only,
# v4 r2fold_only, v5 htinv_only, v6 ht_r2fold; components: lazy vs HT Forward,
# Official BaseMul vs no-R^2 core, Official vs fold BaseInv, Official vs HT inverse.  Common O3GC recipe; the _swapped ELF links
# every object and asm file in reverse order.  supercop-derived, not Native.
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
$(eval $(call htbench_obj,v1,src/kem_lazy_freeze2op_keccak.c,$(KECCAK_INCLUDES)))
$(eval $(call htbench_obj,v2,src/$(HT_CAND).c,$(KECCAK_INCLUDES)))
$(eval $(call htbench_obj,v3,src/kem_lazy_freeze2op_keccak_ht.c,$(KECCAK_INCLUDES)))
$(eval $(call htbench_obj,v4,src/kem_lazy_r2fold_freeze2op_keccak.c,$(KECCAK_INCLUDES)))
$(eval $(call htbench_obj,v5,src/kem_lazy_freeze2op_keccak_htinv.c,$(KECCAK_INCLUDES)))
$(eval $(call htbench_obj,v6,src/kem_lazy_r2fold_freeze2op_keccak_ht.c,$(KECCAK_INCLUDES)))
$(HB)/$(R2INV).o: $(R2INV_C) | $(HB)
	$(CC) $(BENCH_CFLAGS) $(INCLUDES) -c -o $@ $<
HB_OBJS := $(HB)/kem_v0.o $(HB)/kem_v1.o $(HB)/kem_v2.o $(HB)/kem_v3.o $(HB)/kem_v4.o $(HB)/kem_v5.o $(HB)/kem_v6.o \
	$(HB)/mlk_fips202.o $(HB)/mlk_keccakf1600.o $(HB)/symmetric_keccak.o $(HB)/$(R2INV).o
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

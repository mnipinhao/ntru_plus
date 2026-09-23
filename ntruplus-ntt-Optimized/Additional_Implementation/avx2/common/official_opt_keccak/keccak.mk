# Shared rules for the mlkem-native x1 Keccak candidates of Official NTRU+
# 768 / 864 / 1152 AVX2: every SHAKE256 call of the KEM (keypair genf/geng,
# hash_f/g/h) moves from the Official XKCP/CRYPTOGAMS KeccakP-1600-AVX2.s to
# the vendored mlkem-native x1 C Keccak (third_party/mlkem-native-fips202-b3ba7b32).
# Included last by
#   NTRU+768/experiments/avx2_official_opt_freeze_001/Makefile
#   NTRU+864/experiments/avx2_official_opt_001/Makefile
#   NTRU+1152/experiments/avx2_official_opt_001/Makefile
# after lazy.mk (whose variables it reuses) and the base candidate's .mk, with
#   KECCAK_BASE          base candidate KEM overlay (src/$(KECCAK_BASE).c)
#   KECCAK_BASE_ASM      asm the base candidate needs beyond COMMON_ASM
#   KECCAK_BASE_CHECKS   the base candidate's generator --check targets
# Variants (all SHAKE256 in the candidate path on mlkem-native):
#   candidate  src/$(KECCAK_BASE)_keccak.c = base candidate + mlkem-native Keccak
#   control    src/kem_keccak.c            = Official kem.c + mlkem-native Keccak
# Phase A + same-ELF diagnostic build only; no host-control rule, no SUPERCOP campaign.

ifndef KECCAK_BASE
$(error keccak.mk: set KECCAK_BASE, KECCAK_BASE_ASM and KECCAK_BASE_CHECKS first)
endif

KCOMMON := ../../../common/official_opt_keccak
MLK := $(REPO)/third_party/mlkem-native-fips202-b3ba7b32
MLK_SRC := $(MLK)/mlkem/src/fips202
KECCAK_GEN := $(KCOMMON)/tools/generate_keccak_overlays.py
KECCAK_VECTORS := $(KCOMMON)/tests/vectors/shake256_cavp_subset.txt
# Upstream NTRU+ headers first; the mlkem-native tree is reached only as
# "mlkem/src/..." so none of its headers (params.h, poly.h, ...) can shadow NTRU+ ones.
KECCAK_INCLUDES := $(INCLUDES) -I$(KCOMMON)/src -I$(KCOMMON)/config -I$(MLK)
MLK_INCLUDES := -I$(KCOMMON)/config
CAND_SHAKE := ntruplus_mlkfips202_shake256
KECCAK_WRAP := $(KEM_WRAP) -Wl,--wrap=$(CAND_SHAKE) -DCANDIDATE_SHAKE256=$(CAND_SHAKE)
KECCAK_CAND := $(KECCAK_BASE)_keccak

.PHONY: generate-keccak check-keccak-generate keccak-vectors-check keccak-check keccak-sanitize \
	keccak-audit keccak-ct keccak-mutate keccak-config-equivalence keccak-phase-a keccak-record keccak-bench keccak-flat

generate-keccak:
	$(PYTHON) $(KECCAK_GEN) --param $(PARAM) --experiment .

check-keccak-generate: | $(EVIDENCE)
	$(PYTHON) $(KECCAK_GEN) --param $(PARAM) --experiment . --check --meta $(EVIDENCE)/keccak-generation.json

# Needs the NIST CAVP zip (URL and sha256 in the tool): make keccak-vectors-check CAVP_ZIP=...
keccak-vectors-check:
	$(PYTHON) $(KCOMMON)/tools/extract_shake256_vectors.py --zip $(CAVP_ZIP) --check

# $(1)=build dir, $(2)=flags, $(3)=object suffix, $(4)=extra -D
define keccak_objs
$(1)/mlk_fips202$(3).o: $(MLK_SRC)/fips202.c | $(1)
	$(CC) $(2) $(MLK_INCLUDES) $(4) -c -o $$@ $$<
$(1)/mlk_keccakf1600$(3).o: $(MLK_SRC)/keccakf1600.c | $(1)
	$(CC) $(2) $(MLK_INCLUDES) $(4) -c -o $$@ $$<
$(1)/symmetric_keccak$(3).o: $(KCOMMON)/src/symmetric_keccak.c | $(1)
	$(CC) $(2) $(KECCAK_INCLUDES) $(4) -c -o $$@ $$<
endef
$(eval $(call keccak_objs,$(BUILD),$(CFLAGS),,))
$(eval $(call keccak_objs,$(BUILD_SAN),$(SANFLAGS),,))
KECCAK_OBJS = $(1)/mlk_fips202.o $(1)/mlk_keccakf1600.o $(1)/symmetric_keccak.o

# test_kem_lazy.c drives whichever object is renamed to official_lazy_*.
define keccak_variant # $(1)=build dir, $(2)=flags, $(3)=kem overlay name
$(1)/$(3).o: src/$(3).c src/kem_lazy.c | $(1)
	$(CC) $(2) $(KECCAK_INCLUDES) $(LAZY_RENAME) -c -o $$@ $$<
$(1)/test_$(3): $(COMMON)/tests/test_kem_lazy.c $(COMMON)/tests/support/crypto_declassify.c \
		$(KECCAK_BASE_ASM) $(COMMON_C) $(COMMON_ASM) $(call KECCAK_OBJS,$(1)) \
		$(1)/kem_ref.o $(1)/$(3).o $(1)/kat_aes.o $(1)/kat_rng.o | $(1)
	$(CC) $(2) -maes -I$(KAT) $(INCLUDES) $(KECCAK_WRAP) -o $$@ $$^
$(1)/test_$(3)_fretry: $(COMMON)/tests/test_kem_lazy.c $(COMMON)/tests/support/crypto_declassify.c \
		$(KECCAK_BASE_ASM) $(COMMON_C) $(COMMON_ASM) $(call KECCAK_OBJS,$(1)) \
		$(1)/kem_ref.o $(1)/$(3).o $(1)/kat_aes.o $(1)/kat_rng.o | $(1)
	$(CC) $(2) -maes -I$(KAT) $(INCLUDES) $(KECCAK_WRAP) $(FRETRY) -o $$@ $$^
endef
$(eval $(call keccak_variant,$(BUILD),$(CFLAGS),$(KECCAK_CAND)))
$(eval $(call keccak_variant,$(BUILD),$(CFLAGS),kem_keccak))
$(eval $(call keccak_variant,$(BUILD_SAN),$(SANFLAGS),$(KECCAK_CAND)))
$(eval $(call keccak_variant,$(BUILD_SAN),$(SANFLAGS),kem_keccak))

define keccak_shake_test # $(1)=build dir, $(2)=flags
$(1)/test_shake256_keccak: $(KCOMMON)/tests/test_shake256_keccak.c $(COMMON)/tests/support/crypto_declassify.c \
		$(COMMON_C) $(COMMON_ASM) $(call KECCAK_OBJS,$(1)) | $(1)
	$(CC) $(2) $(INCLUDES) -o $$@ $$^
endef
$(eval $(call keccak_shake_test,$(BUILD),$(CFLAGS)))
$(eval $(call keccak_shake_test,$(BUILD_SAN),$(SANFLAGS)))

KECCAK_TESTS := test_$(KECCAK_CAND) test_$(KECCAK_CAND)_fretry test_kem_keccak test_kem_keccak_fretry
keccak_run = $(1)/test_shake256_keccak $(KECCAK_VECTORS) && $(foreach t,$(KECCAK_TESTS),$(2) $(1)/$(t) &&) true

keccak-check: check-upstream $(KECCAK_BASE_CHECKS) check-keccak-generate \
		$(BUILD)/test_shake256_keccak $(addprefix $(BUILD)/,$(KECCAK_TESTS))
	$(call keccak_run,$(BUILD),)

keccak-sanitize: $(BUILD_SAN)/test_shake256_keccak $(addprefix $(BUILD_SAN)/,$(KECCAK_TESTS))
	$(SAN_ENV) $(call keccak_run,$(BUILD_SAN),$(SAN_ENV))

# Stack usage of the new hash path (same CFLAGS + -fstack-usage).
KSU := $(BUILD)/stack_usage
$(KSU):
	mkdir -p $@
$(eval $(call keccak_objs,$(KSU),$(CFLAGS) -fstack-usage,,))
$(KSU)/official_fips202.o: $(OFFICIAL)/fips202.c | $(KSU)
	$(CC) $(CFLAGS) -fstack-usage $(INCLUDES) -c -o $@ $<
$(KSU)/official_symmetric.o: $(OFFICIAL)/symmetric.c | $(KSU)
	$(CC) $(CFLAGS) -fstack-usage $(INCLUDES) -c -o $@ $<

keccak-audit: $(BUILD)/test_$(KECCAK_CAND) $(BUILD)/test_kem_keccak $(call KECCAK_OBJS,$(KSU)) \
		$(KSU)/official_fips202.o $(KSU)/official_symmetric.o \
		$(BUILD)/$(KECCAK_CAND).o $(BUILD)/kem_keccak.o | $(EVIDENCE)
	$(PYTHON) $(KCOMMON)/tools/audit_keccak_linked.py --param $(PARAM) --experiment . \
		--candidate-elf $(BUILD)/test_$(KECCAK_CAND) --control-elf $(BUILD)/test_kem_keccak \
		--candidate-obj $(BUILD)/$(KECCAK_CAND).o --control-obj $(BUILD)/kem_keccak.o \
		--stack-usage-dir $(KSU) --output $(EVIDENCE)/keccak-linked-summary.json

keccak-ct: $(BUILD)/test_$(KECCAK_CAND) | $(EVIDENCE)
	$(PYTHON) $(KCOMMON)/tools/audit_keccak_ct.py --param $(PARAM) --experiment . \
		--elf $(BUILD)/test_$(KECCAK_CAND) --build $(BUILD)/ct --output $(EVIDENCE)/keccak-ct-summary.json

# Mutation check: the SHAKE256 differential must reject 8 one-line Keccak / wrapper mutants.
keccak-mutate: | $(EVIDENCE)
	$(PYTHON) $(KCOMMON)/tools/mutate_keccak.py --param $(PARAM) --experiment . \
		--includes "$(INCLUDES)" --output $(EVIDENCE)/keccak-mutation-check.json

# Needs a clean mlkem-native checkout at the pinned commit: MLK_ROOT=/path/to/mlkem-native
keccak-config-equivalence: | $(EVIDENCE)
	$(PYTHON) $(KCOMMON)/tools/check_keccak_config_equivalence.py --mlk-root $(MLK_ROOT) \
		--build $(BUILD)/config_equivalence --output $(EVIDENCE)/keccak-config-equivalence.json

keccak-phase-a: keccak-check keccak-sanitize keccak-audit keccak-ct keccak-mutate

# Curated, deterministic-shape evidence into the tracked results dir.
keccak-record: keccak-phase-a
	mkdir -p results/keccak-phase-a
	{ echo "== release ($(CFLAGS))" && $(call keccak_run,$(BUILD),) && \
	  echo "== sanitizer ($(SANFLAGS); $(SAN_ENV))" && $(SAN_ENV) $(call keccak_run,$(BUILD_SAN),$(SAN_ENV)); } \
		> $(EVIDENCE)/keccak-closure-tests.log 2>&1
	cp $(EVIDENCE)/keccak-closure-tests.log $(EVIDENCE)/keccak-generation.json \
		$(EVIDENCE)/keccak-linked-summary.json $(EVIDENCE)/keccak-ct-summary.json \
		$(EVIDENCE)/keccak-mutation-check.json results/keccak-phase-a/
	$(if $(MLK_ROOT),$(MAKE) --no-print-directory keccak-config-equivalence && \
		cp $(EVIDENCE)/keccak-config-equivalence.json results/keccak-phase-a/)

# ------------------------------------------------ SUPERCOP-flat feasibility (scratch only)
# Flattens base qualification tree + vendored mlkem-native + adapter into one
# implementation directory under FLAT_OUT and compiles/tries it with every
# okc-amd64 compiler line of the (read-only) SUPERCOP campaign.  Never installs.
keccak-flat:
	$(PYTHON) $(KCOMMON)/tools/export_keccak_flat.py --param $(PARAM) --experiment . \
		--base-qualification $(KECCAK_BASE_QUAL) --out $(FLAT_OUT) --supercop $(SUPERCOP_CAMPAIGN) \
		--pristine $(SUPERCOP_PRISTINE) --machine $(SUPERCOP_MACHINE)

# ------------------------------------------------ same-ELF component/caller diagnostic
# Official (v0), base candidate (v1), base+keccak (v2) and keccak-only (v3)
# KEM translation units, Official / mlkem-native O3 / mlkem-native O2 hash
# wrappers and x1 permutations in one ELF; common O3GC recipe (the O2 copy:
# same flags with -O2), cpucycles from the disposable SUPERCOP campaign (read
# only).  supercop-derived, not Native.  _swapped links everything in reverse.
KB_RENAME = -Dcrypto_kem_keypair=$(1)_keypair -Dcrypto_kem_enc=$(1)_enc -Dcrypto_kem_dec=$(1)_dec
KBENCH_O2 := $(patsubst -O3,-O2,$(BENCH_CFLAGS))
KBENCH_O2_DEFS := -DMLK_CONFIG_NAMESPACE_PREFIX=ntruplus_mlkfips202o2 -DNTRUPLUS_KECCAK_TAG=keccako2
$(eval $(call keccak_objs,$(BUILD)/kbench,$(BENCH_CFLAGS),,))
$(eval $(call keccak_objs,$(BUILD)/kbench,$(KBENCH_O2),_o2,$(KBENCH_O2_DEFS)))
$(BUILD)/kbench:
	mkdir -p $@
define kbench_obj # $(1)=vN $(2)=source
$(BUILD)/kbench/kem_$(1).o: $(COMMON)/bench/kem_diag.c $(2) src/kem_lazy.c | $(BUILD)/kbench
	$(CC) $(BENCH_CFLAGS) -I. $(KECCAK_INCLUDES) $(call KB_RENAME,$(1)) '-DKEM_SOURCE="$(2)"' \
		-DDERAND_NAME=$(1)_enc_derand -c -o $$@ $$<
endef
$(eval $(call kbench_obj,v0,$(OFFICIAL)/kem.c))
$(eval $(call kbench_obj,v1,src/$(KECCAK_BASE).c))
$(eval $(call kbench_obj,v2,src/$(KECCAK_CAND).c))
$(eval $(call kbench_obj,v3,src/kem_keccak.c))
KB := $(BUILD)/kbench
KB_KEM := $(KB)/kem_v0.o $(KB)/kem_v1.o $(KB)/kem_v2.o $(KB)/kem_v3.o
KB_KEM_REV := $(KB)/kem_v3.o $(KB)/kem_v2.o $(KB)/kem_v1.o $(KB)/kem_v0.o
KB_HASH := $(KB)/mlk_fips202.o $(KB)/mlk_keccakf1600.o $(KB)/symmetric_keccak.o \
	$(KB)/mlk_fips202_o2.o $(KB)/mlk_keccakf1600_o2.o $(KB)/symmetric_keccak_o2.o
KB_HASH_REV := $(KB)/symmetric_keccak_o2.o $(KB)/mlk_keccakf1600_o2.o $(KB)/mlk_fips202_o2.o \
	$(KB)/symmetric_keccak.o $(KB)/mlk_keccakf1600.o $(KB)/mlk_fips202.o
KB_COMMON := $(KCOMMON)/bench/bench_keccak_diag.c $(COMMON)/tests/support/crypto_declassify.c
$(BUILD)/bench_keccak_diag: $(KB_COMMON) $(KB_KEM) $(KB_HASH) $(KECCAK_BASE_ASM) $(COMMON_C) $(COMMON_ASM) \
		$(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -maes -I$(KAT) -I$(CPU_INCLUDE) $(INCLUDES) -o $@ $^ $(CPU_LIB)
$(BUILD)/bench_keccak_diag_swapped: $(KB_COMMON) $(KB_KEM_REV) $(KB_HASH_REV) $(COMMON_ASM) $(COMMON_C) \
		$(KECCAK_BASE_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -maes -I$(KAT) -I$(CPU_INCLUDE) $(INCLUDES) -o $@ \
		$(filter %.c,$(KB_COMMON)) $(KB_KEM_REV) $(KB_HASH_REV) \
		$(call reverse,$(COMMON_ASM)) $(call reverse,$(COMMON_C)) $(call reverse,$(KECCAK_BASE_ASM)) \
		$(BUILD)/kat_rng.o $(BUILD)/kat_aes.o $(CPU_LIB)
reverse = $(if $(1),$(call reverse,$(wordlist 2,$(words $(1)),$(1))) $(firstword $(1)))

keccak-bench: $(BUILD)/bench_keccak_diag $(BUILD)/bench_keccak_diag_swapped

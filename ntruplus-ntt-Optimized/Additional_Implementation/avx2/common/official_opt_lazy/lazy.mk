# Shared Phase-A (correctness only) rules for the caller-bounded lazy Forward
# candidates of Official NTRU+864 / NTRU+1152 AVX2.  Included by
# NTRU+{864,1152}/experiments/avx2_official_opt_001/Makefile after PARAM is set.
# No timing, SUPERCOP campaign or host-control rule lives here.

ifndef PARAM
$(error PARAM must be 864 or 1152)
endif

CC ?= cc
PYTHON ?= python3
CFLAGS ?= -O3 -mavx2 -march=native -mtune=native -fPIE -Wall -Wextra -Werror
SANFLAGS ?= -O1 -g -mavx2 -march=native -fPIE -fno-omit-frame-pointer -fsanitize=address,undefined -fno-sanitize-recover=all -Wall -Wextra -Werror
# Pinned pristine SUPERCOP 20260831: only its cryptoint/ and include/ headers
# are read (crypto_uint64.h, crypto_int16.h); nothing there is written.
SUPERCOP_PRISTINE ?= /home/nuc/src/supercop-pristine-20260831

COMMON := ../../../common/official_opt_lazy
REPO := ../../../../../..
OFFICIAL := upstream/supercop-avx2
BUILD := build
BUILD_SAN := build_san
EVIDENCE := $(BUILD)/evidence
KAT := $(REPO)/third_party/NTRUplus-official-main/Reference_Implementation/NTRU+$(PARAM)
LAZY := ntruplus$(PARAM)_officialopt_ntt_caller_lazy
LAZY_ASM := asm/$(LAZY).s

COMMON_C := $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c $(OFFICIAL)/fips202.c $(OFFICIAL)/consts.c
COMMON_ASM := $(OFFICIAL)/KeccakP-1600-AVX2.s $(OFFICIAL)/ntt.s $(OFFICIAL)/basemul.s \
	$(OFFICIAL)/baseinv.s $(OFFICIAL)/invntt.s $(OFFICIAL)/pack.s $(OFFICIAL)/add.s \
	$(OFFICIAL)/cbd.s $(OFFICIAL)/crepmod3.s
INCLUDES := -I$(COMMON)/tests/support -I$(OFFICIAL) -I$(SUPERCOP_PRISTINE)/cryptoint \
	-I$(SUPERCOP_PRISTINE)/include
REF_RENAME := -Dcrypto_kem_keypair=official_ref_keypair -Dcrypto_kem_enc=official_ref_enc \
	-Dcrypto_kem_dec=official_ref_dec
LAZY_RENAME := -Dcrypto_kem_keypair=official_lazy_keypair -Dcrypto_kem_enc=official_lazy_enc \
	-Dcrypto_kem_dec=official_lazy_dec
KEM_WRAP := -Wl,--wrap=randombytes -Wl,--wrap=fips202avx_shake256
FRETRY := -DTEST_F_RETRY -Wl,--wrap=poly_baseinv
FWD_SRC := $(COMMON)/tests/test_forward_caller_lazy.c $(COMMON)/tests/support/crypto_declassify.c $(LAZY_ASM) $(COMMON_C) $(COMMON_ASM)
KEM_TEST_SRC := $(COMMON)/tests/test_kem_lazy.c $(COMMON)/tests/support/crypto_declassify.c \
	$(LAZY_ASM) $(COMMON_C) $(COMMON_ASM)
# The NIST KAT DRBG (third-party, warning-unclean) is built without -Werror.
KAT_CFLAGS := -O2 -maes
KAT_SANFLAGS := -O1 -g -maes -fno-omit-frame-pointer -fsanitize=address,undefined

.DEFAULT_GOAL := check
.PHONY: generate check-generate check-upstream check sanitize audit range-proof phase-a record clean

generate:
	$(PYTHON) $(COMMON)/tools/generate_forward_caller_lazy.py --param $(PARAM) --experiment .

check-generate:
	$(PYTHON) $(COMMON)/tools/generate_forward_caller_lazy.py --param $(PARAM) --experiment . --check

check-upstream:
	$(PYTHON) $(REPO)/scripts/check_supercop_experiment.py --experiment . --parameter $(PARAM)

$(BUILD) $(BUILD_SAN) $(EVIDENCE):
	mkdir -p $@

# ---------------------------------------------------------------- release-flag builds
$(BUILD)/test_forward_caller_lazy: $(FWD_SRC) | $(BUILD)
	$(CC) $(CFLAGS) $(INCLUDES) -DLAZY_NTT=$(LAZY) -o $@ $^

$(BUILD)/kat_aes.o: $(KAT)/kat/aes.c | $(BUILD)
	$(CC) $(KAT_CFLAGS) -c -o $@ $<

$(BUILD)/kat_rng.o: $(KAT)/kat/rng.c | $(BUILD)
	$(CC) $(KAT_CFLAGS) -I$(KAT)/kat -c -o $@ $<

$(BUILD)/kem_ref.o: $(OFFICIAL)/kem.c | $(BUILD)
	$(CC) $(CFLAGS) $(INCLUDES) $(REF_RENAME) -c -o $@ $<

$(BUILD)/kem_lazy.o: src/kem_lazy.c | $(BUILD)
	$(CC) $(CFLAGS) $(INCLUDES) $(LAZY_RENAME) -c -o $@ $<

$(BUILD)/test_kem_lazy: $(KEM_TEST_SRC) $(BUILD)/kem_ref.o $(BUILD)/kem_lazy.o $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -maes -I$(KAT) $(INCLUDES) $(KEM_WRAP) -o $@ $^

$(BUILD)/test_kem_lazy_fretry: $(KEM_TEST_SRC) $(BUILD)/kem_ref.o $(BUILD)/kem_lazy.o $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -maes -I$(KAT) $(INCLUDES) $(KEM_WRAP) $(FRETRY) -o $@ $^

$(BUILD)/official_ntt.o: $(OFFICIAL)/ntt.s | $(BUILD)
	$(CC) -c -o $@ $<

# ---------------------------------------------------------------- sanitizer builds
$(BUILD_SAN)/test_forward_caller_lazy: $(FWD_SRC) | $(BUILD_SAN)
	$(CC) $(SANFLAGS) $(INCLUDES) -DLAZY_NTT=$(LAZY) -o $@ $^

$(BUILD_SAN)/kat_aes.o: $(KAT)/kat/aes.c | $(BUILD_SAN)
	$(CC) $(KAT_SANFLAGS) -c -o $@ $<

$(BUILD_SAN)/kat_rng.o: $(KAT)/kat/rng.c | $(BUILD_SAN)
	$(CC) $(KAT_SANFLAGS) -I$(KAT)/kat -c -o $@ $<

$(BUILD_SAN)/kem_ref.o: $(OFFICIAL)/kem.c | $(BUILD_SAN)
	$(CC) $(SANFLAGS) $(INCLUDES) $(REF_RENAME) -c -o $@ $<

$(BUILD_SAN)/kem_lazy.o: src/kem_lazy.c | $(BUILD_SAN)
	$(CC) $(SANFLAGS) $(INCLUDES) $(LAZY_RENAME) -c -o $@ $<

$(BUILD_SAN)/test_kem_lazy: $(KEM_TEST_SRC) $(BUILD_SAN)/kem_ref.o $(BUILD_SAN)/kem_lazy.o $(BUILD_SAN)/kat_aes.o $(BUILD_SAN)/kat_rng.o | $(BUILD_SAN)
	$(CC) $(SANFLAGS) -maes -I$(KAT) $(INCLUDES) $(KEM_WRAP) -o $@ $^

$(BUILD_SAN)/test_kem_lazy_fretry: $(KEM_TEST_SRC) $(BUILD_SAN)/kem_ref.o $(BUILD_SAN)/kem_lazy.o $(BUILD_SAN)/kat_aes.o $(BUILD_SAN)/kat_rng.o | $(BUILD_SAN)
	$(CC) $(SANFLAGS) -maes -I$(KAT) $(INCLUDES) $(KEM_WRAP) $(FRETRY) -o $@ $^

# ---------------------------------------------------------------- gates
check: check-upstream check-generate $(BUILD)/test_forward_caller_lazy $(BUILD)/test_kem_lazy $(BUILD)/test_kem_lazy_fretry
	$(BUILD)/test_forward_caller_lazy
	$(BUILD)/test_kem_lazy
	$(BUILD)/test_kem_lazy_fretry

# ASan, UBSan (-fno-sanitize-recover=all) and LeakSanitizer are all fatal.
# LeakSanitizer ran fine on the Phase-A host; on hosts whose ptrace policy
# breaks it, run `make sanitize DETECT_LEAKS=0` and record that deviation.
DETECT_LEAKS ?= 1
SAN_ENV := ASAN_OPTIONS=detect_leaks=$(DETECT_LEAKS) UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1
sanitize: $(BUILD_SAN)/test_forward_caller_lazy $(BUILD_SAN)/test_kem_lazy $(BUILD_SAN)/test_kem_lazy_fretry
	$(SAN_ENV) $(BUILD_SAN)/test_kem_lazy
	$(SAN_ENV) $(BUILD_SAN)/test_forward_caller_lazy
	$(SAN_ENV) $(BUILD_SAN)/test_kem_lazy_fretry

audit: $(BUILD)/test_kem_lazy $(BUILD)/official_ntt.o | $(EVIDENCE)
	$(PYTHON) $(COMMON)/tools/audit_forward_caller_lazy.py --param $(PARAM) --experiment . \
		--elf $(BUILD)/test_kem_lazy --official-obj $(BUILD)/official_ntt.o \
		--output $(EVIDENCE)/linked-symbol-summary.json

range-proof: | $(EVIDENCE)
	$(PYTHON) $(COMMON)/range_proof/prove_forward_lazy.py --param $(PARAM) --experiment . \
		--build $(BUILD)/range_proof --output $(EVIDENCE)/range-proof-summary.json

phase-a: check sanitize audit range-proof

# Copy the curated, deterministic-shape evidence into the tracked results dir.
record: phase-a
	mkdir -p results/phase-a
	cp $(EVIDENCE)/linked-symbol-summary.json $(EVIDENCE)/range-proof-summary.json results/phase-a/

clean:
	rm -rf $(BUILD) $(BUILD_SAN)

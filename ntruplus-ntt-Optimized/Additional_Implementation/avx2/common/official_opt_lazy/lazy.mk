# Shared Phase-A (correctness only) rules for the caller-bounded lazy Forward
# candidates of Official NTRU+768 / 864 / 1152 AVX2.  Included by
# NTRU+{864,1152}/experiments/avx2_official_opt_001/Makefile and
# NTRU+768/experiments/avx2_official_opt_freeze_001/Makefile after PARAM is set.
# Phase B adds only the same-ELF diagnostic bench build (`make bench`); the
# timing itself is run by tools/run_forward_caller_lazy_short.py.  No
# host-control rule lives here.

ifndef PARAM
$(error PARAM must be 768, 864 or 1152)
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
.PHONY: bench bench-keypair generate check-generate check-upstream check sanitize audit range-proof phase-a record clean

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
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(COMMON)/range_proof/prove_forward_lazy.py --param $(PARAM) --experiment . \
		--build $(BUILD)/range_proof --output $(EVIDENCE)/range-proof-summary.json

phase-a: check sanitize audit range-proof

# Copy the curated, deterministic-shape evidence into the tracked results dir.
record: phase-a
	mkdir -p results/phase-a
	cp $(EVIDENCE)/linked-symbol-summary.json $(EVIDENCE)/range-proof-summary.json results/phase-a/

# ---------------------------------------------------------------- Phase B same-ELF bench
# cpucycles comes from an initialised disposable SUPERCOP campaign (read only).
SUPERCOP_CAMPAIGN ?= /home/nuc/src/supercop-campaign-lazy-864-1152-20260923-001
SUPERCOP_MACHINE ?= nucpromtlhcubinucai1ummsb209
CPU_INCLUDE := $(SUPERCOP_CAMPAIGN)/bench/$(SUPERCOP_MACHINE)/include/nontimecop/amd64
CPU_LIB := $(SUPERCOP_CAMPAIGN)/bench/$(SUPERCOP_MACHINE)/lib/nontimecop/amd64/libcpucycles.a
# Common O3GC recipe, as the NTRU+768 Round-5 same-ELF bench.
BENCH_CFLAGS := $(CFLAGS) -ffunction-sections -fdata-sections -Wl,--gc-sections

$(BUILD)/bench_kem_ref.o: $(COMMON)/bench/kem_diag.c $(OFFICIAL)/kem.c | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I. $(INCLUDES) $(REF_RENAME) '-DKEM_SOURCE="$(OFFICIAL)/kem.c"' \
		-DDERAND_NAME=officialopt_ref_enc_derand -c -o $@ $<

$(BUILD)/bench_kem_lazy.o: $(COMMON)/bench/kem_diag.c src/kem_lazy.c | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I. $(INCLUDES) $(LAZY_RENAME) '-DKEM_SOURCE="src/kem_lazy.c"' \
		-DDERAND_NAME=officialopt_lazy_enc_derand -c -o $@ $<

$(BUILD)/bench_caller_lazy: $(COMMON)/bench/bench_caller_lazy.c $(COMMON)/tests/support/crypto_declassify.c \
		$(BUILD)/bench_kem_ref.o $(BUILD)/bench_kem_lazy.o $(LAZY_ASM) $(COMMON_C) $(COMMON_ASM) \
		$(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -maes -I$(KAT) -I$(CPU_INCLUDE) $(INCLUDES) -DLAZY_NTT=$(LAZY) -o $@ $^ $(CPU_LIB)

bench: $(BUILD)/bench_caller_lazy

# Phase-B follow-up seed-matched paired Keypair harness (supercop-derived
# diagnostic).  Same O3GC recipe and namespaced KEM objects as the same-ELF
# bench; its own randombytes() replaces the KAT DRBG.  The _swapped ELF links
# the two KEM objects in the opposite order (placement control).
KP_SRC := $(COMMON)/bench/bench_keypair_seedmatched.c $(COMMON)/tests/support/crypto_declassify.c
KP_DEPS := $(LAZY_ASM) $(COMMON_C) $(COMMON_ASM)

$(BUILD)/bench_keypair_seedmatched: $(KP_SRC) $(BUILD)/bench_kem_ref.o $(BUILD)/bench_kem_lazy.o $(KP_DEPS) | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I$(CPU_INCLUDE) $(INCLUDES) -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_keypair_seedmatched_swapped: $(KP_SRC) $(BUILD)/bench_kem_lazy.o $(BUILD)/bench_kem_ref.o $(KP_DEPS) | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I$(CPU_INCLUDE) $(INCLUDES) -o $@ $^ $(CPU_LIB)

bench-keypair: $(BUILD)/bench_keypair_seedmatched $(BUILD)/bench_keypair_seedmatched_swapped

clean:
	rm -rf $(BUILD) $(BUILD_SAN)

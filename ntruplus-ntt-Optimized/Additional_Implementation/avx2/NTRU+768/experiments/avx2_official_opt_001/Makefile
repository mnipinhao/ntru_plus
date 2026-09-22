CC ?= cc
.DEFAULT_GOAL := generate
CFLAGS ?= -O3 -mavx2 -march=native -mtune=native -fPIE -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Werror
OFFICIAL := upstream/supercop-avx2
BUILD := build
SUPERCOP_ROOT ?= /home/nuc/supercop-20260627
SUPERCOP_MACHINE ?= nucpromtlhcubinucai1ummsb209
CPU_INCLUDE := $(SUPERCOP_ROOT)/bench/$(SUPERCOP_MACHINE)/include/nontimecop/amd64
CPU_LIB := $(SUPERCOP_ROOT)/bench/$(SUPERCOP_MACHINE)/lib/nontimecop/amd64/libcpucycles.a
KAT := ../../../../../../third_party/NTRUplus-official-main/Reference_Implementation/NTRU+768
COMMON_C := $(OFFICIAL)/poly.c $(OFFICIAL)/symmetric.c $(OFFICIAL)/fips202.c $(OFFICIAL)/consts.c
COMMON_ASM := $(OFFICIAL)/KeccakP-1600-AVX2.s $(OFFICIAL)/ntt.s $(OFFICIAL)/basemul.s $(OFFICIAL)/baseinv.s $(OFFICIAL)/invntt.s $(OFFICIAL)/pack.s $(OFFICIAL)/add.s $(OFFICIAL)/cbd.s $(OFFICIAL)/crepmod3.s
KEM_INCLUDES := -Itests/support -I$(OFFICIAL) -I$(SUPERCOP_ROOT)/bench/$(SUPERCOP_MACHINE)/include/amd64 -I$(SUPERCOP_ROOT)/include
VARIANT_ASM := asm/ntruplus768_officialopt_basemul_add.s asm/ntruplus768_officialopt_dup_basemul.s asm/ntruplus768_officialopt_shared_diag.s asm/ntruplus768_officialopt_ntt_early_const.s
VARIANT_OBJS := $(BUILD)/kem_ref.o $(BUILD)/kem_dup.o $(BUILD)/kem_fused.o $(BUILD)/kem_shared.o $(BUILD)/kem_forward.o
include serialize_compare.mk
include yang.mk

.PHONY: generate check check-inverse-ct check-inverse-ct-r3 check-inverse-ct-full check-inverse-ct-cohort check-inverse-ct-controls
generate:
	python3 tools/generate_fused_basemul.py
	python3 tools/generate_shared_basemul.py
	python3 tools/generate_forward_early_const.py
	python3 tools/generate_forward_caller_lazy.py
	python3 tools/generate_phase_profile.py

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/test_fused_basemul: tests/test_fused_basemul.c asm/ntruplus768_officialopt_basemul_add.s asm/ntruplus768_officialopt_dup_basemul.s asm/ntruplus768_officialopt_shared_diag.s $(OFFICIAL)/basemul.s $(OFFICIAL)/add.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -o $@ $^

$(BUILD)/test_forward_schedule: tests/test_forward_schedule.c asm/ntruplus768_officialopt_ntt_early_const.s $(OFFICIAL)/ntt.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -o $@ $^

$(BUILD)/test_forward_caller_lazy: tests/test_forward_caller_lazy.c asm/ntruplus768_officialopt_ntt_caller_lazy.s $(OFFICIAL)/ntt.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -o $@ $^

$(BUILD)/test_inverse_ct: tests/test_inverse_ct.c asm/ntruplus768_officialopt_invntt_ct.s $(OFFICIAL)/invntt.s $(OFFICIAL)/basemul.s $(OFFICIAL)/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -o $@ $^

$(BUILD)/test_inverse_ct_r3: tests/test_inverse_ct.c asm/ntruplus768_officialopt_invntt_ct_r3.s $(OFFICIAL)/invntt.s $(OFFICIAL)/basemul.s $(OFFICIAL)/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_r3 -o $@ $^

$(BUILD)/test_inverse_ct_full: tests/test_inverse_ct.c asm/ntruplus768_officialopt_invntt_ct_full.s $(OFFICIAL)/invntt.s $(OFFICIAL)/basemul.s $(OFFICIAL)/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_full -o $@ $^

$(BUILD)/test_inverse_ct_cohort: tests/test_inverse_ct.c asm/ntruplus768_officialopt_invntt_ct_cohort.s $(OFFICIAL)/invntt.s $(OFFICIAL)/basemul.s $(OFFICIAL)/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_cohort -o $@ $^

$(BUILD)/test_inverse_ct_wresident: tests/test_inverse_ct.c asm/ntruplus768_officialopt_invntt_ct_wresident.s $(OFFICIAL)/invntt.s $(OFFICIAL)/basemul.s $(OFFICIAL)/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_wresident -o $@ $^

$(BUILD)/test_inverse_ct_earlynorm: tests/test_inverse_ct.c asm/ntruplus768_officialopt_invntt_ct_earlynorm.s $(OFFICIAL)/invntt.s $(OFFICIAL)/basemul.s $(OFFICIAL)/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_earlynorm -o $@ $^

$(BUILD)/test_inverse_ct_controls: tests/test_inverse_ct_controls.c asm/ntruplus768_officialopt_invntt_ct_cohort.s asm/ntruplus768_officialopt_invntt_ct_wresident.s asm/ntruplus768_officialopt_invntt_ct_earlynorm.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -o $@ $^

$(BUILD)/kem_ct.o: tests/kem_ct_diag.c src/kem_ct.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -Dcrypto_kem_keypair=official_ct_keypair -Dcrypto_kem_enc=official_ct_enc -Dcrypto_kem_dec=official_ct_dec -c -o $@ $<

$(BUILD)/kem_ct_r3.o: tests/kem_ct_diag.c src/kem_ct.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_r3 -Dcrypto_kem_keypair=official_ct_r3_keypair -Dcrypto_kem_enc=official_ct_r3_enc -Dcrypto_kem_dec=official_ct_r3_dec -c -o $@ $<

$(BUILD)/kem_ct_full.o: tests/kem_ct_diag.c src/kem_ct.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_full -Dcrypto_kem_keypair=official_ct_full_keypair -Dcrypto_kem_enc=official_ct_full_enc -Dcrypto_kem_dec=official_ct_full_dec -c -o $@ $<

$(BUILD)/kem_ct_cohort.o: tests/kem_ct_diag.c src/kem_ct.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_cohort -Dcrypto_kem_keypair=official_ct_cohort_keypair -Dcrypto_kem_enc=official_ct_cohort_enc -Dcrypto_kem_dec=official_ct_cohort_dec -c -o $@ $<

$(BUILD)/kem_ct_wresident.o: tests/kem_ct_diag.c src/kem_ct.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_wresident -Dcrypto_kem_keypair=official_ct_wresident_keypair -Dcrypto_kem_enc=official_ct_wresident_enc -Dcrypto_kem_dec=official_ct_wresident_dec -c -o $@ $<

$(BUILD)/kem_ct_earlynorm.o: tests/kem_ct_diag.c src/kem_ct.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_earlynorm -Dcrypto_kem_keypair=official_ct_earlynorm_keypair -Dcrypto_kem_enc=official_ct_earlynorm_enc -Dcrypto_kem_dec=official_ct_earlynorm_dec -c -o $@ $<

$(BUILD)/test_kem_ct: tests/test_kem_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_ct.o asm/ntruplus768_officialopt_invntt_ct.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) $(KEM_INCLUDES) -o $@ $^

$(BUILD)/test_kem_ct_r3: tests/test_kem_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_ct_r3.o asm/ntruplus768_officialopt_invntt_ct_r3.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) $(KEM_INCLUDES) -Dofficial_ct_dec=official_ct_r3_dec -o $@ $^

$(BUILD)/test_kem_ct_full: tests/test_kem_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_ct_full.o asm/ntruplus768_officialopt_invntt_ct_full.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) $(KEM_INCLUDES) -Dofficial_ct_dec=official_ct_full_dec -o $@ $^

$(BUILD)/test_kem_ct_cohort: tests/test_kem_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_ct_cohort.o asm/ntruplus768_officialopt_invntt_ct_cohort.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) $(KEM_INCLUDES) -Dofficial_ct_dec=official_ct_cohort_dec -o $@ $^

$(BUILD)/test_kem_ct_wresident: tests/test_kem_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_ct_wresident.o asm/ntruplus768_officialopt_invntt_ct_wresident.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) $(KEM_INCLUDES) -Dofficial_ct_dec=official_ct_wresident_dec -o $@ $^

$(BUILD)/test_kem_ct_earlynorm: tests/test_kem_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_ct_earlynorm.o asm/ntruplus768_officialopt_invntt_ct_earlynorm.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) $(KEM_INCLUDES) -Dofficial_ct_dec=official_ct_earlynorm_dec -o $@ $^

$(BUILD)/kem_lazy.o: tests/kem_lazy_diag.c src/kem_lazy.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -Dcrypto_kem_keypair=official_lazy_keypair -Dcrypto_kem_enc=official_lazy_enc -Dcrypto_kem_dec=official_lazy_dec -c -o $@ $<

$(BUILD)/test_kem_lazy: tests/test_kem_lazy.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_lazy.o asm/ntruplus768_officialopt_ntt_caller_lazy.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) $(KEM_INCLUDES) -Wl,--wrap=randombytes -Wl,--wrap=fips202avx_shake256 -o $@ $^

$(BUILD)/kem_ref.o: tests/kem_ref_diag.c src/kem_reference.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -Dcrypto_kem_keypair=official_ref_keypair -Dcrypto_kem_enc=official_ref_enc -Dcrypto_kem_dec=official_ref_dec -c -o $@ $<

$(BUILD)/kem_fused.o: tests/kem_fused_diag.c src/kem_fused.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -Dcrypto_kem_keypair=official_fused_keypair -Dcrypto_kem_enc=official_fused_enc -Dcrypto_kem_dec=official_fused_dec -c -o $@ $<

$(BUILD)/kem_dup.o: tests/kem_dup_diag.c src/kem_dup.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -Dcrypto_kem_keypair=official_dup_keypair -Dcrypto_kem_enc=official_dup_enc -Dcrypto_kem_dec=official_dup_dec -c -o $@ $<

$(BUILD)/kem_shared.o: tests/kem_shared_diag.c src/kem_shared.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -Dcrypto_kem_keypair=official_shared_keypair -Dcrypto_kem_enc=official_shared_enc -Dcrypto_kem_dec=official_shared_dec -c -o $@ $<

$(BUILD)/kem_forward.o: tests/kem_forward_diag.c src/kem_forward.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -Dcrypto_kem_keypair=official_forward_keypair -Dcrypto_kem_enc=official_forward_enc -Dcrypto_kem_dec=official_forward_dec -c -o $@ $<

$(BUILD)/kat_aes.o: $(KAT)/kat/aes.c | $(BUILD)
	$(CC) -O3 -maes -c -o $@ $<

$(BUILD)/kat_rng.o: $(KAT)/kat/rng.c | $(BUILD)
	$(CC) -O3 -maes -c -o $@ $<

$(BUILD)/test_kem_fused: tests/test_kem_fused.c tests/support/crypto_declassify.c $(VARIANT_OBJS) $(VARIANT_ASM) $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) $(KEM_INCLUDES) -Wl,--wrap=randombytes -o $@ $^

check: $(BUILD)/test_fused_basemul $(BUILD)/test_forward_schedule $(BUILD)/test_kem_fused $(BUILD)/test_forward_caller_lazy $(BUILD)/test_kem_lazy
	$(BUILD)/test_fused_basemul
	$(BUILD)/test_forward_schedule
	$(BUILD)/test_kem_fused
	$(BUILD)/test_forward_caller_lazy
	$(BUILD)/test_kem_lazy

check-inverse-ct: $(BUILD)/test_inverse_ct $(BUILD)/test_kem_ct
	$(BUILD)/test_inverse_ct
	$(BUILD)/test_kem_ct

check-inverse-ct-r3: $(BUILD)/test_inverse_ct_r3 $(BUILD)/test_kem_ct_r3
	python3 tools/prove_inverse_ct_r3_range.py
	$(BUILD)/test_inverse_ct_r3
	$(BUILD)/test_kem_ct_r3

check-inverse-ct-full: $(BUILD)/test_inverse_ct_full $(BUILD)/test_kem_ct_full
	python3 tools/prove_inverse_ct_full_range.py
	$(BUILD)/test_inverse_ct_full
	$(BUILD)/test_kem_ct_full

check-inverse-ct-cohort: $(BUILD)/test_inverse_ct_cohort $(BUILD)/test_kem_ct_cohort
	python3 tools/prove_inverse_ct_full_range.py
	$(BUILD)/test_inverse_ct_cohort
	$(BUILD)/test_kem_ct_cohort

check-inverse-ct-controls: $(BUILD)/test_inverse_ct_wresident $(BUILD)/test_inverse_ct_earlynorm $(BUILD)/test_inverse_ct_controls $(BUILD)/test_kem_ct_wresident $(BUILD)/test_kem_ct_earlynorm
	python3 tools/prove_inverse_ct_full_range.py
	$(BUILD)/test_inverse_ct_wresident
	$(BUILD)/test_inverse_ct_earlynorm
	$(BUILD)/test_inverse_ct_controls
	$(BUILD)/test_kem_ct_wresident
	$(BUILD)/test_kem_ct_earlynorm

$(BUILD)/bench_fused: bench/bench_fused.c tests/support/crypto_declassify.c $(VARIANT_OBJS) $(VARIANT_ASM) $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_matrix: bench/bench_matrix.c tests/support/crypto_declassify.c $(VARIANT_OBJS) $(VARIANT_ASM) $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_cutpoints: bench/bench_cutpoints.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_phase_research: bench/bench_phase_research.c generated/poly_phase_profile.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(filter-out $(OFFICIAL)/poly.c,$(COMMON_C)) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_caller_lazy: bench/bench_caller_lazy.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_lazy.o asm/ntruplus768_officialopt_ntt_caller_lazy.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_inverse_ct: bench/bench_inverse_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_ct.o asm/ntruplus768_officialopt_invntt_ct.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_inverse_ct_r3: bench/bench_inverse_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_ct_r3.o asm/ntruplus768_officialopt_invntt_ct_r3.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_r3 -Dofficial_ct_dec=official_ct_r3_dec -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_inverse_ct_r3_compare: bench/bench_inverse_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_ct.o $(BUILD)/kem_ct_r3.o asm/ntruplus768_officialopt_invntt_ct.s asm/ntruplus768_officialopt_invntt_ct_r3.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -DCT_R3_COMPARE -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_inverse_ct_full: bench/bench_inverse_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_ct_full.o asm/ntruplus768_officialopt_invntt_ct_full.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_full -Dofficial_ct_dec=official_ct_full_dec -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_inverse_ct_full_compare: bench/bench_inverse_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_ct.o $(BUILD)/kem_ct_full.o asm/ntruplus768_officialopt_invntt_ct.s asm/ntruplus768_officialopt_invntt_ct_full.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -DCT_R3_COMPARE -Dntruplus768_officialopt_invntt_ct_r3=ntruplus768_officialopt_invntt_ct_full -Dofficial_ct_r3_dec=official_ct_full_dec -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_inverse_ct_cohort: bench/bench_inverse_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_ct_cohort.o asm/ntruplus768_officialopt_invntt_ct_cohort.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_cohort -Dofficial_ct_dec=official_ct_cohort_dec -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_inverse_ct_cohort_compare: bench/bench_inverse_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_ct.o $(BUILD)/kem_ct_cohort.o asm/ntruplus768_officialopt_invntt_ct.s asm/ntruplus768_officialopt_invntt_ct_cohort.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -DCT_R3_COMPARE -Dntruplus768_officialopt_invntt_ct_r3=ntruplus768_officialopt_invntt_ct_cohort -Dofficial_ct_r3_dec=official_ct_cohort_dec -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_inverse_ct_wresident: bench/bench_inverse_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_ct_wresident.o asm/ntruplus768_officialopt_invntt_ct_wresident.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_wresident -Dofficial_ct_dec=official_ct_wresident_dec -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_inverse_ct_earlynorm: bench/bench_inverse_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_ct_earlynorm.o asm/ntruplus768_officialopt_invntt_ct_earlynorm.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_earlynorm -Dofficial_ct_dec=official_ct_earlynorm_dec -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_inverse_ct_wresident_vs_cohort: bench/bench_inverse_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_ct_cohort.o $(BUILD)/kem_ct_wresident.o asm/ntruplus768_officialopt_invntt_ct_cohort.s asm/ntruplus768_officialopt_invntt_ct_wresident.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -DCT_R3_COMPARE -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_cohort -Dntruplus768_officialopt_invntt_ct_r3=ntruplus768_officialopt_invntt_ct_wresident -Dofficial_ct_dec=official_ct_cohort_dec -Dofficial_ct_r3_dec=official_ct_wresident_dec -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_inverse_ct_earlynorm_vs_cohort: bench/bench_inverse_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_ct_cohort.o $(BUILD)/kem_ct_earlynorm.o asm/ntruplus768_officialopt_invntt_ct_cohort.s asm/ntruplus768_officialopt_invntt_ct_earlynorm.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -DCT_R3_COMPARE -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_cohort -Dntruplus768_officialopt_invntt_ct_r3=ntruplus768_officialopt_invntt_ct_earlynorm -Dofficial_ct_dec=official_ct_cohort_dec -Dofficial_ct_r3_dec=official_ct_earlynorm_dec -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_inverse_ct_pmu: bench/bench_inverse_ct_pmu.c asm/ntruplus768_officialopt_invntt_ct_cohort.s asm/ntruplus768_officialopt_invntt_ct_wresident.s asm/ntruplus768_officialopt_invntt_ct_earlynorm.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -o $@ $^

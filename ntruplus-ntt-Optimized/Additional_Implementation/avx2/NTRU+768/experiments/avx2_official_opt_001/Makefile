CC ?= cc
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

.PHONY: generate check
generate:
	python3 tools/generate_fused_basemul.py
	python3 tools/generate_shared_basemul.py
	python3 tools/generate_forward_early_const.py

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/test_fused_basemul: tests/test_fused_basemul.c asm/ntruplus768_officialopt_basemul_add.s asm/ntruplus768_officialopt_dup_basemul.s asm/ntruplus768_officialopt_shared_diag.s $(OFFICIAL)/basemul.s $(OFFICIAL)/add.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -o $@ $^

$(BUILD)/test_forward_schedule: tests/test_forward_schedule.c asm/ntruplus768_officialopt_ntt_early_const.s $(OFFICIAL)/ntt.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -o $@ $^

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

check: $(BUILD)/test_fused_basemul $(BUILD)/test_forward_schedule $(BUILD)/test_kem_fused
	$(BUILD)/test_fused_basemul
	$(BUILD)/test_forward_schedule
	$(BUILD)/test_kem_fused

$(BUILD)/bench_fused: bench/bench_fused.c tests/support/crypto_declassify.c $(VARIANT_OBJS) $(VARIANT_ASM) $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_matrix: bench/bench_matrix.c tests/support/crypto_declassify.c $(VARIANT_OBJS) $(VARIANT_ASM) $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -o $@ $^ $(CPU_LIB)

$(BUILD)/bench_cutpoints: bench/bench_cutpoints.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -o $@ $^ $(CPU_LIB)

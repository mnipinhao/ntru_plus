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

.PHONY: generate check
generate:
	python3 tools/generate_fused_basemul.py

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/test_fused_basemul: tests/test_fused_basemul.c asm/ntruplus768_officialopt_basemul_add.s $(OFFICIAL)/basemul.s $(OFFICIAL)/add.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -o $@ $^

$(BUILD)/kem_ref.o: src/kem_reference.c | $(BUILD)
	$(CC) $(CFLAGS) -Itests/support -I$(OFFICIAL) -I$(SUPERCOP_ROOT)/bench/nucpromtlhcubinucai1ummsb209/include/amd64 -I$(SUPERCOP_ROOT)/include -Dcrypto_kem_keypair=official_ref_keypair -Dcrypto_kem_enc=official_ref_enc -Dcrypto_kem_dec=official_ref_dec -c -o $@ $<

$(BUILD)/kem_fused.o: src/kem_fused.c | $(BUILD)
	$(CC) $(CFLAGS) -Itests/support -I$(OFFICIAL) -I$(SUPERCOP_ROOT)/bench/nucpromtlhcubinucai1ummsb209/include/amd64 -I$(SUPERCOP_ROOT)/include -Dcrypto_kem_keypair=official_fused_keypair -Dcrypto_kem_enc=official_fused_enc -Dcrypto_kem_dec=official_fused_dec -c -o $@ $<

$(BUILD)/kat_aes.o: $(KAT)/kat/aes.c | $(BUILD)
	$(CC) -O3 -maes -c -o $@ $<

$(BUILD)/kat_rng.o: $(KAT)/kat/rng.c | $(BUILD)
	$(CC) -O3 -maes -c -o $@ $<

$(BUILD)/test_kem_fused: tests/test_kem_fused.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_fused.o asm/ntruplus768_officialopt_basemul_add.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(SUPERCOP_ROOT)/bench/nucpromtlhcubinucai1ummsb209/include/amd64 -I$(SUPERCOP_ROOT)/include -Wl,--wrap=randombytes -o $@ $^

check: $(BUILD)/test_fused_basemul $(BUILD)/test_kem_fused
	$(BUILD)/test_fused_basemul
	$(BUILD)/test_kem_fused

$(BUILD)/bench_fused: bench/bench_fused.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_fused.o asm/ntruplus768_officialopt_basemul_add.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) -I$(SUPERCOP_ROOT)/bench/$(SUPERCOP_MACHINE)/include/amd64 -I$(SUPERCOP_ROOT)/include -o $@ $^ $(CPU_LIB)

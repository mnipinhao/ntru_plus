.PHONY: check-serialize-compare
$(BUILD)/bench_serialize_compare: bench/bench_serialize_compare.c tests/support/crypto_declassify.c $(BUILD)/kem_lazy.o $(BUILD)/kem_serialize_compare.o asm/ntruplus768_officialopt_ntt_caller_lazy.s asm/ntruplus768_officialopt_serialize_compare.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -o $@ $^ $(CPU_LIB)

check-serialize-compare: $(BUILD)/test_serialize_compare $(BUILD)/test_kem_serialize_compare $(BUILD)/test_lazy_f_retry
	$(BUILD)/test_serialize_compare
	$(BUILD)/test_kem_serialize_compare
	$(BUILD)/test_lazy_f_retry

$(BUILD)/test_lazy_f_retry: tests/test_kem_lazy.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_lazy.o asm/ntruplus768_officialopt_ntt_caller_lazy.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) $(KEM_INCLUDES) -DTEST_F_RETRY -Wl,--wrap=poly_baseinv -Wl,--wrap=randombytes -Wl,--wrap=fips202avx_shake256 -o $@ $^

$(BUILD)/test_serialize_compare: tests/test_serialize_compare.c asm/ntruplus768_officialopt_serialize_compare.s $(OFFICIAL)/pack.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -o $@ $^

$(BUILD)/kem_serialize_compare.o: tests/kem_serialize_compare_diag.c src/kem_serialize_compare.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -Dcrypto_kem_keypair=official_compare_keypair -Dcrypto_kem_enc=official_compare_enc -Dcrypto_kem_dec=official_compare_dec -c -o $@ $<

$(BUILD)/test_kem_serialize_compare: tests/test_kem_lazy.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_serialize_compare.o asm/ntruplus768_officialopt_ntt_caller_lazy.s asm/ntruplus768_officialopt_serialize_compare.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) $(KEM_INCLUDES) -DTEST_F_RETRY -Wl,--wrap=poly_baseinv -Dofficial_lazy_keypair=official_compare_keypair -Dofficial_lazy_enc=official_compare_enc -Dofficial_lazy_dec=official_compare_dec -Wl,--wrap=randombytes -Wl,--wrap=fips202avx_shake256 -o $@ $^

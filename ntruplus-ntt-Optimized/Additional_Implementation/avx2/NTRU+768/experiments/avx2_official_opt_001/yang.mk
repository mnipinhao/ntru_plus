YANG_ASM = asm/ntruplus768_officialopt_invntt_yang_factored.s
YANG_DEF = -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_yang_factored -Dofficial_ct_dec=official_yang_dec
YANG_LINK = $(BUILD)/kem_ref.o $(BUILD)/kem_lazy.o $(BUILD)/kem_yang.o $(YANG_ASM) asm/ntruplus768_officialopt_ntt_caller_lazy.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o
$(BUILD)/kem_yang.o: tests/kem_yang_diag.c src/kem_lazy.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -Dcrypto_kem_keypair=official_yang_keypair -Dcrypto_kem_enc=official_yang_enc -Dcrypto_kem_dec=official_yang_dec -c -o $@ $<
$(BUILD)/test_inverse_yang: tests/test_inverse_ct.c $(YANG_ASM) $(OFFICIAL)/invntt.s $(OFFICIAL)/basemul.s $(OFFICIAL)/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) $(YANG_DEF) -o $@ $^
$(BUILD)/test_kem_yang: tests/test_kem_ct.c tests/support/crypto_declassify.c $(YANG_LINK) | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) $(KEM_INCLUDES) $(YANG_DEF) -o $@ $^
$(BUILD)/bench_yang: bench/bench_inverse_ct.c tests/support/crypto_declassify.c $(YANG_LINK) | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) $(YANG_DEF) -Dofficial_ref_dec=official_lazy_dec -o $@ $^ $(CPU_LIB)
.PHONY: check-yang
$(BUILD)/kem_wlazy.o: tests/kem_yang_diag.c src/kem_lazy.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -DYANG_INVERSE=ntruplus768_officialopt_invntt_ct_wresident -Dcrypto_kem_keypair=official_wlazy_keypair -Dcrypto_kem_enc=official_wlazy_enc -Dcrypto_kem_dec=official_wlazy_dec -c -o $@ $<
$(BUILD)/bench_yang_wresident: bench/bench_inverse_ct.c tests/support/crypto_declassify.c $(YANG_LINK) $(BUILD)/kem_wlazy.o asm/ntruplus768_officialopt_invntt_ct_wresident.s | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -DCT_R3_COMPARE -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_ct_wresident -Dntruplus768_officialopt_invntt_ct_r3=ntruplus768_officialopt_invntt_yang_factored -Dofficial_ct_dec=official_wlazy_dec -Dofficial_ct_r3_dec=official_yang_dec -o $@ $^ $(CPU_LIB)
$(BUILD)/test_yang_guard: tests/test_yang_guard.c $(YANG_ASM) $(OFFICIAL)/invntt.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -o $@ $^
check-yang: $(BUILD)/test_inverse_yang $(BUILD)/test_kem_yang $(BUILD)/test_yang_guard
	$(BUILD)/test_inverse_yang
	$(BUILD)/test_kem_yang
	$(BUILD)/test_yang_guard

YANG_PAIR32_ASM = asm/ntruplus768_officialopt_invntt_yang_pair32.s
YANG_PAIR32_DEF = -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_yang_pair32 -Dofficial_ct_dec=official_yang_pair32_dec
$(BUILD)/kem_yang_pair32.o: tests/kem_yang_diag.c src/kem_lazy.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -DYANG_INVERSE=ntruplus768_officialopt_invntt_yang_pair32 -Dcrypto_kem_keypair=official_yang_pair32_keypair -Dcrypto_kem_enc=official_yang_pair32_enc -Dcrypto_kem_dec=official_yang_pair32_dec -c -o $@ $<
$(BUILD)/test_inverse_yang_pair32: tests/test_inverse_ct.c $(YANG_PAIR32_ASM) $(OFFICIAL)/invntt.s $(OFFICIAL)/basemul.s $(OFFICIAL)/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) $(YANG_PAIR32_DEF) -o $@ $^
$(BUILD)/test_kem_yang_pair32: tests/test_kem_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_yang_pair32.o $(YANG_PAIR32_ASM) asm/ntruplus768_officialopt_ntt_caller_lazy.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) $(KEM_INCLUDES) $(YANG_PAIR32_DEF) -o $@ $^
$(BUILD)/test_yang_pair32_guard: tests/test_yang_guard.c $(YANG_PAIR32_ASM) $(OFFICIAL)/invntt.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -Dntruplus768_officialopt_invntt_yang_factored=ntruplus768_officialopt_invntt_yang_pair32 -o $@ $^
.PHONY: check-yang-pair32
check-yang-pair32: $(BUILD)/test_inverse_yang_pair32 $(BUILD)/test_kem_yang_pair32 $(BUILD)/test_yang_pair32_guard
	$(BUILD)/test_inverse_yang_pair32
	$(BUILD)/test_kem_yang_pair32
	$(BUILD)/test_yang_pair32_guard

YANG_PAIR32_LINK = $(BUILD)/kem_ref.o $(BUILD)/kem_lazy.o $(BUILD)/kem_yang_pair32.o $(YANG_PAIR32_ASM) asm/ntruplus768_officialopt_ntt_caller_lazy.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o
$(BUILD)/bench_yang_pair32: bench/bench_inverse_ct.c tests/support/crypto_declassify.c $(YANG_PAIR32_LINK) | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) $(YANG_PAIR32_DEF) -Dofficial_ref_dec=official_lazy_dec -o $@ $^ $(CPU_LIB)
$(BUILD)/bench_yang_pair32_factored: bench/bench_inverse_ct.c tests/support/crypto_declassify.c $(YANG_PAIR32_LINK) $(BUILD)/kem_yang.o $(YANG_ASM) | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -DCT_R3_COMPARE -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_yang_factored -Dntruplus768_officialopt_invntt_ct_r3=ntruplus768_officialopt_invntt_yang_pair32 -Dofficial_ct_dec=official_yang_dec -Dofficial_ct_r3_dec=official_yang_pair32_dec -o $@ $^ $(CPU_LIB)

YANG_STAGE5REUSE_ASM = asm/ntruplus768_officialopt_invntt_yang_stage5reuse.s
YANG_STAGE5REUSE_DEF = -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_yang_stage5reuse -Dofficial_ct_dec=official_yang_stage5reuse_dec
$(BUILD)/kem_yang_stage5reuse.o: tests/kem_yang_diag.c src/kem_lazy.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -DYANG_INVERSE=ntruplus768_officialopt_invntt_yang_stage5reuse -Dcrypto_kem_keypair=official_yang_stage5reuse_keypair -Dcrypto_kem_enc=official_yang_stage5reuse_enc -Dcrypto_kem_dec=official_yang_stage5reuse_dec -c -o $@ $<
$(BUILD)/test_inverse_yang_stage5reuse: tests/test_inverse_ct.c $(YANG_STAGE5REUSE_ASM) $(OFFICIAL)/invntt.s $(OFFICIAL)/basemul.s $(OFFICIAL)/crepmod3.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) $(YANG_STAGE5REUSE_DEF) -o $@ $^
$(BUILD)/test_kem_yang_stage5reuse: tests/test_kem_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_yang_stage5reuse.o $(YANG_STAGE5REUSE_ASM) asm/ntruplus768_officialopt_ntt_caller_lazy.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) $(KEM_INCLUDES) $(YANG_STAGE5REUSE_DEF) -o $@ $^
$(BUILD)/test_yang_stage5reuse_guard: tests/test_yang_guard.c $(YANG_STAGE5REUSE_ASM) $(OFFICIAL)/invntt.s $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -Dntruplus768_officialopt_invntt_yang_factored=ntruplus768_officialopt_invntt_yang_stage5reuse -o $@ $^
$(BUILD)/test_yang_stage5reuse_raw: tests/test_yang_stage5reuse_raw.c $(YANG_PAIR32_ASM) $(YANG_STAGE5REUSE_ASM) $(OFFICIAL)/consts.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -o $@ $^
.PHONY: check-yang-stage5reuse
check-yang-stage5reuse: $(BUILD)/test_inverse_yang_stage5reuse $(BUILD)/test_kem_yang_stage5reuse $(BUILD)/test_yang_stage5reuse_guard $(BUILD)/test_yang_stage5reuse_raw
	$(BUILD)/test_inverse_yang_stage5reuse
	$(BUILD)/test_kem_yang_stage5reuse
	$(BUILD)/test_yang_stage5reuse_guard
	$(BUILD)/test_yang_stage5reuse_raw

$(BUILD)/bench_yang_stage5reuse_pair32: bench/bench_inverse_ct.c tests/support/crypto_declassify.c $(YANG_PAIR32_LINK) $(BUILD)/kem_yang_stage5reuse.o $(YANG_STAGE5REUSE_ASM) | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -DCT_R3_COMPARE -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_yang_pair32 -Dntruplus768_officialopt_invntt_ct_r3=ntruplus768_officialopt_invntt_yang_stage5reuse -Dofficial_ct_dec=official_yang_pair32_dec -Dofficial_ct_r3_dec=official_yang_stage5reuse_dec -o $@ $^ $(CPU_LIB)
$(BUILD)/bench_yang_stage5reuse_pair32_reversed: bench/bench_inverse_ct.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_lazy.o $(BUILD)/kem_yang_pair32.o $(BUILD)/kem_yang_stage5reuse.o $(YANG_STAGE5REUSE_ASM) $(YANG_PAIR32_ASM) asm/ntruplus768_officialopt_ntt_caller_lazy.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -DCT_R3_COMPARE -Dntruplus768_officialopt_invntt_ct=ntruplus768_officialopt_invntt_yang_pair32 -Dntruplus768_officialopt_invntt_ct_r3=ntruplus768_officialopt_invntt_yang_stage5reuse -Dofficial_ct_dec=official_yang_pair32_dec -Dofficial_ct_r3_dec=official_yang_stage5reuse_dec -o $@ $^ $(CPU_LIB)

REPO_BENCH = ../../../../../../bench
$(BUILD)/bench_yang_stage5reuse_mlkem_batch: bench/bench_yang_mlkem_batch.c $(REPO_BENCH)/mlkem_batch.c $(REPO_BENCH)/mlkem_batch.h tests/support/crypto_declassify.c $(YANG_PAIR32_LINK) $(BUILD)/kem_yang_stage5reuse.o $(YANG_STAGE5REUSE_ASM) | $(BUILD)
	$(CC) $(CFLAGS) -I$(REPO_BENCH) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -o $@ bench/bench_yang_mlkem_batch.c $(REPO_BENCH)/mlkem_batch.c tests/support/crypto_declassify.c $(YANG_PAIR32_LINK) $(BUILD)/kem_yang_stage5reuse.o $(YANG_STAGE5REUSE_ASM) $(CPU_LIB)
$(BUILD)/bench_yang_stage5reuse_mlkem_batch_reversed: bench/bench_yang_mlkem_batch.c $(REPO_BENCH)/mlkem_batch.c $(REPO_BENCH)/mlkem_batch.h tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_lazy.o $(BUILD)/kem_yang_pair32.o $(BUILD)/kem_yang_stage5reuse.o $(YANG_STAGE5REUSE_ASM) $(YANG_PAIR32_ASM) asm/ntruplus768_officialopt_ntt_caller_lazy.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o | $(BUILD)
	$(CC) $(CFLAGS) -I$(REPO_BENCH) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -o $@ bench/bench_yang_mlkem_batch.c $(REPO_BENCH)/mlkem_batch.c tests/support/crypto_declassify.c $(BUILD)/kem_ref.o $(BUILD)/kem_lazy.o $(BUILD)/kem_yang_pair32.o $(BUILD)/kem_yang_stage5reuse.o $(YANG_STAGE5REUSE_ASM) $(YANG_PAIR32_ASM) asm/ntruplus768_officialopt_ntt_caller_lazy.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o $(CPU_LIB)

# Fixed-layout A/B: separate ELFs use the same public symbol and link order.
# The generated inverse overlays have equal linked symbol size.
YANG_FIXED_COMMON = $(BUILD)/kem_ref.o $(BUILD)/kem_yang_fixed.o asm/ntruplus768_officialopt_ntt_caller_lazy.s $(COMMON_C) $(COMMON_ASM) $(BUILD)/kat_aes.o $(BUILD)/kat_rng.o
$(BUILD)/kem_yang_fixed.o: tests/kem_yang_diag.c src/kem_lazy.c | $(BUILD)
	$(CC) $(CFLAGS) $(KEM_INCLUDES) -DYANG_INVERSE=ntruplus768_officialopt_invntt_yang_fixed -Dcrypto_kem_keypair=official_fixed_keypair -Dcrypto_kem_enc=official_fixed_enc -Dcrypto_kem_dec=official_fixed_dec -c -o $@ $<
$(BUILD)/bench_yang_fixed_control: bench/bench_yang_fixed_image.c $(REPO_BENCH)/mlkem_batch.c $(REPO_BENCH)/mlkem_batch.h tests/support/crypto_declassify.c $(YANG_FIXED_COMMON) asm/yang_fixed_control.s | $(BUILD)
	$(CC) $(CFLAGS) -I$(REPO_BENCH) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -Wl,--build-id=none -o $@ bench/bench_yang_fixed_image.c $(REPO_BENCH)/mlkem_batch.c tests/support/crypto_declassify.c $(YANG_FIXED_COMMON) asm/yang_fixed_control.s $(CPU_LIB)
$(BUILD)/bench_yang_fixed_candidate: bench/bench_yang_fixed_image.c $(REPO_BENCH)/mlkem_batch.c $(REPO_BENCH)/mlkem_batch.h tests/support/crypto_declassify.c $(YANG_FIXED_COMMON) asm/yang_fixed_candidate.s | $(BUILD)
	$(CC) $(CFLAGS) -I$(REPO_BENCH) -I$(OFFICIAL) -I$(KAT) -I$(CPU_INCLUDE) $(KEM_INCLUDES) -Wl,--build-id=none -o $@ bench/bench_yang_fixed_image.c $(REPO_BENCH)/mlkem_batch.c tests/support/crypto_declassify.c $(YANG_FIXED_COMMON) asm/yang_fixed_candidate.s $(CPU_LIB)

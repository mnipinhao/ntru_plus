CC ?= cc
PYTHON ?= python3
CFLAGS ?= -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE -D__STDC_WANT_LIB_EXT1__=1 -I. -DNTRUPLUS1152_ASM_BASEMUL_RINV -DNTRUPLUS1152_ASM_BASEINV_NUM -DNTRUPLUS1152_ASM_BASEINV_FINISH
C_SRC := kem.c symmetric.c fips202.c hash_fixed.c base.c inverse.c \
         pack.c support.c api_glue.c
ASM_SRC := keccakf1600.S basemul_rinv.S baseinv_num.S baseinv_finish.S ntt.S inverse16_tail.S ntt_top.S ntt_tail.S ntt9.S \
           inverse_ntt.S inverse9.S inverse16.S crepmod3_raw.S

TESTS := test_kem test_canonical test_abi test_baseinv_fail

.PHONY: check kat kat-check tests clean shake-prefixed

test_kem: test/test_kem.c randombytes.c $(C_SRC) $(ASM_SRC)
	$(CC) $(CFLAGS) $^ -o $@

PQCgenKAT_kem: kat/PQCgenKAT_kem.c kat/rng.c kat/aes.c $(C_SRC) $(ASM_SRC)
	$(CC) $(CFLAGS) -Ikat $^ -o $@

kat: PQCgenKAT_kem
	./PQCgenKAT_kem

kat-check: kat
	cmp PQCkemKAT_3488.rsp ../../ntruplus-ntt-Optimized/KAT/NTRU+1152/PQCkemKAT_3488.rsp
	shasum -a 256 PQCkemKAT_3488.rsp

test_canonical: test/test_canonical.c randombytes.c $(C_SRC) $(ASM_SRC)
	$(CC) $(CFLAGS) $^ -o $@

test_abi: test/test_abi.c test/abi_sentinel.S randombytes.c $(C_SRC) $(ASM_SRC)
	$(CC) $(CFLAGS) $^ -o $@

test_baseinv_fail: test/test_baseinv_fail.c randombytes.c $(C_SRC) $(ASM_SRC)
	$(CC) $(CFLAGS) $^ -o $@

test_zeroization: test/test_zeroization.c randombytes.c $(C_SRC) $(ASM_SRC)
	$(CC) $(CFLAGS) -DSECURE_CLEAR_AUDIT_HOOK=1 $^ -o $@

tests: $(TESTS) test_zeroization
	@for t in $(TESTS) test_zeroization; do echo "--- $$t"; ./$$t || exit 1; done

check: kat-check tests shake-prefixed

clean:
	$(RM) $(TESTS) test_zeroization PQCgenKAT_kem PQCkemKAT_3488.req PQCkemKAT_3488.rsp
	$(RM) -r *.dSYM

shake-prefixed:
	$(CC) $(CPPFLAGS) $(CFLAGS) -I. -o $(BUILD_DIR)/test_shake_prefixed \
	  test/test_shake_prefixed.c fips202.c keccakf1600.S
	$(BUILD_DIR)/test_shake_prefixed

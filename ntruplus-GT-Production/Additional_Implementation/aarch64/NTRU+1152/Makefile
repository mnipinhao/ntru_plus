CC ?= cc
PYTHON ?= python3
# No -march here on purpose.  NEON is baseline on AArch64, so -march=armv8-a+simd
# added nothing, but it suppresses __ARM_FEATURE_SHA3 -- which is what selects a
# v8.4-A Keccak backend.  NTRU+864 hit exactly that and had to drop the flag
# before its backend became reachable; letting the compiler's default target
# decide matches NTRU+768 and NTRU+864.
#
# -D__STDC_WANT_LIB_EXT1__=1 is gone too: secure_clear.h declares memset_s
# itself now, so the flag no longer changes anything.
CFLAGS ?= -O3 -std=c11 -D_DEFAULT_SOURCE -I. -DNTRUPLUS1152_ASM_BASEMUL_RINV -DNTRUPLUS1152_ASM_BASEINV_NUM -DNTRUPLUS1152_ASM_BASEINV_FINISH
C_SRC := kem.c symmetric.c fips202.c hash_fixed.c base.c inverse.c \
         pack.c support.c api_glue.c
ASM_SRC := keccakf1600.S keccakf1600_v84a.S basemul_rinv.S unpack.S baseinv_num.S baseinv_finish.S ntt.S inverse16_tail.S ntt_top.S ntt_tail.S ntt9.S \
           inverse_ntt.S inverse9.S inverse16.S crepmod3_raw.S

TESTS := test_kem test_canonical test_abi test_baseinv_fail

.PHONY: check kat kat-check tests clean shake-prefixed keccak-v84a
.PHONY: zeroization-source-check check-release manifest-check export-check

# Assembly clearing must be checked statically: the runtime hook in
# test_zeroization only sees clears made through the C primitive.
check-release:
	$(PYTHON) scripts/check_release.py

manifest-check: check-release
	shasum -a 256 -c SOURCE-MANIFEST.sha256

export-check:
	$(PYTHON) scripts/export_supercop.py --self-check

zeroization-source-check:
	$(PYTHON) scripts/check_zeroization.py

test_kem: test/test_kem.c randombytes.c $(C_SRC) $(ASM_SRC)
	$(CC) $(CFLAGS) $^ -o $@

PQCgenKAT_kem: kat/PQCgenKAT_kem.c kat/rng.c kat/aes.c $(C_SRC) $(ASM_SRC)
	$(CC) $(CFLAGS) -Ikat $^ -o $@

kat: PQCgenKAT_kem
	./PQCgenKAT_kem

kat-check: kat
	./PQCgenKAT_kem
	cmp PQCkemKAT_3488.rsp kat/expected/PQCkemKAT_3488.rsp
	cmp PQCkemKAT_3488.req kat/expected/PQCkemKAT_3488.req

test_canonical: test/test_canonical.c randombytes.c $(C_SRC) $(ASM_SRC)
	$(CC) $(CFLAGS) $^ -o $@

test_abi: test/test_abi.c test/abi_sentinel.S randombytes.c $(C_SRC) $(ASM_SRC)
	$(CC) $(CFLAGS) $^ -o $@

test_baseinv_fail: test/test_baseinv_fail.c randombytes.c $(C_SRC) $(ASM_SRC)
	$(CC) $(CFLAGS) $^ -o $@

test_zeroization: test/test_zeroization.c randombytes.c $(C_SRC) $(ASM_SRC)
	$(CC) $(CFLAGS) -DSECURE_CLEAR_AUDIT_HOOK=1 $^ -o $@

tests: zeroization-source-check $(TESTS) test_zeroization
	@for t in $(TESTS) test_zeroization; do echo "--- $$t"; ./$$t || exit 1; done

check: manifest-check tests kat-check export-check

clean:
	$(RM) test_shake_prefixed
	$(RM) $(TESTS) test_zeroization PQCgenKAT_kem PQCkemKAT_3488.req PQCkemKAT_3488.rsp
	$(RM) -r *.dSYM

shake-prefixed:
	$(CC) $(CPPFLAGS) $(CFLAGS) -I. -o test_shake_prefixed \
	  test/test_shake_prefixed.c fips202.c keccakf1600.S keccakf1600_v84a.S
	./test_shake_prefixed

# Reports "skipped" rather than failing where the target has no FEAT_SHA3.
keccak-v84a:
	$(CC) $(CPPFLAGS) $(CFLAGS) -I. -o test_keccak_v84a \
	  test/test_keccak_v84a.c keccakf1600.S keccakf1600_v84a.S
	./test_keccak_v84a

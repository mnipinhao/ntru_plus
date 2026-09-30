CC ?= cc
PYTHON ?= python3
# No -march here on purpose.  NEON is baseline on AArch64, so -march=armv8-a+simd
# would add nothing, but it would suppress __ARM_FEATURE_SHA3 -- which is what
# selects the v8.4-A Keccak backend.  Letting the compiler's default target
# decide matches NTRU+768 and NTRU+864.
CFLAGS ?= -O3 -std=c11 -D_DEFAULT_SOURCE -I.
C_SRC := kem.c symmetric.c fips202.c hash_fixed.c base.c inverse.c \
         pack.c support.c api_glue.c
ASM_SRC := keccakf1600.S keccakf1600_v84a.S keccakf1600_x2_v84a.S basemul_rinv.S unpack.S baseinv_num.S baseinv_finish.S ntt.S inverse16_tail.S ntt_top.S ntt_tail.S ntt9.S \
           inverse_ntt.S inverse9.S inverse16.S crepmod3_raw.S

# Build output stays outside the package (check-release rejects build products
# inside the tree), in a directory named after this package directory's path,
# so that two checkouts or copies never share build products.
BUILD_ROOT ?= /tmp/ntruplus$(subst /,-,$(abspath ..))
BUILD_DIR ?= $(BUILD_ROOT)/$(notdir $(CURDIR))
TESTS := test_kem test_canonical test_abi test_baseinv_fail
TEST_BINS := $(addprefix $(BUILD_DIR)/,$(TESTS) test_zeroization)
KAT_GENERATOR := $(BUILD_DIR)/PQCgenKAT_kem

.PHONY: check kat kat-check tests clean shake-prefixed keccak-v84a
.PHONY: zeroization-source-check check-release manifest-check export-check

$(BUILD_DIR):
	mkdir -p $@

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

$(BUILD_DIR)/test_kem: test/test_kem.c randombytes.c $(C_SRC) $(ASM_SRC) | $(BUILD_DIR)
	$(CC) $(CFLAGS) $^ -o $@

$(KAT_GENERATOR): kat/PQCgenKAT_kem.c kat/rng.c kat/aes.c $(C_SRC) $(ASM_SRC) | $(BUILD_DIR)
	$(CC) $(CFLAGS) -Ikat $^ -o $@

# The generator writes PQCkemKAT_3488.req/.rsp into its working directory.
kat: $(KAT_GENERATOR)
	cd $(BUILD_DIR) && ./PQCgenKAT_kem

kat-check: kat
	cd $(BUILD_DIR) && ./PQCgenKAT_kem
	cmp $(BUILD_DIR)/PQCkemKAT_3488.rsp kat/expected/PQCkemKAT_3488.rsp
	cmp $(BUILD_DIR)/PQCkemKAT_3488.req kat/expected/PQCkemKAT_3488.req

$(BUILD_DIR)/test_canonical: test/test_canonical.c randombytes.c $(C_SRC) $(ASM_SRC) | $(BUILD_DIR)
	$(CC) $(CFLAGS) $^ -o $@

$(BUILD_DIR)/test_abi: test/test_abi.c test/abi_sentinel.S randombytes.c $(C_SRC) $(ASM_SRC) | $(BUILD_DIR)
	$(CC) $(CFLAGS) $^ -o $@

$(BUILD_DIR)/test_baseinv_fail: test/test_baseinv_fail.c randombytes.c $(C_SRC) $(ASM_SRC) | $(BUILD_DIR)
	$(CC) $(CFLAGS) $^ -o $@

$(BUILD_DIR)/test_zeroization: test/test_zeroization.c randombytes.c $(C_SRC) $(ASM_SRC) | $(BUILD_DIR)
	$(CC) $(CFLAGS) -DSECURE_CLEAR_AUDIT_HOOK=1 $^ -o $@

# The tests run from the package directory; the binaries live in BUILD_DIR.
tests: zeroization-source-check $(TEST_BINS)
	@for t in $(TESTS) test_zeroization; do echo "--- $$t"; $(BUILD_DIR)/$$t || exit 1; done

check: manifest-check tests kat-check export-check keccak-v84a shake-prefixed

clean:
	$(RM) $(TEST_BINS) $(KAT_GENERATOR)
	$(RM) $(BUILD_DIR)/PQCkemKAT_3488.req $(BUILD_DIR)/PQCkemKAT_3488.rsp
	$(RM) $(BUILD_DIR)/test_shake_prefixed $(BUILD_DIR)/test_keccak_v84a
	$(RM) -r $(BUILD_DIR)/*.dSYM
	-rmdir $(BUILD_DIR)

shake-prefixed: | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -I. -o $(BUILD_DIR)/test_shake_prefixed \
	  test/test_shake_prefixed.c fips202.c keccakf1600.S keccakf1600_v84a.S keccakf1600_x2_v84a.S
	$(BUILD_DIR)/test_shake_prefixed

# Reports "skipped" rather than failing where the target has no FEAT_SHA3.
keccak-v84a: | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -I. -o $(BUILD_DIR)/test_keccak_v84a \
	  test/test_keccak_v84a.c keccakf1600.S keccakf1600_v84a.S
	$(BUILD_DIR)/test_keccak_v84a

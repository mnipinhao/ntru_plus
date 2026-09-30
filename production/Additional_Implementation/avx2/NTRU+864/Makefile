# Tested with GCC 15.2.0 (Ubuntu) as `cc`; any C11 compiler that accepts the GNU
# assembler syntax, <immintrin.h> and the flags below may work, untested.
PYTHON ?= python3

# Build output stays outside the package (check-release rejects build products
# inside the tree), in a directory named after this package directory's path,
# so that two checkouts or copies never share build products.
BUILD_ROOT ?= /tmp/ntruplus$(subst /,-,$(abspath ..))
BUILD_DIR ?= $(BUILD_ROOT)/$(notdir $(CURDIR))
OBJ_DIR := $(BUILD_DIR)/obj
AUDIT_DIR := $(BUILD_DIR)/audit
SAN_DIR := $(BUILD_DIR)/sanitize

CPPFLAGS := -I.
# Build contract: docs/IMPLEMENTATION.md, section 10 (why -O3 and -mbmi -mbmi2:
# mlkem-native's C Keccak; the assembly needs only AVX2; no -march is set).
# `override` keeps the required flags when CFLAGS is given on the command line
# (for example `make CFLAGS="-O3 -g"`).
CFLAGS ?= -O3
override CFLAGS += -mavx2 -mbmi -mbmi2 -std=c11 -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wshadow
override CFLAGS += -ffunction-sections -fdata-sections
override LDFLAGS += -Wl,--gc-sections
KAT_CFLAGS := $(filter-out -Wpedantic -Wmissing-prototypes -Wshadow,$(CFLAGS)) -Wno-unused-result \
	-Wno-sign-compare -Wno-unused-parameter
SANFLAGS ?= -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined \
	-fno-sanitize-recover=all
SAN_ENV := ASAN_OPTIONS=detect_leaks=1 UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1

# The KEM source closure (exported to SUPERCOP by scripts/export_supercop.py).
KEM_C := kem.c symmetric.c consts.c baseinv.c sotp_decode.c fips202.c keccakf1600.c
KEM_ASM := add.s cbd.s baseinv_1.s basemul_scale.s basemul_montgomery.s basemul_shoup.s \
	ntt.s invntt_crepmod3.s pack.s
KEM_HEADERS := api.h abi.h params.h poly.h consts.h symmetric.h util.h fips202.h \
	keccakf1600.h mlkem_native_config.h
KEM_LICENSES := LICENSE LICENSE.mlkem-native

# The assembly objects are the same in every build; the audit and sanitizer
# builds recompile only the C.
ASM_OBJECTS := $(addprefix $(OBJ_DIR)/,$(KEM_ASM:.s=.o))
KEM_OBJECTS := $(addprefix $(OBJ_DIR)/,$(KEM_C:.c=.o)) $(ASM_OBJECTS)
AUDIT_OBJECTS := $(addprefix $(AUDIT_DIR)/,$(KEM_C:.c=.o)) $(ASM_OBJECTS)
SAN_OBJECTS := $(addprefix $(SAN_DIR)/,$(KEM_C:.c=.o)) $(ASM_OBJECTS)
SHAKE_OBJECTS := $(addprefix $(OBJ_DIR)/,symmetric.o fips202.o keccakf1600.o)

TEST_KEM := $(BUILD_DIR)/test_kem
TEST_ABI := $(BUILD_DIR)/test_abi
TEST_CANONICAL := $(BUILD_DIR)/test_canonical
TEST_ZEROIZATION := $(BUILD_DIR)/test_zeroization
TEST_SHAKE_PREFIXED := $(BUILD_DIR)/test_shake_prefixed
KAT_GENERATOR := $(BUILD_DIR)/PQCgenKAT_kem

KAT_REQ := kat/expected/PQCkemKAT_2624.req
KAT_RSP := kat/expected/PQCkemKAT_2624.rsp
GENERATED_KAT_REQ := $(BUILD_DIR)/PQCkemKAT_2624.req
GENERATED_KAT_RSP := $(BUILD_DIR)/PQCkemKAT_2624.rsp

.PHONY: all check check-release manifest-check test abi canonical zeroization
.PHONY: zeroization-source-check kat kat-check shake-prefixed size symbols
.PHONY: symbols-check export-check keccak-check sanitize clean

all: $(TEST_KEM)

$(OBJ_DIR) $(AUDIT_DIR) $(SAN_DIR):
	mkdir -p $@

$(OBJ_DIR)/%.o: %.c $(KEM_HEADERS) Makefile | $(OBJ_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@
$(OBJ_DIR)/%.o: %.s Makefile | $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(AUDIT_DIR)/%.o: %.c $(KEM_HEADERS) Makefile | $(AUDIT_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -DNTRUPLUS_SECURE_CLEAR_AUDIT_HOOK -c $< -o $@
$(SAN_DIR)/%.o: %.c $(KEM_HEADERS) Makefile | $(SAN_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(SANFLAGS) -c $< -o $@
# kem.c is the only KEM source that includes randombytes.h (not a KEM header:
# SUPERCOP and applications supply randombytes).
$(OBJ_DIR)/kem.o $(AUDIT_DIR)/kem.o $(SAN_DIR)/kem.o: randombytes.h

# The test and KAT programs compile their .c sources and link the objects.
LINK_INPUTS = $(filter %.c %.S %.o,$^)
$(TEST_KEM): test/test_kem.c randombytes.c randombytes.h $(KEM_OBJECTS)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(LINK_INPUTS) $(LDFLAGS) -o $@
$(TEST_ABI): test/test_abi.c test/abi_sentinel.S randombytes.c randombytes.h $(KEM_OBJECTS)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(LINK_INPUTS) $(LDFLAGS) -o $@
$(TEST_CANONICAL): test/test_canonical.c randombytes.c randombytes.h $(KEM_OBJECTS)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(LINK_INPUTS) $(LDFLAGS) -o $@
$(TEST_ZEROIZATION): test/test_zeroization.c randombytes.c randombytes.h $(AUDIT_OBJECTS)
	$(CC) $(CPPFLAGS) $(CFLAGS) -DNTRUPLUS_SECURE_CLEAR_AUDIT_HOOK $(LINK_INPUTS) $(LDFLAGS) -o $@
$(TEST_SHAKE_PREFIXED): test/test_shake_prefixed.c $(SHAKE_OBJECTS)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(LINK_INPUTS) $(LDFLAGS) -o $@
$(KAT_GENERATOR): kat/PQCgenKAT_kem.c kat/rng.c kat/aes.c $(KEM_OBJECTS)
	$(CC) $(CPPFLAGS) -Ikat $(KAT_CFLAGS) $(LINK_INPUTS) $(LDFLAGS) -o $@

check-release:
	$(PYTHON) scripts/check_release.py

manifest-check: check-release
	shasum -a 256 -c --quiet SOURCE-MANIFEST.sha256
	@echo "manifest-check: $$(wc -l < SOURCE-MANIFEST.sha256) files match SOURCE-MANIFEST.sha256"

test: $(TEST_KEM) $(TEST_ABI)
	$(TEST_KEM)
	$(TEST_ABI)

abi: $(TEST_ABI)
	$(TEST_ABI)

canonical: $(TEST_CANONICAL)
	$(TEST_CANONICAL)

zeroization-source-check:
	$(PYTHON) scripts/check_zeroization.py

zeroization: zeroization-source-check $(TEST_ZEROIZATION)
	$(TEST_ZEROIZATION)

kat: $(KAT_GENERATOR)
	cd $(BUILD_DIR) && ./PQCgenKAT_kem

kat-check: kat $(KAT_REQ) $(KAT_RSP)
	cmp $(GENERATED_KAT_REQ) $(KAT_REQ)
	cmp $(GENERATED_KAT_RSP) $(KAT_RSP)
	shasum -a 256 $(GENERATED_KAT_RSP)

shake-prefixed: $(TEST_SHAKE_PREFIXED)
	$(TEST_SHAKE_PREFIXED)

# The KEM objects define exactly the three NIST entry points (crypto_kem_keypair,
# crypto_kem_enc, crypto_kem_dec) under their plain names, every other global
# symbol carries the package prefix, and nothing outside the documented
# externals is imported.
symbols-check: $(KEM_OBJECTS)
	$(PYTHON) scripts/check_release.py --objects $(KEM_OBJECTS)

# The SUPERCOP export is deterministic and its source list equals the
# manifest's KEM closure.
export-check:
	$(PYTHON) scripts/export_supercop.py --self-check

# The vendored mlkem-native Keccak equals upstream minus the recorded removals
# plus the recorded include rewrites, and the sibling packages' copies.  With
# MLKEM_NATIVE=<mlkem-native checkout at b3ba7b32>, the removed
# ranges are also checked against upstream's text.
keccak-check:
	$(PYTHON) scripts/check_release.py --keccak $(if $(MLKEM_NATIVE),--upstream $(MLKEM_NATIVE))

check: manifest-check test canonical zeroization kat-check shake-prefixed \
	symbols-check export-check keccak-check

# ASan + UBSan + LSan build of test_kem, test_canonical, test_shake_prefixed
# and the KAT; test_abi and test_zeroization are not part of it.  Not part of
# check: it needs the sanitizer runtimes.
sanitize: $(SAN_OBJECTS) | $(SAN_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(SANFLAGS) test/test_kem.c randombytes.c $(SAN_OBJECTS) -o $(SAN_DIR)/test_kem
	$(CC) $(CPPFLAGS) $(CFLAGS) $(SANFLAGS) test/test_canonical.c randombytes.c $(SAN_OBJECTS) -o $(SAN_DIR)/test_canonical
	$(CC) $(CPPFLAGS) $(CFLAGS) $(SANFLAGS) test/test_shake_prefixed.c $(addprefix $(SAN_DIR)/,symmetric.o fips202.o keccakf1600.o) -o $(SAN_DIR)/test_shake_prefixed
	$(CC) $(CPPFLAGS) -Ikat $(KAT_CFLAGS) $(SANFLAGS) kat/PQCgenKAT_kem.c kat/rng.c kat/aes.c $(SAN_OBJECTS) -o $(SAN_DIR)/PQCgenKAT_kem
	$(SAN_ENV) $(SAN_DIR)/test_kem
	$(SAN_ENV) $(SAN_DIR)/test_canonical
	$(SAN_ENV) $(SAN_DIR)/test_shake_prefixed
	cd $(SAN_DIR) && $(SAN_ENV) ./PQCgenKAT_kem
	cmp $(SAN_DIR)/PQCkemKAT_2624.rsp $(KAT_RSP)
	@echo "sanitize: ASan+UBSan+LSan tests and KAT pass"

size: $(KEM_OBJECTS) $(TEST_KEM)
	size $(KEM_OBJECTS)
	size $(TEST_KEM)

symbols: $(KEM_OBJECTS)
	nm -g --defined-only $(KEM_OBJECTS)

clean:
	$(RM) -r $(OBJ_DIR) $(AUDIT_DIR) $(SAN_DIR)
	$(RM) $(TEST_KEM) $(TEST_ABI) $(TEST_CANONICAL) $(TEST_ZEROIZATION)
	$(RM) $(TEST_SHAKE_PREFIXED) $(KAT_GENERATOR)
	$(RM) $(GENERATED_KAT_REQ) $(GENERATED_KAT_RSP)
	-rmdir $(BUILD_DIR)

CC ?= gcc
PYTHON ?= python3
RM ?= rm -f
UNAME_S := $(shell uname -s)

BUILD_ROOT ?= /tmp/ntruplus-gt-production
BUILD_DIR ?= $(BUILD_ROOT)/NTRU+768
TEST_KEM := $(BUILD_DIR)/test_kem
TEST_ABI := $(BUILD_DIR)/test_abi
TEST_ZEROIZATION := $(BUILD_DIR)/test_zeroization
TEST_CANONICAL := $(BUILD_DIR)/test_canonical
TEST_NTT_SMALL := $(BUILD_DIR)/test_ntt_small
TEST_SUPPORT := $(BUILD_DIR)/test_support
KAT_GENERATOR := $(BUILD_DIR)/PQCgenKAT_kem

CPPFLAGS := -I.
CFLAGS ?= -O3 -fomit-frame-pointer
CFLAGS += -std=c99 -Wall -Wextra -Wpedantic
CFLAGS += -ffunction-sections -fdata-sections

ifeq ($(UNAME_S),Darwin)
LDFLAGS += -Wl,-dead_strip
NM_GLOBAL_FLAGS := -gU
SIZE_FLAGS := -m
else
LDFLAGS += -Wl,--gc-sections
NM_GLOBAL_FLAGS := -g --defined-only
SIZE_FLAGS :=
endif

PUBLIC_ASM := \
	ntt.S \
	base.S \
	pack.S \
	cbd.S \
	crepmod3.S \
	kem_api.S

INTERNAL_ASM := \
	add.S

INTERNAL_C := \
	keygen.c \
	keygen_lambda.c \
	basemul_lambda.c

KEM_SOURCES := \
	kem.c \
	symmetric.c \
	fips202.c \
	$(INTERNAL_C) \
	$(PUBLIC_ASM) \
	$(INTERNAL_ASM)

KAT_REQ := kat/expected/PQCkemKAT_2336.req
KAT_RSP := kat/expected/PQCkemKAT_2336.rsp
GENERATED_KAT_REQ := $(BUILD_DIR)/PQCkemKAT_2336.req
GENERATED_KAT_RSP := $(BUILD_DIR)/PQCkemKAT_2336.rsp

.PHONY: all check check-release manifest-check test abi canonical zeroization
.PHONY: zeroization-source-check kat kat-check size symbols clean

all: $(TEST_KEM)

$(BUILD_DIR):
	mkdir -p $@

$(TEST_KEM): test/test.c randombytes.c $(KEM_SOURCES) | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ $(LDFLAGS) -o $@

$(TEST_ABI): test/test_abi.c test/abi_sentinel.S test/legacy/verify.c test/legacy/verify.S test/legacy/support.S randombytes.c $(KEM_SOURCES) | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ $(LDFLAGS) -o $@

$(TEST_ZEROIZATION): test/test_zeroization.c randombytes.c $(KEM_SOURCES) | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -DGT_SECURE_CLEAR_AUDIT_HOOK=1 \
		$^ $(LDFLAGS) -o $@

$(TEST_CANONICAL): test/test_canonical.c randombytes.c $(KEM_SOURCES) | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ $(LDFLAGS) -o $@

$(TEST_NTT_SMALL): test/test_ntt_small.c randombytes.c $(KEM_SOURCES) | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ $(LDFLAGS) -o $@

.PHONY: small
small: check-release $(TEST_NTT_SMALL)
	$(TEST_NTT_SMALL)

$(KAT_GENERATOR): kat/PQCgenKAT_kem.c kat/rng.c kat/aes.c $(KEM_SOURCES) | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ $(LDFLAGS) -o $@

check-release:
	$(PYTHON) scripts/check_release.py

manifest-check: check-release
	shasum -a 256 -c SOURCE-MANIFEST.sha256

test: check-release $(TEST_KEM) $(TEST_ABI)
	$(TEST_KEM)
	$(TEST_ABI)

$(TEST_SUPPORT): test/test_support.c $(KEM_SOURCES) randombytes.c | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ $(LDFLAGS) -o $@

.PHONY: support-check
support-check: $(TEST_SUPPORT)
	$(TEST_SUPPORT)

check: support-check

abi: check-release $(TEST_ABI)
	$(TEST_ABI)

canonical: check-release $(TEST_CANONICAL)
	$(TEST_CANONICAL)

zeroization-source-check:
	$(PYTHON) scripts/check_zeroization.py

zeroization: zeroization-source-check $(TEST_ZEROIZATION)
	$(TEST_ZEROIZATION)

kat: check-release $(KAT_GENERATOR)
	cd $(BUILD_DIR) && ./PQCgenKAT_kem

kat-check: kat $(KAT_REQ) $(KAT_RSP)
	cmp $(GENERATED_KAT_REQ) $(KAT_REQ)
	cmp $(GENERATED_KAT_RSP) $(KAT_RSP)
	shasum -a 256 $(GENERATED_KAT_RSP)

check: manifest-check test canonical small zeroization kat-check

size: $(TEST_KEM)
	size $(SIZE_FLAGS) $(TEST_KEM)

symbols: $(TEST_KEM)
	nm $(NM_GLOBAL_FLAGS) $(TEST_KEM)

clean:
	$(RM) $(TEST_NTT_SMALL) $(TEST_SUPPORT)
	$(RM) $(TEST_KEM) $(TEST_ABI) $(TEST_ZEROIZATION) $(TEST_CANONICAL)
	$(RM) $(KAT_GENERATOR)
	$(RM) $(GENERATED_KAT_REQ) $(GENERATED_KAT_RSP)
	-rmdir $(BUILD_DIR)

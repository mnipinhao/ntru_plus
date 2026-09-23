CC ?= gcc
PYTHON ?= python3
RM ?= rm -f

BUILD_ROOT ?= /tmp/ntruplus-production
BUILD_DIR ?= $(BUILD_ROOT)/NTRU+864
TEST_KEM := $(BUILD_DIR)/test_kem
TEST_ABI := $(BUILD_DIR)/test_abi
TEST_CANONICAL := $(BUILD_DIR)/test_canonical
TEST_BASEINV_FAIL := $(BUILD_DIR)/test_baseinv_fail
TEST_ZEROIZATION := $(BUILD_DIR)/test_zeroization
TEST_KECCAK_V84A := $(BUILD_DIR)/test_keccak_v84a
TEST_SHAKE_PREFIXED := $(BUILD_DIR)/test_shake_prefixed
KAT_GENERATOR := $(BUILD_DIR)/PQCgenKAT_kem
SHARED_LIBRARY := $(BUILD_DIR)/libntruplus.so

CPPFLAGS := -I.
CFLAGS ?= -O3
# No -march here on purpose: NEON is baseline on AArch64, so the old
# -march=armv8-a+simd added nothing but did suppress __ARM_FEATURE_SHA3, which
# is what selects keccakf1600_v84a.S.  Letting the compiler's default target
# decide matches NTRU+768 and gives SHA3 on hosts that have it (Apple silicon)
# and the scalar backend on hosts that do not (Raspberry Pi 5).
CFLAGS += -std=c11 -D_DEFAULT_SOURCE
CFLAGS += -ffunction-sections -fdata-sections
# macOS ld spells dead-code elimination differently and rejects --gc-sections.
# Same split NTRU+768 uses.
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
LDFLAGS += -Wl,-dead_strip
else
LDFLAGS += -Wl,--gc-sections
endif

# keccakf1600_v84a.S is compiled unconditionally: the file guards itself on the
# compiler's own __ARM_FEATURE_SHA3, so it is empty on targets without FEAT_SHA3
# and no build-system probing is needed.  NTRU+768 uses the same arrangement.
# The compiler's default target is what decides: Apple clang defaults to an
# Apple core and gets SHA3 with no flags at all, while the Pi 5's gcc defaults
# to generic armv8-a and gets the scalar backend.  To force it, use
# -mcpu=<core> or -march=<arch>+sha3; note that -march=native does NOT define
# __ARM_FEATURE_SHA3 under Apple clang (measured), so do not rely on it.

HEADERS := $(wildcard *.h)
KEM_OBJECTS := \
	$(BUILD_DIR)/symmetric.o \
	$(BUILD_DIR)/fips202.o \
	$(BUILD_DIR)/ntt_api.o \
	$(BUILD_DIR)/base.o \
	$(BUILD_DIR)/add.o \
	$(BUILD_DIR)/crepmod3.o \
	$(BUILD_DIR)/cbd.o \
	$(BUILD_DIR)/ntt.o \
	$(BUILD_DIR)/ntt9.o \
	$(BUILD_DIR)/ntt_top.o \
	$(BUILD_DIR)/unpack.o \
	$(BUILD_DIR)/unpack_api.o \
	$(BUILD_DIR)/kem.o \
	$(BUILD_DIR)/ntt_tail.o \
	$(BUILD_DIR)/pack.o \
	$(BUILD_DIR)/inverse_api.o \
	$(BUILD_DIR)/inverse.o \
	$(BUILD_DIR)/baseinv_num.o \
	$(BUILD_DIR)/baseinv_prefix.o \
	$(BUILD_DIR)/baseinv_inverse.o \
	$(BUILD_DIR)/baseinv_recover.o \
	$(BUILD_DIR)/baseinv_finish.o \
	$(BUILD_DIR)/inverse16_paired.o \
	$(BUILD_DIR)/inverse_tail_direct.o \
	$(BUILD_DIR)/inverse_route.o \
	$(BUILD_DIR)/crepmod3_raw.o \
	$(BUILD_DIR)/basemul_rinv.o \
	$(BUILD_DIR)/inverse9.o \
	$(BUILD_DIR)/support_abi.o \
	$(BUILD_DIR)/hash_fixed.o \
	$(BUILD_DIR)/keccakf1600.o \
	$(BUILD_DIR)/keccakf1600_v84a.o
KAT_REQ := kat/expected/PQCkemKAT_2624.req
KAT_RSP := kat/expected/PQCkemKAT_2624.rsp
GENERATED_KAT_REQ := $(BUILD_DIR)/PQCkemKAT_2624.req
GENERATED_KAT_RSP := $(BUILD_DIR)/PQCkemKAT_2624.rsp

.PHONY: all check check-release manifest-check test abi canonical zeroization
.PHONY: zeroization-source-check kat kat-check shared export-check clean keccak-v84a shake-prefixed

all: $(TEST_KEM)

$(BUILD_DIR):
	mkdir -p $@

$(BUILD_DIR)/%.o: %.c $(HEADERS) Makefile | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -fPIC -c $< -o $@

$(BUILD_DIR)/%.o: %.S $(HEADERS) Makefile | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -fPIC -c $< -o $@


$(TEST_KEM): test/test_kem.c randombytes.c $(KEM_OBJECTS) | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ $(LDFLAGS) -o $@

$(TEST_ABI): test/test_abi.c test/abi_sentinel.S randombytes.c $(KEM_OBJECTS) | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ $(LDFLAGS) -o $@

$(TEST_BASEINV_FAIL): test/test_baseinv_fail.c randombytes.c $(KEM_OBJECTS) | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ $(LDFLAGS) -o $@

$(TEST_CANONICAL): test/test_canonical.c randombytes.c $(KEM_OBJECTS) | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ $(LDFLAGS) -o $@

$(BUILD_DIR)/kem_audit.o: kem.c $(HEADERS) Makefile | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -fPIC -DSECURE_CLEAR_AUDIT_HOOK=1 -c $< -o $@

$(BUILD_DIR)/symmetric_audit.o: symmetric.c $(HEADERS) Makefile | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -fPIC -DSECURE_CLEAR_AUDIT_HOOK=1 -c $< -o $@

AUDIT_OBJECTS := $(filter-out $(BUILD_DIR)/kem.o $(BUILD_DIR)/symmetric.o,$(KEM_OBJECTS))
AUDIT_OBJECTS += $(BUILD_DIR)/kem_audit.o $(BUILD_DIR)/symmetric_audit.o

$(TEST_ZEROIZATION): test/test_zeroization.c randombytes.c $(AUDIT_OBJECTS) | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -DSECURE_CLEAR_AUDIT_HOOK=1 $^ $(LDFLAGS) -o $@

$(KAT_GENERATOR): kat/PQCgenKAT_kem.c kat/rng.c kat/aes.c $(KEM_OBJECTS) | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -Ikat $^ $(LDFLAGS) -o $@

$(SHARED_LIBRARY): $(KEM_OBJECTS) | $(BUILD_DIR)
	$(CC) -shared -Wl,-Bsymbolic $^ $(LDFLAGS) -o $@

check-release:
	$(PYTHON) scripts/check_release.py

manifest-check: check-release
	shasum -a 256 -c SOURCE-MANIFEST.sha256

test: check-release $(TEST_KEM) $(TEST_ABI) $(TEST_BASEINV_FAIL)
	$(TEST_KEM)
	$(TEST_ABI)
	$(TEST_BASEINV_FAIL)

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

$(TEST_KECCAK_V84A): test/test_keccak_v84a.c keccakf1600.S keccakf1600_v84a.S | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ -o $@

# Reports "skipped" rather than failing where the target has no FEAT_SHA3.
keccak-v84a: $(TEST_KECCAK_V84A)
	$(TEST_KECCAK_V84A)

$(TEST_SHAKE_PREFIXED): test/test_shake_prefixed.c fips202.c keccakf1600.S \
  keccakf1600_v84a.S | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ -o $@

shake-prefixed: $(TEST_SHAKE_PREFIXED)
	$(TEST_SHAKE_PREFIXED)

shared: $(SHARED_LIBRARY)

export-check:
	$(PYTHON) scripts/export_supercop.py --self-check

check: manifest-check test canonical zeroization kat-check export-check \
  keccak-v84a shake-prefixed

clean:
	$(RM) $(TEST_KEM) $(TEST_ABI) $(TEST_CANONICAL) $(TEST_ZEROIZATION)
	$(RM) $(KAT_GENERATOR) $(GENERATED_KAT_REQ) $(GENERATED_KAT_RSP)
	$(RM) $(SHARED_LIBRARY)
	$(RM) $(KEM_OBJECTS) $(BUILD_DIR)/kem_audit.o $(BUILD_DIR)/symmetric_audit.o
	-rmdir $(BUILD_DIR)

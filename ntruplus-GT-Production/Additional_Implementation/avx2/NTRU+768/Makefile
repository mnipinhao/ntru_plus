CC ?= gcc
BUILD_DIR ?= build

COMMON_FLAGS = -Wall -Wextra -Wpedantic -Wmissing-prototypes \
	-Wredundant-decls -Wshadow -Wpointer-arith -mavx2 -mbmi2 \
	-mpopcnt -maes -march=native -mtune=native -O3 -fomit-frame-pointer \
	-ffunction-sections -fdata-sections
CFLAGS += $(COMMON_FLAGS)
NISTFLAGS += $(COMMON_FLAGS) -Wno-unused-result
LDFLAGS += -Wl,--gc-sections \
	-Wl,--undefined=ntruplus768_pack_m_highrange12699_avx2 \
	-Wl,-T,e0v-tail.ld

C_SOURCES_BEFORE_ENCAP = baseinv.c consts.c decap.c
C_SOURCES_AFTER_ENCAP = fips202.c kem.c keygen.c poly.c symmetric.c
ASM_SOURCES = \
	add.s basemul.s batch_inverse.s cbd.s crepmod3.s invntt.s ntt.s \
	ntt_m.s ntt_p.s pack.s rhash.s KeccakP-1600-AVX2.s
# encap-slot-pad.s is deliberately adjacent to encap.c: both fragments use
# the same input section, preserving the qualified 611-byte caller slot.
SOURCES = $(C_SOURCES_BEFORE_ENCAP) encap.c encap-slot-pad.s \
	$(C_SOURCES_AFTER_ENCAP) $(ASM_SOURCES)
HEADERS = e0v-tail.ld \
	KeccakP-1600-SnP.h api.h baseinv.h basemul.h consts.h fips202.h \
	internal.h ntt.h ntt_bounds.h params.h poly.h symmetric.h util.h

# The test and KAT harness are vendored from the Official NTRU+ AVX2 tree so
# that this release package validates without linking to another source tree.
TEST_SOURCE = test/test.c
TEST_HEADER = test/counter.h
RANDOMBYTES_SOURCE = randombytes.c
RANDOMBYTES_HEADER = randombytes.h
KAT_SOURCES = kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c
KAT_HEADERS = kat/aes.h kat/rng.h
KAT_EXPECTED_REQ = kat/expected/PQCkemKAT_2336.req
KAT_EXPECTED_RSP = kat/expected/PQCkemKAT_2336.rsp
GENERATED_KAT_REQ = $(BUILD_DIR)/PQCkemKAT_2336.req
GENERATED_KAT_RSP = $(BUILD_DIR)/PQCkemKAT_2336.rsp

.PHONY: all check test test-run PQCgenKAT_kem kat-run kat-check check-hashes \
	qualified-supercop clean

all: test PQCgenKAT_kem

check: check-hashes test-run kat-check

test: $(BUILD_DIR)/test

$(BUILD_DIR)/test: $(HEADERS) $(SOURCES) $(RANDOMBYTES_HEADER) \
		$(RANDOMBYTES_SOURCE) $(TEST_SOURCE) $(TEST_HEADER)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(LDFLAGS) -I. -Itest -o $@ \
		$(RANDOMBYTES_SOURCE) $(TEST_SOURCE) $(SOURCES)

test-run: $(BUILD_DIR)/test
	$(BUILD_DIR)/test

PQCgenKAT_kem: $(BUILD_DIR)/PQCgenKAT_kem

$(BUILD_DIR)/PQCgenKAT_kem: $(HEADERS) $(SOURCES) $(KAT_HEADERS) $(KAT_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(NISTFLAGS) $(LDFLAGS) -I. -Ikat -o $@ \
		$(KAT_SOURCES) $(SOURCES)

kat-run: $(BUILD_DIR)/PQCgenKAT_kem
	cd $(BUILD_DIR) && ./PQCgenKAT_kem

kat-check: kat-run $(KAT_EXPECTED_REQ) $(KAT_EXPECTED_RSP)
	cmp $(GENERATED_KAT_REQ) $(KAT_EXPECTED_REQ)
	cmp $(GENERATED_KAT_RSP) $(KAT_EXPECTED_RSP)

check-hashes:
	sha256sum -c SHA256SUMS

qualified-supercop:
	@test -n "$(SUPERCOP_ROOT)" || \
		(echo "set SUPERCOP_ROOT to a prepared SUPERcop tree" >&2; exit 64)
	python3 qualified/build-supercop.py --supercop-root "$(SUPERCOP_ROOT)"

clean:
	$(RM) -r $(BUILD_DIR) qualified/build

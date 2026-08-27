CC ?= gcc
OFFICIAL_ROOT ?= ../../../../third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768
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
	ntt_m.s ntt_p.s pack.s KeccakP-1600-AVX2.s
# encap-slot-pad.s is deliberately adjacent to encap.c: both fragments use
# the same input section, preserving the qualified 611-byte caller slot.
SOURCES = $(C_SOURCES_BEFORE_ENCAP) encap.c encap-slot-pad.s \
	$(C_SOURCES_AFTER_ENCAP) $(ASM_SOURCES)
HEADERS = e0v-tail.ld \
	KeccakP-1600-SnP.h api.h baseinv.h basemul.h consts.h fips202.h \
	internal.h ntt.h ntt_bounds.h params.h poly.h symmetric.h util.h

TEST_SOURCE = $(OFFICIAL_ROOT)/test/test.c
RANDOMBYTES_SOURCE = $(OFFICIAL_ROOT)/randombytes.c
RANDOMBYTES_HEADER = $(OFFICIAL_ROOT)/randombytes.h
KAT_SOURCES = \
	$(OFFICIAL_ROOT)/kat/PQCgenKAT_kem.c \
	$(OFFICIAL_ROOT)/kat/aes.c \
	$(OFFICIAL_ROOT)/kat/rng.c
KAT_HEADERS = $(OFFICIAL_ROOT)/kat/aes.h $(OFFICIAL_ROOT)/kat/rng.h

.PHONY: all check test test-run PQCgenKAT_kem kat-run check-hashes \
	qualified-supercop clean

all: test PQCgenKAT_kem

check: check-hashes test-run kat-run

test: $(BUILD_DIR)/test

$(BUILD_DIR)/test: $(HEADERS) $(SOURCES) $(RANDOMBYTES_HEADER) \
		$(RANDOMBYTES_SOURCE) $(TEST_SOURCE)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(LDFLAGS) -I. -I$(OFFICIAL_ROOT) -o $@ \
		$(RANDOMBYTES_SOURCE) $(TEST_SOURCE) $(SOURCES)

test-run: $(BUILD_DIR)/test
	$(BUILD_DIR)/test

PQCgenKAT_kem: $(BUILD_DIR)/PQCgenKAT_kem

$(BUILD_DIR)/PQCgenKAT_kem: $(HEADERS) $(SOURCES) $(KAT_HEADERS) $(KAT_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(NISTFLAGS) $(LDFLAGS) -I. -I$(OFFICIAL_ROOT) -o $@ \
		$(KAT_SOURCES) $(SOURCES)

kat-run: $(BUILD_DIR)/PQCgenKAT_kem
	cd $(BUILD_DIR) && ./PQCgenKAT_kem

check-hashes:
	sha256sum -c SHA256SUMS

qualified-supercop:
	@test -n "$(SUPERCOP_ROOT)" || \
		(echo "set SUPERCOP_ROOT to a prepared SUPERcop tree" >&2; exit 64)
	python3 qualified/build-supercop.py --supercop-root "$(SUPERCOP_ROOT)"

clean:
	$(RM) -r $(BUILD_DIR) qualified/build

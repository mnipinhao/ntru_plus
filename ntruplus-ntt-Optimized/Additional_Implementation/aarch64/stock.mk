# Shared stock AArch64 build used by parameter sets that do not use the
# NTRU+768 Good-Thomas production topology.

CC ?= gcc
CPPFLAGS += -D_DEFAULT_SOURCE
CFLAGS += -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls \
  -Wshadow -Wpointer-arith -O3 -fomit-frame-pointer
NISTFLAGS += -Wno-unused-result -O3 -fomit-frame-pointer
RM ?= /bin/rm -f

BUILD_DIR ?= build

SOURCES = ../common/kem.c symmetric.c poly.c \
  asm/add.s asm/ntt.s asm/base.s asm/crepmod3.s asm/pack.s asm/cbd.s
HEADERS = api.h params.h poly.h symmetric.h

HAS_SHAKE256_ASM ?= 1

ifeq ($(HAS_SHAKE256_ASM),1)
SOURCES += CE/fips202.c CE/f1600.S
HEADERS += CE/fips202.h
CPPFLAGS += -DSUPPORTS_SHAKE256_ASM
else
SOURCES += NO_CE/fips202.c
HEADERS += NO_CE/fips202.h
endif

.PHONY: all PQCgenKAT_kem test run-test check check-production-boundary clean

all: test PQCgenKAT_kem

check-production-boundary:
	python3 ../scripts/check_neon_lanes.py --production .

PQCgenKAT_kem: check-production-boundary $(HEADERS) kat/aes.h kat/rng.h $(SOURCES) \
  kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(NISTFLAGS) -I. -o $(BUILD_DIR)/PQCgenKAT_kem \
	  kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c $(SOURCES)

test: check-production-boundary $(HEADERS) randombytes.h $(SOURCES) randombytes.c test/test.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -I. -o $(BUILD_DIR)/test \
	  randombytes.c test/test.c $(SOURCES)

run-test check: test
	./$(BUILD_DIR)/test

clean:
	$(RM) PQCkemKAT_*.req PQCkemKAT_*.rsp
	$(RM) -r $(BUILD_DIR)

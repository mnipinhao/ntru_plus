CC =gcc
PYTHON ?= python3
CFLAGS += -Wall -Wextra -Wpedantic -Wmissing-prototypes -Wredundant-decls \
  -Wshadow -Wpointer-arith -O3 -fomit-frame-pointer
NISTFLAGS += -Wno-unused-result -O3 -fomit-frame-pointer
RM = /bin/rm -f

SOURCES= kem.c symmetric.c poly.c asm/add.s asm/ntt.s asm/base.s asm/crepmod3.s asm/pack.s asm/cbd.s
HEADERS= api.h params.h poly.h symmetric.h


HAS_SHAKE256_ASM := 1

ifeq ($(HAS_SHAKE256_ASM), 1)
	SOURCES+=CE/fips202.c CE/f1600.S
	HEADERS+=CE/fips202.h
	CFLAGS += -DSUPPORTS_SHAKE256_ASM
else
	SOURCES+=NO_CE/fips202.c
	HEADERS+=NO_CE/fips202.h
endif

.PHONY: all PQCgenKAT_kem test test_gt_reference dump_forward_mapping csv_viewers clean

BUILD_DIR = build

all: \
	test \
	PQCgenKAT_kem

PQCgenKAT_kem: $(HEADERS) kat/aes.h kat/rng.h $(SOURCES) kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(NISTFLAGS) -I. -o $(BUILD_DIR)/PQCgenKAT_kem kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c $(SOURCES)

test: $(HEADERS) randombytes.h $(SOURCES) randombytes.c test/test.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/test randombytes.c test/test.c $(SOURCES)

test_gt_reference: $(HEADERS) ntt.h ntt.c gt_test/test_gt_reference.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/test_gt_reference gt_test/test_gt_reference.c

dump_forward_mapping: $(HEADERS) ntt.h ntt.c gt_test/dump_forward_mapping.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/dump_forward_mapping gt_test/dump_forward_mapping.c
	./$(BUILD_DIR)/dump_forward_mapping > $(BUILD_DIR)/forward_mapping.csv
	$(PYTHON) gt_test/make_register_pack_viewer.py $(BUILD_DIR)/gt_register_pack_plan.csv -o $(BUILD_DIR)/gt_register_pack_plan.html
	$(PYTHON) gt_test/make_csv_viewers.py $(BUILD_DIR)

csv_viewers: dump_forward_mapping

clean:
	$(RM) PQCkemKAT_*.req PQCkemKAT_*.rsp
	$(RM) -r $(BUILD_DIR)

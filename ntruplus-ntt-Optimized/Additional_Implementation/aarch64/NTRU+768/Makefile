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

.PHONY: all PQCgenKAT_kem test test_gt_reference test_polyntt_harness test_polyntt_asm test_polyinvntt_asm dump_forward_mapping gt_phase123_flow_viewer csv_viewers clean

BUILD_DIR = build
POLYNTT_ASM ?= asm/my_ntt.s asm/slothy/my_32ntt.opt.s
POLYINVNTT_ASM ?= asm/inv_my_ntt.s
POLYNTT_TEST_CFLAGS ?=
POLYNTT_ASM_FLAGS ?=

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

test_polyntt_harness: $(HEADERS) ntt.h ntt.c gt_test/test_polyntt_asm.c gt_test/polyntt_reference_shim.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) -I. -o $(BUILD_DIR)/test_polyntt_harness gt_test/test_polyntt_asm.c gt_test/polyntt_reference_shim.c ntt.c

test_polyntt_asm: $(HEADERS) ntt.h ntt.c gt_test/test_polyntt_asm.c $(POLYNTT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -I. -o $(BUILD_DIR)/test_polyntt_asm gt_test/test_polyntt_asm.c ntt.c $(POLYNTT_ASM)

test_polyinvntt_asm: $(HEADERS) ntt.h ntt.c gt_test/test_polyinvntt_asm.c $(POLYNTT_ASM) $(POLYINVNTT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -I. -o $(BUILD_DIR)/test_polyinvntt_asm gt_test/test_polyinvntt_asm.c ntt.c $(POLYNTT_ASM) $(POLYINVNTT_ASM)

dump_forward_mapping: $(HEADERS) ntt.h ntt.c gt_test/dump_forward_mapping.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/dump_forward_mapping gt_test/dump_forward_mapping.c
	./$(BUILD_DIR)/dump_forward_mapping
	$(PYTHON) gt_test/make_register_pack_viewer.py $(BUILD_DIR)/gt_register_pack_plan.csv -o $(BUILD_DIR)/gt_register_pack_plan.html
	$(PYTHON) gt_test/make_csv_viewers.py $(BUILD_DIR)
	$(PYTHON) gt_test/make_phase123_viewer.py $(BUILD_DIR) -o $(BUILD_DIR)/gt_phase123_flow_viewer.html

gt_phase123_flow_viewer: dump_forward_mapping

csv_viewers: dump_forward_mapping

clean:
	$(RM) PQCkemKAT_*.req PQCkemKAT_*.rsp
	$(RM) -r $(BUILD_DIR)

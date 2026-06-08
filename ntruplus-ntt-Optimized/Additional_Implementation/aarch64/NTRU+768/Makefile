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

.PHONY: all PQCgenKAT_kem test test_gt_reference test_gt_base_ref test_gt_base_asm test_gt_basemul_asm test_polyntt_harness test_polyntt_asm test_polyinvntt_asm test_kem_invntt_contract analyze_invntt32_ranges bench_gt_basemul_ref bench_gt_basemul_asm bench_gt_basemul_stock bench_gt_basemul_compare bench_gt_basemuladd_ref bench_gt_basemuladd_asm bench_gt_basemuladd_stock bench_gt_basemuladd_compare bench_polyinvntt_asm bench_polyinvntt_oldgather bench_polyinvntt_eagerrow bench_polyinvntt_kpqc_final bench_polyinvntt_compare bench_kem_dec bench_kem_dec_kpqc_final dump_forward_mapping gt_phase123_flow_viewer csv_viewers clean

BUILD_DIR = build
POLYNTT_ASM ?= asm/my_ntt.s asm/slothy/my_32ntt.opt.s
POLYINVNTT_ASM ?= asm/inv_my_ntt.s
BASE_GT_ASM ?= asm/base_gt.s
BASE_GT_BENCH_LABEL ?= gt_basemul_asm
KEM_NTT_ASM ?= asm/ntt.s
KEM_INVNTT_ASM ?=
KEM_CREPMOD3_ASM ?= asm/crepmod3.s
# Default KEM keeps stock KPQC base layout.  GT KEM tests override this with
# gt_test/poly_gt_base_ref.c ntt.c or ntt.c asm/base_gt_ref.s.
KEM_BASE_SOURCES ?= poly.c asm/base.s
KEM_BENCH_LABEL ?= kpqc_final_kem_dec
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

test_gt_base_ref: $(HEADERS) ntt.h ntt.c gt_test/poly_gt_base_ref.c gt_test/test_gt_base_ref.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/test_gt_base_ref gt_test/test_gt_base_ref.c gt_test/poly_gt_base_ref.c ntt.c

test_gt_base_asm: $(HEADERS) ntt.h ntt.c gt_test/test_gt_base_ref.c asm/base_gt_ref.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -DTEST_GT_BASE_USE_ABI -I. -o $(BUILD_DIR)/test_gt_base_asm gt_test/test_gt_base_ref.c ntt.c asm/base_gt_ref.s

test_gt_basemul_asm: $(HEADERS) ntt.h ntt.c gt_test/poly_gt_base_ref.c gt_test/test_gt_basemul_asm.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) $(BASE_GT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DGT_BASE_REF_NO_ABI_WRAPPERS -I. -o $(BUILD_DIR)/test_gt_basemul_asm gt_test/test_gt_basemul_asm.c gt_test/poly_gt_base_ref.c ntt.c $(POLYNTT_ASM) $(POLYINVNTT_ASM) $(BASE_GT_ASM)

test_polyntt_harness: $(HEADERS) ntt.h ntt.c gt_test/test_polyntt_asm.c gt_test/polyntt_reference_shim.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) -I. -o $(BUILD_DIR)/test_polyntt_harness gt_test/test_polyntt_asm.c gt_test/polyntt_reference_shim.c ntt.c

test_polyntt_asm: $(HEADERS) ntt.h ntt.c gt_test/test_polyntt_asm.c $(POLYNTT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -I. -o $(BUILD_DIR)/test_polyntt_asm gt_test/test_polyntt_asm.c ntt.c $(POLYNTT_ASM)

test_polyinvntt_asm: $(HEADERS) ntt.h ntt.c gt_test/test_polyinvntt_asm.c $(POLYNTT_ASM) $(POLYINVNTT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -I. -o $(BUILD_DIR)/test_polyinvntt_asm gt_test/test_polyinvntt_asm.c ntt.c $(POLYNTT_ASM) $(POLYINVNTT_ASM)

test_kem_invntt_contract: $(HEADERS) randombytes.h gt_test/test_kem_invntt_contract.c randombytes.c kem.c symmetric.c $(KEM_BASE_SOURCES) asm/add.s $(KEM_CREPMOD3_ASM) asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S $(KEM_NTT_ASM) $(KEM_INVNTT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -I. -o $(BUILD_DIR)/test_kem_invntt_contract gt_test/test_kem_invntt_contract.c randombytes.c kem.c symmetric.c $(KEM_BASE_SOURCES) asm/add.s $(KEM_CREPMOD3_ASM) asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S $(KEM_NTT_ASM) $(KEM_INVNTT_ASM)

analyze_invntt32_ranges: $(HEADERS) ntt.h ntt.c gt_test/analyze_invntt32_ranges.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -I. -o $(BUILD_DIR)/analyze_invntt32_ranges gt_test/analyze_invntt32_ranges.c

bench_polyinvntt_asm: $(HEADERS) ntt.h ntt.c gt_test/bench_polyinvntt_asm.c $(POLYNTT_ASM) $(POLYINVNTT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"gt_rowbitrev_invntt_rowlazy\" -I. -o $(BUILD_DIR)/bench_polyinvntt_asm gt_test/bench_polyinvntt_asm.c $(POLYNTT_ASM) $(POLYINVNTT_ASM)

bench_polyinvntt_oldgather: $(HEADERS) ntt.h ntt.c gt_test/bench_polyinvntt_asm.c $(POLYNTT_ASM) asm/inv_my_ntt_oldgather.s asm/slothy/invntt_opt.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"gt_rowbitrev_invntt_oldgather\" -I. -o $(BUILD_DIR)/bench_polyinvntt_oldgather gt_test/bench_polyinvntt_asm.c $(POLYNTT_ASM) asm/inv_my_ntt_oldgather.s

bench_polyinvntt_eagerrow: $(HEADERS) ntt.h ntt.c gt_test/bench_polyinvntt_asm.c $(POLYNTT_ASM) asm/inv_my_ntt_eagerrow.s asm/slothy/invntt_opt.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"gt_rowbitrev_invntt_eagerrow\" -I. -o $(BUILD_DIR)/bench_polyinvntt_eagerrow gt_test/bench_polyinvntt_asm.c $(POLYNTT_ASM) asm/inv_my_ntt_eagerrow.s

bench_polyinvntt_kpqc_final: $(HEADERS) gt_test/bench_polyinvntt_asm.c asm/ntt.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"kpqc_final_invntt\" -I. -o $(BUILD_DIR)/bench_polyinvntt_kpqc_final gt_test/bench_polyinvntt_asm.c asm/ntt.s

bench_polyinvntt_compare: bench_polyinvntt_asm bench_polyinvntt_kpqc_final
	./$(BUILD_DIR)/bench_polyinvntt_asm
	./$(BUILD_DIR)/bench_polyinvntt_kpqc_final

bench_gt_basemul_ref: $(HEADERS) ntt.h ntt.c gt_test/poly_gt_base_ref.c gt_test/bench_gt_basemul.c asm/base_gt_ref.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DGT_BASE_REF_NO_ABI_WRAPPERS -DBENCH_EXPECT_GT -DBENCH_LABEL=\"gt_basemul_scalar_ref\" -I. -o $(BUILD_DIR)/bench_gt_basemul_ref gt_test/bench_gt_basemul.c gt_test/poly_gt_base_ref.c ntt.c asm/base_gt_ref.s

bench_gt_basemul_asm: $(HEADERS) ntt.h ntt.c gt_test/poly_gt_base_ref.c gt_test/bench_gt_basemul.c $(BASE_GT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DGT_BASE_REF_NO_ABI_WRAPPERS -DBENCH_EXPECT_GT -DBENCH_LABEL=\"$(BASE_GT_BENCH_LABEL)\" -I. -o $(BUILD_DIR)/bench_gt_basemul_asm gt_test/bench_gt_basemul.c gt_test/poly_gt_base_ref.c ntt.c $(BASE_GT_ASM)

bench_gt_basemul_stock: $(HEADERS) ntt.h ntt.c gt_test/bench_gt_basemul.c asm/base.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"stock_basemul_raw\" -I. -o $(BUILD_DIR)/bench_gt_basemul_stock gt_test/bench_gt_basemul.c ntt.c asm/base.s

bench_gt_basemul_compare: bench_gt_basemul_ref bench_gt_basemul_asm bench_gt_basemul_stock
	./$(BUILD_DIR)/bench_gt_basemul_ref
	./$(BUILD_DIR)/bench_gt_basemul_asm
	./$(BUILD_DIR)/bench_gt_basemul_stock

bench_gt_basemuladd_ref: $(HEADERS) ntt.h ntt.c gt_test/poly_gt_base_ref.c gt_test/bench_gt_basemul.c asm/base_gt_ref.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DGT_BASE_REF_NO_ABI_WRAPPERS -DBENCH_EXPECT_GT -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_basemuladd_scalar_ref\" -I. -o $(BUILD_DIR)/bench_gt_basemuladd_ref gt_test/bench_gt_basemul.c gt_test/poly_gt_base_ref.c ntt.c asm/base_gt_ref.s

bench_gt_basemuladd_asm: $(HEADERS) ntt.h ntt.c gt_test/poly_gt_base_ref.c gt_test/bench_gt_basemul.c asm/base_gt.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DGT_BASE_REF_NO_ABI_WRAPPERS -DBENCH_EXPECT_GT -DBENCH_OP_ADD -DBENCH_LABEL=\"gt_basemuladd_asm\" -I. -o $(BUILD_DIR)/bench_gt_basemuladd_asm gt_test/bench_gt_basemul.c gt_test/poly_gt_base_ref.c ntt.c asm/base_gt.s

bench_gt_basemuladd_stock: $(HEADERS) ntt.h ntt.c gt_test/bench_gt_basemul.c asm/base.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_OP_ADD -DBENCH_LABEL=\"stock_basemuladd_raw\" -I. -o $(BUILD_DIR)/bench_gt_basemuladd_stock gt_test/bench_gt_basemul.c ntt.c asm/base.s

bench_gt_basemuladd_compare: bench_gt_basemuladd_ref bench_gt_basemuladd_asm bench_gt_basemuladd_stock
	./$(BUILD_DIR)/bench_gt_basemuladd_ref
	./$(BUILD_DIR)/bench_gt_basemuladd_asm
	./$(BUILD_DIR)/bench_gt_basemuladd_stock

bench_kem_dec: $(HEADERS) randombytes.h gt_test/bench_kem_dec.c randombytes.c kem.c symmetric.c $(KEM_BASE_SOURCES) asm/add.s $(KEM_CREPMOD3_ASM) asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S $(KEM_NTT_ASM) $(KEM_INVNTT_ASM)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"$(KEM_BENCH_LABEL)\" -I. -o $(BUILD_DIR)/bench_kem_dec gt_test/bench_kem_dec.c randombytes.c kem.c symmetric.c $(KEM_BASE_SOURCES) asm/add.s $(KEM_CREPMOD3_ASM) asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S $(KEM_NTT_ASM) $(KEM_INVNTT_ASM)

bench_kem_dec_kpqc_final: $(HEADERS) randombytes.h gt_test/bench_kem_dec.c randombytes.c kem.c symmetric.c poly.c asm/add.s asm/base.s asm/crepmod3.s asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S asm/ntt.s
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(POLYNTT_TEST_CFLAGS) $(POLYNTT_ASM_FLAGS) -DBENCH_LABEL=\"kpqc_final_kem_dec\" -I. -o $(BUILD_DIR)/bench_kem_dec_kpqc_final gt_test/bench_kem_dec.c randombytes.c kem.c symmetric.c poly.c asm/add.s asm/base.s asm/crepmod3.s asm/pack.s asm/cbd.s CE/fips202.c CE/f1600.S asm/ntt.s

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

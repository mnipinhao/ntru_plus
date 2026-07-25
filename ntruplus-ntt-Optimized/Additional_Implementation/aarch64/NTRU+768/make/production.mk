.PHONY: all PQCgenKAT_kem test check-production-layout
.PHONY: test_kem_gt_production test_kem_gt_production_opt test_kem_gt_production_opt_rminus1
.PHONY: test_kem_gt_production_default test_kem_gt_production_q31 test_kem_gt_production_no_q31
.PHONY: test_kem_gt_production_legacy_ntt

all: test PQCgenKAT_kem

PQCgenKAT_kem: $(HEADERS) $(SHAKE_HEADERS) kat/aes.h kat/rng.h kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c ntt.h $(GT_PRODUCTION_DEFAULT_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(NISTFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/PQCgenKAT_kem kat/PQCgenKAT_kem.c kat/aes.c kat/rng.c $(GT_PRODUCTION_DEFAULT_KEM_SOURCES)

test: test_kem_gt_production_default
test_kem_gt_production: test_kem_gt_production_default
test_kem_gt_production_opt: test_kem_gt_production_default
test_kem_gt_production_opt_rminus1: test_kem_gt_production_default

test_kem_gt_production_default: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(GT_PRODUCTION_DEFAULT_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_DEFAULT_FLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_production_default randombytes.c test/test.c $(GT_PRODUCTION_DEFAULT_KEM_SOURCES)

test_kem_gt_production_q31: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(GT_PRODUCTION_Q31_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_Q31_FLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_production_q31 randombytes.c test/test.c $(GT_PRODUCTION_Q31_KEM_SOURCES)

test_kem_gt_production_no_q31: $(HEADERS) $(SHAKE_HEADERS) randombytes.h randombytes.c test/test.c ntt.h $(GT_PRODUCTION_NO_Q31_KEM_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 $(GT_PRODUCTION_NO_Q31_FLAGS) -Wno-unused-function -I. -o $(BUILD_DIR)/test_kem_gt_production_no_q31 randombytes.c test/test.c $(GT_PRODUCTION_NO_Q31_KEM_SOURCES)

test_kem_gt_production_legacy_ntt:
	$(MAKE) -B test_kem_gt_production_default GT_PRODUCTION_USE_LEGACY_NTT=1

check-production-layout:
	python3 scripts/check_production_layout.py \
		--keygen-layout $(GT_PRODUCTION_KEYGEN_LAYOUT)

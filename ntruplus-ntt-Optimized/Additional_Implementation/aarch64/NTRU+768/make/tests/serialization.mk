.PHONY: test_gt_canonical_serialization test_gt_canonical_serialization_asm
.PHONY: test_gt_canonical_pack_boundary
.PHONY: test_gt_canonical_pack_chunk_candidates
.PHONY: test_gt_canonical_pack_full_candidates
.PHONY: test_gt_canonical_unpack_chunk_candidate
.PHONY: test_gt_canonical_unpack_full_candidate
.PHONY: test_gt_canonical_normalize verify_gt_canonical_permutation

test_gt_canonical_serialization: $(HEADERS) poly_gt_canonical.c \
		gt_test/test_gt_canonical_serialization.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -I. -o \
		$(BUILD_DIR)/test_gt_canonical_serialization \
		gt_test/test_gt_canonical_serialization.c poly_gt_canonical.c
	./$(BUILD_DIR)/test_gt_canonical_serialization

test_gt_canonical_serialization_asm: $(HEADERS) poly_gt_canonical.c \
		$(GT_CANONICAL_PACK_ASM) gt_test/test_gt_canonical_serialization.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -I. -o \
		$(BUILD_DIR)/test_gt_canonical_serialization_asm \
		gt_test/test_gt_canonical_serialization.c poly_gt_canonical.c \
		$(GT_CANONICAL_PACK_ASM)
	./$(BUILD_DIR)/test_gt_canonical_serialization_asm

test_gt_canonical_pack_boundary: $(HEADERS) poly_gt_canonical.c \
		$(GT_CANONICAL_PACK_ASM) gt_test/test_gt_canonical_pack_boundary.c \
		gt_test/canonical_pack_abi_sentinel.S
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -I. -o \
		$(BUILD_DIR)/test_gt_canonical_pack_boundary \
		gt_test/test_gt_canonical_pack_boundary.c \
		gt_test/canonical_pack_abi_sentinel.S poly_gt_canonical.c \
		$(GT_CANONICAL_PACK_ASM)
	./$(BUILD_DIR)/test_gt_canonical_pack_boundary

test_gt_canonical_pack_chunk_candidates: $(HEADERS) \
		$(GT_CANONICAL_PACK_ASM) \
		asm/gt/experiment/canonical_pack_chunk_candidates.S \
		asm/gt/experiment/canonical_pack_full_candidates.S \
		asm/gt/experiment/poly_canonical_pack_cross_chunk.S \
		asm/gt/experiment/poly_canonical_pack_compact.S \
		gt_test/canonical_pack_chunk_abi_sentinel.S \
		gt_test/test_gt_canonical_pack_chunk_candidates.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -I. -o \
		$(BUILD_DIR)/test_gt_canonical_pack_chunk_candidates \
		gt_test/test_gt_canonical_pack_chunk_candidates.c \
		gt_test/canonical_pack_chunk_abi_sentinel.S \
		$(GT_CANONICAL_PACK_ASM) \
		asm/gt/experiment/canonical_pack_chunk_candidates.S \
		asm/gt/experiment/canonical_pack_full_candidates.S \
		asm/gt/experiment/poly_canonical_pack_cross_chunk.S \
		asm/gt/experiment/poly_canonical_pack_compact.S
	./$(BUILD_DIR)/test_gt_canonical_pack_chunk_candidates

test_gt_canonical_pack_full_candidates: $(HEADERS) \
		$(GT_CANONICAL_PACK_ASM) \
		asm/gt/experiment/canonical_pack_chunk_candidates.S \
		asm/gt/experiment/canonical_pack_full_candidates.S \
		asm/gt/experiment/poly_canonical_pack_cross_chunk.S \
		asm/gt/experiment/poly_canonical_pack_compact.S \
		gt_test/canonical_pack_chunk_abi_sentinel.S \
		gt_test/test_gt_canonical_pack_full_candidates.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -I. -o \
		$(BUILD_DIR)/test_gt_canonical_pack_full_candidates \
		gt_test/test_gt_canonical_pack_full_candidates.c \
		gt_test/canonical_pack_chunk_abi_sentinel.S \
		$(GT_CANONICAL_PACK_ASM) \
		asm/gt/experiment/canonical_pack_chunk_candidates.S \
		asm/gt/experiment/canonical_pack_full_candidates.S \
		asm/gt/experiment/poly_canonical_pack_cross_chunk.S \
		asm/gt/experiment/poly_canonical_pack_compact.S
	./$(BUILD_DIR)/test_gt_canonical_pack_full_candidates

test_gt_canonical_unpack_chunk_candidate: $(HEADERS) \
		$(GT_CANONICAL_PACK_ASM) \
		asm/gt/experiment/canonical_unpack_chunk_candidates.S \
		asm/gt/support/poly_canonical_unpack_u1.S \
		gt_test/canonical_unpack_abi_sentinel.S \
		gt_test/test_gt_canonical_unpack_chunk_candidate.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -I. -o \
		$(BUILD_DIR)/test_gt_canonical_unpack_chunk_candidate \
		gt_test/test_gt_canonical_unpack_chunk_candidate.c \
		gt_test/canonical_unpack_abi_sentinel.S \
		$(GT_CANONICAL_PACK_ASM) \
		asm/gt/experiment/canonical_unpack_chunk_candidates.S \
		asm/gt/support/poly_canonical_unpack_u1.S
	./$(BUILD_DIR)/test_gt_canonical_unpack_chunk_candidate

test_gt_canonical_unpack_full_candidate: $(HEADERS) \
		$(GT_CANONICAL_PACK_ASM) \
		asm/gt/experiment/canonical_unpack_chunk_candidates.S \
		asm/gt/support/poly_canonical_unpack_u1.S \
		gt_test/canonical_unpack_abi_sentinel.S \
		gt_test/test_gt_canonical_unpack_full_candidate.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -I. -o \
		$(BUILD_DIR)/test_gt_canonical_unpack_full_candidate \
		gt_test/test_gt_canonical_unpack_full_candidate.c \
		gt_test/canonical_unpack_abi_sentinel.S \
		$(GT_CANONICAL_PACK_ASM) \
		asm/gt/experiment/canonical_unpack_chunk_candidates.S \
		asm/gt/support/poly_canonical_unpack_u1.S
	./$(BUILD_DIR)/test_gt_canonical_unpack_full_candidate

test_gt_canonical_normalize: params.h gt_test/test_gt_canonical_normalize.c
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -I. -o \
		$(BUILD_DIR)/test_gt_canonical_normalize \
		gt_test/test_gt_canonical_normalize.c
	./$(BUILD_DIR)/test_gt_canonical_normalize

verify_gt_canonical_permutation:
	python3 scripts/verify_gt_canonical_permutation.py

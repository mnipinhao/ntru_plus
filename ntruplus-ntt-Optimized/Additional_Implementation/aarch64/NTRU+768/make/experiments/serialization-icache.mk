.PHONY: generate_gt_serialization_icache_candidates
.PHONY: test_gt_serialization_icache_candidates

GT_SERIALIZATION_ICACHE_DIR := experiments/gt_production_icache_size
GT_SERIALIZATION_ICACHE_GENERATED := $(GT_SERIALIZATION_ICACHE_DIR)/generated

generate_gt_serialization_icache_candidates:
	python3 $(GT_SERIALIZATION_ICACHE_DIR)/generate_serialization_candidates.py

test_gt_serialization_icache_candidates: generate_gt_serialization_icache_candidates
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -std=c99 -I. -o \
		$(BUILD_DIR)/test_gt_serialization_icache_candidates \
		$(GT_SERIALIZATION_ICACHE_DIR)/test_serialization_candidates.c \
		$(GT_SERIALIZATION_ICACHE_DIR)/serialization_candidate_abi_sentinel.S \
		asm/gt/support/poly_canonical_pack.S \
		asm/gt/keygen_bpq_cq/pack_cq.S \
		$(GT_SERIALIZATION_ICACHE_GENERATED)/poly_tobytes_shared_compact_namespaced.S \
		$(GT_SERIALIZATION_ICACHE_GENERATED)/keygen_pack_shared_core_namespaced.S
	./$(BUILD_DIR)/test_gt_serialization_icache_candidates

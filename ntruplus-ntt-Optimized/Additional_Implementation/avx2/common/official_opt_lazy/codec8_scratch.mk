# SCRATCH decision-gate measurement for a direct 12-bit codec on the Official
# NTRU+768 / NTRU+1152 AVX2 8-way layout (docs/ntruplus768-1152-direct-codec.md).
# Included by
#   NTRU+768/experiments/avx2_official_opt_freeze_001/Makefile
#   NTRU+1152/experiments/avx2_official_opt_001/Makefile
# after freeze2op.mk (whose FREEZE_ASM it reuses).  The kernels are intrinsics
# (bench/scratch_codec8.c), not a candidate: no KEM binding, no generator.
#   make codec8-scratch-check   differential sweep, release and ASan/UBSan builds
#   make codec8-scratch-bench   same-ELF component ELFs (normal and reversed link order)
#   make codec8-scratch-count   dynamic instructions per call (perf stat instructions:u)

CODEC8_KERNEL := $(COMMON)/bench/scratch_codec8.c
CODEC8_BENCH := $(COMMON)/bench/bench_codec8_scratch.c
CODEC8_DEFS := -DFREEZE_TOBYTES=$(FREEZE)
CODEC8_SRC := $(CODEC8_BENCH) $(OFFICIAL)/pack.s $(OFFICIAL)/consts.c $(FREEZE_ASM) $(CODEC8_KERNEL)
CODEC8_SRC_REV := $(CODEC8_KERNEL) $(FREEZE_ASM) $(OFFICIAL)/consts.c $(OFFICIAL)/pack.s $(CODEC8_BENCH)

.PHONY: codec8-scratch-check codec8-scratch-bench codec8-scratch-count

$(BUILD)/bench_codec8_scratch: $(CODEC8_SRC) | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I$(CPU_INCLUDE) $(INCLUDES) $(CODEC8_DEFS) -o $@ $^ $(CPU_LIB)
$(BUILD)/bench_codec8_scratch_swapped: $(CODEC8_SRC_REV) | $(BUILD)
	$(CC) $(BENCH_CFLAGS) -I$(CPU_INCLUDE) $(INCLUDES) $(CODEC8_DEFS) -o $@ $^ $(CPU_LIB)
$(BUILD_SAN)/bench_codec8_scratch: $(CODEC8_SRC) | $(BUILD_SAN)
	$(CC) $(SANFLAGS) -I$(CPU_INCLUDE) $(INCLUDES) $(CODEC8_DEFS) -o $@ $^ $(CPU_LIB)

codec8-scratch-check: $(BUILD)/bench_codec8_scratch $(BUILD_SAN)/bench_codec8_scratch
	$(BUILD)/bench_codec8_scratch check
	$(SAN_ENV) $(BUILD_SAN)/bench_codec8_scratch check

codec8-scratch-bench: $(BUILD)/bench_codec8_scratch $(BUILD)/bench_codec8_scratch_swapped

CODEC8_COUNT_N := 1000000
CODEC8_COUNT = taskset -c 1 perf stat -x, -e instructions:u $(BUILD)/count_codec8_scratch $(1) $(CODEC8_COUNT_N) 2>&1 \
	| awk -F, '$$3 ~ /instructions/ && $$1 ~ /^[0-9]+$$/ {print $$1}'
$(BUILD)/count_codec8_scratch: $(COMMON)/bench/count_codec8_scratch.c $(OFFICIAL)/pack.s $(OFFICIAL)/consts.c \
		$(FREEZE_ASM) $(CODEC8_KERNEL) | $(BUILD)
	$(CC) $(BENCH_CFLAGS) $(INCLUDES) $(CODEC8_DEFS) -o $@ $^

codec8-scratch-count: $(BUILD)/count_codec8_scratch
	@base=$$($(call CODEC8_COUNT,0)); for v in 1 2 3 4 5 6; do \
	  t=$$($(call CODEC8_COUNT,$$v)); echo "variant $$v: $$(( (t - base) / $(CODEC8_COUNT_N) )) instructions/call"; done

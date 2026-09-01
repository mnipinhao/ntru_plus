CC ?= gcc
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Wpedantic -march=armv8-a+simd
BENCH_ABI_CFLAGS := -ffixed-v8 -ffixed-v9 -ffixed-v10 -ffixed-v11 \
	-ffixed-v12 -ffixed-v13 -ffixed-v14 -ffixed-v15
BUILD := build
DEPS := deps

.PHONY: all clean
all: $(BUILD)/bench_gt864_forward_pmu $(BUILD)/sizes.txt

$(BUILD):
	mkdir -p $@

$(BUILD)/official.o: $(DEPS)/official_ntt.s | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/top-split.o: $(DEPS)/gt864_top_split.s | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/pass2.o: $(DEPS)/gt864_forward_six_bank_pass2.S | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/wrapper.o: $(DEPS)/gt864_forward_poly_ntt_experiment.S | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/bench_gt864_forward_pmu: bench_gt864_forward_pmu.c \
		$(DEPS)/gt864_fr0_to_official_map.h $(BUILD)/official.o \
		$(BUILD)/top-split.o $(BUILD)/pass2.o $(BUILD)/wrapper.o
	$(CC) $(CFLAGS) $(BENCH_ABI_CFLAGS) -I$(DEPS) -o $@ \
		bench_gt864_forward_pmu.c \
		$(BUILD)/official.o $(BUILD)/top-split.o $(BUILD)/pass2.o \
		$(BUILD)/wrapper.o

$(BUILD)/sizes.txt: $(BUILD)/official.o $(BUILD)/top-split.o \
		$(BUILD)/pass2.o $(BUILD)/wrapper.o
	size $^ > $@

clean:
	rm -f -r $(BUILD)

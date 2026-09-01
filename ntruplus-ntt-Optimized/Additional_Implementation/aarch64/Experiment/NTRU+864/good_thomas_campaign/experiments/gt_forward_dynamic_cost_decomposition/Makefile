CC ?= gcc
CFLAGS ?= -O3 -std=c11 -Wall -Wextra -Wpedantic -march=armv8-a+simd
BENCH_ABI_CFLAGS := -ffixed-v8 -ffixed-v9 -ffixed-v10 -ffixed-v11 \
	-ffixed-v12 -ffixed-v13 -ffixed-v14 -ffixed-v15
BUILD := build
DEPS := deps

.PHONY: all static clean
all: $(BUILD)/bench_components

$(BUILD):
	mkdir -p $@

static: | $(BUILD)
	python3 analyze_assembly.py $(BUILD)/assembly-analysis.json
	python3 -m json.tool $(BUILD)/assembly-analysis.json >/dev/null

$(BUILD)/%.o: $(DEPS)/% | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

OBJECTS := $(BUILD)/official_ntt.s.o $(BUILD)/gt864_top_split.s.o \
	$(BUILD)/gt864_forward_six_bank_pass2.S.o \
	$(BUILD)/gt864_forward_poly_ntt_experiment.S.o \
	$(BUILD)/gt864_forward_noop.S.o

$(BUILD)/bench_components: bench_components.c \
		$(DEPS)/gt864_fr0_to_official_map.h $(OBJECTS)
	$(CC) $(CFLAGS) $(BENCH_ABI_CFLAGS) -I$(DEPS) -o $@ \
		bench_components.c $(OBJECTS)

clean:
	rm -f -r $(BUILD)

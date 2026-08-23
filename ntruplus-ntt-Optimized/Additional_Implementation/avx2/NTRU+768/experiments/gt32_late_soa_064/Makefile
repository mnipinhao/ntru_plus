CC ?= cc
PYTHON ?= python3
CFLAGS := -O3 -g -mavx2 -Wall -Wextra -Werror -Wpedantic
GTBASE := ../avx2_gt32_tile4_official_001

.PHONY: all test audit bench-short pmu clean
all: build/test build/bench

build:
	mkdir -p build

build/full_bridge.o: src/full_bridge.S ../gt32_late_soa_063/src/late_soa.S \
	$(GTBASE)/generated/tile4_constants.inc \
	$(GTBASE)/generated/tile4_basemul_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/tile4.o: $(GTBASE)/src/tile4_asm.S $(GTBASE)/generated/tile4_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/basemul.o: $(GTBASE)/src/tile4_basemul_asm.S \
	$(GTBASE)/generated/tile4_basemul_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/forward_soa.o: $(GTBASE)/src/tile4_forward_bm_soa_attribution_asm.S \
	$(GTBASE)/generated/tile4_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/basemul_attr.o: $(GTBASE)/src/tile4_basemul_attribution_asm.S \
	$(GTBASE)/generated/tile4_constants.inc \
	$(GTBASE)/generated/tile4_basemul_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/test.o: tests/test.c src/full_bridge.h | build
	$(CC) $(CFLAGS) -Isrc -c $< -o $@

build/bench.o: bench/bench.c src/full_bridge.h | build
	$(CC) $(CFLAGS) -Isrc -c $< -o $@

OBJS := build/full_bridge.o build/tile4.o build/basemul.o \
	build/forward_soa.o build/basemul_attr.o

build/test: build/test.o $(OBJS)
	$(CC) $(CFLAGS) $^ -o $@

build/bench: build/bench.o $(OBJS)
	$(CC) $(CFLAGS) $^ -o $@

test: build/test
	./build/test

audit: build/bench
	$(PYTHON) tools/audit.py

bench-short: build/bench
	$(PYTHON) tools/run_short.py

pmu: build/bench
	$(PYTHON) tools/run_pmu.py

clean:
	rm -rf build results/short.json results/pmu.json results/static.json

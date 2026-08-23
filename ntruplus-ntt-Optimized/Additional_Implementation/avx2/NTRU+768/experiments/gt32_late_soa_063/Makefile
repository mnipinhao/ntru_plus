CC ?= cc
PYTHON ?= python3
CFLAGS := -O3 -g -mavx2 -Wall -Wextra -Werror -Wpedantic
HWA := ../gt32_hwa16_island_061
GTBASE := ../avx2_gt32_tile4_official_001

.PHONY: all test audit bench-short pmu clean
all: build/test build/bench

build:
	mkdir -p build

build/late_soa.o: src/late_soa.S $(GTBASE)/generated/tile4_constants.inc \
	$(GTBASE)/generated/tile4_basemul_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/control.o: $(HWA)/src/control_tile4.S $(HWA)/generated/hwa16_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/test.o: tests/test.c src/late_soa.h | build
	$(CC) $(CFLAGS) -Isrc -c $< -o $@

build/bench.o: bench/bench.c src/late_soa.h | build
	$(CC) $(CFLAGS) -Isrc -c $< -o $@

build/test: build/test.o build/late_soa.o build/control.o
	$(CC) $(CFLAGS) $^ -o $@

build/bench: build/bench.o build/late_soa.o build/control.o
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

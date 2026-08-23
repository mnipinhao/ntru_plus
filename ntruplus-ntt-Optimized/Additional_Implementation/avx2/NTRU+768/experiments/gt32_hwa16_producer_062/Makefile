CC ?= cc
PYTHON ?= python3
CFLAGS := -O3 -g -mavx2 -Wall -Wextra -Werror -Wpedantic
GTBASE := ../avx2_gt32_tile4_official_001

.PHONY: all test audit bench-short pmu clean
all: build/test build/bench

build:
	mkdir -p build

build/producer.o: src/producer.S $(GTBASE)/generated/tile4_constants.inc | build
	$(CC) $(CFLAGS) -I$(GTBASE)/generated -c $< -o $@

build/frontend.o: $(GTBASE)/src/tile4_asm.S | build
	$(CC) $(CFLAGS) -DGT32_FRONTEND_GATE_VARIANTS -c $< -o $@

build/reference.o: src/reference.c src/producer.h | build
	$(CC) $(CFLAGS) -Isrc -c $< -o $@

build/test.o: tests/test.c src/producer.h | build
	$(CC) $(CFLAGS) -Isrc -c $< -o $@

build/bench.o: bench/bench.c src/producer.h | build
	$(CC) $(CFLAGS) -Isrc -c $< -o $@

build/test: build/test.o build/producer.o build/frontend.o build/reference.o
	$(CC) $(CFLAGS) $^ -o $@

build/bench: build/bench.o build/producer.o
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

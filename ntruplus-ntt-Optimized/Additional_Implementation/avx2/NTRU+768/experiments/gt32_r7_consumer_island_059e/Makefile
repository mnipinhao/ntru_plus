CC ?= cc
CFLAGS := -O3 -mavx2 -Wall -Wextra -Werror
ROOT := ../avx2_gt32_tile4_official_001

.PHONY: all clean generate run
all: generate build/bench

generate:
	python3 tools/generate_gate.py

build:
	mkdir -p build

build/island.o: src/r7_consumer_island_asm.S generated/r7_consumer_island_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/b3.o: $(ROOT)/src/tile4_basemul_asm.S | build
	$(CC) $(CFLAGS) -I$(ROOT)/src -c $< -o $@

build/q24.o: $(ROOT)/src/tile4_q24_codec_asm.S | build
	$(CC) $(CFLAGS) -I$(ROOT)/src -c $< -o $@

build/bench.o: bench/bench.c | build
	$(CC) $(CFLAGS) -c $< -o $@

build/bench: build/bench.o build/island.o build/b3.o build/q24.o
	$(CC) $(CFLAGS) $^ -o $@

run: build/bench
	./build/bench

clean:
	rm -rf build


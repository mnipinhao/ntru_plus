CC ?= cc
CFLAGS := -O3 -mavx2 -Wall -Wextra -Werror
ROOT := ../avx2_gt32_tile4_official_001

.PHONY: all clean run
all: build/bench

build:
	mkdir -p build

build/r7.o: src/r7_late_exit_asm.S | build
	$(CC) $(CFLAGS) -c $< -o $@

build/q24.o: $(ROOT)/src/tile4_q24_codec_asm.S | build
	$(CC) $(CFLAGS) -I$(ROOT)/src -c $< -o $@

build/bench.o: bench/bench.c | build
	$(CC) $(CFLAGS) -c $< -o $@

build/bench: build/bench.o build/r7.o build/q24.o
	$(CC) $(CFLAGS) $^ -o $@

run: build/bench
	./build/bench

clean:
	rm -rf build

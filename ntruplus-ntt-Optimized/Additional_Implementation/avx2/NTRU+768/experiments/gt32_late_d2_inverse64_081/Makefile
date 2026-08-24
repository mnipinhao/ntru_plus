CC ?= cc
PYTHON ?= python3
CFLAGS := -O3 -g -mavx2 -fno-stack-protector -Wall -Wextra -Werror -Wpedantic
LATE := ../gt32_late_soa_063
HWA := ../gt32_hwa16_island_061

.PHONY: all constants test bench-supercop clean
all: build/test build/measure

constants: generated/inverse64_constants.inc
generated/inverse64_constants.inc: tools/gen_asm_constants.py generated/inverse64_endpoint.json
	$(PYTHON) tools/gen_asm_constants.py

build:
	mkdir -p build results

build/candidate.o: src/candidate.S generated/inverse64_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/normalize.o: src/normalize.S generated/inverse64_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/control.o: src/control.S ../avx2_gt32_tile4_official_001/generated/tile4_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/redeposit.o: ../gt32_late_d2_079/src/redeposit.S ../avx2_gt32_tile4_official_001/generated/tile4_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/late_soa.o: $(LATE)/src/late_soa.S | build
	$(CC) $(CFLAGS) -c $< -o $@

build/hwa16.o: $(HWA)/src/hwa16.S $(HWA)/generated/hwa16_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/test.o: tests/test.c src/gate.h | build
	$(CC) $(CFLAGS) -Isrc -c $< -o $@

build/measure.o: bench/measure.c src/gate.h | build
	$(CC) $(CFLAGS) -Isrc -c $< -o $@

OBJECTS := build/candidate.o build/normalize.o build/control.o build/redeposit.o build/late_soa.o build/hwa16.o
build/test: build/test.o $(OBJECTS)
	$(CC) $(CFLAGS) $^ -o $@
build/measure: build/measure.o $(OBJECTS)
	$(CC) $(CFLAGS) $^ -o $@

test: build/test
	./build/test

bench-supercop: build/measure
	$(PYTHON) tools/run_supercop_style.py

clean:
	rm -rf build results

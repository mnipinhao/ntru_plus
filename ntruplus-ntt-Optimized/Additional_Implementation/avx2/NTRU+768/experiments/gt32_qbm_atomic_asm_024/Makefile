CC ?= gcc
CFLAGS ?= -O3 -mavx2 -Wall -Wextra -Werror -std=c11
GT16 := ../avx2_gt16_quadratic_official_001
INCLUDES := -Isrc -I$(GT16)/src -I$(GT16)/generated

.PHONY: all check bench pmu clean

all: check

build:
	mkdir -p build

build/qbm_normal.o: src/qbm_atomic.S | build
	$(CC) -O3 -mavx2 -c $< -o $@

build/qbm_reversed.o: src/qbm_atomic.S | build
	$(CC) -O3 -mavx2 -DREVERSED=1 -c $< -o $@

build/test_normal: tests/test_qbm_atomic.c build/qbm_normal.o $(GT16)/src/qbm_intrinsic.c | build
	$(CC) $(CFLAGS) $(INCLUDES) tests/test_qbm_atomic.c \
		$(GT16)/src/qbm_intrinsic.c build/qbm_normal.o -o $@

build/test_reversed: tests/test_qbm_atomic.c build/qbm_reversed.o $(GT16)/src/qbm_intrinsic.c | build
	$(CC) $(CFLAGS) $(INCLUDES) tests/test_qbm_atomic.c \
		$(GT16)/src/qbm_intrinsic.c build/qbm_reversed.o -o $@

build/bench_normal: bench/bench_qbm_atomic.c build/qbm_normal.o | build
	$(CC) $(CFLAGS) $(INCLUDES) $< build/qbm_normal.o -o $@

build/bench_reversed: bench/bench_qbm_atomic.c build/qbm_reversed.o | build
	$(CC) $(CFLAGS) $(INCLUDES) $< build/qbm_reversed.o -o $@

build/pmu_normal: bench/pmu_qbm_atomic.c build/qbm_normal.o | build
	$(CC) $(CFLAGS) $(INCLUDES) $< build/qbm_normal.o -o $@

build/pmu_reversed: bench/pmu_qbm_atomic.c build/qbm_reversed.o | build
	$(CC) $(CFLAGS) $(INCLUDES) $< build/qbm_reversed.o -o $@

check: build/test_normal build/test_reversed build/bench_normal build/bench_reversed \
	build/pmu_normal build/pmu_reversed
	build/test_normal
	build/test_reversed
	python3 tools/audit_asm.py

bench: check
	python3 tools/run_bench.py

pmu: check
	python3 tools/run_pmu.py

clean:
	rm -rf build results/qbm-atomic-short.json results/qbm-atomic-pmu.json generated

CC ?= cc
PYTHON ?= python3
CFLAGS := -O3 -g -mavx2 -Wall -Wextra -Werror -Wpedantic

.PHONY: all generate test audit bench-short pmu clean
all: build/test build/bench build/test_v3 build/bench_v3

generate: generated/hwa16_constants.inc generated/manifest.json

generated/hwa16_constants.inc generated/manifest.json generated/v3_constants.inc \
generated/v3_mapping_survey.json: tools/generate.py
	$(PYTHON) tools/generate.py

build:
	mkdir -p build

build/control.o: src/control_tile4.S generated/hwa16_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/hwa16.o: src/hwa16.S generated/hwa16_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/hwa16_v3.o: src/hwa16_v3.S generated/hwa16_constants.inc generated/v3_constants.inc | build
	$(CC) $(CFLAGS) -c $< -o $@

build/reference.o: src/reference.c src/hwa16.h | build
	$(CC) $(CFLAGS) -Isrc -c $< -o $@

build/test.o: tests/test.c src/hwa16.h | build
	$(CC) $(CFLAGS) -Isrc -c $< -o $@

build/bench.o: bench/bench.c src/hwa16.h | build
	$(CC) $(CFLAGS) -Isrc -c $< -o $@

build/test_v3.o: tests/test_v3.c src/hwa16.h | build
	$(CC) $(CFLAGS) -Isrc -c $< -o $@

build/bench_v3.o: bench/bench_v3.c src/hwa16.h | build
	$(CC) $(CFLAGS) -Isrc -c $< -o $@

build/test: build/test.o build/reference.o build/control.o build/hwa16.o
	$(CC) $(CFLAGS) $^ -o $@

build/bench: build/bench.o build/reference.o build/control.o build/hwa16.o
	$(CC) $(CFLAGS) $^ -o $@

build/test_v3: build/test_v3.o build/reference.o build/control.o build/hwa16_v3.o
	$(CC) $(CFLAGS) $^ -o $@

build/bench_v3: build/bench_v3.o build/reference.o build/control.o build/hwa16_v3.o
	$(CC) $(CFLAGS) $^ -o $@

test: build/test build/test_v3
	./build/test
	./build/test_v3

audit: build/bench build/bench_v3
	$(PYTHON) tools/audit.py > results/static-audit.json
	cat results/static-audit.json

bench-short: build/bench build/bench_v3
	$(PYTHON) tools/run_short.py
	$(PYTHON) tools/run_v3_short.py

pmu: build/bench build/bench_v3
	$(PYTHON) tools/run_pmu.py
	$(PYTHON) tools/run_v3_pmu.py

clean:
	rm -rf build generated/hwa16_constants.inc generated/manifest.json \
		generated/v3_constants.inc generated/v3_mapping_survey.json \
		results/short.json results/v3-short.json results/static-audit.json results/pmu.json \
		results/v3-pmu.json

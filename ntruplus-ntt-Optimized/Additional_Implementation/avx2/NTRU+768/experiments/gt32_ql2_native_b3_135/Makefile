ROOT := ../..
CC ?= gcc
CFLAGS := -O3 -mavx2 -march=native -fomit-frame-pointer -fno-pie -Wall -Wextra
LDFLAGS := -no-pie -Wl,--build-id=none
SB := /home/nuc/supercop-20260627/bench/nucpromtlhcubinucai1ummsb209
BUILD := build
CONTROL := ../gt32_ql2_shared_convergence_103/generated/basemul_ql2.s

.PHONY: check benchmark clean

$(BUILD):
	mkdir -p $@

$(BUILD)/control.o: $(CONTROL) | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

generated/ql2_lambda.inc: tools/generate_constants.py
	python3 $<

$(BUILD)/candidate.o: src/ql2_native_b3.S generated/ql2_lambda.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/test: tests/test.c src/tables.c $(BUILD)/control.o $(BUILD)/candidate.o
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

$(BUILD)/bench-normal: bench/bench.c src/tables.c $(BUILD)/control.o $(BUILD)/candidate.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(SB)/include/nontimecop/amd64 -o $@ $^ $(SB)/lib/nontimecop/amd64/libcpucycles.a

$(BUILD)/bench-reversed: bench/bench.c src/tables.c $(BUILD)/candidate.o $(BUILD)/control.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(SB)/include/nontimecop/amd64 -o $@ $^ $(SB)/lib/nontimecop/amd64/libcpucycles.a

$(BUILD)/pmu: bench/pmu.c src/tables.c $(BUILD)/control.o $(BUILD)/candidate.o
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

check: $(BUILD)/test
	./$(BUILD)/test
	python3 tools/audit.py

benchmark: check $(BUILD)/bench-normal $(BUILD)/bench-reversed
	python3 tools/run_benchmark.py
	$(MAKE) $(BUILD)/pmu
	python3 tools/run_pmu.py

clean:
	rm -rf $(BUILD) generated results

ROOT := ../..
CC ?= gcc
CFLAGS := -O3 -mavx2 -march=native -fomit-frame-pointer -fno-pie -Wall -Wextra
LDFLAGS := -no-pie -Wl,--build-id=none
SB := /home/nuc/supercop-20260627/bench/nucpromtlhcubinucai1ummsb209
BUILD := build

.PHONY: all check benchmark clean

all: generated/reopen-survey.json

$(BUILD):
	mkdir -p $@

generated/ql2_native_b3_e_minus1.S generated/reopen-survey.json: tools/generate_gate.py
	python3 $<

$(BUILD)/e0.o: ../gt32_ql2_native_b3_135/src/ql2_native_b3.S ../gt32_ql2_native_b3_135/generated/ql2_lambda.inc | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/em1.o: generated/ql2_native_b3_e_minus1.S | $(BUILD)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD)/test: tests/test.c $(BUILD)/e0.o $(BUILD)/em1.o
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

$(BUILD)/bench-normal: bench/bench.c $(BUILD)/e0.o $(BUILD)/em1.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(SB)/include/nontimecop/amd64 -o $@ $^ $(SB)/lib/nontimecop/amd64/libcpucycles.a

$(BUILD)/bench-reversed: bench/bench.c $(BUILD)/em1.o $(BUILD)/e0.o
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(SB)/include/nontimecop/amd64 -o $@ $^ $(SB)/lib/nontimecop/amd64/libcpucycles.a

check: all $(BUILD)/test
	./$(BUILD)/test

benchmark: check $(BUILD)/bench-normal $(BUILD)/bench-reversed
	python3 tools/run_benchmark.py

clean:
	rm -rf $(BUILD) generated results

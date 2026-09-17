ROOT:=../..
CC?=gcc
CFLAGS:=-O3 -mavx2 -march=native -mtune=native -fomit-frame-pointer -fno-pie -ffunction-sections -fdata-sections -Wall -Wextra
LDFLAGS:=-no-pie -Wl,--build-id=none -Wl,--gc-sections
SB:=/home/nuc/supercop-20260627/bench/nucpromtlhcubinucai1ummsb209
BUILD:=build
COMMON_C:=$(ROOT)/consts.c
COMMON_S:=$(ROOT)/ntt.s $(ROOT)/ntt_m.s $(ROOT)/pack.s generated/dual_output.s

.PHONY: generate check audit benchmark all clean

generate: generated/dual_output.s

generated/dual_output.s: tools/generate_asm.py
	python3 $<

$(BUILD):
	mkdir -p $@

$(BUILD)/test: tests/test.c $(COMMON_C) $(COMMON_S) generated/dual_output.s | $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Iinclude -o $@ tests/test.c $(COMMON_C) $(COMMON_S)

$(BUILD)/bench: bench/bench.c $(COMMON_C) $(COMMON_S) generated/dual_output.s | $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Iinclude -I$(SB)/include/nontimecop/amd64 -o $@ bench/bench.c $(COMMON_C) $(COMMON_S) $(SB)/lib/nontimecop/amd64/libcpucycles.a

check: $(BUILD)/test
	./$(BUILD)/test

audit: $(BUILD)/bench
	python3 tools/audit.py

benchmark: check audit
	python3 tools/run_benchmark.py

all: benchmark

clean:
	rm -rf $(BUILD) results/raw

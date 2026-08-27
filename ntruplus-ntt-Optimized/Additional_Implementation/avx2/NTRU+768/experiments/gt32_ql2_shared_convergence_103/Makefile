ROOT:=../..
CC?=gcc
CFLAGS:=-O3 -mavx2 -mbmi2 -mpopcnt -maes -march=native -mtune=native -fomit-frame-pointer -fno-pie -ffunction-sections -fdata-sections -Wall -Wextra
LDFLAGS:=-no-pie -Wl,--build-id=none -Wl,--gc-sections
SB:=/home/nuc/supercop-20260627/bench/nucpromtlhcubinucai1ummsb209
BUILD:=build
COMMON_C:=$(ROOT)/baseinv.c $(ROOT)/consts.c $(ROOT)/encap.c $(ROOT)/fips202.c $(ROOT)/poly.c $(ROOT)/symmetric.c src/candidate.c
COMMON_S:=$(ROOT)/add.s $(ROOT)/batch_inverse.s $(ROOT)/cbd.s $(ROOT)/ntt.s $(ROOT)/KeccakP-1600-AVX2.s generated/ntt_ql2.s generated/basemul_ql2.s generated/pack_ql2.s

.PHONY: generate check audit benchmark clean
generate: generated/ntt_ql2.s generated/basemul_ql2.s generated/pack_ql2.s
generated/ntt_ql2.s generated/basemul_ql2.s generated/pack_ql2.s generated/static.json: tools/generate_asm.py
	python3 $<
$(BUILD):
	mkdir -p $@
$(BUILD)/test: tests/test.c $(COMMON_C) $(COMMON_S) generated/static.json | $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Isrc -o $@ tests/test.c $(COMMON_C) $(COMMON_S)
$(BUILD)/bench: bench/bench.c $(COMMON_C) $(COMMON_S) generated/static.json | $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Isrc -I$(SB)/include/nontimecop/amd64 -o $@ bench/bench.c $(COMMON_C) $(COMMON_S) $(SB)/lib/nontimecop/amd64/libcpucycles.a
$(BUILD)/bench_pmu: bench/bench_pmu.c $(COMMON_C) $(COMMON_S) generated/static.json | $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Isrc -o $@ bench/bench_pmu.c $(COMMON_C) $(COMMON_S)
check: $(BUILD)/test
	./$(BUILD)/test
audit: $(BUILD)/bench $(BUILD)/bench_pmu
	mkdir -p results
	python3 tools/audit.py
	./$(BUILD)/bench_pmu > results/pmu.txt
benchmark: check audit
	python3 tools/run_benchmark.py
clean:
	rm -rf $(BUILD) generated results/raw results/benchmark.json results/pmu.txt

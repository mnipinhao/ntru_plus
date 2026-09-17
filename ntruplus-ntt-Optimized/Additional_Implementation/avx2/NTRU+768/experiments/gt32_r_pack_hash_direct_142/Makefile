ROOT:=../..
CC?=gcc
CFLAGS:=-O3 -mavx2 -mbmi2 -mpopcnt -maes -march=native -mtune=native -fomit-frame-pointer -fno-pie -ffunction-sections -fdata-sections -Wall -Wextra
LDFLAGS:=-no-pie -Wl,--build-id=none -Wl,--gc-sections -Wl,--undefined=ntruplus768_pack_m_highrange12699_avx2 -Wl,-T,$(ROOT)/e0v-tail.ld
SB:=/home/nuc/supercop-20260627/bench/nucpromtlhcubinucai1ummsb209
BUILD:=build
COMMON_C:=$(ROOT)/baseinv.c $(ROOT)/consts.c $(ROOT)/encap.c $(ROOT)/fips202.c $(ROOT)/poly.c $(ROOT)/symmetric.c src/candidate.c
COMMON_S:=$(ROOT)/add.s $(ROOT)/basemul.s $(ROOT)/batch_inverse.s $(ROOT)/cbd.s $(ROOT)/crepmod3.s $(ROOT)/invntt.s $(ROOT)/ntt.s $(ROOT)/ntt_m.s $(ROOT)/ntt_p.s $(ROOT)/pack.s $(ROOT)/KeccakP-1600-AVX2.s

.PHONY: check benchmark pmu clean
$(BUILD):
	mkdir -p $@
$(BUILD)/test: tests/test.c $(COMMON_C) $(COMMON_S) | $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Isrc -o $@ tests/test.c $(COMMON_C) $(COMMON_S)
$(BUILD)/bench: bench/bench.c $(COMMON_C) $(COMMON_S) | $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Isrc -I$(SB)/include/nontimecop/amd64 -o $@ bench/bench.c $(COMMON_C) $(COMMON_S) $(SB)/lib/nontimecop/amd64/libcpucycles.a
$(BUILD)/bench_pmu: bench/bench_pmu.c $(COMMON_C) $(COMMON_S) | $(BUILD)
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Isrc -o $@ bench/bench_pmu.c $(COMMON_C) $(COMMON_S)
check: $(BUILD)/test
	./$(BUILD)/test
benchmark: check $(BUILD)/bench
	python3 tools/run_benchmark.py
pmu: $(BUILD)/bench_pmu
	python3 tools/run_pmu.py
clean:
	rm -rf $(BUILD) results/raw results/benchmark.json results/pmu.json

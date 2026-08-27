ROOT:=../..
CFLAGS:=-O3 -mavx2 -mbmi2 -mpopcnt -maes -march=native -mtune=native -fomit-frame-pointer -fno-pie -ffunction-sections -fdata-sections -Wall -Wextra
LDFLAGS:=-no-pie -Wl,--build-id=none -Wl,--gc-sections
COMMON_C:=$(ROOT)/baseinv.c $(ROOT)/consts.c $(ROOT)/encap.c $(ROOT)/fips202.c $(ROOT)/poly.c $(ROOT)/symmetric.c
COMMON_S:=$(ROOT)/add.s $(ROOT)/batch_inverse.s $(ROOT)/cbd.s $(ROOT)/ntt.s $(ROOT)/KeccakP-1600-AVX2.s generated/ntt_ql2.s generated/basemul_fused.s generated/pack_ql2.s

.PHONY: all generate check audit benchmark clean
all: check audit
generate: generated/ntt_ql2.s generated/basemul_fused.s generated/pack_ql2.s
generated/ntt_ql2.s generated/basemul_fused.s generated/pack_ql2.s: tools/generate.py
	python3 tools/generate.py
build/test: generate tests/test.c src/candidate.c src/candidate.h
	mkdir -p build
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Isrc -o $@ tests/test.c src/candidate.c $(COMMON_C) $(COMMON_S)
check: build/test
	./build/test
build/bench: generate bench/bench.c src/candidate.c
	mkdir -p build
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Isrc -o $@ bench/bench.c src/candidate.c $(COMMON_C) $(COMMON_S)
build/bench_pmu: generate bench/bench_pmu.c src/candidate.c
	mkdir -p build
	$(CC) $(CFLAGS) $(LDFLAGS) -I$(ROOT) -Isrc -o $@ bench/bench_pmu.c src/candidate.c $(COMMON_C) $(COMMON_S)
audit: build/bench
	python3 tools/audit.py
benchmark: check audit
	python3 tools/run_benchmark.py
	$(MAKE) build/bench_pmu
	./build/bench_pmu > results/pmu.txt
clean:
	rm -rf build generated/*.s generated/*.json results/*.json results/raw

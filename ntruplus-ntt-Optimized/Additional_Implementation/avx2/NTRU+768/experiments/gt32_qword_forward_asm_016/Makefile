CC ?= gcc
PYTHON ?= python3
CFLAGS ?= -O3 -mavx2 -Wall -Wextra -Werror
ROOT := ../..
OFFICIAL_ROOT := ../../../../../../third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768
ASM := generated/qword_forward_asm.S
TEST := build/test_qword_forward
BENCH := build/bench_qword_kem
ROOT_C := $(ROOT)/baseinv.c $(ROOT)/consts.c $(ROOT)/decap.c \
	$(ROOT)/encap.c $(ROOT)/fips202.c $(ROOT)/keygen.c $(ROOT)/poly.c \
	$(ROOT)/symmetric.c
ROOT_ASM := $(ROOT)/add.s $(ROOT)/basemul.s $(ROOT)/batch_inverse.s \
	$(ROOT)/cbd.s $(ROOT)/crepmod3.s $(ROOT)/invntt.s $(ROOT)/ntt.s \
	$(ROOT)/ntt_m.s $(ROOT)/ntt_p.s $(ROOT)/pack.s \
	$(ROOT)/KeccakP-1600-AVX2.s

.PHONY: all check clean

all: $(TEST) $(BENCH)

$(ASM): tools/generate_qword_forward_asm.py ../gt32_cross_r3_qword_semantic_packet_013/generated/qword_semantic_packet_gate.json
	$(PYTHON) $< --output $@

$(TEST): test_qword_forward.c $(ASM) ../../ntt.s ../../ntt_m.s
	mkdir -p build
	$(CC) $(CFLAGS) -o $@ test_qword_forward.c $(ASM) ../../ntt.s ../../ntt_m.s

build/encap_qword.o: $(ROOT)/encap.c
	mkdir -p build
	$(CC) $(CFLAGS) -I$(ROOT) \
		-Dntruplus768_enc_derand_impl=ntruplus768_enc_derand_qword_impl \
		-Dntruplus768_ntt_frontend_avx2=gt32_qword_ntt_frontend_avx2 \
		-Dntruplus768_ntt_m_avx2=gt32_qword_ntt_m_avx2 -c $< -o $@

build/decap_qword.o: $(ROOT)/decap.c
	mkdir -p build
	$(CC) $(CFLAGS) -I$(ROOT) \
		-Dntruplus768_dec_impl=ntruplus768_dec_qword_impl \
		-Dntruplus768_ntt_frontend_avx2=gt32_qword_ntt_frontend_avx2 \
		-Dntruplus768_ntt_m_avx2=gt32_qword_ntt_m_avx2 -c $< -o $@

$(BENCH): bench_qword_kem.c $(ASM) build/encap_qword.o build/decap_qword.o \
		$(ROOT_C) $(ROOT_ASM) $(OFFICIAL_ROOT)/randombytes.c
	mkdir -p build
	$(CC) $(CFLAGS) -ffunction-sections -fdata-sections -Wl,--gc-sections \
		-I$(ROOT) -I$(OFFICIAL_ROOT) -o $@ bench_qword_kem.c $(ASM) \
		build/encap_qword.o build/decap_qword.o $(OFFICIAL_ROOT)/randombytes.c \
		$(ROOT_C) $(ROOT_ASM)

check: $(TEST) $(BENCH)
	$(TEST)
	$(BENCH)

bench: $(BENCH)
	$(BENCH)

clean:
	rm -rf build generated

CC ?= cc
PYTHON ?= python3
CFLAGS ?= -O3 -std=c11 -march=armv8-a+simd -I. -D__STDC_WANT_LIB_EXT1__=1
C_SRC := kem.c symmetric.c fips202.c base.c inverse.c inverse16_tail.c \
         pack.c support.c api_glue.c
ASM_SRC := ntt.S ntt_top.S ntt_tail.S ntt9.S \
           inverse_ntt.S inverse9.S inverse16.S crepmod3_raw.S

.PHONY: check kat kat-check clean

test_kem: test/test_kem.c randombytes.c $(C_SRC) $(ASM_SRC)
	$(CC) $(CFLAGS) $^ -o $@

PQCgenKAT_kem: kat/PQCgenKAT_kem.c kat/rng.c kat/aes.c $(C_SRC) $(ASM_SRC)
	$(CC) $(CFLAGS) -Ikat $^ -o $@

kat: PQCgenKAT_kem
	./PQCgenKAT_kem

kat-check: kat
	cmp PQCkemKAT_3488.rsp ../../ntruplus-ntt-Optimized/KAT/NTRU+1152/PQCkemKAT_3488.rsp
	shasum -a 256 PQCkemKAT_3488.rsp

check: test_kem kat-check
	./test_kem

clean:
	$(RM) test_kem PQCgenKAT_kem PQCkemKAT_3488.req PQCkemKAT_3488.rsp
	$(RM) -r *.dSYM

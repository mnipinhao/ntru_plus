CC = cc
PYTHON ?= python3
CFLAGS = -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE -fPIC -ffunction-sections -fdata-sections
.DEFAULT_GOAL := all
HEADERS := $(wildcard *.h NO_CE/*.h)
TOBYTES_OBJECTS := gt864_p47_decaps_compare.o gt864_p18_tobytes_full.o gt864_p18_tobytes_small.o gt864_tobytes.o
NATIVE_OBJECTS := gt864_native.o gt864_native_public.o gt864_native_baseinv_num.o gt864_native_baseinv_prefix.o gt864_native_baseinv_inverse.o gt864_native_baseinv_recover.o gt864_native_baseinv_finish.o
NATIVE_OBJECTS += gt864_p35_inverse16_ternary.o gt864_p35_inverse_tail_ternary.o
HASH_OBJECTS := hash_g_fixed.o keccakf1600.o
hash_g_fixed.o: hash_g_fixed.c
	$(CC) $(CFLAGS) -I. -c $< -o $@
keccakf1600.o: keccakf1600.S
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c $< -o $@
NATIVE_OBJECTS += gt864_crepmod3_raw.o gt864_native_basemul.o gt864_native_inverse9.o gt864_support_abi.o
$(NATIVE_OBJECTS): $(HEADERS) Makefile
gt864_native.o: gt864_native.c
	$(CC) $(CFLAGS) -I. -c $< -o $@
$(filter-out gt864_native.o,$(NATIVE_OBJECTS)): %.o: %.S
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c $< -o $@
$(filter %.o,$(TOBYTES_OBJECTS)): $(HEADERS) Makefile
gt864_tobytes.o: gt864_tobytes.c
	$(CC) $(CFLAGS) -I. -c $< -o $@
gt864_p47_decaps_compare.o: gt864_p47_decaps_compare.S gt864_p18_tobytes.h
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c $< -o $@
gt864_p18_tobytes_full.o: gt864_p18_tobytes_full.S gt864_p18_tobytes.h
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c $< -o $@
gt864_p18_tobytes_small.o: gt864_p18_tobytes_small.S gt864_p18_tobytes.h
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c $< -o $@
# Rebuild after headers or source-selection policy changes; avoid stale objects.
$(patsubst %.c,%.o,$(wildcard *.c)): $(HEADERS) Makefile
$(patsubst %.s,%.o,$(wildcard *.s)): $(HEADERS) Makefile
$(patsubst %.S,%.o,$(wildcard *.S)): $(HEADERS) Makefile
fips202.o kem-normal.o: $(HEADERS) Makefile
.PHONY: all check check-release manifest-check test abi canonical zeroization zeroization-source-check kat kat-check shared export-check clean
symmetric.o: symmetric.c
	$(CC) $(CFLAGS) -I. -x c -c symmetric.c -o symmetric.o
fips202.o: NO_CE/fips202.c
	$(CC) $(CFLAGS) -I. -x c -c NO_CE/fips202.c -o fips202.o
transform_api.o: transform_api.c
	$(CC) $(CFLAGS) -I. -x c -c transform_api.c -o transform_api.o
gt864_fr0_basemul_d1.o: gt864_fr0_basemul_d1.c
	$(CC) $(CFLAGS) -I. -x c -c gt864_fr0_basemul_d1.c -o gt864_fr0_basemul_d1.o
add.o: add.s
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -Dpoly_sub=gt864_raw_poly_sub -D_poly_sub=_gt864_raw_poly_sub -Dpoly_triple=gt864_raw_poly_triple -D_poly_triple=_gt864_raw_poly_triple -c add.s -o add.o
crepmod3.o: crepmod3.s
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -Dpoly_crepmod3=gt864_raw_poly_crepmod3 -D_poly_crepmod3=_gt864_raw_poly_crepmod3 -c crepmod3.s -o crepmod3.o
cbd.o: cbd.s
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -Dpoly_cbd1=gt864_raw_poly_cbd1 -D_poly_cbd1=_gt864_raw_poly_cbd1 -Dpoly_sotp_encode=gt864_raw_poly_sotp_encode -D_poly_sotp_encode=_gt864_raw_poly_sotp_encode -Dpoly_sotp_decode=gt864_raw_poly_sotp_decode -D_poly_sotp_decode=_gt864_raw_poly_sotp_decode -c cbd.s -o cbd.o
gt864_forward_poly_ntt.o: gt864_forward_poly_ntt.S
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c gt864_forward_poly_ntt.S -o gt864_forward_poly_ntt.o
gt864_forward_six_bank.o: gt864_forward_six_bank.S
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c gt864_forward_six_bank.S -o gt864_forward_six_bank.o
gt864_top_split.o: gt864_top_split.s
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c gt864_top_split.s -o gt864_top_split.o
cluster_transpose_frombytes.o: cluster_transpose_frombytes.c
	$(CC) $(CFLAGS) -I. -x c -c cluster_transpose_frombytes.c -o cluster_transpose_frombytes.o
byte_api.o: byte_api.c
	$(CC) $(CFLAGS) -I. -x c -c byte_api.c -o byte_api.o
kem-normal.o: kem.c
	$(CC) $(CFLAGS) -I. -Dpoly_ntt=gt_d1_poly_ntt -Dpoly_invntt=gt_d1_poly_invntt -Dpoly_baseinv=gt864_native_poly_baseinv -Dpoly_basemul=gt_d1_poly_basemul -Dpoly_basemul_add=gt_d1_poly_basemul_add -c kem.c -o kem-normal.o
KEM_OBJECTS := symmetric.o fips202.o transform_api.o gt864_fr0_basemul_d1.o
KEM_OBJECTS += add.o crepmod3.o cbd.o
KEM_OBJECTS += gt864_forward_poly_ntt.o gt864_forward_six_bank.o gt864_top_split.o
KEM_OBJECTS += cluster_transpose_frombytes.o byte_api.o kem-normal.o tail_layout.o
KEM_OBJECTS += $(TOBYTES_OBJECTS) $(NATIVE_OBJECTS) $(HASH_OBJECTS)

# The production contract is the directly linked KEM/KAT executables.  The
# shared object remains only as a benchmark/profiling compatibility target.
all: test_kem

shared: libgt864.so

libgt864.so: $(KEM_OBJECTS)
	$(CC) -shared -Wl,-Bsymbolic -Wl,--gc-sections $^ -o $@

tail_layout.o: tail_layout.S
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c $< -o $@

manifest-check:
	shasum -a 256 -c SOURCE-MANIFEST.sha256

test: test_kem test_abi
	./test_kem
	./test_abi

test_kem: test/test_kem.c randombytes.c $(KEM_OBJECTS)
	$(CC) $(CFLAGS) -I. $^ -Wl,--gc-sections -o $@

test_abi: test/test_abi.c test/abi_sentinel.S randombytes.c $(KEM_OBJECTS)
	$(CC) $(CFLAGS) -I. $^ -Wl,--gc-sections -o $@

test_canonical: test/test_canonical.c randombytes.c $(KEM_OBJECTS)
	$(CC) $(CFLAGS) -I. $^ -Wl,--gc-sections -o $@

kem-audit.o: kem.c
	$(CC) $(CFLAGS) -I. -DGT_SECURE_CLEAR_AUDIT_HOOK=1 -Dpoly_ntt=gt_d1_poly_ntt -Dpoly_invntt=gt_d1_poly_invntt -Dpoly_baseinv=gt864_native_poly_baseinv -Dpoly_basemul=gt_d1_poly_basemul -Dpoly_basemul_add=gt_d1_poly_basemul_add -c $< -o $@

symmetric-audit.o: symmetric.c
	$(CC) $(CFLAGS) -I. -DGT_SECURE_CLEAR_AUDIT_HOOK=1 -c $< -o $@

AUDIT_OBJECTS := $(filter-out kem-normal.o symmetric.o,$(KEM_OBJECTS)) kem-audit.o symmetric-audit.o
test_zeroization: test/test_zeroization.c randombytes.c $(AUDIT_OBJECTS)
	$(CC) $(CFLAGS) -I. -DGT_SECURE_CLEAR_AUDIT_HOOK=1 $^ -Wl,--gc-sections -o $@

PQCgenKAT_kem: kat/PQCgenKAT_kem.c kat/rng.c kat/aes.c $(KEM_OBJECTS)
	$(CC) $(CFLAGS) -I. -Ikat $^ -Wl,--gc-sections -o $@

kat: PQCgenKAT_kem
	./PQCgenKAT_kem

check-release:
	$(PYTHON) scripts/check_release.py

abi: test_abi
	./test_abi

canonical: test_canonical
	./test_canonical

zeroization-source-check:
	$(PYTHON) scripts/check_zeroization.py

zeroization: zeroization-source-check test_zeroization
	./test_zeroization

kat-check: kat
	cmp PQCkemKAT_2624.req kat/expected/PQCkemKAT_2624.req
	cmp PQCkemKAT_2624.rsp kat/expected/PQCkemKAT_2624.rsp
	shasum -a 256 PQCkemKAT_2624.rsp

export-check:
	$(PYTHON) scripts/export_supercop.py --self-check

check:
	$(MAKE) clean
	$(MAKE) check-release manifest-check test canonical zeroization kat-check export-check
	$(MAKE) clean

clean:
	rm -f *.o *.so test_kem test_abi test_canonical test_zeroization PQCgenKAT_kem PQCkemKAT_*.req PQCkemKAT_*.rsp

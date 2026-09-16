CC = cc
CFLAGS = -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE -fPIC -ffunction-sections -fdata-sections
.DEFAULT_GOAL := all
HEADERS := $(wildcard *.h NO_CE/*.h)
TOBYTES_OBJECTS := gt864_p47_decaps_compare.o gt864_p18_tobytes_full.o gt864_p18_tobytes_small.o gt864_tobytes.o gt864_tobytes_public.o gt864_tobytes_full_core.o gt864_tobytes_small_core.o gt864_tobytes_merge_core.o gt864_pair_merge_small.o gt864_pair_merge_full.o
NATIVE_OBJECTS := gt864_native.o gt864_native_public.o gt864_native_baseinv_num.o gt864_native_baseinv_prefix.o gt864_native_baseinv_inverse.o gt864_native_baseinv_recover.o gt864_native_baseinv_finish.o
NATIVE_OBJECTS += gt864_p35_inverse16_ternary.o gt864_p35_inverse_tail_ternary.o
NATIVE_OBJECTS += gt864_crepmod3_raw.o gt864_native_basemul.o gt864_native_center864.o gt864_native_inverse9.o gt864_native_inverse16_lazy.o gt864_native_inverse_tail_lazy.o gt864_support_abi.o
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
gt864_tobytes_public.o gt864_tobytes_full_core.o gt864_tobytes_small_core.o gt864_tobytes_merge_core.o gt864_pair_merge_small.o gt864_pair_merge_full.o: %.o: %.S
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c $< -o $@
# Rebuild after headers or source-selection policy changes; avoid stale objects.
$(patsubst %.c,%.o,$(wildcard *.c)): $(HEADERS) Makefile
$(patsubst %.s,%.o,$(wildcard *.s)): $(HEADERS) Makefile
$(patsubst %.S,%.o,$(wildcard *.S)): $(HEADERS) Makefile
fips202.o raw_pack.o kem-normal.o: $(HEADERS) Makefile
.PHONY: all check manifest-check test kat
all: libgt864.so
symmetric.o: symmetric.c
	$(CC) $(CFLAGS) -I. -x c -c symmetric.c -o symmetric.o
poly.o: poly.c
	$(CC) $(CFLAGS) -I. -x c -c poly.c -o poly.o
fips202.o: NO_CE/fips202.c
	$(CC) $(CFLAGS) -I. -x c -c NO_CE/fips202.c -o fips202.o
gt864_poly_api.o: gt864_poly_api.c
	$(CC) $(CFLAGS) -I. -x c -c gt864_poly_api.c -o gt864_poly_api.o
gt864_fr0_basemul.o: gt864_fr0_basemul.c
	$(CC) $(CFLAGS) -I. -x c -c gt864_fr0_basemul.c -o gt864_fr0_basemul.o
gt864_fr0_basemul_d1.o: gt864_fr0_basemul_d1.c
	$(CC) $(CFLAGS) -I. -x c -c gt864_fr0_basemul_d1.c -o gt864_fr0_basemul_d1.o
gt864_fr0_inverse_asm_wrapper.o: gt864_fr0_inverse_asm_wrapper.c
	$(CC) $(CFLAGS) -I. -x c -c gt864_fr0_inverse_asm_wrapper.c -o gt864_fr0_inverse_asm_wrapper.o
add.o: add.s
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -Dpoly_sub=gt864_raw_poly_sub -D_poly_sub=_gt864_raw_poly_sub -Dpoly_triple=gt864_raw_poly_triple -D_poly_triple=_gt864_raw_poly_triple -c add.s -o add.o
ntt.o: ntt.s
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c ntt.s -o ntt.o
base.o: base.s
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c base.s -o base.o
crepmod3.o: crepmod3.s
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -Dpoly_crepmod3=gt864_raw_poly_crepmod3 -D_poly_crepmod3=_gt864_raw_poly_crepmod3 -c crepmod3.s -o crepmod3.o
pack.o: pack.s
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c pack.s -o pack.o
cbd.o: cbd.s
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -Dpoly_cbd1=gt864_raw_poly_cbd1 -D_poly_cbd1=_gt864_raw_poly_cbd1 -Dpoly_sotp_encode=gt864_raw_poly_sotp_encode -D_poly_sotp_encode=_gt864_raw_poly_sotp_encode -Dpoly_sotp_decode=gt864_raw_poly_sotp_decode -D_poly_sotp_decode=_gt864_raw_poly_sotp_decode -c cbd.s -o cbd.o
gt864_forward_poly_ntt.o: gt864_forward_poly_ntt.S
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c gt864_forward_poly_ntt.S -o gt864_forward_poly_ntt.o
gt864_forward_six_bank.o: gt864_forward_six_bank.S
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c gt864_forward_six_bank.S -o gt864_forward_six_bank.o
gt864_top_split.o: gt864_top_split.s
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c gt864_top_split.s -o gt864_top_split.o
gt864_fr0_inverse9_block.o: gt864_fr0_inverse9_block.S
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c gt864_fr0_inverse9_block.S -o gt864_fr0_inverse9_block.o
gt864_inverse16_blocks.o: gt864_inverse16_blocks.s
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c gt864_inverse16_blocks.s -o gt864_inverse16_blocks.o
cluster_transpose_frombytes.o: cluster_transpose_frombytes.c
	$(CC) $(CFLAGS) -I. -x c -c cluster_transpose_frombytes.c -o cluster_transpose_frombytes.o
byte_api.o: byte_api.c
	$(CC) $(CFLAGS) -I. -x c -c byte_api.c -o byte_api.o
input_once_frombytes.o: input_once_frombytes.c
	$(CC) $(CFLAGS) -I. -x c -c input_once_frombytes.c -o input_once_frombytes.o
byte_boundary.o: byte_boundary.c
	$(CC) $(CFLAGS) -I. -x c -c byte_boundary.c -o byte_boundary.o
route9.o: route9.c
	$(CC) $(CFLAGS) -I. -x c -c route9.c -o route9.o
raw_pack.o: pack.s
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -Dpoly_tobytes_asm=raw_to -Dpoly_frombytes_asm=raw_from -Dpoly_shuffle_asm=raw_shuffle -Dpoly_shuffle2_asm=raw_shuffle2 -D_poly_tobytes_asm=_raw_to -D_poly_frombytes_asm=_raw_from -D_poly_shuffle_asm=_raw_shuffle -D_poly_shuffle2_asm=_raw_shuffle2 -c pack.s -o raw_pack.o
stock_wrapper.o: stock_wrapper.S
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c stock_wrapper.S -o stock_wrapper.o
kem-normal.o: kem.c
	$(CC) $(CFLAGS) -I. -Dpoly_ntt=gt_d1_poly_ntt -Dpoly_invntt=gt_d1_poly_invntt -Dpoly_baseinv=gt864_native_poly_baseinv -Dpoly_basemul=gt_d1_poly_basemul -Dpoly_basemul_add=gt_d1_poly_basemul_add -Dpoly_frombytes=p3b12_candidate_frombytes -c kem.c -o kem-normal.o
libgt864.so: symmetric.o poly.o fips202.o gt864_poly_api.o gt864_fr0_basemul.o gt864_fr0_basemul_d1.o gt864_fr0_inverse_asm_wrapper.o add.o ntt.o base.o crepmod3.o pack.o cbd.o gt864_forward_poly_ntt.o gt864_forward_six_bank.o gt864_top_split.o gt864_fr0_inverse9_block.o gt864_inverse16_blocks.o cluster_transpose_frombytes.o byte_api.o input_once_frombytes.o byte_boundary.o route9.o raw_pack.o stock_wrapper.o kem-normal.o tail_variants.o $(TOBYTES_OBJECTS) $(NATIVE_OBJECTS)
	$(CC) -shared -Wl,-Bsymbolic -Wl,--gc-sections symmetric.o poly.o fips202.o gt864_poly_api.o gt864_fr0_basemul.o gt864_fr0_basemul_d1.o gt864_fr0_inverse_asm_wrapper.o add.o ntt.o base.o crepmod3.o pack.o cbd.o gt864_forward_poly_ntt.o gt864_forward_six_bank.o gt864_top_split.o gt864_fr0_inverse9_block.o gt864_inverse16_blocks.o cluster_transpose_frombytes.o byte_api.o input_once_frombytes.o byte_boundary.o route9.o raw_pack.o stock_wrapper.o kem-normal.o tail_variants.o $(TOBYTES_OBJECTS) $(NATIVE_OBJECTS) -o libgt864.so

tail_variants.o: tail_variants.S
	$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c $< -o $@

manifest-check:
	shasum -a 256 -c SOURCE-MANIFEST.sha256

test: test_kem
	./test_kem

test_kem: test/test_kem.c randombytes.c libgt864.so
	$(CC) $(CFLAGS) -I. test/test_kem.c randombytes.c -L. -lgt864 -Wl,-rpath,'$$ORIGIN' -o $@

PQCgenKAT_kem: kat/PQCgenKAT_kem.c kat/rng.c kat/aes.c libgt864.so
	$(CC) $(CFLAGS) -I. -Ikat kat/PQCgenKAT_kem.c kat/rng.c kat/aes.c -L. -lgt864 -Wl,-rpath,'$$ORIGIN' -o $@

kat: PQCgenKAT_kem
	./PQCgenKAT_kem

check: manifest-check test kat

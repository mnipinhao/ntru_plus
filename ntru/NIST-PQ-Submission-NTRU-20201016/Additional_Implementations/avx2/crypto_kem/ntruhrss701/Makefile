
CC=/usr/bin/cc
LDFLAGS=-lcrypto
CFLAGS = -march=native -DCRYPTO_NAMESPACE\(s\)=ntru_\#\#s

SOURCES = cmov.c fips202.c kem.c owcpa.c pack3.c packq.c poly.c poly_r2_inv.c poly_s3_inv.c PQCgenKAT_kem.c rng.c sample.c sample_iid.c
HEADERS = api_bytes.h api.h cmov.h crypto_hash_sha3256.h fips202.h kem.h owcpa.h params.h poly.h poly_r2_inv.h rng.h sample.h
OBJS = poly_lift.s poly_mod_3_Phi_n.s poly_mod_q_Phi_n.s poly_r2_mul.s poly_rq_mul.s poly_rq_to_s3.s square_12_701_shufbytes.s square_15_701_shufbytes.s square_168_701_shufbytes.s square_1_701_patience.s square_27_701_shufbytes.s square_336_701_shufbytes.s square_3_701_patience.s square_42_701_shufbytes.s square_6_701_patience.s square_84_701_shufbytes.s vec32_sample_iid.s

PQCgenKAT_kem: $(HEADERS) $(SOURCES) $(OBJS) 
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) $(LDFLAGS)

.PHONY: clean

clean:
	-rm PQCgenKAT_kem

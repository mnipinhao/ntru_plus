#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "randombytes.h"

#include "tile4_kem_prepared_p0.h"
#include "tile4_kem_prepared_p0_control.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "publickeybytes", "secretkeybytes",
	"outputbytes", "ciphertextbytes", 0 };
const long long sizes[] = { crypto_kem_PUBLICKEYBYTES,
	crypto_kem_SECRETKEYBYTES, crypto_kem_BYTES,
	crypto_kem_CIPHERTEXTBYTES };

#define TIMINGS 32
static long long cycles[TIMINGS + 1];
static unsigned char *pk, *sk, *coins, *ct0, *ct1, *ss0, *ss1;
static gt32_prepared_pk_generic_p0 *generic_pk;
static gt32_prepared_sk_generic_p0 *generic_sk;
static gt32_prepared_pk_p0 *fixed_pk;
static gt32_prepared_sk_p0 *fixed_sk;
static volatile unsigned result_sink;

void preallocate(void) {}

static void require_equal(const char *label, const void *a, const void *b,
	size_t length)
{
	if (memcmp(a, b, length) != 0) {
		fprintf(stderr, "prepared-fixed differential failed: %s\n", label);
		abort();
	}
}

void allocate(void)
{
	pk = alignedcalloc(crypto_kem_PUBLICKEYBYTES);
	sk = alignedcalloc(crypto_kem_SECRETKEYBYTES);
	coins = alignedcalloc(NTRUPLUS_N / 8);
	ct0 = alignedcalloc(crypto_kem_CIPHERTEXTBYTES);
	ct1 = alignedcalloc(crypto_kem_CIPHERTEXTBYTES);
	ss0 = alignedcalloc(crypto_kem_BYTES);
	ss1 = alignedcalloc(crypto_kem_BYTES);
	generic_pk = (gt32_prepared_pk_generic_p0 *)(void *)alignedcalloc(
		sizeof *generic_pk);
	generic_sk = (gt32_prepared_sk_generic_p0 *)(void *)alignedcalloc(
		sizeof *generic_sk);
	fixed_pk = (gt32_prepared_pk_p0 *)(void *)alignedcalloc(sizeof *fixed_pk);
	fixed_sk = (gt32_prepared_sk_p0 *)(void *)alignedcalloc(sizeof *fixed_sk);

	crypto_kem_keypair(pk, sk);
	randombytes(coins, NTRUPLUS_N / 8);
	if (gt32_prepare_pk_generic_p0(generic_pk, pk) != 0 ||
		gt32_prepare_sk_generic_p0(generic_sk, sk) != 0 ||
		gt32_prepare_pk_p0(fixed_pk, pk) != 0 ||
		gt32_prepare_sk_p0(fixed_sk, sk) != 0)
		abort();
	gt32_enc_derand_prepared_generic_p0(ct0, ss0, generic_pk, coins);
	gt32_enc_derand_prepared_p0(ct1, ss1, fixed_pk, coins);
	require_equal("enc ciphertext", ct0, ct1, crypto_kem_CIPHERTEXTBYTES);
	require_equal("enc shared secret", ss0, ss1, crypto_kem_BYTES);
	gt32_dec_prepared_generic_p0(ss0, ct0, generic_sk);
	gt32_dec_prepared_p0(ss1, ct0, fixed_sk);
	require_equal("valid dec shared secret", ss0, ss1, crypto_kem_BYTES);
	for (size_t i = 0; i < 16; ++i) {
		ct1[i * (crypto_kem_CIPHERTEXTBYTES / 16)] ^= 1;
		int r0 = gt32_dec_prepared_generic_p0(ss0, ct1, generic_sk);
		int r1 = gt32_dec_prepared_p0(ss1, ct1, fixed_sk);
		if (r0 != r1)
			abort();
		require_equal("malformed dec shared secret", ss0, ss1,
			crypto_kem_BYTES);
		ct1[i * (crypto_kem_CIPHERTEXTBYTES / 16)] ^= 1;
	}
}

static void measure_void(const char *label, void (*fn)(void))
{
	for (int i = 0; i <= TIMINGS; ++i) {
		cycles[i] = cpucycles();
		fn();
	}
	for (int i = 0; i < TIMINGS; ++i)
		cycles[i] = cycles[i + 1] - cycles[i];
	printentry(-1, label, cycles, TIMINGS);
}

static void enc_generic(void) { result_sink += (unsigned)
	gt32_enc_derand_prepared_generic_p0(ct0, ss0, generic_pk, coins); }
static void enc_fixed(void) { result_sink += (unsigned)
	gt32_enc_derand_prepared_p0(ct1, ss1, fixed_pk, coins); }
static void dec_generic(void) { result_sink += (unsigned)
	gt32_dec_prepared_generic_p0(ss0, ct0, generic_sk); }
static void dec_fixed(void) { result_sink += (unsigned)
	gt32_dec_prepared_p0(ss1, ct0, fixed_sk); }
static void prepare_pk_generic(void) { result_sink += (unsigned)
	gt32_prepare_pk_generic_p0(generic_pk, pk); }
static void prepare_pk_fixed(void) { result_sink += (unsigned)
	gt32_prepare_pk_p0(fixed_pk, pk); }
static void prepare_sk_generic(void) { result_sink += (unsigned)
	gt32_prepare_sk_generic_p0(generic_sk, sk); }
static void prepare_sk_fixed(void) { result_sink += (unsigned)
	gt32_prepare_sk_p0(fixed_sk, sk); }
static void keypair_marker(void) { result_sink++; }

void measure(void)
{
	for (int loop = 0; loop < LOOPS; ++loop) {
		if ((loop & 1) == 0) {
			measure_void("keypair_cycles", keypair_marker);
			measure_void("enc_generic_cycles", enc_generic);
			measure_void("enc_fixed_cycles", enc_fixed);
			measure_void("dec_generic_cycles", dec_generic);
			measure_void("dec_fixed_cycles", dec_fixed);
			measure_void("prepare_pk_generic_cycles", prepare_pk_generic);
			measure_void("prepare_pk_fixed_cycles", prepare_pk_fixed);
			measure_void("prepare_sk_generic_cycles", prepare_sk_generic);
			measure_void("prepare_sk_fixed_cycles", prepare_sk_fixed);
		} else {
			measure_void("prepare_sk_fixed_cycles", prepare_sk_fixed);
			measure_void("prepare_sk_generic_cycles", prepare_sk_generic);
			measure_void("prepare_pk_fixed_cycles", prepare_pk_fixed);
			measure_void("prepare_pk_generic_cycles", prepare_pk_generic);
			measure_void("dec_fixed_cycles", dec_fixed);
			measure_void("dec_generic_cycles", dec_generic);
			measure_void("enc_fixed_cycles", enc_fixed);
			measure_void("enc_generic_cycles", enc_generic);
			measure_void("keypair_cycles", keypair_marker);
		}
	}
}

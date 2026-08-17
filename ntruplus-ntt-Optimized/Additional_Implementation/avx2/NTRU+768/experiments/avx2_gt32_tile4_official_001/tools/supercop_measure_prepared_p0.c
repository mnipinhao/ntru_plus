#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "randombytes.h"

#include "tile4_kem_prepared_p0.h"

extern int crypto_kem_enc_derand_gt32_candidate(unsigned char *,
	unsigned char *, const unsigned char *, const unsigned char *);
extern int crypto_kem_dec_gt32_native_rcheck_candidate(unsigned char *,
	const unsigned char *, const unsigned char *);

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
static gt32_prepared_pk_p0 *prepared_pk;
static gt32_prepared_sk_p0 *prepared_sk;
static volatile unsigned result_sink;

void preallocate(void) {}

static void require_equal(const char *label, const void *a, const void *b,
	size_t length)
{
	if (memcmp(a, b, length) != 0) {
		fprintf(stderr, "prepared differential failed: %s\n", label);
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
	prepared_pk = (gt32_prepared_pk_p0 *)(void *)alignedcalloc(
		sizeof *prepared_pk);
	prepared_sk = (gt32_prepared_sk_p0 *)(void *)alignedcalloc(
		sizeof *prepared_sk);

	crypto_kem_keypair(pk, sk);
	randombytes(coins, NTRUPLUS_N / 8);
	if (gt32_prepare_pk_p0(prepared_pk, pk) != 0 ||
		gt32_prepare_sk_p0(prepared_sk, sk) != 0)
		abort();
	crypto_kem_enc_derand_gt32_candidate(ct0, ss0, pk, coins);
	gt32_enc_derand_prepared_p0(ct1, ss1, prepared_pk, coins);
	require_equal("enc ciphertext", ct0, ct1, crypto_kem_CIPHERTEXTBYTES);
	require_equal("enc shared secret", ss0, ss1, crypto_kem_BYTES);
	crypto_kem_dec_gt32_native_rcheck_candidate(ss0, ct0, sk);
	gt32_dec_prepared_p0(ss1, ct0, prepared_sk);
	require_equal("valid dec shared secret", ss0, ss1, crypto_kem_BYTES);

	for (size_t i = 0; i < 16; ++i) {
		ct1[i * (crypto_kem_CIPHERTEXTBYTES / 16)] ^= 1;
		int r0 = crypto_kem_dec_gt32_native_rcheck_candidate(ss0, ct1, sk);
		int r1 = gt32_dec_prepared_p0(ss1, ct1, prepared_sk);
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

static void enc_control(void)
{
	result_sink += (unsigned)crypto_kem_enc_derand_gt32_candidate(
		ct0, ss0, pk, coins);
}

static void enc_prepared(void)
{
	result_sink += (unsigned)gt32_enc_derand_prepared_p0(
		ct1, ss1, prepared_pk, coins);
}

static void dec_control(void)
{
	result_sink += (unsigned)crypto_kem_dec_gt32_native_rcheck_candidate(
		ss0, ct0, sk);
}

static void dec_prepared(void)
{
	result_sink += (unsigned)gt32_dec_prepared_p0(ss1, ct0, prepared_sk);
}

static void prepare_pk(void)
{
	result_sink += (unsigned)gt32_prepare_pk_p0(prepared_pk, pk);
}

static void prepare_sk(void)
{
	result_sink += (unsigned)gt32_prepare_sk_p0(prepared_sk, sk);
}

static void keypair_control(void)
{
	/* Compatibility marker for the stock SUPERCOP result collector. */
	result_sink++;
}

void measure(void)
{
	for (int loop = 0; loop < LOOPS; ++loop) {
		if ((loop & 1) == 0) {
			measure_void("keypair_cycles", keypair_control);
			measure_void("enc_control_cycles", enc_control);
			measure_void("enc_prepared_cycles", enc_prepared);
			measure_void("dec_control_cycles", dec_control);
			measure_void("dec_prepared_cycles", dec_prepared);
			measure_void("prepare_pk_cycles", prepare_pk);
			measure_void("prepare_sk_cycles", prepare_sk);
		} else {
			measure_void("prepare_sk_cycles", prepare_sk);
			measure_void("prepare_pk_cycles", prepare_pk);
			measure_void("dec_prepared_cycles", dec_prepared);
			measure_void("dec_control_cycles", dec_control);
			measure_void("enc_prepared_cycles", enc_prepared);
			measure_void("enc_control_cycles", enc_control);
			measure_void("keypair_cycles", keypair_control);
		}
	}
}

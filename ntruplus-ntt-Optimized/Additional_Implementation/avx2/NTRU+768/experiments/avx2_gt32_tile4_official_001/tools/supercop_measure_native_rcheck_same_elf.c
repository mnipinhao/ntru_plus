#include <stdlib.h>
#include "randombytes.h"
#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "tile4.h"

extern int crypto_kem_dec_gt32_global_inverse_candidate(unsigned char *,
	const unsigned char *, const unsigned char *);
extern int crypto_kem_dec_gt32_native_rcheck_candidate(unsigned char *,
	const unsigned char *, const unsigned char *);

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "publickeybytes", "secretkeybytes",
	"outputbytes", "ciphertextbytes", 0 };
const long long sizes[] = { crypto_kem_PUBLICKEYBYTES,
	crypto_kem_SECRETKEYBYTES, crypto_kem_BYTES,
	crypto_kem_CIPHERTEXTBYTES };

static unsigned char *p, *s, *k, *c, *t0, *t1;
static int16_t *recovered, *derived;
static unsigned char *rbytes0, *rbytes1;
static volatile unsigned c5_sink;
#define TIMINGS 32
static long long cycles[TIMINGS + 1];

void preallocate(void) {}

void allocate(void)
{
	p = alignedcalloc(crypto_kem_PUBLICKEYBYTES);
	s = alignedcalloc(crypto_kem_SECRETKEYBYTES);
	k = alignedcalloc(crypto_kem_BYTES);
	c = alignedcalloc(crypto_kem_CIPHERTEXTBYTES);
	t0 = alignedcalloc(crypto_kem_BYTES);
	t1 = alignedcalloc(crypto_kem_BYTES);
	recovered = (int16_t *)(void *)alignedcalloc(
		GT32_TILE4_POLY_WORDS * sizeof *recovered);
	derived = (int16_t *)(void *)alignedcalloc(
		GT32_TILE4_POLY_WORDS * sizeof *derived);
	rbytes0 = alignedcalloc(GT32_TILE4_SERIALIZED_BYTES);
	rbytes1 = alignedcalloc(GT32_TILE4_SERIALIZED_BYTES);
	for (int i = 0; i < GT32_TILE4_POLY_WORDS; ++i) {
		recovered[i] = (int16_t)((i % 3823) - 1911);
		derived[i] = (int16_t)(recovered[i] + ((i % 5) - 2) * 3457);
	}
	gt32_q24_encode_soa_asm(rbytes0, recovered);
	crypto_kem_keypair(p, s);
	crypto_kem_enc(c, k, p);
}

static int verify_bytes_local(const unsigned char *a,
	const unsigned char *b, int length)
{
	unsigned char acc = 0;
	for (int i = 0; i < length; ++i)
		acc |= (unsigned char)(a[i] ^ b[i]);
	return (int)((-(unsigned long long)acc) >> 63);
}

static void c5_control(void)
{
	gt32_q24_encode_soa_lazy10788_asm(rbytes1, derived);
	c5_sink += (unsigned)verify_bytes_local(rbytes0, rbytes1,
		GT32_TILE4_SERIALIZED_BYTES);
}

static void c5_candidate(void)
{
	c5_sink += (unsigned)gt32_tile4_soa_equal_modq_12699_asm(recovered,
		derived);
}

static void measure_c5(const char *label, void (*fn)(void))
{
	int i;
	for (i = 0; i <= TIMINGS; ++i) {
		cycles[i] = cpucycles();
		fn();
	}
	for (i = 0; i < TIMINGS; ++i)
		cycles[i] = cycles[i + 1] - cycles[i];
	printentry(-1, label, cycles, TIMINGS);
}

static void measure_decap(const char *label,
	int (*fn)(unsigned char *, const unsigned char *, const unsigned char *),
	unsigned char *out)
{
	int i;
	for (i = 0; i <= TIMINGS; ++i) {
		cycles[i] = cpucycles();
		fn(out, c, s);
	}
	for (i = 0; i < TIMINGS; ++i)
		cycles[i] = cycles[i + 1] - cycles[i];
	printentry(-1, label, cycles, TIMINGS);
}

static void measure_keypair(const char *label)
{
	int i;
	for (i = 0; i <= TIMINGS; ++i) {
		cycles[i] = cpucycles();
		crypto_kem_keypair(p, s);
	}
	for (i = 0; i < TIMINGS; ++i)
		cycles[i] = cycles[i + 1] - cycles[i];
	printentry(-1, label, cycles, TIMINGS);
}

static void measure_encap(const char *label)
{
	int i;
	for (i = 0; i <= TIMINGS; ++i) {
		cycles[i] = cpucycles();
		crypto_kem_enc(c, k, p);
	}
	for (i = 0; i < TIMINGS; ++i)
		cycles[i] = cycles[i + 1] - cycles[i];
	printentry(-1, label, cycles, TIMINGS);
}

void measure(void)
{
	int loop;
	for (loop = 0; loop < LOOPS; ++loop) {
		if ((loop & 1) == 0) {
			measure_decap("dec_control_cycles",
				crypto_kem_dec_gt32_global_inverse_candidate, t0);
			measure_decap("dec_candidate_cycles",
				crypto_kem_dec_gt32_native_rcheck_candidate, t1);
			measure_encap("enc_control_cycles");
			measure_encap("enc_candidate_cycles");
			measure_keypair("keypair_control_cycles");
			measure_keypair("keypair_cycles");
			measure_c5("c5_control_cycles", c5_control);
			measure_c5("c5_candidate_cycles", c5_candidate);
		} else {
			measure_decap("dec_candidate_cycles",
				crypto_kem_dec_gt32_native_rcheck_candidate, t1);
			measure_decap("dec_control_cycles",
				crypto_kem_dec_gt32_global_inverse_candidate, t0);
			measure_encap("enc_candidate_cycles");
			measure_encap("enc_control_cycles");
			measure_keypair("keypair_cycles");
			measure_keypair("keypair_control_cycles");
			measure_c5("c5_candidate_cycles", c5_candidate);
			measure_c5("c5_control_cycles", c5_control);
		}
	}
}

#include <stdint.h>
#include <stdlib.h>

#ifdef SUPERCOP
#include "crypto_kem.h"
#endif
#include "api.h"

unsigned long long randombytes_calls;
unsigned long long randombytes_bytes;

static uint64_t random_state = UINT64_C(0x9e3779b97f4a7c15);
static volatile uint8_t benchmark_sink;

void crypto_declassify(const void *input, unsigned long long length)
{
	(void)input;
	(void)length;
}

void randombytes(unsigned char *output, unsigned long long length)
{
	randombytes_calls++;
	randombytes_bytes += length;
	for (unsigned long long i = 0; i < length; i++) {
		random_state ^= random_state << 7;
		random_state ^= random_state >> 9;
		random_state ^= random_state << 8;
		output[i] = (uint8_t)random_state;
	}
}

int main(int argc, char **argv)
{
	unsigned long iterations = 20000;
	unsigned char pk[NTRUPLUS_PUBLICKEYBYTES];
	unsigned char sk[NTRUPLUS_SECRETKEYBYTES];
	unsigned char ct[NTRUPLUS_CIPHERTEXTBYTES];
	unsigned char ss[NTRUPLUS_SSBYTES];

	if (argc == 2)
		iterations = strtoul(argv[1], 0, 10);
	if (crypto_kem_keypair(pk, sk) != 0)
		return 1;
	for (unsigned long i = 0; i < iterations; i++) {
		if (crypto_kem_enc(ct, ss, pk) != 0)
			return 2;
		benchmark_sink ^= ct[i % NTRUPLUS_CIPHERTEXTBYTES];
	}
	return 0;
}

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"

int gt034_encap_control(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);
int gt034_encap_candidate(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);

static uint64_t state = UINT64_C(0x034f011ca11e7a55);

static uint32_t random32(void)
{
	state ^= state << 13;
	state ^= state >> 7;
	state ^= state << 17;
	return (uint32_t)state;
}

static void pack_pair(uint8_t out[3], uint16_t a, uint16_t b)
{
	out[0] = (uint8_t)a;
	out[1] = (uint8_t)((a >> 8) | (b << 4));
	out[2] = (uint8_t)(b >> 4);
}

int main(void)
{
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES];
	uint8_t coins[NTRUPLUS_N / 8];
	uint8_t ct_control[NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t ct_candidate[NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t ss_control[NTRUPLUS_SSBYTES];
	uint8_t ss_candidate[NTRUPLUS_SSBYTES];
	for (size_t trial = 0; trial < 1000; trial++) {
		for (size_t i = 0; i < NTRUPLUS_N / 2; i++)
			pack_pair(pk + 3 * i, (uint16_t)(random32() % 3457),
				(uint16_t)(random32() % 3457));
		for (size_t i = 0; i < sizeof coins; i++)
			coins[i] = (uint8_t)random32();
		int rc_control = gt034_encap_control(ct_control, ss_control, pk, coins);
		int rc_candidate = gt034_encap_candidate(ct_candidate, ss_candidate, pk, coins);
		if (rc_control != rc_candidate
			|| memcmp(ct_control, ct_candidate, sizeof ct_control) != 0
			|| memcmp(ss_control, ss_candidate, sizeof ss_control) != 0) {
			fprintf(stderr, "full Encap mismatch trial=%zu\n", trial);
			return 1;
		}
	}
	puts("034 full Encap: 1000 deterministic byte-exact trials PASS");
	return 0;
}


#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "encap_lifetime_031.h"
#include "internal.h"

static uint64_t rng_state = UINT64_C(0x031c0ffee1234567);

static uint32_t random32(void)
{
	rng_state ^= rng_state << 13;
	rng_state ^= rng_state >> 7;
	rng_state ^= rng_state << 17;
	return (uint32_t)rng_state;
}

static void pack_pair(uint8_t out[3], uint16_t a, uint16_t b)
{
	out[0] = (uint8_t)a;
	out[1] = (uint8_t)((a >> 8) | (b << 4));
	out[2] = (uint8_t)(b >> 4);
}

static void canonical_pk(uint8_t pk[NTRUPLUS_PUBLICKEYBYTES])
{
	for (size_t i = 0; i < NTRUPLUS_N / 2; i++)
		pack_pair(pk + 3 * i, (uint16_t)(random32() % 3457),
			(uint16_t)(random32() % 3457));
}

static void set_slot(uint8_t pk[NTRUPLUS_PUBLICKEYBYTES], size_t slot,
	uint16_t value)
{
	size_t pair = slot / 2;
	uint16_t a = (uint16_t)(pk[3 * pair]
		| ((uint16_t)(pk[3 * pair + 1] & 15) << 8));
	uint16_t b = (uint16_t)((pk[3 * pair + 1] >> 4)
		| ((uint16_t)pk[3 * pair + 2] << 4));
	if ((slot & 1) == 0)
		a = value;
	else
		b = value;
	pack_pair(pk + 3 * pair, a, b);
}

static int compare_trace(const gt32_encap_031_trace *a,
	const gt32_encap_031_trace *b, size_t trial)
{
	if (memcmp(a, b, sizeof *a) != 0) {
		fprintf(stderr, "checkpoint mismatch trial=%zu\n", trial);
		return 0;
	}
	return 1;
}

int main(void)
{
	static gt32_encap_031_trace control, candidate;
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES];
	uint8_t coins[NTRUPLUS_N / 8];
	uint8_t prod_ct[NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t prod_ss[NTRUPLUS_SSBYTES];
	uint8_t candidate_ct[NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t candidate_ss[NTRUPLUS_SSBYTES];

	for (size_t trial = 0; trial < 1000; trial++) {
		canonical_pk(pk);
		for (size_t i = 0; i < sizeof coins; i++)
			coins[i] = (uint8_t)random32();
		if (gt32_encap_031_control_trace(&control, pk, coins) != 0
			|| gt32_encap_031_candidate_trace(&candidate, pk, coins) != 0
			|| !compare_trace(&control, &candidate, trial))
			return 1;
		if (ntruplus768_enc_derand_impl(prod_ct, prod_ss, pk, coins) != 0
			|| memcmp(prod_ct, candidate.ciphertext, sizeof prod_ct) != 0
			|| memcmp(prod_ss, candidate.shared_secret, sizeof prod_ss) != 0) {
			fprintf(stderr, "production mismatch trial=%zu\n", trial);
			return 1;
		}
		if (gt32_encap_lifetime_031(candidate_ct, candidate_ss, pk, coins) != 0
			|| memcmp(candidate_ct, prod_ct, sizeof prod_ct) != 0
			|| memcmp(candidate_ss, prod_ss, sizeof prod_ss) != 0) {
			fprintf(stderr, "candidate entry mismatch trial=%zu\n", trial);
			return 1;
		}
	}

	memset(pk, 0, sizeof pk);
	memset(coins, 0xa5, sizeof coins);
	for (size_t slot = 0; slot < NTRUPLUS_N; slot++) {
		uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES];
		uint8_t ss[NTRUPLUS_SSBYTES];
		uint8_t candidate_reject_ct[NTRUPLUS_CIPHERTEXTBYTES];
		uint8_t candidate_reject_ss[NTRUPLUS_SSBYTES];
		memset(pk, 0, sizeof pk);
		set_slot(pk, slot, 3457);
		memset(&control, 0x5a, sizeof control);
		memset(&candidate, 0x5a, sizeof candidate);
		memset(ct, 0x5a, sizeof ct);
		memset(ss, 0x5a, sizeof ss);
		memset(candidate_reject_ct, 0x5a, sizeof candidate_reject_ct);
		memset(candidate_reject_ss, 0x5a, sizeof candidate_reject_ss);
		if (gt32_encap_031_control_trace(&control, pk, coins) != 1
			|| gt32_encap_031_candidate_trace(&candidate, pk, coins) != 1
			|| memcmp(&control, &candidate, sizeof control) != 0
			|| gt32_encap_lifetime_031(candidate_reject_ct,
				candidate_reject_ss, pk, coins) != 1
			|| ntruplus768_enc_derand_impl(ct, ss, pk, coins) != 1) {
			fprintf(stderr, "noncanonical rejection mismatch slot=%zu\n", slot);
			return 1;
		}
		for (size_t i = 0; i < sizeof ct; i++)
			if (ct[i] != 0) {
				fprintf(stderr, "nonzero rejected ciphertext slot=%zu\n", slot);
				return 1;
			}
		for (size_t i = 0; i < sizeof ss; i++)
			if (ss[i] != 0) {
				fprintf(stderr, "nonzero rejected secret slot=%zu\n", slot);
				return 1;
			}
		if (memcmp(candidate_reject_ct, ct, sizeof ct) != 0
			|| memcmp(candidate_reject_ss, ss, sizeof ss) != 0) {
			fprintf(stderr, "candidate rejection output mismatch slot=%zu\n",
				slot);
			return 1;
		}
	}

	puts("031 spec gate: 1000 exact checkpoint trials + 768 noncanonical slots PASS");
	return 0;
}

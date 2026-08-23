#include "late066.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "internal.h"

static void exact_words(const char *label, unsigned trial,
	const int16_t expected[NTRUPLUS_N],
	const int16_t actual[NTRUPLUS_N])
{
	for (unsigned i = 0; i < NTRUPLUS_N; ++i) {
		if (expected[i] == actual[i])
			continue;
		fprintf(stderr,
			"%s trial=%u word=%u expected=%d actual=%d\n",
			label, trial, i, expected[i], actual[i]);
		exit(1);
	}
}
static void exact_bytes(const char *label, unsigned trial,
	const uint8_t *expected, const uint8_t *actual, size_t length)
{
	for (size_t i = 0; i < length; ++i) {
		if (expected[i] == actual[i])
			continue;
		fprintf(stderr,
			"%s trial=%u byte=%zu expected=%u actual=%u\n",
			label, trial, i, (unsigned)expected[i], (unsigned)actual[i]);
		exit(1);
	}
}

static void compare_decap_case(unsigned trial, const uint8_t *ct,
	const uint8_t *sk, int expect_valid, const uint8_t *expected_ss)
{
	uint8_t root_ss[NTRUPLUS_SSBYTES];
	uint8_t control_ss[NTRUPLUS_SSBYTES];
	uint8_t candidate_ss[NTRUPLUS_SSBYTES];
	const int root_fail = ntruplus768_dec_impl(root_ss, ct, sk);
	const int control_fail = late066_dec_control(control_ss, ct, sk);
	const int candidate_fail = late066_dec_candidate(candidate_ss, ct, sk);
	if (root_fail != control_fail || root_fail != candidate_fail) {
		fprintf(stderr, "decap-status trial=%u root=%d control=%d candidate=%d\n",
			trial, root_fail, control_fail, candidate_fail);
		exit(1);
	}
	exact_bytes("full-control", trial, root_ss, control_ss, sizeof root_ss);
	exact_bytes("full-candidate", trial, root_ss, candidate_ss,
		sizeof root_ss);
	if (expect_valid != 0) {
		if (root_fail != 0) {
			fprintf(stderr, "valid decapsulation rejected: trial=%u\n", trial);
			exit(1);
		}
		exact_bytes("encap-shared-secret", trial, expected_ss, root_ss,
			sizeof root_ss);
	}
}

int main(void)
{
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES];
	uint8_t sk[NTRUPLUS_SECRETKEYBYTES];
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t mutated[NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t enc_ss[NTRUPLUS_SSBYTES];
	uint8_t coins[NTRUPLUS_N / 8];
	uint8_t msg0[NTRUPLUS_N / 8];
	uint8_t msg1[NTRUPLUS_N / 8];
	uint8_t recovered0[NTRUPLUS_POLYBYTES];
	uint8_t recovered1[NTRUPLUS_POLYBYTES];
	int16_t c[NTRUPLUS_N] __attribute__((aligned(64)));
	int16_t f[NTRUPLUS_N] __attribute__((aligned(64)));
	int16_t hinv[NTRUPLUS_N] __attribute__((aligned(64)));
	int16_t post0[NTRUPLUS_N] __attribute__((aligned(64)));
	int16_t post1[NTRUPLUS_N] __attribute__((aligned(64)));
	int16_t crep0[NTRUPLUS_N] __attribute__((aligned(64)));
	int16_t crep1[NTRUPLUS_N] __attribute__((aligned(64)));
	late066_region_scratch scratch0;
	late066_region_scratch scratch1;
	unsigned valid_trials = 0;
	unsigned invalid_trials = 0;

	for (unsigned key = 0; key < 8; ++key) {
		if (ntruplus768_keypair_impl(pk, sk) != 0) {
			fprintf(stderr, "keypair failed\n");
			return 1;
		}
		for (unsigned trial = 0; trial < 32; ++trial) {
			for (unsigned i = 0; i < sizeof coins; ++i)
				coins[i] = (uint8_t)(17U * key + 29U * trial + 13U * i);
			if (ntruplus768_enc_derand_impl(ct, enc_ss, pk, coins) != 0
				|| ntruplus768_unpack3_m_avx2(c, f, hinv, ct, sk) != 0) {
				fprintf(stderr, "valid setup failed: key=%u trial=%u\n",
					key, trial);
				return 1;
			}

			late066_post_i1_control(post0, c, f, &scratch0);
			late066_post_i1_candidate(post1, c, f, &scratch1);
			exact_words("post-I1", valid_trials, post0, post1);
			late066_crep_control(crep0, c, f, &scratch0);
			late066_crep_candidate(crep1, c, f, &scratch1);
			exact_words("crepmod3", valid_trials, crep0, crep1);

			if (late066_recover_trace_control(msg0, recovered0, ct, sk)
				!= late066_recover_trace_candidate(msg1, recovered1, ct, sk)) {
				fprintf(stderr, "recover-status trial=%u\n", valid_trials);
				return 1;
			}
			exact_bytes("recovered-message", valid_trials, msg0, msg1,
				sizeof msg0);
			exact_bytes("recovered-r", valid_trials, recovered0, recovered1,
				sizeof recovered0);
			compare_decap_case(valid_trials, ct, sk, 1, enc_ss);
			++valid_trials;

			if (trial < 8) {
				memcpy(mutated, ct, sizeof mutated);
				mutated[(37U * trial + 11U * key) % sizeof mutated]
					^= (uint8_t)(1U << ((trial + key) & 7U));
				compare_decap_case(invalid_trials, mutated, sk, 0, NULL);
				++invalid_trials;
			}
		}
	}

	static const uint8_t fills[] = {0x00, 0xff, 0x55, 0xaa, 0x80};
	for (unsigned i = 0; i < sizeof fills; ++i) {
		memset(mutated, fills[i], sizeof mutated);
		compare_decap_case(invalid_trials, mutated, sk, 0, NULL);
		++invalid_trials;
	}

	printf("Late-SoA 066 correctness passed: valid=%u invalid=%u "
	       "postI1=exact crepmod3=exact trace=exact full=byte-exact\n",
		valid_trials, invalid_trials);
	return 0;
}

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gate_068.h"
#include "internal.h"
#include "poly.h"
#include "symmetric.h"

static uint64_t rng_state = UINT64_C(0x068c05ab1f4e299d);

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

static void make_inputs(uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	uint8_t coins[NTRUPLUS_N / 8])
{
	for (size_t i = 0; i < NTRUPLUS_N / 2; i++)
		pack_pair(pk + 3 * i, (uint16_t)(random32() % 3457),
			(uint16_t)(random32() % 3457));
	for (size_t i = 0; i < NTRUPLUS_N / 8; i++)
		coins[i] = (uint8_t)random32();
}

static int make_operands(int16_t h[NTRUPLUS_N], int16_t r[NTRUPLUS_N],
	int16_t m[NTRUPLUS_N], const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t hash[HASH_H_OUTBYTES];
	uint8_t r_bytes[NTRUPLUS_POLYBYTES];
	int16_t coefficients[NTRUPLUS_N] __attribute__((aligned(64)));
	int16_t frontend[NTRUPLUS_N] __attribute__((aligned(64)));

	if (ntruplus768_unpack_m_avx2(h, pk) != 0)
		return 0;
	memcpy(msg, coins, NTRUPLUS_N / 8);
	hash_f(msg + NTRUPLUS_N / 8, pk);
	hash_h(hash, msg);
	poly_cbd1((poly *)(void *)coefficients, hash + NTRUPLUS_SYMBYTES);
	ntruplus768_ntt_frontend_avx2(frontend, coefficients);
	ntruplus768_ntt_m_avx2(r, frontend);
	ntruplus768_pack_m_lazy10788_avx2(r_bytes, r);
	hash_g(r_bytes, r_bytes);
	poly_sotp_encode((poly *)(void *)coefficients, msg, r_bytes);
	ntruplus768_ntt_frontend_avx2(frontend, coefficients);
	ntruplus768_ntt_m_avx2(m, frontend);
	return 1;
}

int main(void)
{
	static int16_t h[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t r[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t m[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t scratch[8][NTRUPLUS_N] __attribute__((aligned(64)));
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES];
	uint8_t coins[NTRUPLUS_N / 8];
	uint8_t outputs[8][NTRUPLUS_POLYBYTES];
	gt32_068_fn functions[8] = {
		gt32_068_control_normal,
		gt32_068_reference_normal,
		gt32_068_candidate_normal,
		gt32_068_inline_normal,
		gt32_068_control_reversed,
		gt32_068_reference_reversed,
		gt32_068_candidate_reversed,
		gt32_068_inline_reversed,
	};
	const char *names[8] = {
		"control-normal", "reference-normal", "candidate-shared-normal",
		"candidate-inline-normal", "control-reversed", "reference-reversed",
		"candidate-shared-reversed", "candidate-inline-reversed",
	};

	for (size_t trial = 0; trial < 1000; trial++) {
		make_inputs(pk, coins);
		if (!make_operands(h, r, m, pk, coins)) {
			fprintf(stderr, "fixture failure at trial %zu\n", trial);
			return 1;
		}
		for (size_t variant = 0; variant < 8; variant++) {
			memset(outputs[variant], 0xa5, sizeof outputs[variant]);
			functions[variant](outputs[variant], h, r, m,
				scratch[variant]);
			if (memcmp(outputs[variant], outputs[0], sizeof outputs[0]) != 0) {
				for (size_t byte = 0; byte < sizeof outputs[0]; byte++) {
					if (outputs[variant][byte] != outputs[0][byte]) {
						fprintf(stderr, "%s mismatch trial=%zu byte=%zu "
							"got=%u expected=%u\n", names[variant], trial,
							byte, outputs[variant][byte], outputs[0][byte]);
						break;
					}
				}
				return 1;
			}
		}
	}
	puts("068 correctness: 1000 real-Encap operand trials, C0/C1/C2-shared/C2-inline normal/reversed byte-exact PASS");
	return 0;
}

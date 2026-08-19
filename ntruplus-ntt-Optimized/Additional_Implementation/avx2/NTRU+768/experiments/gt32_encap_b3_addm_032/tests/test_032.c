#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "encap_b3_addm_032.h"
#include "encap_lifetime_031.h"
#include "internal.h"
#include "poly.h"
#include "range_contract.h"
#include "symmetric.h"

typedef int (*encap_fn)(uint8_t *, uint8_t *, const uint8_t *,
	const uint8_t *);

static uint64_t rng_state = UINT64_C(0x032b3add5a17c0de);

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

static int all_zero(const uint8_t *value, size_t bytes)
{
	for (size_t i = 0; i < bytes; i++)
		if (value[i] != 0)
			return 0;
	return 1;
}

static int check_full(encap_fn fn, const char *name,
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8],
	const uint8_t expected_ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t expected_ss[NTRUPLUS_SSBYTES])
{
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t ss[NTRUPLUS_SSBYTES];
	if (fn(ct, ss, pk, coins) != 0
		|| memcmp(ct, expected_ct, sizeof ct) != 0
		|| memcmp(ss, expected_ss, sizeof ss) != 0) {
		fprintf(stderr, "%s full-caller mismatch\n", name);
		return 0;
	}
	return 1;
}

static int make_operands(int16_t h[NTRUPLUS_N], int16_t r_hat[NTRUPLUS_N],
	int16_t m_hat[NTRUPLUS_N], const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8], int *m_coeff_max)
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t buf[HASH_H_OUTBYTES];
	uint8_t r_bytes[NTRUPLUS_POLYBYTES];
	int16_t coeff[NTRUPLUS_N] __attribute__((aligned(64)));
	int16_t frontend[NTRUPLUS_N] __attribute__((aligned(64)));

	if (ntruplus768_unpack_m_avx2(h, pk) != 0)
		return 0;
	memcpy(msg, coins, NTRUPLUS_N / 8);
	hash_f(msg + NTRUPLUS_N / 8, pk);
	hash_h(buf, msg);
	poly_cbd1((poly *)(void *)coeff, buf + NTRUPLUS_SYMBYTES);
	ntruplus768_ntt_frontend_avx2(frontend, coeff);
	ntruplus768_ntt_m_avx2(r_hat, frontend);
	ntruplus768_pack_m_lazy10788_avx2(r_bytes, r_hat);
	hash_g(r_bytes, r_bytes);
	poly_sotp_encode((poly *)(void *)coeff, msg, r_bytes);
	for (size_t i = 0; i < NTRUPLUS_N; i++) {
		int value = coeff[i];
		int magnitude = value < 0 ? -value : value;
		if (magnitude > *m_coeff_max)
			*m_coeff_max = magnitude;
	}
	ntruplus768_ntt_frontend_avx2(frontend, coeff);
	ntruplus768_ntt_m_avx2(m_hat, frontend);
	return 1;
}

int main(void)
{
	static gt32_encap_031_trace trace;
	static int16_t h[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t outputs[4][NTRUPLUS_N] __attribute__((aligned(64)));
	uint8_t packed[4][NTRUPLUS_POLYBYTES];
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES];
	uint8_t coins[NTRUPLUS_N / 8];
	uint8_t expected_ct[NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t expected_ss[NTRUPLUS_SSBYTES];
	gt32_032_local_fn locals[4] = {
		gt32_032_local_control_normal,
		gt32_032_local_candidate_normal,
		gt32_032_local_control_reversed,
		gt32_032_local_candidate_reversed,
	};
	encap_fn callers[4] = {
		gt32_032_encap_control_normal,
		gt32_032_encap_candidate_normal,
		gt32_032_encap_control_reversed,
		gt32_032_encap_candidate_reversed,
	};
	const char *names[4] = {
		"control-normal", "candidate-normal",
		"control-reversed", "candidate-reversed",
	};
	int max_abs = 0;
	int m_coeff_max = 0;

	for (size_t trial = 0; trial < 1000; trial++) {
		canonical_pk(pk);
		for (size_t i = 0; i < sizeof coins; i++)
			coins[i] = (uint8_t)random32();
		if (!make_operands(h, trace.r_hat, trace.m_hat, pk, coins,
				&m_coeff_max)
			|| gt32_encap_031_candidate_trace(&trace, pk, coins) != 0
			|| gt32_encap_lifetime_031(expected_ct, expected_ss,
				pk, coins) != 0) {
			fprintf(stderr, "031 fixture failed trial=%zu\n", trial);
			return 1;
		}
		for (size_t variant = 0; variant < 4; variant++) {
			locals[variant](outputs[variant], h, trace.r_hat,
				trace.m_hat);
			ntruplus768_pack_m_highrange12699_avx2(packed[variant],
				outputs[variant]);
			if (memcmp(outputs[variant], outputs[0],
					sizeof outputs[0]) != 0
				|| memcmp(packed[variant], packed[0],
					sizeof packed[0]) != 0) {
				fprintf(stderr, "%s local mismatch trial=%zu\n",
					names[variant], trial);
				return 1;
			}
			if (!check_full(callers[variant], names[variant], pk, coins,
					expected_ct, expected_ss))
				return 1;
		}
		if (memcmp(packed[0], expected_ct, sizeof expected_ct) != 0) {
			fprintf(stderr, "Q24 serialization mismatch trial=%zu\n", trial);
			return 1;
		}
		for (size_t i = 0; i < NTRUPLUS_N; i++) {
			int value = outputs[0][i];
			int magnitude = value < 0 ? -value : value;
			if (magnitude > max_abs)
				max_abs = magnitude;
			if (magnitude > GT32_032_SUM_BOUND) {
				fprintf(stderr, "range failure trial=%zu lane=%zu value=%d "
					"m=%d b3=%d\n", trial, i, value,
					trace.m_hat[i], value - trace.m_hat[i]);
				return 1;
			}
		}
	}

	memset(coins, 0xa5, sizeof coins);
	for (size_t slot = 0; slot < NTRUPLUS_N; slot++) {
		memset(pk, 0, sizeof pk);
		set_slot(pk, slot, 3457);
		for (size_t variant = 0; variant < 4; variant++) {
			uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES];
			uint8_t ss[NTRUPLUS_SSBYTES];
			memset(ct, 0x5a, sizeof ct);
			memset(ss, 0x5a, sizeof ss);
			if (callers[variant](ct, ss, pk, coins) != 1
				|| !all_zero(ct, sizeof ct)
				|| !all_zero(ss, sizeof ss)) {
				fprintf(stderr, "%s rejection mismatch slot=%zu\n",
					names[variant], slot);
				return 1;
			}
		}
	}

	printf("032 correctness: 1000 exact local/full trials, max |m_coeff|=%d, "
		"max |word|=%d; 768-slot rejection PASS\n", m_coeff_max, max_abs);
	return 0;
}

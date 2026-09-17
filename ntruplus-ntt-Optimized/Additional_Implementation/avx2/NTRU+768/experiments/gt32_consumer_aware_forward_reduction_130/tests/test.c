#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "internal.h"

void gt32_130_control_normal(int16_t *, const int16_t *);
void gt32_130_candidate_normal(int16_t *, const int16_t *);

static uint64_t state = UINT64_C(0x130d1ff3a7c5e901);

static uint32_t random32(void)
{
	state ^= state << 13;
	state ^= state >> 7;
	state ^= state << 17;
	return (uint32_t)state;
}

static int modq(int value)
{
	value %= 3457;
	return value < 0 ? value + 3457 : value;
}

static void require_modq_equal(const int16_t *a, const int16_t *b,
	const char *where, size_t trial)
{
	for (size_t i = 0; i < NTRUPLUS_N; i++) {
		if (modq(a[i]) != modq(b[i])) {
			fprintf(stderr, "%s mismatch trial=%zu word=%zu: %d != %d\n",
				where, trial, i, a[i], b[i]);
			exit(1);
		}
	}
}

int main(void)
{
	static int16_t coeff_r[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t coeff_m[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t frontend_r[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t frontend_m[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t r0[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t r1[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t m0[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t m1[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t h[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t p0[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t p1[NTRUPLUS_N] __attribute__((aligned(64)));
	static uint8_t wire0[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
	static uint8_t wire1[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));

	for (size_t trial = 0; trial < 10000; trial++) {
		for (size_t i = 0; i < NTRUPLUS_N; i++) {
			coeff_r[i] = (int16_t)((int)(random32() % 3) - 1);
			coeff_m[i] = (int16_t)((int)(random32() % 3) - 1);
			h[i] = (int16_t)(random32() % 3457);
		}
		ntruplus768_ntt_frontend_avx2(frontend_r, coeff_r);
		ntruplus768_ntt_frontend_avx2(frontend_m, coeff_m);
		gt32_130_control_normal(r0, frontend_r);
		gt32_130_candidate_normal(r1, frontend_r);
		gt32_130_control_normal(m0, frontend_m);
		gt32_130_candidate_normal(m1, frontend_m);
		require_modq_equal(r0, r1, "Forward(r)", trial);
		require_modq_equal(m0, m1, "Forward(m)", trial);
		ntruplus768_pack_m_lazy10788_avx2(wire0, r0);
		ntruplus768_pack_m_lazy10788_avx2(wire1, r1);
		if (memcmp(wire0, wire1, sizeof wire0) != 0) {
			fprintf(stderr, "r Q24 mismatch trial=%zu\n", trial);
			return 1;
		}
		ntruplus768_basemul_general_m_avx2(p0, h, r0);
		ntruplus768_basemul_general_m_avx2(p1, h, r1);
		require_modq_equal(p0, p1, "general B3", trial);
		ntruplus768_pack_m_sum_highrange12699_avx2(wire0, p0, m0);
		ntruplus768_pack_m_sum_highrange12699_avx2(wire1, p1, m1);
		if (memcmp(wire0, wire1, sizeof wire0) != 0) {
			fprintf(stderr, "B3+m Q24 mismatch trial=%zu\n", trial);
			return 1;
		}
	}
	puts("PASS 10000 Forward/B3/Q24 differential trials");
	return 0;
}

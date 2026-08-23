#include "hwa16.h"

#include <string.h>

#define QINV 12929
#define RSQ 867
#define R (-147)

static const int16_t omega32_mont[32] = {
	-147, 484, -794, 874, 109, 864, -446, -554,
	366, -429, -1339, 11, -1118, 177, 1181, 1591,
	147, -484, 794, -874, -109, -864, 446, 554,
	-366, 429, 1339, -11, 1118, -177, -1181, -1591
};

static int16_t centered(int32_t x)
{
	x %= HWA16_Q;
	if (x < 0) x += HWA16_Q;
	if (x > HWA16_Q / 2) x -= HWA16_Q;
	return (int16_t)x;
}

static int16_t high16(int32_t x) { return (int16_t)(x >> 16); }

static int16_t mont(int16_t x, int16_t factor)
{
	const int16_t fq = (int16_t)(uint16_t)((uint32_t)(uint16_t)factor * QINV);
	const int16_t low = (int16_t)(uint16_t)((uint32_t)(uint16_t)x
		* (uint32_t)(uint16_t)fq);
	return (int16_t)(high16((int32_t)x * factor)
		- high16((int32_t)low * HWA16_Q));
}

static unsigned bitreverse(unsigned x, unsigned bits)
{
	unsigned y = 0;
	for (unsigned i = 0; i < bits; ++i) {
		y = (y << 1) | (x & 1U);
		x >>= 1;
	}
	return y;
}

static unsigned fwd_power(unsigned stage, unsigned group)
{
	if (stage == 1U) return 0;
	return bitreverse(group >> (6U - stage), stage - 1U) << (5U - stage);
}

static int16_t lambda_mont(unsigned q_index)
{
	/* branch=0,k3=0; calculate with the same finite-field convention. */
	int32_t x = 1;
	const unsigned power = (3U * bitreverse(q_index, 5)) % 96U;
	for (unsigned i = 0; i < power; ++i) x = (x * 675) % HWA16_Q;
	/* inverse(2)=1729. */
	x = (x * 1729) % HWA16_Q;
	x = (x * (65536 % HWA16_Q)) % HWA16_Q;
	return centered(x);
}

void hwa16_from_tile4(int16_t out[HWA16_WORDS], const int16_t in[HWA16_WORDS])
{
	int16_t tmp[HWA16_WORDS];
	for (unsigned c = 0; c < 4; ++c)
		for (unsigned q = 0; q < 32; ++q)
			tmp[32U * c + q] = in[16U * (q / 4U) + 4U * (q % 4U) + c];
	memcpy(out, tmp, sizeof(tmp));
}

void hwa16_to_tile4(int16_t out[HWA16_WORDS], const int16_t in[HWA16_WORDS])
{
	int16_t tmp[HWA16_WORDS];
	for (unsigned c = 0; c < 4; ++c)
		for (unsigned q = 0; q < 32; ++q)
			tmp[16U * (q / 4U) + 4U * (q % 4U) + c] = in[32U * c + q];
	memcpy(out, tmp, sizeof(tmp));
}

static const uint8_t v3_bits[HWA16_V3_MAPPINGS][5] = {
	{0, 3, 2, 1, 4},
	{0, 1, 2, 3, 4},
	{0, 2, 3, 1, 4}
};

static unsigned v3_q(enum hwa16_v3_mapping mapping, unsigned g, unsigned lane)
{
	const unsigned physical[5] = {
		g, (lane >> 3) & 1U, (lane >> 2) & 1U, (lane >> 1) & 1U, lane & 1U
	};
	unsigned q_index = 0;
	for (unsigned d = 0; d < 5; ++d)
		q_index |= physical[d] << v3_bits[(unsigned)mapping][d];
	return q_index;
}

void hwa16_v3_from_tile4(int16_t out[HWA16_WORDS], const int16_t in[HWA16_WORDS],
	enum hwa16_v3_mapping mapping)
{
	int16_t tmp[HWA16_WORDS];
	for (unsigned c = 0; c < 4; ++c)
		for (unsigned g = 0; g < 2; ++g)
			for (unsigned lane = 0; lane < 16; ++lane) {
				const unsigned q_index = v3_q(mapping, g, lane);
				tmp[32U * c + 16U * g + lane] =
					in[16U * (q_index / 4U) + 4U * (q_index % 4U) + c];
			}
	memcpy(out, tmp, sizeof(tmp));
}

void hwa16_v3_to_tile4(int16_t out[HWA16_WORDS], const int16_t in[HWA16_WORDS],
	enum hwa16_v3_mapping mapping)
{
	int16_t tmp[HWA16_WORDS];
	for (unsigned c = 0; c < 4; ++c)
		for (unsigned g = 0; g < 2; ++g)
			for (unsigned lane = 0; lane < 16; ++lane) {
				const unsigned q_index = v3_q(mapping, g, lane);
				tmp[16U * (q_index / 4U) + 4U * (q_index % 4U) + c] =
					in[32U * c + 16U * g + lane];
			}
	memcpy(out, tmp, sizeof(tmp));
}

static void forward_stream(int16_t x[32])
{
	for (unsigned stage = 1; stage <= 5; ++stage) {
		const unsigned distance = 32U >> stage;
		for (unsigned group = 0; group < 32; group += 2U * distance) {
			const int16_t factor = omega32_mont[fwd_power(stage, group)];
			for (unsigned j = 0; j < distance; ++j) {
				const int16_t low = x[group + j];
				const int16_t high = stage == 1U ? x[group + distance + j]
					: mont(x[group + distance + j], factor);
				x[group + j] = (int16_t)(low + high);
				x[group + distance + j] = (int16_t)(low - high);
			}
		}
	}
}

static void inverse_stream(int16_t x[32])
{
	for (unsigned length = 2; length <= 32; length <<= 1) {
		const unsigned distance = length >> 1;
		for (unsigned group = 0; group < 32; group += length)
			for (unsigned j = 0; j < distance; ++j) {
				const int16_t factor = omega32_mont[(32U - j * (32U / length)) & 31U];
				const int16_t low = x[group + j];
				const int16_t high = length == 2U ? x[group + distance + j]
					: mont(x[group + distance + j], factor);
				x[group + j] = (int16_t)(low + high);
				x[group + distance + j] = (int16_t)(low - high);
			}
	}
}

static void transform(int16_t out[HWA16_WORDS], const int16_t in[HWA16_WORDS], int inv)
{
	int16_t tmp[HWA16_WORDS];
	memcpy(tmp, in, sizeof(tmp));
	for (unsigned c = 0; c < 4; ++c) {
		int16_t x[32];
		memcpy(x, tmp + 32U * c, sizeof(x));
		if (inv) inverse_stream(x); else forward_stream(x);
		memcpy(out + 32U * c, x, sizeof(x));
	}
}

void hwa16_forward_ref(int16_t out[HWA16_WORDS], const int16_t in[HWA16_WORDS])
{
	transform(out, in, 0);
}

void hwa16_inverse_ref(int16_t out[HWA16_WORDS], const int16_t in[HWA16_WORDS])
{
	transform(out, in, 1);
}

void hwa16_basemul_ref(int16_t out[HWA16_WORDS], const int16_t a[HWA16_WORDS],
	const int16_t b[HWA16_WORDS])
{
	for (unsigned q = 0; q < 32; ++q) {
		const int16_t lambda = lambda_mont(q);
		int16_t av[4], bv[4], cv[4];
		for (unsigned c = 0; c < 4; ++c) {
			av[c] = a[32U * c + q];
			bv[c] = b[32U * c + q];
		}
		int16_t wrapped = (int16_t)(mont(av[1], bv[3]) + mont(av[2], bv[2]));
		wrapped = (int16_t)(wrapped + mont(av[3], bv[1]));
		cv[0] = (int16_t)(mont(wrapped, lambda) + mont(av[0], bv[0]));
		wrapped = (int16_t)(mont(av[2], bv[3]) + mont(av[3], bv[2]));
		cv[1] = (int16_t)(mont(wrapped, lambda) + mont(av[0], bv[1])
			+ mont(av[1], bv[0]));
		wrapped = mont(av[3], bv[3]);
		cv[2] = (int16_t)(mont(wrapped, lambda) + mont(av[0], bv[2])
			+ mont(av[1], bv[1]) + mont(av[2], bv[0]));
		cv[3] = centered((int32_t)mont(av[0], bv[3]) + mont(av[1], bv[2])
			+ mont(av[2], bv[1]) + mont(av[3], bv[0]));
		for (unsigned c = 0; c < 4; ++c) out[32U * c + q] = cv[c];
	}
	(void)RSQ;
	(void)R;
}

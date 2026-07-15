#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "gt_ntt_avx2.h"
#include "gt_ntt_tables.h"

#define QINV 12929
#define ZETA_TOP (-1033)
#define OMEGA3 (-886)

_Static_assert(sizeof(gt_frontend_scratch) == 1536,
	"frontend scratch contract changed");
_Static_assert(sizeof(gt_stage2_scratch) == 1536,
	"stage2 scratch contract changed");

/* Linked from the verified AArch64 portable GT reference. */
void ntt_gt_rowbitrevlayout(int16_t r[GT_NTT_N],
	const int16_t a[GT_NTT_N]);

static uint32_t rng_state = 1;

static uint32_t next_u32(void)
{
	uint32_t x = rng_state;

	x ^= x << 13;
	x ^= x >> 17;
	x ^= x << 5;
	rng_state = x;
	return x;
}

static int16_t montgomery_reduce(int32_t a)
{
	const int16_t t = (int16_t)a * QINV;

	return (int16_t)((a - (int32_t)t * GT_NTT_Q) >> 16);
}

static int16_t fqmul(int16_t a, int16_t b)
{
	return montgomery_reduce((int32_t)a * b);
}

static int16_t centered(int32_t a)
{
	int32_t r = a % GT_NTT_Q;

	if (r > GT_NTT_Q / 2) {
		r -= GT_NTT_Q;
	}
	if (r < -(GT_NTT_Q / 2)) {
		r += GT_NTT_Q;
	}
	return (int16_t)r;
}

static int16_t barrett_reduce(int16_t a)
{
	const int32_t v = ((1 << 26) + GT_NTT_Q / 2) / GT_NTT_Q;
	const int32_t quotient = (v * a + (1 << 25)) >> 26;

	return (int16_t)(a - quotient * GT_NTT_Q);
}

static int congruent(int16_t a, int16_t b)
{
	return centered((int32_t)a - b) == 0;
}

static int in_symmetric_bound(int16_t value, int bound)
{
	return (int)value >= -bound && (int)value <= bound;
}

static unsigned bitreverse_limited(unsigned x, unsigned bits)
{
	unsigned result = 0;

	for (unsigned i = 0; i < bits; i++) {
		result = (result << 1) | (x & 1U);
		x >>= 1;
	}
	return result;
}

static unsigned twiddle_power(unsigned stage, unsigned lo)
{
	if (stage == 1) {
		return 0;
	}
	return bitreverse_limited(lo >> (6 - stage), stage - 1)
		<< (5 - stage);
}

static unsigned input_index(unsigned n3, unsigned n32)
{
	return (64U * n3 + 33U * n32) % 96U;
}

static void scalar_frontend(int16_t rows[3][32][8],
	const int16_t in[GT_NTT_N])
{
	for (unsigned q = 0; q < 32; q++) {
		for (unsigned stream = 0; stream < 8; stream++) {
			const unsigned branch = stream >> 2;
			const unsigned lane = stream & 3U;
			int16_t x[3];

			for (unsigned n3 = 0; n3 < 3; n3++) {
				const unsigned n = input_index(n3, q);
				const int16_t low = in[4U * n + lane];
				const int16_t high = in[384U + 4U * n + lane];
				const int16_t split = fqmul(high, ZETA_TOP);
				const int16_t value = branch == 0
					? (int16_t)(low + split)
					: (int16_t)(low + high - split);

				x[n3] = fqmul(value, gt_twist[branch][n]);
			}

			{
				const int16_t t = fqmul(centered(x[1] - x[2]), OMEGA3);

				rows[0][q][stream] = centered(x[0] + x[1] + x[2]);
				rows[1][q][stream] = centered(x[0] - x[2] + t);
				rows[2][q][stream] = centered(x[0] - x[1] - t);
			}
		}
	}
}

static void scalar_stages12(int16_t rows[3][32][8])
{
	for (unsigned row = 0; row < 3; row++) {
		for (unsigned stage = 1; stage <= 2; stage++) {
			const unsigned distance = 1U << (5 - stage);

			for (unsigned lo = 0; lo < 32; lo++) {
				if ((lo & distance) != 0) {
					continue;
				}
				for (unsigned stream = 0; stream < 8; stream++) {
					const unsigned hi = lo + distance;
					const int16_t u = rows[row][lo][stream];
					const int16_t t = fqmul(rows[row][hi][stream],
						gt_omega32[twiddle_power(stage, lo)]);

					rows[row][lo][stream] = centered(u + t);
					rows[row][hi][stream] = centered(u - t);
				}
			}
		}
	}
}

static int check_montgomery(void)
{
	int16_t a[16];
	int16_t b[16];
	int16_t got[16];

	for (unsigned round = 0; round < 1000; round++) {
		for (unsigned lane = 0; lane < 16; lane++) {
			a[lane] = (int16_t)((int)(next_u32() % 55297U) - 27648);
			b[lane] = (int16_t)((int)(next_u32() % 3457U) - 1728);
		}
		gt_ntt_avx2_montgomery_test(got, a, b);
		for (unsigned lane = 0; lane < 16; lane++) {
			const int16_t want = fqmul(a[lane], b[lane]);

			if (got[lane] != want) {
				fprintf(stderr,
					"Montgomery mismatch round=%u lane=%u got=%d want=%d\n",
					round, lane, got[lane], want);
				return 1;
			}
		}
	}
	return 0;
}

static int check_barrett(void)
{
	int16_t input[16];
	int16_t got[16];

	for (int base = -27648; base <= 27648; base += 16) {
		for (unsigned lane = 0; lane < 16; lane++) {
			int value = base + (int)lane;

			if (value > 27648) {
				value = 27648;
			}
			input[lane] = (int16_t)value;
		}
		gt_ntt_avx2_barrett_test(got, input);
		for (unsigned lane = 0; lane < 16; lane++) {
			const int16_t want = barrett_reduce(input[lane]);

			if (got[lane] != want) {
				fprintf(stderr,
					"Barrett mismatch input=%d got=%d want=%d\n",
					input[lane], got[lane], want);
				return 1;
			}
		}
	}
	return 0;
}

static int check_frontend(const int16_t input[GT_NTT_N])
{
	gt_frontend_scratch got;
	int16_t want[3][32][8];

	gt_ntt_avx2_frontend(&got, input);
	scalar_frontend(want, input);
	for (unsigned q = 0; q < 32; q++) {
		for (unsigned stream = 0; stream < 8; stream++) {
			if (!in_symmetric_bound(got.row01[q][stream], 3 * 3456) ||
			    !in_symmetric_bound(got.row01[q][8 + stream], 3 * 3456) ||
			    !in_symmetric_bound(got.row2[q][stream], 3 * 3456)) {
				fprintf(stderr, "frontend range failure Q=%u stream=%u\n",
					q, stream);
				return 1;
			}
			if (!congruent(got.row01[q][stream], want[0][q][stream]) ||
			    !congruent(got.row01[q][8 + stream], want[1][q][stream]) ||
			    !congruent(got.row2[q][stream], want[2][q][stream])) {
				fprintf(stderr, "frontend mismatch Q=%u stream=%u\n",
					q, stream);
				return 1;
			}
		}
	}
	return 0;
}

static int check_stage2(const int16_t input[GT_NTT_N])
{
	gt_frontend_scratch frontend;
	gt_stage2_scratch got;
	int16_t want[3][32][8];

	gt_ntt_avx2_frontend(&frontend, input);
	gt_ntt_avx2_stage12(&got, &frontend);
	scalar_frontend(want, input);
	scalar_stages12(want);
	for (unsigned q = 0; q < 32; q++) {
		for (unsigned stream = 0; stream < 8; stream++) {
			if (!in_symmetric_bound(got.row01[q][stream], 5 * 3456) ||
			    !in_symmetric_bound(got.row01[q][8 + stream], 5 * 3456)) {
				fprintf(stderr, "row01 stage2 range failure Q=%u stream=%u\n",
					q, stream);
				return 1;
			}
			if (!congruent(got.row01[q][stream], want[0][q][stream]) ||
			    !congruent(got.row01[q][8 + stream], want[1][q][stream])) {
				fprintf(stderr, "row01 stage2 mismatch Q=%u stream=%u\n",
					q, stream);
				return 1;
			}
		}
	}
	for (unsigned q = 0; q < 16; q++) {
		for (unsigned stream = 0; stream < 8; stream++) {
			if (!in_symmetric_bound(got.row2_packed[q][stream], 5 * 3456) ||
			    !in_symmetric_bound(got.row2_packed[q][8 + stream], 5 * 3456)) {
				fprintf(stderr, "row2 stage2 range failure Q=%u stream=%u\n",
					q, stream);
				return 1;
			}
			if (!congruent(got.row2_packed[q][stream],
					want[2][q][stream]) ||
			    !congruent(got.row2_packed[q][8 + stream],
					want[2][q + 16][stream])) {
				fprintf(stderr, "row2 stage2 mismatch Q=%u stream=%u\n",
					q, stream);
				return 1;
			}
		}
	}
	return 0;
}

static int check_stage5_range(const int16_t input[GT_NTT_N])
{
	gt_frontend_scratch frontend;
	gt_stage2_scratch scratch;

	gt_ntt_avx2_frontend(&frontend, input);
	gt_ntt_avx2_stage12(&scratch, &frontend);
	gt_ntt_avx2_stage345(&scratch);
	for (unsigned q = 0; q < 32; q++) {
		for (unsigned lane = 0; lane < 16; lane++) {
			if (!in_symmetric_bound(scratch.row01[q][lane], 8 * 3456)) {
				fprintf(stderr, "row01 stage5 range failure Q=%u lane=%u\n",
					q, lane);
				return 1;
			}
		}
	}
	for (unsigned q = 0; q < 16; q++) {
		for (unsigned lane = 0; lane < 16; lane++) {
			if (!in_symmetric_bound(scratch.row2_packed[q][lane], 8 * 3456)) {
				fprintf(stderr, "row2 stage5 range failure Q=%u lane=%u\n",
					q, lane);
				return 1;
			}
		}
	}
	return 0;
}

static int check_full(const int16_t input[GT_NTT_N], const char *label)
{
	int16_t want[GT_NTT_N];
	int16_t got[GT_NTT_N];
	int16_t inplace[GT_NTT_N];

	ntt_gt_rowbitrevlayout(want, input);
	gt_ntt_avx2(got, input);
	memcpy(inplace, input, sizeof(inplace));
	gt_ntt_avx2(inplace, inplace);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (!congruent(got[i], want[i]) || got[i] != inplace[i]) {
			fprintf(stderr,
				"full mismatch case=%s i=%u got=%d want=%d inplace=%d\n",
				label, i, got[i], want[i], inplace[i]);
			return 1;
		}
		if (got[i] < -1729 || got[i] > 1729) {
			fprintf(stderr, "non-centered output case=%s i=%u value=%d\n",
				label, i, got[i]);
			return 1;
		}
	}
	return 0;
}

int main(void)
{
	int16_t input[GT_NTT_N];

	if (check_montgomery() != 0 || check_barrett() != 0) {
		return 1;
	}

	memset(input, 0, sizeof(input));
	input[0] = 1;
	if (check_frontend(input) != 0 || check_stage2(input) != 0 ||
	    check_stage5_range(input) != 0 || check_full(input, "impulse") != 0) {
		return 1;
	}

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		input[i] = (i & 1U) != 0 ? 3456 : -3456;
	}
	if (check_frontend(input) != 0 || check_stage2(input) != 0 ||
	    check_stage5_range(input) != 0 || check_full(input, "boundary") != 0) {
		return 1;
	}

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		input[i] = 3456;
	}
	if (check_frontend(input) != 0 || check_stage2(input) != 0 ||
	    check_stage5_range(input) != 0 || check_full(input, "all-max") != 0) {
		return 1;
	}

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		input[i] = -3456;
	}
	if (check_frontend(input) != 0 || check_stage2(input) != 0 ||
	    check_stage5_range(input) != 0 || check_full(input, "all-min") != 0) {
		return 1;
	}

	for (unsigned round = 0; round < 200; round++) {
		char label[32];

		for (unsigned i = 0; i < GT_NTT_N; i++) {
			input[i] = (int16_t)((int)(next_u32() % 6913U) - 3456);
		}
		(void)snprintf(label, sizeof(label), "random-%u", round);
		if (check_full(input, label) != 0) {
			return 1;
		}
		if (round < 8 && (check_frontend(input) != 0 ||
		    check_stage2(input) != 0 || check_stage5_range(input) != 0)) {
			return 1;
		}
	}

	puts("GT AVX2 prototype: all differential and layout tests passed");
	return 0;
}

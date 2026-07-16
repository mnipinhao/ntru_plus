#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "gt_basemul_soa.h"
#include "gt_invntt_soa.h"
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
void invntt_gt_rowbitrevlayout_exact(int16_t r[GT_NTT_N],
	const int16_t a[GT_NTT_N]);
void basemul(int16_t r[4], const int16_t a[4], const int16_t b[4],
	int16_t zeta);
extern const int16_t gt_rowbitrev_lambda[2][96];

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

static int16_t centered_i64(int64_t a)
{
	int64_t r = a % GT_NTT_Q;

	if (r > GT_NTT_Q / 2) {
		r -= GT_NTT_Q;
	}
	if (r < -(GT_NTT_Q / 2)) {
		r += GT_NTT_Q;
	}
	return (int16_t)r;
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

#if defined(GT_HAVE_AVX2_ASM)
static int check_packed_barrett_asm(void)
{
	int16_t input[16];
	int16_t got[16];

	for (int base = -8 * (GT_NTT_Q - 1);
	     base <= 8 * (GT_NTT_Q - 1); base += 16) {
		for (unsigned lane = 0; lane < 16; lane++) {
			const int value = base + (int)lane;

			input[lane] = (int16_t)(value <= 8 * (GT_NTT_Q - 1)
				? value : 8 * (GT_NTT_Q - 1));
		}
		gt_ntt_avx2_barrett_packed_asm(got, input);
		for (unsigned lane = 0; lane < 16; lane++) {
			const int value = base + (int)lane;

			if (value > 8 * (GT_NTT_Q - 1)) {
				continue;
			}
			if (!congruent(got[lane], input[lane]) || got[lane] < 0 ||
			    got[lane] > GT_NTT_Q) {
				fprintf(stderr,
					"packed ASM Barrett failure input=%d output=%d\n",
					value, got[lane]);
				return 1;
			}
		}
	}
	return 0;
}
#endif

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

static int check_soa_mapping(void)
{
	int16_t input[GT_NTT_N];
	int16_t soa[GT_NTT_N];
	int16_t roundtrip[GT_NTT_N];

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		input[i] = (int16_t)((int)i - GT_NTT_N / 2);
	}
	gt_ntt_rowbitrev_to_soa(soa, input);
	gt_ntt_soa_to_rowbitrev(roundtrip, soa);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (roundtrip[i] != input[i]) {
			fprintf(stderr, "SoA mapping round-trip mismatch i=%u\n", i);
			return 1;
		}
	}
	return 0;
}

static int16_t factor_qinv_ref(int16_t factor)
{
	return (int16_t)(uint16_t)((uint32_t)(uint16_t)factor * QINV);
}

static int check_soa_lambda_table(void)
{
	for (unsigned k3 = 0; k3 < 3; k3++) {
		for (unsigned q = 0; q < 32; q++) {
			const unsigned block = (32U * k3 + 3U * q) % 96U;
			const unsigned batch = 4U * k3 + q / 8U;

			for (unsigned branch = 0; branch < 2; branch++) {
				const unsigned lane = 8U * branch + q % 8U;
				const int16_t want =
					gt_rowbitrev_lambda[branch][block];

				if (gt_soa_lambda[batch][lane] != want ||
				    gt_soa_lambda_qinv[batch][lane] !=
					factor_qinv_ref(want)) {
					fprintf(stderr,
						"SoA lambda mismatch k3=%u Q=%u branch=%u\n",
						k3, q, branch);
					return 1;
				}
			}
		}
	}
	return 0;
}

static void basemul_rowbitrev_reference(int16_t out[GT_NTT_N],
	const int16_t a[GT_NTT_N], const int16_t b[GT_NTT_N])
{
	for (unsigned branch = 0; branch < 2; branch++) {
		for (unsigned block = 0; block < 96; block++) {
			const unsigned offset = 384U * branch + 4U * block;

			basemul(out + offset, a + offset, b + offset,
				gt_rowbitrev_lambda[branch][block]);
		}
	}
}

static void forward_soa(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N])
{
#if defined(GT_HAVE_AVX2_ASM)
	gt_ntt_avx2_asm_soa(out, in);
#else
	int16_t rowbitrev[GT_NTT_N];

	gt_ntt_avx2(rowbitrev, in);
	gt_ntt_rowbitrev_to_soa(out, rowbitrev);
#endif
}

static void schoolbook_mul(int16_t out[GT_NTT_N],
	const int16_t a[GT_NTT_N], const int16_t b[GT_NTT_N])
{
	int64_t temporary[2 * GT_NTT_N - 1] = {0};

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		for (unsigned j = 0; j < GT_NTT_N; j++) {
			temporary[i + j] += (int64_t)a[i] * b[j];
		}
	}
	/* X^768 = X^384 - 1. */
	for (int i = 2 * GT_NTT_N - 2; i >= GT_NTT_N; i--) {
		const int64_t value = temporary[i];

		temporary[i - GT_NTT_N / 2] += value;
		temporary[i - GT_NTT_N] -= value;
	}
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		out[i] = centered_i64(temporary[i]);
	}
}

#if defined(GT_HAVE_AVX2_ASM)
static int check_invntt_ntt32_asm_case(const int16_t input[GT_NTT_N],
	const char *label)
{
	int16_t want[GT_NTT_N] __attribute__((aligned(32)));
	int16_t got[GT_NTT_N] __attribute__((aligned(32)));

	gt_invntt_soa_ntt32_intrinsic(want, input);
	gt_invntt_soa_ntt32_asm(got, input);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (got[i] != want[i]) {
			fprintf(stderr,
				"inverse NTT32 ASM boundary mismatch case=%s i=%u got=%d want=%d\n",
				label, i, got[i], want[i]);
			return 1;
		}
		if (got[i] < 0 || got[i] > GT_NTT_Q) {
			fprintf(stderr,
				"inverse NTT32 ASM range failure case=%s i=%u value=%d\n",
				label, i, got[i]);
			return 1;
		}
	}
	return 0;
}

static int check_invntt_dft3_asm_rows(const int16_t rows[GT_NTT_N],
	const char *label)
{
	int16_t want[GT_NTT_N] __attribute__((aligned(32)));
	int16_t got[GT_NTT_N] __attribute__((aligned(32)));

	memcpy(want, rows, sizeof(want));
	memcpy(got, rows, sizeof(got));
	gt_invntt_soa_dft3_intrinsic(want);
	gt_invntt_soa_dft3_asm(got);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (got[i] != want[i]) {
			fprintf(stderr,
				"inverse DFT3 ASM boundary mismatch case=%s i=%u got=%d want=%d\n",
				label, i, got[i], want[i]);
			return 1;
		}
		if (got[i] < 0 || got[i] > GT_NTT_Q) {
			fprintf(stderr,
				"inverse DFT3 ASM range failure case=%s i=%u value=%d\n",
				label, i, got[i]);
			return 1;
		}
	}
	return 0;
}

static int check_invntt_dft3_asm_case(const int16_t input[GT_NTT_N],
	const char *label)
{
	int16_t rows[GT_NTT_N] __attribute__((aligned(32)));

	/* Build a valid [0,q] inverse-NTT32 scratch boundary first. */
	gt_invntt_soa_ntt32_intrinsic(rows, input);
	return check_invntt_dft3_asm_rows(rows, label);
}

static int check_invntt_postprocess_asm_rows(
	const int16_t rows[GT_NTT_N], const char *label)
{
	int16_t want[GT_NTT_N];
	int16_t got[GT_NTT_N];

	gt_invntt_soa_postprocess_intrinsic(want, rows);
	gt_invntt_soa_postprocess_asm(got, rows);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (got[i] != want[i]) {
			fprintf(stderr,
				"inverse postprocess ASM mismatch case=%s i=%u got=%d want=%d\n",
				label, i, got[i], want[i]);
			return 1;
		}
		if (!in_symmetric_bound(got[i], GT_NTT_Q - 1)) {
			fprintf(stderr,
				"inverse postprocess ASM range failure case=%s i=%u value=%d\n",
				label, i, got[i]);
			return 1;
		}
	}
	return 0;
}

static int check_invntt_postprocess_asm_case(
	const int16_t input[GT_NTT_N], const char *label)
{
	int16_t rows[GT_NTT_N] __attribute__((aligned(32)));

	gt_invntt_soa_ntt32_intrinsic(rows, input);
	gt_invntt_soa_dft3_intrinsic(rows);
	return check_invntt_postprocess_asm_rows(rows, label);
}
#endif

static int check_inverse_soa_case(const int16_t input[GT_NTT_N],
	const char *label)
{
	int16_t rowbitrev[GT_NTT_N];
	int16_t want[GT_NTT_N];
	int16_t got[GT_NTT_N];
	int16_t inplace[GT_NTT_N];
#if defined(GT_HAVE_AVX2_ASM)
	int16_t hybrid[GT_NTT_N];
	int16_t hybrid_inplace[GT_NTT_N];
	int16_t dft3_hybrid[GT_NTT_N];
	int16_t dft3_hybrid_inplace[GT_NTT_N];
	int16_t postprocess_hybrid[GT_NTT_N];
	int16_t postprocess_hybrid_inplace[GT_NTT_N];
	int16_t fused[GT_NTT_N];
	int16_t fused_inplace[GT_NTT_N];
#endif

	gt_ntt_soa_to_rowbitrev(rowbitrev, input);
	invntt_gt_rowbitrevlayout_exact(want, rowbitrev);
	gt_invntt_soa_avx2(got, input);
	memcpy(inplace, input, sizeof(inplace));
	gt_invntt_soa_avx2(inplace, inplace);
#if defined(GT_HAVE_AVX2_ASM)
	gt_invntt_soa_avx2_hybrid(hybrid, input);
	memcpy(hybrid_inplace, input, sizeof(hybrid_inplace));
	gt_invntt_soa_avx2_hybrid(hybrid_inplace, hybrid_inplace);
	gt_invntt_soa_avx2_dft3_hybrid(dft3_hybrid, input);
	memcpy(dft3_hybrid_inplace, input, sizeof(dft3_hybrid_inplace));
	gt_invntt_soa_avx2_dft3_hybrid(dft3_hybrid_inplace,
		dft3_hybrid_inplace);
	gt_invntt_soa_avx2_postprocess_hybrid(postprocess_hybrid, input);
	memcpy(postprocess_hybrid_inplace, input,
		sizeof(postprocess_hybrid_inplace));
	gt_invntt_soa_avx2_postprocess_hybrid(postprocess_hybrid_inplace,
		postprocess_hybrid_inplace);
	gt_invntt_soa_avx2_fused_asm(fused, input);
	memcpy(fused_inplace, input, sizeof(fused_inplace));
	gt_invntt_soa_avx2_fused_asm(fused_inplace, fused_inplace);
#endif
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (!congruent(got[i], want[i]) || got[i] != inplace[i]) {
			fprintf(stderr,
				"SoA inverse mismatch case=%s i=%u got=%d want=%d inplace=%d\n",
				label, i, got[i], want[i], inplace[i]);
			return 1;
		}
		if (!in_symmetric_bound(got[i], GT_NTT_Q - 1)) {
			fprintf(stderr,
				"SoA inverse range failure case=%s i=%u value=%d\n",
				label, i, got[i]);
			return 1;
		}
#if defined(GT_HAVE_AVX2_ASM)
		if (hybrid[i] != got[i] || hybrid[i] != hybrid_inplace[i]) {
			fprintf(stderr,
				"hybrid inverse mismatch case=%s i=%u hybrid=%d intrinsic=%d inplace=%d\n",
				label, i, hybrid[i], got[i], hybrid_inplace[i]);
			return 1;
		}
		if (dft3_hybrid[i] != got[i] ||
		    dft3_hybrid[i] != dft3_hybrid_inplace[i]) {
			fprintf(stderr,
				"DFT3 hybrid inverse mismatch case=%s i=%u hybrid=%d intrinsic=%d inplace=%d\n",
				label, i, dft3_hybrid[i], got[i],
				dft3_hybrid_inplace[i]);
			return 1;
		}
		if (postprocess_hybrid[i] != got[i] ||
		    postprocess_hybrid[i] != postprocess_hybrid_inplace[i]) {
			fprintf(stderr,
				"postprocess hybrid inverse mismatch case=%s i=%u hybrid=%d intrinsic=%d inplace=%d\n",
				label, i, postprocess_hybrid[i], got[i],
				postprocess_hybrid_inplace[i]);
			return 1;
		}
		if (fused[i] != got[i] || fused[i] != fused_inplace[i]) {
			fprintf(stderr,
				"fused ASM inverse mismatch case=%s i=%u fused=%d intrinsic=%d inplace=%d\n",
				label, i, fused[i], got[i], fused_inplace[i]);
			return 1;
		}
#endif
	}
	return 0;
}

static int check_polymul_soa_case(const int16_t a[GT_NTT_N],
	const int16_t b[GT_NTT_N], const char *label)
{
	int16_t a_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t b_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t product_soa[GT_NTT_N] __attribute__((aligned(32)));
	int16_t got[GT_NTT_N];
	int16_t want[GT_NTT_N];
#if defined(GT_HAVE_AVX2_ASM)
	int16_t hybrid[GT_NTT_N];
	int16_t dft3_hybrid[GT_NTT_N];
	int16_t postprocess_hybrid[GT_NTT_N];
	int16_t fused[GT_NTT_N];
#endif

	forward_soa(a_soa, a);
	forward_soa(b_soa, b);
	gt_basemul_soa_avx2(product_soa, a_soa, b_soa);
	gt_invntt_soa_avx2(got, product_soa);
#if defined(GT_HAVE_AVX2_ASM)
	gt_invntt_soa_avx2_hybrid(hybrid, product_soa);
	gt_invntt_soa_avx2_dft3_hybrid(dft3_hybrid, product_soa);
	gt_invntt_soa_avx2_postprocess_hybrid(postprocess_hybrid, product_soa);
	gt_invntt_soa_avx2_fused_asm(fused, product_soa);
#endif
	schoolbook_mul(want, a, b);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (!congruent(got[i], want[i])) {
			fprintf(stderr,
				"SoA polynomial multiplication mismatch case=%s i=%u got=%d want=%d\n",
				label, i, got[i], want[i]);
			return 1;
		}
#if defined(GT_HAVE_AVX2_ASM)
		if (hybrid[i] != got[i]) {
			fprintf(stderr,
				"hybrid polynomial multiplication mismatch case=%s i=%u hybrid=%d intrinsic=%d\n",
				label, i, hybrid[i], got[i]);
			return 1;
		}
		if (dft3_hybrid[i] != got[i]) {
			fprintf(stderr,
				"DFT3 hybrid polynomial multiplication mismatch case=%s i=%u hybrid=%d intrinsic=%d\n",
				label, i, dft3_hybrid[i], got[i]);
			return 1;
		}
		if (postprocess_hybrid[i] != got[i]) {
			fprintf(stderr,
				"postprocess hybrid polynomial multiplication mismatch case=%s i=%u hybrid=%d intrinsic=%d\n",
				label, i, postprocess_hybrid[i], got[i]);
			return 1;
		}
		if (fused[i] != got[i]) {
			fprintf(stderr,
				"fused ASM polynomial multiplication mismatch case=%s i=%u fused=%d intrinsic=%d\n",
				label, i, fused[i], got[i]);
			return 1;
		}
#endif
	}
	return 0;
}

static int check_basemul_soa_case(const int16_t a[GT_NTT_N],
	const int16_t b[GT_NTT_N], const char *label)
{
	int16_t a_rowbitrev[GT_NTT_N];
	int16_t b_rowbitrev[GT_NTT_N];
	int16_t want_rowbitrev[GT_NTT_N];
	int16_t want[GT_NTT_N];
	int16_t got[GT_NTT_N];

	gt_ntt_soa_to_rowbitrev(a_rowbitrev, a);
	gt_ntt_soa_to_rowbitrev(b_rowbitrev, b);
	basemul_rowbitrev_reference(want_rowbitrev, a_rowbitrev, b_rowbitrev);
	gt_ntt_rowbitrev_to_soa(want, want_rowbitrev);
	gt_basemul_soa_avx2(got, a, b);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (!congruent(got[i], want[i])) {
			fprintf(stderr,
				"SoA basemul mismatch case=%s i=%u got=%d want=%d\n",
				label, i, got[i], want[i]);
			return 1;
		}
		if (!in_symmetric_bound(got[i], GT_NTT_Q - 1)) {
			fprintf(stderr,
				"SoA basemul range failure case=%s i=%u value=%d\n",
				label, i, got[i]);
			return 1;
		}
	}
	return 0;
}

static int check_forward_basemul_case(const int16_t a[GT_NTT_N],
	const int16_t b[GT_NTT_N], const char *label)
{
	int16_t a_rowbitrev[GT_NTT_N];
	int16_t b_rowbitrev[GT_NTT_N];
	int16_t want_rowbitrev[GT_NTT_N];
	int16_t want[GT_NTT_N];
	int16_t a_soa[GT_NTT_N];
	int16_t b_soa[GT_NTT_N];
	int16_t got[GT_NTT_N];

	ntt_gt_rowbitrevlayout(a_rowbitrev, a);
	ntt_gt_rowbitrevlayout(b_rowbitrev, b);
	basemul_rowbitrev_reference(want_rowbitrev, a_rowbitrev, b_rowbitrev);
	gt_ntt_rowbitrev_to_soa(want, want_rowbitrev);
#if defined(GT_HAVE_AVX2_ASM)
	gt_ntt_avx2_asm_soa(a_soa, a);
	gt_ntt_avx2_asm_soa(b_soa, b);
#else
	gt_ntt_avx2(a_rowbitrev, a);
	gt_ntt_avx2(b_rowbitrev, b);
	gt_ntt_rowbitrev_to_soa(a_soa, a_rowbitrev);
	gt_ntt_rowbitrev_to_soa(b_soa, b_rowbitrev);
#endif
	gt_basemul_soa_avx2(got, a_soa, b_soa);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (!congruent(got[i], want[i])) {
			fprintf(stderr,
				"forward+SoA basemul mismatch case=%s i=%u got=%d want=%d\n",
				label, i, got[i], want[i]);
			return 1;
		}
	}
	return 0;
}

static int check_full(const int16_t input[GT_NTT_N], const char *label)
{
	int16_t want[GT_NTT_N];
	int16_t got[GT_NTT_N];
	int16_t inplace[GT_NTT_N];
#if defined(GT_HAVE_AVX2_ASM)
	int16_t want_soa[GT_NTT_N];
	int16_t got_soa[GT_NTT_N];
	int16_t inplace_soa[GT_NTT_N];
#endif
	int16_t inverse_input[GT_NTT_N] __attribute__((aligned(32)));
	int16_t inverse_output[GT_NTT_N];
#if defined(GT_HAVE_AVX2_ASM)
	int16_t hybrid_inverse_output[GT_NTT_N];
	int16_t dft3_hybrid_inverse_output[GT_NTT_N];
	int16_t postprocess_hybrid_inverse_output[GT_NTT_N];
	int16_t fused_inverse_output[GT_NTT_N];
#endif

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

#if defined(GT_HAVE_AVX2_ASM)
	gt_ntt_rowbitrev_to_soa(want_soa, want);
	gt_ntt_avx2_asm_soa(got_soa, input);
	memcpy(inplace_soa, input, sizeof(inplace_soa));
	gt_ntt_avx2_asm_soa(inplace_soa, inplace_soa);
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (!congruent(got_soa[i], want_soa[i]) ||
		    got_soa[i] != inplace_soa[i]) {
			fprintf(stderr,
				"ASM SoA mismatch case=%s i=%u got=%d want=%d inplace=%d\n",
				label, i, got_soa[i], want_soa[i], inplace_soa[i]);
			return 1;
		}
		if (got_soa[i] < 0 || got_soa[i] > GT_NTT_Q) {
			fprintf(stderr,
				"ASM SoA range failure case=%s i=%u value=%d\n",
				label, i, got_soa[i]);
			return 1;
		}
	}
#endif
	forward_soa(inverse_input, input);
	gt_invntt_soa_avx2(inverse_output, inverse_input);
#if defined(GT_HAVE_AVX2_ASM)
	gt_invntt_soa_avx2_hybrid(hybrid_inverse_output, inverse_input);
	gt_invntt_soa_avx2_dft3_hybrid(dft3_hybrid_inverse_output,
		inverse_input);
	gt_invntt_soa_avx2_postprocess_hybrid(
		postprocess_hybrid_inverse_output, inverse_input);
	gt_invntt_soa_avx2_fused_asm(fused_inverse_output, inverse_input);
#endif
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (!congruent(inverse_output[i], input[i])) {
			fprintf(stderr,
				"SoA round-trip mismatch case=%s i=%u got=%d want=%d\n",
				label, i, inverse_output[i], input[i]);
			return 1;
		}
#if defined(GT_HAVE_AVX2_ASM)
		if (hybrid_inverse_output[i] != inverse_output[i]) {
			fprintf(stderr,
				"hybrid SoA round-trip mismatch case=%s i=%u hybrid=%d intrinsic=%d\n",
				label, i, hybrid_inverse_output[i], inverse_output[i]);
			return 1;
		}
		if (dft3_hybrid_inverse_output[i] != inverse_output[i]) {
			fprintf(stderr,
				"DFT3 hybrid SoA round-trip mismatch case=%s i=%u hybrid=%d intrinsic=%d\n",
				label, i, dft3_hybrid_inverse_output[i],
				inverse_output[i]);
			return 1;
		}
		if (postprocess_hybrid_inverse_output[i] != inverse_output[i]) {
			fprintf(stderr,
				"postprocess hybrid SoA round-trip mismatch case=%s i=%u hybrid=%d intrinsic=%d\n",
				label, i, postprocess_hybrid_inverse_output[i],
				inverse_output[i]);
			return 1;
		}
		if (fused_inverse_output[i] != inverse_output[i]) {
			fprintf(stderr,
				"fused ASM SoA round-trip mismatch case=%s i=%u fused=%d intrinsic=%d\n",
				label, i, fused_inverse_output[i], inverse_output[i]);
			return 1;
		}
#endif
	}
	return 0;
}

int main(void)
{
	int16_t input[GT_NTT_N];
	int16_t basemul_a[GT_NTT_N];
	int16_t basemul_b[GT_NTT_N];
#if defined(GT_HAVE_AVX2_ASM)
	int16_t dft3_boundary[GT_NTT_N] __attribute__((aligned(32)));
#endif
	static const int16_t basemul_boundaries[] = {
		0, 1, -1, 1728, -1728, 3456, -3456, 3457, -3457
	};

	if (check_montgomery() != 0 || check_barrett() != 0 ||
	    check_soa_mapping() != 0 || check_soa_lambda_table() != 0) {
		return 1;
	}
#if defined(GT_HAVE_AVX2_ASM)
	if (check_packed_barrett_asm() != 0) {
		return 1;
	}
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		static const int16_t boundaries[] = {0, 1, GT_NTT_Q - 1, GT_NTT_Q};
		const unsigned row = i / (GT_NTT_N / 3U);

		dft3_boundary[i] = boundaries[(5U * i + row) % 4U];
	}
	if (check_invntt_dft3_asm_rows(dft3_boundary,
		"inverse-dft3-direct-boundary") != 0 ||
	    check_invntt_postprocess_asm_rows(dft3_boundary,
		"inverse-postprocess-direct-boundary") != 0) {
		return 1;
	}
#endif

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		const unsigned count = sizeof(basemul_boundaries) /
			sizeof(basemul_boundaries[0]);

		basemul_a[i] = basemul_boundaries[i % count];
		basemul_b[i] = basemul_boundaries[(3U * i + 1U) % count];
	}
	if (check_basemul_soa_case(basemul_a, basemul_b, "boundary") != 0) {
		return 1;
	}
	if (check_inverse_soa_case(basemul_a, "inverse-boundary") != 0) {
		return 1;
	}
#if defined(GT_HAVE_AVX2_ASM)
	if (check_invntt_ntt32_asm_case(basemul_a,
		"inverse-ntt32-boundary") != 0 ||
	    check_invntt_dft3_asm_case(basemul_a,
		"inverse-dft3-boundary") != 0 ||
	    check_invntt_postprocess_asm_case(basemul_a,
		"inverse-postprocess-boundary") != 0) {
		return 1;
	}
#endif
	for (unsigned i = 0; i < GT_NTT_N; i++) {
		if (basemul_a[i] == GT_NTT_Q || basemul_a[i] == -GT_NTT_Q) {
			basemul_a[i] = 0;
		}
		if (basemul_b[i] == GT_NTT_Q || basemul_b[i] == -GT_NTT_Q) {
			basemul_b[i] = 0;
		}
	}
	if (check_forward_basemul_case(basemul_a, basemul_b,
		"forward-boundary") != 0) {
		return 1;
	}
	for (unsigned round = 0; round < 200; round++) {
		char label[32];

		for (unsigned i = 0; i < GT_NTT_N; i++) {
			basemul_a[i] =
				(int16_t)((int)(next_u32() % 6915U) - 3457);
			basemul_b[i] =
				(int16_t)((int)(next_u32() % 6915U) - 3457);
		}
		(void)snprintf(label, sizeof(label), "basemul-random-%u", round);
		if (check_basemul_soa_case(basemul_a, basemul_b, label) != 0) {
			return 1;
		}
		if (round < 100 && check_inverse_soa_case(basemul_a, label) != 0) {
			return 1;
		}
#if defined(GT_HAVE_AVX2_ASM)
		if (round < 100 &&
		    check_invntt_ntt32_asm_case(basemul_a, label) != 0) {
			return 1;
		}
		if (round < 100 &&
		    check_invntt_dft3_asm_case(basemul_a, label) != 0) {
			return 1;
		}
		if (round < 100 &&
		    check_invntt_postprocess_asm_case(basemul_a, label) != 0) {
			return 1;
		}
#endif
		if (round < 16) {
			for (unsigned i = 0; i < GT_NTT_N; i++) {
				if (basemul_a[i] == GT_NTT_Q ||
				    basemul_a[i] == -GT_NTT_Q) {
					basemul_a[i] = 0;
				}
				if (basemul_b[i] == GT_NTT_Q ||
				    basemul_b[i] == -GT_NTT_Q) {
					basemul_b[i] = 0;
				}
			}
			if (check_forward_basemul_case(
				basemul_a, basemul_b, label) != 0) {
				return 1;
			}
		}
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

	for (unsigned i = 0; i < GT_NTT_N; i++) {
		basemul_a[i] = (i & 1U) != 0 ? 3456 : -3456;
		basemul_b[i] = i % 3U == 0 ? 3456 : (i % 3U == 1 ? -3456 : 0);
	}
	if (check_polymul_soa_case(basemul_a, basemul_b,
		"polymul-boundary") != 0) {
		return 1;
	}

	for (unsigned round = 0; round < 16; round++) {
		char label[32];

		for (unsigned i = 0; i < GT_NTT_N; i++) {
			basemul_a[i] = (int16_t)((int)(next_u32() % 3U) - 1);
			basemul_b[i] = (int16_t)((int)(next_u32() % 3U) - 1);
		}
		(void)snprintf(label, sizeof(label), "polymul-random-%u", round);
		if (check_polymul_soa_case(basemul_a, basemul_b, label) != 0) {
			return 1;
		}
	}

	puts("GT AVX2 forward/basemul/inverse: all differential, layout, and polynomial-product tests passed");
	return 0;
}

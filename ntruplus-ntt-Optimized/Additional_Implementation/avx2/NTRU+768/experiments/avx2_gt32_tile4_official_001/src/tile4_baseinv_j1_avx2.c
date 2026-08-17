#include <immintrin.h>
#include <stdint.h>

#include "tile4.h"
#include "../generated/tile4_basemul_constants.h"

#define QINV 12929

static inline __m256i fqmul(__m256i a, __m256i b, __m256i bqinv,
	__m256i q)
{
	const __m256i low = _mm256_mullo_epi16(a, bqinv);
	const __m256i high = _mm256_mulhi_epi16(a, b);
	return _mm256_sub_epi16(high, _mm256_mulhi_epi16(low, q));
}

static inline __m256i fqmul_auto(__m256i a, __m256i b, __m256i q,
	__m256i qinv)
{
	return fqmul(a, b, _mm256_mullo_epi16(b, qinv), q);
}

static inline __m256i fqsqr(__m256i a, __m256i q, __m256i qinv)
{
	return fqmul_auto(a, a, q, qinv);
}

static inline __m256i center_once(__m256i value, __m256i q)
{
	const __m256i halfq = _mm256_set1_epi16(GT32_TILE4_Q / 2);
	const __m256i minus_halfq = _mm256_set1_epi16(-(GT32_TILE4_Q / 2));
	value = _mm256_sub_epi16(value,
		_mm256_and_si256(_mm256_cmpgt_epi16(value, halfq), q));
	value = _mm256_add_epi16(value,
		_mm256_and_si256(_mm256_cmpgt_epi16(minus_halfq, value), q));
	return value;
}

static inline __m256i fqinv(__m256i value, __m256i q, __m256i qinv)
{
	const __m256i value_qinv = _mm256_mullo_epi16(value, qinv);
	__m256i t0 = fqsqr(value, q, qinv);
	t0 = fqsqr(t0, q, qinv);
	t0 = fqsqr(t0, q, qinv);
	t0 = fqsqr(t0, q, qinv);
	__m256i t1 = fqmul(t0, value, value_qinv, q);

	__m256i t1_qinv = _mm256_mullo_epi16(t1, qinv);
	t0 = fqsqr(t0, q, qinv);
	t0 = fqsqr(t0, q, qinv);
	t0 = fqsqr(t0, q, qinv);
	t1 = fqmul(t0, t1, t1_qinv, q);

	t1_qinv = _mm256_mullo_epi16(t1, qinv);
	t0 = fqmul(t0, t1, t1_qinv, q);
	t1 = fqmul(t0, t1, t1_qinv, q);
	const __m256i t0_qinv = _mm256_mullo_epi16(t0, qinv);
	t1 = fqmul(t1, t0, t0_qinv, q);
	t0 = fqsqr(t1, q, qinv);
	t0 = fqsqr(t0, q, qinv);
	t1_qinv = _mm256_mullo_epi16(t1, qinv);
	return fqmul(t0, t1, t1_qinv, q);
}

static inline void transpose4(__m256i in0, __m256i in1, __m256i in2,
	__m256i in3, __m256i *out0, __m256i *out1, __m256i *out2,
	__m256i *out3)
{
	const __m256i t0 = _mm256_unpacklo_epi16(in0, in1);
	const __m256i t1 = _mm256_unpackhi_epi16(in0, in1);
	const __m256i t2 = _mm256_unpacklo_epi16(in2, in3);
	const __m256i t3 = _mm256_unpackhi_epi16(in2, in3);
	const __m256i u0 = _mm256_unpacklo_epi32(t0, t2);
	const __m256i u1 = _mm256_unpackhi_epi32(t0, t2);
	const __m256i u2 = _mm256_unpacklo_epi32(t1, t3);
	const __m256i u3 = _mm256_unpackhi_epi32(t1, t3);
	*out0 = _mm256_unpacklo_epi64(u0, u2);
	*out1 = _mm256_unpackhi_epi64(u0, u2);
	*out2 = _mm256_unpacklo_epi64(u1, u3);
	*out3 = _mm256_unpackhi_epi64(u1, u3);
}

static int batch_inverse_j1(__m256i denominator[12], __m256i q,
	__m256i qinv)
{
	/* Six independent two-vector chains, matching Official's ILP topology. */
	__m256i prefix[12];
	__m256i operand_qinv[12];
	for (unsigned chain = 0; chain < 6; chain++) {
		const unsigned offset = 2U * chain;
		prefix[offset] = denominator[offset];
		operand_qinv[offset + 1] = _mm256_mullo_epi16(
			denominator[offset + 1], qinv);
		prefix[offset + 1] = fqmul(prefix[offset], denominator[offset + 1],
			operand_qinv[offset + 1], q);
	}
	const __m256i zero = _mm256_setzero_si256();
	__m256i zero_lanes = _mm256_cmpeq_epi16(prefix[1], zero);
	for (unsigned chain = 1; chain < 6; chain++)
		zero_lanes = _mm256_or_si256(zero_lanes,
			_mm256_cmpeq_epi16(prefix[2U * chain + 1U], zero));
	const int failure = !_mm256_testz_si256(zero_lanes, zero_lanes);

	__m256i r1[6], r1_qinv[6];
	for (unsigned i = 0; i < 6; i++) {
		r1[i] = prefix[2U * i + 1U];
		r1_qinv[i] = _mm256_mullo_epi16(r1[i], qinv);
	}
	__m256i r2[3] = {
		fqmul(r1[0], r1[1], r1_qinv[1], q),
		fqmul(r1[2], r1[3], r1_qinv[3], q),
		fqmul(r1[4], r1[5], r1_qinv[5], q),
	};
	__m256i r2_qinv[3];
	for (unsigned i = 0; i < 3; i++)
		r2_qinv[i] = _mm256_mullo_epi16(r2[i], qinv);
	__m256i pc2[3];
	pc2[0] = r2[0];
	pc2[1] = fqmul(pc2[0], r2[1], r2_qinv[1], q);
	pc2[2] = fqmul(pc2[1], r2[2], r2_qinv[2], q);
	__m256i pc2_qinv[2] = {
		_mm256_mullo_epi16(pc2[0], qinv),
		_mm256_mullo_epi16(pc2[1], qinv),
	};

	__m256i inverse = fqinv(pc2[2], q, qinv);
	__m256i inv1[3];
	inv1[2] = fqmul(inverse, pc2[1], pc2_qinv[1], q);
	inverse = fqmul(inverse, r2[2], r2_qinv[2], q);
	inv1[1] = fqmul(inverse, pc2[0], pc2_qinv[0], q);
	inverse = fqmul(inverse, r2[1], r2_qinv[1], q);
	inv1[0] = inverse;

	__m256i inv0[6];
	inv0[1] = fqmul(inv1[0], r1[0], r1_qinv[0], q);
	inv0[0] = fqmul(inv1[0], r1[1], r1_qinv[1], q);
	inv0[3] = fqmul(inv1[1], r1[2], r1_qinv[2], q);
	inv0[2] = fqmul(inv1[1], r1[3], r1_qinv[3], q);
	inv0[5] = fqmul(inv1[2], r1[4], r1_qinv[4], q);
	inv0[4] = fqmul(inv1[2], r1[5], r1_qinv[5], q);
	for (unsigned chain = 0; chain < 6; chain++) {
		const unsigned offset = 2U * chain;
		const __m256i second = denominator[offset + 1U];
		const __m256i inv_qinv = _mm256_mullo_epi16(inv0[chain], qinv);
		denominator[offset + 1] = fqmul(prefix[offset], inv0[chain],
			inv_qinv, q);
		denominator[offset] = fqmul(inv0[chain], second,
			operand_qinv[offset + 1U], q);
	}
	/*
	 * det has e=-3.  This simple 12-way Montgomery trick yields each
	 * reciprocal at e=5; J1's numerator finalizer needs e=4.
	 */
	const __m256i one = _mm256_set1_epi16(1);
	for (unsigned i = 0; i < 12; i++)
		denominator[i] = fqmul(denominator[i], one, qinv, q);
	return failure;
}

int gt32_tile4_baseinv_j1_aos_avx2(gt32_baseinv_j1_aos_e1_t *out,
	const gt32_f0_aos_e0_t *in)
{
	const __m256i q = _mm256_set1_epi16(GT32_TILE4_Q);
	const __m256i qinv = _mm256_set1_epi16(QINV);
	__m256i denominator[12] __attribute__((aligned(32)));

	/* Phase 1: four AoS vectors -> 16 full-width leaves -> numerator/den. */
	for (unsigned block = 0; block < 12; block++) {
		const int16_t *source = in->words + 64U * block;
		int16_t *destination = out->words + 64U * block;
		__m256i a0, a1, a2, a3;
		transpose4(_mm256_load_si256((const __m256i *)(source + 0)),
			_mm256_load_si256((const __m256i *)(source + 16)),
			_mm256_load_si256((const __m256i *)(source + 32)),
			_mm256_load_si256((const __m256i *)(source + 48)),
			&a0, &a1, &a2, &a3);
		const __m256i lambda = _mm256_load_si256((const __m256i *)
			gt32_tile4_lambda_transpose_mont[block]);
		const __m256i lambda_qinv = _mm256_mullo_epi16(lambda, qinv);
		const __m256i a0a0 = fqsqr(a0, q, qinv);
		const __m256i a0a2 = fqmul_auto(a0, a2, q, qinv);
		const __m256i a1a1 = fqsqr(a1, q, qinv);
		const __m256i a1a3 = fqmul_auto(a1, a3, q, qinv);
		const __m256i a2a2 = fqsqr(a2, q, qinv);
		const __m256i a3a3 = fqsqr(a3, q, qinv);
		const __m256i t0_inner = _mm256_sub_epi16(a2a2,
			_mm256_add_epi16(a1a3, a1a3));
		const __m256i t0 = _mm256_add_epi16(a0a0,
			fqmul(t0_inner, lambda, lambda_qinv, q));
		const __m256i t1 = _mm256_sub_epi16(
			_mm256_add_epi16(a1a1, fqmul(a3a3, lambda,
				lambda_qinv, q)), _mm256_add_epi16(a0a2, a0a2));
		const __m256i det = _mm256_sub_epi16(fqsqr(t0, q, qinv),
			fqmul(fqsqr(t1, q, qinv), lambda, lambda_qinv, q));
		denominator[block] = det;

		const __m256i a0t0 = fqmul_auto(a0, t0, q, qinv);
		const __m256i a1t0 = fqmul_auto(a1, t0, q, qinv);
		const __m256i a2t0 = fqmul_auto(a2, t0, q, qinv);
		const __m256i a3t0 = fqmul_auto(a3, t0, q, qinv);
		const __m256i a0t1 = fqmul_auto(a0, t1, q, qinv);
		const __m256i a1t1 = fqmul_auto(a1, t1, q, qinv);
		const __m256i a2t1 = fqmul_auto(a2, t1, q, qinv);
		const __m256i a3t1 = fqmul_auto(a3, t1, q, qinv);
		const __m256i n0 = _mm256_add_epi16(a0t0,
			fqmul(a2t1, lambda, lambda_qinv, q));
		const __m256i n1 = _mm256_sub_epi16(_mm256_setzero_si256(),
			_mm256_add_epi16(fqmul(a3t1, lambda, lambda_qinv, q), a1t0));
		const __m256i n2 = _mm256_add_epi16(a2t0, a0t1);
		const __m256i n3 = _mm256_sub_epi16(_mm256_setzero_si256(),
			_mm256_add_epi16(a1t1, a3t0));
		_mm256_store_si256((__m256i *)(destination + 0), n0);
		_mm256_store_si256((__m256i *)(destination + 16), n1);
		_mm256_store_si256((__m256i *)(destination + 32), n2);
		_mm256_store_si256((__m256i *)(destination + 48), n3);
	}

	const int failure = batch_inverse_j1(denominator, q, qinv);
	const __m256i keep = _mm256_set1_epi16((int16_t)-(failure == 0));
	for (unsigned block = 0; block < 12; block++) {
		int16_t *destination = out->words + 64U * block;
		const __m256i inverse = denominator[block];
		const __m256i inverse_qinv = _mm256_mullo_epi16(inverse, qinv);
		__m256i r0 = fqmul(_mm256_load_si256((const __m256i *)(destination + 0)),
			inverse, inverse_qinv, q);
		__m256i r1 = fqmul(_mm256_load_si256((const __m256i *)(destination + 16)),
			inverse, inverse_qinv, q);
		__m256i r2 = fqmul(_mm256_load_si256((const __m256i *)(destination + 32)),
			inverse, inverse_qinv, q);
		__m256i r3 = fqmul(_mm256_load_si256((const __m256i *)(destination + 48)),
			inverse, inverse_qinv, q);
		__m256i o0, o1, o2, o3;
		transpose4(r0, r1, r2, r3, &o0, &o1, &o2, &o3);
		o0 = center_once(o0, q);
		o1 = center_once(o1, q);
		o2 = center_once(o2, q);
		o3 = center_once(o3, q);
		_mm256_store_si256((__m256i *)(destination + 0),
			_mm256_and_si256(o0, keep));
		_mm256_store_si256((__m256i *)(destination + 16),
			_mm256_and_si256(o1, keep));
		_mm256_store_si256((__m256i *)(destination + 32),
			_mm256_and_si256(o2, keep));
		_mm256_store_si256((__m256i *)(destination + 48),
			_mm256_and_si256(o3, keep));
	}
	return failure;
}

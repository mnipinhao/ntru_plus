#include "tile4_dual_terminal.h"

#include <immintrin.h>

int gt32_sotp_decode_sidecar(uint8_t msg[GT32_SOTP_PLANE_BYTES],
	const gt32_sotp_sidecar_t *sidecar,
	const uint8_t buf[2 * GT32_SOTP_PLANE_BYTES])
{
	const uint8_t *const buf_lo = buf;
	const uint8_t *const buf_hi = buf + GT32_SOTP_PLANE_BYTES;
	__m256i fail = _mm256_setzero_si256();

	for (unsigned offset = 0; offset < GT32_SOTP_PLANE_BYTES;
		offset += 32) {
		const __m256i t1 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(buf_lo + offset));
		const __m256i t2 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(buf_hi + offset));
		const __m256i neg = _mm256_loadu_si256(
			(const __m256i *)(const void *)(sidecar->neg + offset));
		const __m256i nz = _mm256_loadu_si256(
			(const __m256i *)(const void *)(sidecar->nz + offset));
		const __m256i pos = _mm256_xor_si256(nz, neg);
		const __m256i bad_neg = _mm256_andnot_si256(t2, neg);
		const __m256i bad_pos = _mm256_and_si256(t2, pos);
		const __m256i decoded = _mm256_xor_si256(
			_mm256_xor_si256(t1, t2), nz);

		fail = _mm256_or_si256(fail,
			_mm256_or_si256(bad_neg, bad_pos));
		_mm256_storeu_si256((__m256i *)(void *)(msg + offset), decoded);
	}

	const int result = !_mm256_testz_si256(fail, fail);
	const __m256i keep = _mm256_set1_epi8((char)(result - 1));
	for (unsigned offset = 0; offset < GT32_SOTP_PLANE_BYTES;
		offset += 32) {
		__m256i value = _mm256_loadu_si256(
			(const __m256i *)(const void *)(msg + offset));
		value = _mm256_and_si256(value, keep);
		_mm256_storeu_si256((__m256i *)(void *)(msg + offset), value);
	}
	return result;
}

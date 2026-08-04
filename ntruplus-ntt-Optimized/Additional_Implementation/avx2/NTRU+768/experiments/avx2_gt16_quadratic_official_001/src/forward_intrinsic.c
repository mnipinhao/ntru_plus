#include "forward_intrinsic.h"

#include <immintrin.h>
#include <stddef.h>

#include "qbm_intrinsic.h"
#include "quadratic-constants.h"

enum { Q = 3457, CENTER = 1728 };

static const uint8_t bitreverse4[16] = {
    0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15,
};
static const uint8_t split_low_bytes[32] __attribute__((aligned(32))) = {
    0,1,2,3,0,1,2,3, 8,9,10,11,8,9,10,11,
    0,1,2,3,0,1,2,3, 8,9,10,11,8,9,10,11,
};
static const uint8_t split_high_bytes[32] __attribute__((aligned(32))) = {
    4,5,6,7,4,5,6,7, 12,13,14,15,12,13,14,15,
    4,5,6,7,4,5,6,7, 12,13,14,15,12,13,14,15,
};

static int16_t frontend_rows[768] __attribute__((aligned(32)));
static int16_t transform_rows[768] __attribute__((aligned(32)));

static inline __m256i montmul_vector(__m256i x, __m256i mont, __m256i qinv)
{
    const __m256i q = _mm256_set1_epi16(Q);
    const __m256i m = _mm256_mullo_epi16(x, qinv);
    const __m256i high = _mm256_mulhi_epi16(x, mont);
    return _mm256_sub_epi16(high, _mm256_mulhi_epi16(m, q));
}

static inline __m256i montmul16(__m256i x, const int16_t mont[16],
                                const int16_t qinv[16])
{
    return montmul_vector(x,
        _mm256_load_si256((const __m256i *)mont),
        _mm256_load_si256((const __m256i *)qinv));
}

static inline __m256i montmul_scalar(__m256i x, int16_t mont, int16_t qinv)
{
    return montmul_vector(x, _mm256_set1_epi16(mont),
                         _mm256_set1_epi16(qinv));
}

static inline __m256i center_once(__m256i x)
{
    const __m256i q = _mm256_set1_epi16(Q);
    const __m256i center = _mm256_set1_epi16(CENTER);
    const __m256i negative_center = _mm256_set1_epi16(-CENTER);
    __m256i mask = _mm256_cmpgt_epi16(x, center);
    x = _mm256_sub_epi16(x, _mm256_and_si256(mask, q));
    mask = _mm256_cmpgt_epi16(negative_center, x);
    return _mm256_add_epi16(x, _mm256_and_si256(mask, q));
}

static inline __m256i load_quartic4(const int16_t *input)
{
    return _mm256_broadcastq_epi64(_mm_loadl_epi64((const __m128i *)input));
}

static inline __m256i frontend_one(const int16_t in[768], size_t natural)
{
    const __m256i low0 = load_quartic4(in + 4 * natural);
    const __m256i low1 = load_quartic4(in + 4 * (natural + 48));
    const __m256i high0 = load_quartic4(in + 4 * (natural + 96));
    const __m256i high1 = load_quartic4(in + 4 * (natural + 144));
    /* The public forward input is in [-3,4].  Fuse both R2 butterflies and
     * F^-n into four ordinary signed products; the generated per-lane bound
     * proves their raw sum fits int16.  One identity Montgomery reduction
     * then replaces four chained Montgomery multiplications. */
    __m256i sum = _mm256_mullo_epi16(low0,
        _mm256_load_si256((const __m256i *)round4c_forward_linear_c0[natural]));
    sum = _mm256_add_epi16(sum, _mm256_mullo_epi16(low1,
        _mm256_load_si256((const __m256i *)round4c_forward_linear_c1[natural])));
    sum = _mm256_add_epi16(sum, _mm256_mullo_epi16(high0,
        _mm256_load_si256((const __m256i *)round4c_forward_linear_c2[natural])));
    sum = _mm256_add_epi16(sum, _mm256_mullo_epi16(high1,
        _mm256_load_si256((const __m256i *)round4c_forward_linear_c3[natural])));
    return montmul_scalar(sum, round4c_forward_identity_mont,
                          round4c_forward_identity_qinv);
}

void round4c_forward_frontend_intrinsic(int16_t out[768],
                                        const int16_t in[768])
{
    for (size_t i3 = 0; i3 < 3; ++i3) {
        for (size_t i16 = 0; i16 < 16; ++i16) {
            const size_t natural = (16 * i3 + 33 * i16) % 48;
            _mm256_store_si256((__m256i *)(out + 16 * (16 * i3 + i16)),
                               frontend_one(in, natural));
        }
    }
}

static inline void dft3(__m256i x0, __m256i x1, __m256i x2,
                        __m256i output[3], int center_output)
{
    const __m256i t = montmul_scalar(
        _mm256_sub_epi16(x1, x2), round4c_fwd3_omega_mont,
        round4c_fwd3_omega_qinv);
    output[0] = _mm256_add_epi16(_mm256_add_epi16(x0, x1), x2);
    output[1] = _mm256_add_epi16(_mm256_sub_epi16(x0, x2), t);
    output[2] = _mm256_sub_epi16(_mm256_sub_epi16(x0, x1), t);
    if (center_output) {
        output[0] = center_once(output[0]);
        output[1] = center_once(output[1]);
        output[2] = center_once(output[2]);
    }
}

void round4c_forward_dft3_intrinsic(int16_t out[768],
                                    const int16_t in[768], int center_output)
{
    for (size_t position = 0; position < 16; ++position) {
        __m256i output[3];
        dft3(_mm256_load_si256((const __m256i *)(in + 16 * position)),
             _mm256_load_si256((const __m256i *)(in + 16 * (16 + position))),
             _mm256_load_si256((const __m256i *)(in + 16 * (32 + position))),
             output, center_output);
        for (size_t row = 0; row < 3; ++row)
            _mm256_store_si256(
                (__m256i *)(out + 16 * (16 * row + bitreverse4[position])),
                output[row]);
    }
}

static void forward_ntt16_layers(int16_t values[768], size_t last_length)
{
    size_t twiddle_offset = 0;
    for (size_t length = 2; length <= last_length; length *= 2) {
        const size_t half = length / 2;
        for (size_t k3 = 0; k3 < 3; ++k3) {
            const size_t batch = 16 * k3;
            for (size_t start = 0; start < 16; start += length) {
                for (size_t index = 0; index < half; ++index) {
                    const size_t low_vector = batch + start + index;
                    const size_t high_vector = low_vector + half;
                    const __m256i low = _mm256_load_si256(
                        (const __m256i *)(values + 16 * low_vector));
                    __m256i high = _mm256_load_si256(
                        (const __m256i *)(values + 16 * high_vector));
                    if (index != 0)
                        high = montmul_scalar(
                            high,
                            round4c_fwd16_twiddle_mont[twiddle_offset + index],
                            round4c_fwd16_twiddle_qinv[twiddle_offset + index]);
                    __m256i sum = _mm256_add_epi16(low, high);
                    __m256i difference = _mm256_sub_epi16(low, high);
                    if (length == 2 || length == 8) {
                        sum = center_once(sum);
                        difference = center_once(difference);
                    }
                    _mm256_store_si256(
                        (__m256i *)(values + 16 * low_vector), sum);
                    _mm256_store_si256(
                        (__m256i *)(values + 16 * high_vector), difference);
                }
            }
        }
        twiddle_offset += half;
    }
}

void round4c_forward_ntt16_intrinsic(int16_t values[768])
{
    forward_ntt16_layers(values, 16);
}

static inline __m256i split_one(__m256i x, size_t vector)
{
    const __m256i low_mask = _mm256_load_si256(
        (const __m256i *)split_low_bytes);
    const __m256i high_mask = _mm256_load_si256(
        (const __m256i *)split_high_bytes);
    const __m256i low = _mm256_shuffle_epi8(x, low_mask);
    const __m256i high = _mm256_shuffle_epi8(x, high_mask);
    return _mm256_add_epi16(low, montmul16(
        high, round4c_split_mont[vector], round4c_split_qinv[vector]));
}

static void forward_ntt16_fused_split(int16_t out[768], int16_t values[768])
{
    forward_ntt16_layers(values, 8);
    const size_t twiddle_offset = 7;
    for (size_t k3 = 0; k3 < 3; ++k3) {
        const size_t batch = 16 * k3;
        for (size_t index = 0; index < 8; ++index) {
            const size_t low_vector = batch + index;
            const size_t high_vector = low_vector + 8;
            const __m256i low = _mm256_load_si256(
                (const __m256i *)(values + 16 * low_vector));
            __m256i high = _mm256_load_si256(
                (const __m256i *)(values + 16 * high_vector));
            if (index != 0)
                high = montmul_scalar(
                    high, round4c_fwd16_twiddle_mont[twiddle_offset + index],
                    round4c_fwd16_twiddle_qinv[twiddle_offset + index]);
            _mm256_storeu_si256((__m256i *)(out + 16 * low_vector),
                split_one(_mm256_add_epi16(low, high), low_vector));
            _mm256_storeu_si256((__m256i *)(out + 16 * high_vector),
                split_one(_mm256_sub_epi16(low, high), high_vector));
        }
    }
}

static void frontend_dft3_fused(int16_t out[768], const int16_t in[768])
{
    for (size_t i16 = 0; i16 < 16; ++i16) {
        __m256i output[3];
        __m256i input[3];
        for (size_t i3 = 0; i3 < 3; ++i3) {
            const size_t natural = (16 * i3 + 33 * i16) % 48;
            input[i3] = frontend_one(in, natural);
        }
        dft3(input[0], input[1], input[2], output, 1);
        for (size_t k3 = 0; k3 < 3; ++k3)
            _mm256_store_si256(
                (__m256i *)(out + 16 * (16 * k3 + bitreverse4[i16])),
                output[k3]);
    }
}

void round4c_forward_f0_materialized(int16_t out[768], const int16_t in[768])
{
    round4c_forward_frontend_intrinsic(frontend_rows, in);
    round4c_forward_dft3_intrinsic(transform_rows, frontend_rows, 1);
    round4c_forward_ntt16_intrinsic(transform_rows);
    round4c_split_intrinsic(out, transform_rows);
}

void round4c_forward_f0_fused(int16_t out[768], const int16_t in[768])
{
    frontend_dft3_fused(transform_rows, in);
    forward_ntt16_fused_split(out, transform_rows);
}

static void frontend_bitreversed(int16_t out[768], const int16_t in[768])
{
    for (size_t i3 = 0; i3 < 3; ++i3) {
        for (size_t i16 = 0; i16 < 16; ++i16) {
            const size_t natural = (16 * i3 + 33 * i16) % 48;
            _mm256_store_si256(
                (__m256i *)(out + 16 * (16 * i3 + bitreverse4[i16])),
                frontend_one(in, natural));
        }
    }
}

void round4c_forward_f1_materialized(int16_t out[768], const int16_t in[768])
{
    frontend_bitreversed(transform_rows, in);
    round4c_forward_ntt16_intrinsic(transform_rows);
    for (size_t k16 = 0; k16 < 16; ++k16) {
        __m256i output[3];
        dft3(_mm256_load_si256(
                 (const __m256i *)(transform_rows + 16 * k16)),
             _mm256_load_si256(
                 (const __m256i *)(transform_rows + 16 * (16 + k16))),
             _mm256_load_si256(
                 (const __m256i *)(transform_rows + 16 * (32 + k16))),
             output, 0);
        for (size_t k3 = 0; k3 < 3; ++k3)
            _mm256_store_si256(
                (__m256i *)(frontend_rows + 16 * (16 * k3 + k16)),
                output[k3]);
    }
    round4c_split_intrinsic(out, frontend_rows);
}

void round4c_forward_f1_fused(int16_t out[768], const int16_t in[768])
{
    frontend_bitreversed(transform_rows, in);
    round4c_forward_ntt16_intrinsic(transform_rows);
    for (size_t k16 = 0; k16 < 16; ++k16) {
        __m256i output[3];
        dft3(_mm256_load_si256(
                 (const __m256i *)(transform_rows + 16 * k16)),
             _mm256_load_si256(
                 (const __m256i *)(transform_rows + 16 * (16 + k16))),
             _mm256_load_si256(
                 (const __m256i *)(transform_rows + 16 * (32 + k16))),
             output, 0);
        for (size_t k3 = 0; k3 < 3; ++k3) {
            const size_t vector = 16 * k3 + k16;
            _mm256_storeu_si256((__m256i *)(out + 16 * vector),
                                split_one(output[k3], vector));
        }
    }
}

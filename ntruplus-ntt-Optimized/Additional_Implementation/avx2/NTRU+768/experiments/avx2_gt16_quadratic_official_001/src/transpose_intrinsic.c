#include "transpose_intrinsic.h"

#include <immintrin.h>
#include <stddef.h>

static void transpose16(__m256i out[16], const __m256i in[16])
{
    __m256i a[16], b[16], c[16];
    for (size_t i = 0; i < 8; ++i) {
        a[2 * i] = _mm256_unpacklo_epi16(in[2 * i], in[2 * i + 1]);
        a[2 * i + 1] = _mm256_unpackhi_epi16(in[2 * i], in[2 * i + 1]);
    }
    for (size_t group = 0; group < 4; ++group) {
        const size_t i = 4 * group;
        b[i] = _mm256_unpacklo_epi32(a[i], a[i + 2]);
        b[i + 1] = _mm256_unpackhi_epi32(a[i], a[i + 2]);
        b[i + 2] = _mm256_unpacklo_epi32(a[i + 1], a[i + 3]);
        b[i + 3] = _mm256_unpackhi_epi32(a[i + 1], a[i + 3]);
    }
    for (size_t group = 0; group < 2; ++group) {
        const size_t i = 8 * group;
        for (size_t j = 0; j < 4; ++j) {
            c[i + 2 * j] = _mm256_unpacklo_epi64(b[i + j], b[i + j + 4]);
            c[i + 2 * j + 1] = _mm256_unpackhi_epi64(b[i + j], b[i + j + 4]);
        }
    }
    for (size_t i = 0; i < 8; ++i) {
        out[i] = _mm256_permute2x128_si256(c[i], c[i + 8], 0x20);
        out[i + 8] = _mm256_permute2x128_si256(c[i], c[i + 8], 0x31);
    }
}

void round4c_vertical_to_soa(int16_t out[768], const int16_t in[768])
{
    for (size_t k3 = 0; k3 < 3; ++k3) {
        __m256i rows[16], columns[16];
        for (size_t k16 = 0; k16 < 16; ++k16)
            rows[k16] = _mm256_loadu_si256(
                (const __m256i *)(in + 16 * (16 * k3 + k16)));
        transpose16(columns, rows);
        for (size_t branch = 0; branch < 4; ++branch)
            for (size_t degree = 0; degree < 4; ++degree)
                _mm256_storeu_si256(
                    (__m256i *)(out + 16 * ((branch * 3 + k3) * 4 + degree)),
                    columns[4 * branch + degree]);
    }
}

void round4c_soa_to_vertical(int16_t out[768], const int16_t in[768])
{
    for (size_t k3 = 0; k3 < 3; ++k3) {
        __m256i rows[16], columns[16];
        for (size_t branch = 0; branch < 4; ++branch)
            for (size_t degree = 0; degree < 4; ++degree)
                columns[4 * branch + degree] = _mm256_loadu_si256(
                    (const __m256i *)(in + 16 * ((branch * 3 + k3) * 4 + degree)));
        transpose16(rows, columns);
        for (size_t k16 = 0; k16 < 16; ++k16)
            _mm256_storeu_si256(
                (__m256i *)(out + 16 * (16 * k3 + k16)), rows[k16]);
    }
}

#include "lane_ntt16_intrinsic.h"

#include <immintrin.h>
#include <stddef.h>

enum { Q = 3457 };

static const int16_t stage_mont[4][16] __attribute__((aligned(32))) = {
    {-147,-147,-147,-147,-147,-147,-147,-147,
     -147,-147,-147,-147,-147,-147,-147,-147},
    {-147,366,-147,366,-147,366,-147,366,
     -147,366,-147,366,-147,366,-147,366},
    {-147,109,366,-1118,-147,109,366,-1118,
     -147,109,366,-1118,-147,109,366,-1118},
    {-147,-794,109,-446,366,-1339,-1118,1181,
     -147,-794,109,-446,366,-1339,-1118,1181},
};

static const int16_t stage_qinv[4][16] __attribute__((aligned(32))) = {
    {-19,-19,-19,-19,-19,-19,-19,-19,
     -19,-19,-19,-19,-19,-19,-19,-19},
    {-19,13422,-19,13422,-19,13422,-19,13422,
     -19,13422,-19,13422,-19,13422,-19,13422},
    {-19,-32531,13422,28834,-19,-32531,13422,28834,
     -19,-32531,13422,28834,-19,-32531,13422,28834},
    {-19,23526,-32531,834,13422,-10427,28834,-739,
     -19,23526,-32531,834,13422,-10427,28834,-739},
};

static const int16_t high_mask[4][16] __attribute__((aligned(32))) = {
    {0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1,0,-1},
    {0,0,-1,-1,0,0,-1,-1,0,0,-1,-1,0,0,-1,-1},
    {0,0,0,0,-1,-1,-1,-1,0,0,0,0,-1,-1,-1,-1},
    {0,0,0,0,0,0,0,0,-1,-1,-1,-1,-1,-1,-1,-1},
};

static const uint8_t swap_words[32] __attribute__((aligned(32))) = {
    2,3,0,1,6,7,4,5,10,11,8,9,14,15,12,13,
    2,3,0,1,6,7,4,5,10,11,8,9,14,15,12,13,
};

static inline __m256i montmul(__m256i x, __m256i mont, __m256i qinv)
{
    const __m256i q = _mm256_set1_epi16(Q);
    const __m256i m = _mm256_mullo_epi16(x, qinv);
    const __m256i high = _mm256_mulhi_epi16(x, mont);
    return _mm256_sub_epi16(high, _mm256_mulhi_epi16(m, q));
}

static inline __m256i partner(__m256i x, size_t stage)
{
    switch (stage) {
    case 0:
        return _mm256_shuffle_epi8(
            x, _mm256_load_si256((const __m256i *)swap_words));
    case 1:
        return _mm256_shuffle_epi32(x, 0xb1);
    case 2:
        return _mm256_permute4x64_epi64(x, 0xb1);
    default:
        return _mm256_permute2x128_si256(x, x, 0x01);
    }
}

static inline __m256i lane_stage(__m256i x, size_t stage)
{
    const __m256i mask = _mm256_load_si256(
        (const __m256i *)high_mask[stage]);
    const __m256i paired = partner(x, stage);
    if (stage == 0) {
        const __m256i sum = _mm256_add_epi16(x, paired);
        const __m256i difference = _mm256_sub_epi16(paired, x);
        return _mm256_blendv_epi8(sum, difference, mask);
    }
    const __m256i low = _mm256_blendv_epi8(x, paired, mask);
    __m256i high = _mm256_blendv_epi8(paired, x, mask);
    high = montmul(high,
        _mm256_load_si256((const __m256i *)stage_mont[stage]),
        _mm256_load_si256((const __m256i *)stage_qinv[stage]));
    const __m256i sum = _mm256_add_epi16(low, high);
    const __m256i difference = _mm256_sub_epi16(low, high);
    return _mm256_blendv_epi8(sum, difference, mask);
}

static inline __m256i center10(__m256i x)
{
    const __m256i estimate = _mm256_mulhrs_epi16(
        x, _mm256_set1_epi16(10));
    return _mm256_sub_epi16(
        x, _mm256_mullo_epi16(estimate, _mm256_set1_epi16(Q)));
}

static inline __m256i lane_ntt16(__m256i x)
{
    x = lane_stage(x, 0);
    x = lane_stage(x, 1);
    x = lane_stage(x, 2);
    x = center10(x);
    return lane_stage(x, 3);
}

void round4c_lane_ntt16_x1(int16_t out[16], const int16_t in[16])
{
    _mm256_store_si256((__m256i *)out,
        lane_ntt16(_mm256_load_si256((const __m256i *)in)));
}

static inline void lane_ntt16_x3(int16_t out[48], const int16_t in[48])
{
    __m256i x0 = _mm256_load_si256((const __m256i *)(in + 0));
    __m256i x1 = _mm256_load_si256((const __m256i *)(in + 16));
    __m256i x2 = _mm256_load_si256((const __m256i *)(in + 32));
    for (size_t stage = 0; stage < 3; ++stage) {
        x0 = lane_stage(x0, stage);
        x1 = lane_stage(x1, stage);
        x2 = lane_stage(x2, stage);
    }
    x0 = center10(x0);
    x1 = center10(x1);
    x2 = center10(x2);
    x0 = lane_stage(x0, 3);
    x1 = lane_stage(x1, 3);
    x2 = lane_stage(x2, 3);
    _mm256_store_si256((__m256i *)(out + 0), x0);
    _mm256_store_si256((__m256i *)(out + 16), x1);
    _mm256_store_si256((__m256i *)(out + 32), x2);
}

void round4c_lane_ntt16_x3(int16_t out[48], const int16_t in[48])
{
    lane_ntt16_x3(out, in);
}

void round4c_lane_ntt16_batch_x1(int16_t out[768], const int16_t in[768])
{
    for (size_t transform = 0; transform < 48; ++transform) {
        const __m256i x = _mm256_load_si256(
            (const __m256i *)(in + 16 * transform));
        _mm256_store_si256((__m256i *)(out + 16 * transform),
                           lane_ntt16(x));
    }
}

void round4c_lane_ntt16_batch_x3(int16_t out[768], const int16_t in[768])
{
    for (size_t tile = 0; tile < 16; ++tile)
        lane_ntt16_x3(out + 48 * tile, in + 48 * tile);
}

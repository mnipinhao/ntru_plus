/*
 * SCRATCH (exploratory only, not a candidate): direct 12-bit codec kernels for
 * the Official NTRU+768 / NTRU+1152 AVX2 8-way layout, written with intrinsics
 * for the decision-gate measurement in docs/ntruplus768-1152-direct-codec.md.
 * Layout: in 128-coefficient block b, register r (bytes 32r..32r+31), word l
 * holds wire coefficient 128b + 8l + r.  Wire group l (12 bytes, coefficients
 * 8l..8l+7) therefore sits in word l of all eight registers.
 *
 *   codec8_scratch_tobytes_pack  freeze (Barrett + 2-op) -> Official dense shift
 *       pack (3 words per 4 coefficients) -> vpunpck{l,h}wd -> 7-op in-lane dword
 *       interleave per half -> 16 x 16-byte stores at 12*group, ascending
 *       (each spills 4 bytes the next store overwrites; last group 8+4 bytes).
 *   codec8_scratch_tobytes_madd  exp002-literal: vpunpck{l,h}wd + vpmaddwd(1,4096)
 *       -> 4x4 dword transpose -> vpshufb (drop 4th byte) -> same stores.
 *   codec8_scratch_frombytes     16-byte loads at 12*group (xmm + vinserti128)
 *       -> vpshufb to raw 16-bit words -> 8x8 word transpose -> and 0xfff /
 *       srl 4 -> vpmaxuw accumulator, one compare at the end.
 * Contract as NTRU+864 exp002: 32-byte aligned poly, byte array unaligned, no
 * overlap between them; nothing is read or written outside the poly/wire bytes.
 */
#include <immintrin.h>
#include <stdint.h>
#include "params.h"

#define NB (NTRUPLUS_N / 128)
typedef struct { int16_t coeffs[NTRUPLUS_N]; } __attribute__((aligned(32))) spoly;
void codec8_scratch_tobytes_pack(uint8_t *out, const spoly *a);
void codec8_scratch_tobytes_madd(uint8_t *out, const spoly *a);
int codec8_scratch_frombytes(spoly *r, const uint8_t *in);

static inline __m256i freeze(__m256i x, __m256i v, __m256i q) {
    __m256i t = _mm256_mulhrs_epi16(x, v);
    t = _mm256_mullo_epi16(t, q);
    x = _mm256_sub_epi16(x, t);
    t = _mm256_add_epi16(x, q);
    return _mm256_min_epu16(x, t);
}

#define ST(p, x) _mm_storeu_si128((__m128i *)(p), (x))

void codec8_scratch_tobytes_pack(uint8_t *out, const spoly *a) {
    const __m256i v = _mm256_set1_epi16(9), q = _mm256_set1_epi16(NTRUPLUS_Q);
    const __m256i *in = (const __m256i *)a->coeffs;
    for (int b = 0; b < NB; b++, in += 8, out += 192) {
        __m256i R[8];
        for (int r = 0; r < 8; r++) R[r] = freeze(_mm256_load_si256(in + r), v, q);
        __m256i A0 = _mm256_xor_si256(R[0], _mm256_slli_epi16(R[1], 12));
        __m256i A1 = _mm256_xor_si256(_mm256_srli_epi16(R[1], 4), _mm256_slli_epi16(R[2], 8));
        __m256i A2 = _mm256_xor_si256(_mm256_srli_epi16(R[2], 8), _mm256_slli_epi16(R[3], 4));
        __m256i B0 = _mm256_xor_si256(R[4], _mm256_slli_epi16(R[5], 12));
        __m256i B1 = _mm256_xor_si256(_mm256_srli_epi16(R[5], 4), _mm256_slli_epi16(R[6], 8));
        __m256i B2 = _mm256_xor_si256(_mm256_srli_epi16(R[6], 8), _mm256_slli_epi16(R[7], 4));
        __m256i X[2] = {_mm256_unpacklo_epi16(A0, A1), _mm256_unpackhi_epi16(A0, A1)};
        __m256i Y[2] = {_mm256_unpacklo_epi16(A2, B0), _mm256_unpackhi_epi16(A2, B0)};
        __m256i Z[2] = {_mm256_unpacklo_epi16(B1, B2), _mm256_unpackhi_epi16(B1, B2)};
        __m256i O[2][4];
        for (int h = 0; h < 2; h++) {
            __m256i XYl = _mm256_unpacklo_epi32(X[h], Y[h]);
            __m256i XYh = _mm256_unpackhi_epi32(X[h], Y[h]);
            __m256i Zs = _mm256_srli_si256(Z[h], 4);
            O[h][0] = _mm256_unpacklo_epi64(XYl, Z[h]);
            O[h][1] = _mm256_alignr_epi8(Zs, XYl, 8);
            O[h][2] = _mm256_blend_epi32(XYh, Z[h], 0x44);
            O[h][3] = _mm256_unpackhi_epi64(XYh, Zs);
        }
        /* group l: lane0 l=4h+j, lane1 l=8+4h+j; ascending store order */
        for (int h = 0; h < 2; h++)
            for (int j = 0; j < 4; j++) ST(out + 12 * (4 * h + j), _mm256_castsi256_si128(O[h][j]));
        for (int h = 0; h < 2; h++)
            for (int j = 0; j < 4; j++) {
                __m128i hi = _mm256_extracti128_si256(O[h][j], 1);
                uint8_t *p = out + 12 * (8 + 4 * h + j);
                if (b == NB - 1 && h == 1 && j == 3) {
                    _mm_storel_epi64((__m128i *)p, hi);
                    *(int32_t *)(p + 8) = _mm_extract_epi32(hi, 2);
                } else
                    ST(p, hi);
            }
    }
}

void codec8_scratch_tobytes_madd(uint8_t *out, const spoly *a) {
    const __m256i v = _mm256_set1_epi16(9), q = _mm256_set1_epi16(NTRUPLUS_Q);
    const __m256i k = _mm256_set1_epi32(1 | (4096 << 16));
    const __m256i sh = _mm256_setr_epi8(0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, -1, -1, -1, -1,
                                        0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, -1, -1, -1, -1);
    const __m256i *in = (const __m256i *)a->coeffs;
    for (int b = 0; b < NB; b++, in += 8, out += 192) {
        __m256i R[8], O[2][4];
        for (int r = 0; r < 8; r++) R[r] = freeze(_mm256_load_si256(in + r), v, q);
        for (int h = 0; h < 2; h++) {
            __m256i D[4];
            for (int s2 = 0; s2 < 4; s2++)
                D[s2] = _mm256_madd_epi16(h ? _mm256_unpackhi_epi16(R[2 * s2], R[2 * s2 + 1])
                                            : _mm256_unpacklo_epi16(R[2 * s2], R[2 * s2 + 1]), k);
            __m256i t0 = _mm256_unpacklo_epi32(D[0], D[1]), t1 = _mm256_unpackhi_epi32(D[0], D[1]);
            __m256i t2 = _mm256_unpacklo_epi32(D[2], D[3]), t3 = _mm256_unpackhi_epi32(D[2], D[3]);
            O[h][0] = _mm256_shuffle_epi8(_mm256_unpacklo_epi64(t0, t2), sh);
            O[h][1] = _mm256_shuffle_epi8(_mm256_unpackhi_epi64(t0, t2), sh);
            O[h][2] = _mm256_shuffle_epi8(_mm256_unpacklo_epi64(t1, t3), sh);
            O[h][3] = _mm256_shuffle_epi8(_mm256_unpackhi_epi64(t1, t3), sh);
        }
        for (int h = 0; h < 2; h++)
            for (int j = 0; j < 4; j++) ST(out + 12 * (4 * h + j), _mm256_castsi256_si128(O[h][j]));
        for (int h = 0; h < 2; h++)
            for (int j = 0; j < 4; j++) {
                __m128i hi = _mm256_extracti128_si256(O[h][j], 1);
                uint8_t *p = out + 12 * (8 + 4 * h + j);
                if (b == NB - 1 && h == 1 && j == 3) {
                    _mm_storel_epi64((__m128i *)p, hi);
                    *(int32_t *)(p + 8) = _mm_extract_epi32(hi, 2);
                } else
                    ST(p, hi);
            }
    }
}

static inline __m256i ld2(const uint8_t *p0, const uint8_t *p1) {
    return _mm256_inserti128_si256(_mm256_castsi128_si256(_mm_loadu_si128((const __m128i *)p0)),
                                   _mm_loadu_si128((const __m128i *)p1), 1);
}

int codec8_scratch_frombytes(spoly *r, const uint8_t *in) {
    const __m256i m = _mm256_setr_epi8(0, 1, 1, 2, 3, 4, 4, 5, 6, 7, 7, 8, 9, 10, 10, 11,
                                       0, 1, 1, 2, 3, 4, 4, 5, 6, 7, 7, 8, 9, 10, 10, 11);
    const __m256i mlast = _mm256_setr_epi8(0, 1, 1, 2, 3, 4, 4, 5, 6, 7, 7, 8, 9, 10, 10, 11,
                                           4, 5, 5, 6, 7, 8, 8, 9, 10, 11, 11, 12, 13, 14, 14, 15);
    const __m256i low = _mm256_set1_epi16(0x0fff);
    __m256i acc = _mm256_setzero_si256();
    __m256i *o = (__m256i *)r->coeffs;
    for (int b = 0; b < NB; b++, in += 192, o += 8) {
        __m256i Q[8];
        for (int l = 0; l < 8; l++) {
            int last = (b == NB - 1 && l == 7);
            Q[l] = ld2(in + 12 * l, in + 12 * (l + 8) - (last ? 4 : 0));
            Q[l] = _mm256_shuffle_epi8(Q[l], last ? mlast : m);
        }
        /* 8x8 word transpose per lane: rows l (words r) -> R_r (words l) */
        __m256i s1[8], s2[8], R[8];
        for (int k = 0; k < 4; k++) {
            s1[2 * k] = _mm256_unpacklo_epi16(Q[2 * k], Q[2 * k + 1]);
            s1[2 * k + 1] = _mm256_unpackhi_epi16(Q[2 * k], Q[2 * k + 1]);
        }
        /* s1[2k]: dwords (l=2k,2k+1) for r=0..3; s1[2k+1]: r=4..7 */
        for (int k = 0; k < 2; k++)
            for (int hh = 0; hh < 2; hh++) {
                __m256i a0 = s1[4 * k + hh], a1 = s1[4 * k + 2 + hh];
                s2[4 * k + 2 * hh] = _mm256_unpacklo_epi32(a0, a1);     /* r=4hh+0,1 ; l=4k..4k+3 */
                s2[4 * k + 2 * hh + 1] = _mm256_unpackhi_epi32(a0, a1); /* r=4hh+2,3 */
            }
        for (int t = 0; t < 4; t++) {
            __m256i a0 = s2[t], a1 = s2[4 + t];
            int rb = (t >> 1) * 4 + (t & 1) * 2;
            R[rb] = _mm256_unpacklo_epi64(a0, a1);
            R[rb + 1] = _mm256_unpackhi_epi64(a0, a1);
        }
        for (int k = 0; k < 8; k++) {
            R[k] = (k & 1) ? _mm256_srli_epi16(R[k], 4) : _mm256_and_si256(R[k], low);
            acc = _mm256_max_epu16(acc, R[k]);
            _mm256_store_si256(o + k, R[k]);
        }
    }
    __m256i gt = _mm256_cmpgt_epi16(acc, _mm256_set1_epi16(NTRUPLUS_Q - 1));
    return _mm256_movemask_epi8(gt) != 0;
}

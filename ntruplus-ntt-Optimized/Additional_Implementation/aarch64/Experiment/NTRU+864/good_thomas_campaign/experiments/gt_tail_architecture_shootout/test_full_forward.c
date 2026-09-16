#include "gt864_fr0_to_official_map.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define N 864
#define Q 3457

extern void poly_ntt(int16_t *, const int16_t *);
extern void gt864_forward_poly_ntt_all_one_mul_b3(int16_t *, const int16_t *);
extern void gt864_forward_poly_ntt_a1_t1(int16_t *, const int16_t *);
extern void gt864_forward_poly_ntt_a1_t2(int16_t *, const int16_t *);
extern void gt864_top_split_ld3(int16_t *, const int16_t *);
extern void gt864_tail_layout_bank_major_inplace(int16_t *, const int16_t *);
extern void gt864_tail_t2_six_bank_simd(int16_t *, const int16_t *);
extern void gt864_one_bank_a1_t0(int16_t *, const int16_t *);
extern void gt864_one_bank_a1_t1(int16_t *, const int16_t *);
extern void gt864_one_bank_a1_t2(int16_t *, const int16_t *);
extern void gt864_forward_six_bank_pass2_a1_t0(int16_t *, const int16_t *);
extern void gt864_forward_six_bank_pass2_a1_t1(int16_t *, const int16_t *);
extern void gt864_forward_six_bank_pass2_a1_t2(int16_t *, const int16_t *);

static uint32_t rng = 0xa1f011U;

static uint32_t random_u32(void)
{
    rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
    return rng;
}

static int centered(int value)
{
    value %= Q;
    if (value < 0) value += Q;
    if (value > Q / 2) value -= Q;
    return value;
}

static int match(const int16_t official[N], const int16_t candidate[N],
                 const char *name)
{
    for (int i = 0; i < N; ++i)
        if (centered(official[i]) !=
            centered(candidate[gt864_fr0_for_official[i]])) {
            fprintf(stderr, "%s mismatch at official %d\n", name, i);
            return 0;
        }
    return 1;
}

int main(void)
{
    int16_t input[N], official[N], t0[N], t1[N], t2[N];
    int16_t p0[896], p1[896], p2[896], one0[144], one1[144], one2[144];
    for (int trial = 0; trial < 48; ++trial) {
        for (int i = 0; i < N; ++i)
            input[i] = trial < 8 ? (int16_t)(i == trial ? 1 : 0) :
                       (int16_t)((int)(random_u32() % Q) - 1728);
        poly_ntt(official, input);
        gt864_top_split_ld3(p0, input);
        memcpy(p1, p0, sizeof(p0));
        memcpy(p2, p0, sizeof(p0));
        gt864_tail_layout_bank_major_inplace(p1 + 768, p1 + 768);
        gt864_tail_t2_six_bank_simd(p2 + 768, p2 + 768);
        gt864_one_bank_a1_t0(one0, p0);
        gt864_one_bank_a1_t1(one1, p1);
        gt864_one_bank_a1_t2(one2, p2);
        for (int i = 0; i < 144; ++i)
            if (centered(one0[i]) != centered(one1[i]) ||
                centered(one0[i]) != centered(one2[i])) {
                fprintf(stderr, "one mismatch trial=%d i=%d values=%d/%d/%d\n",
                        trial, i, one0[i], one1[i], one2[i]);
                return 1;
            }
        gt864_forward_six_bank_pass2_a1_t0(t0, p0);
        gt864_forward_six_bank_pass2_a1_t1(t1, p1);
        gt864_forward_six_bank_pass2_a1_t2(t2, p2);
        for (int i = 0; i < N; ++i)
            if (centered(t0[i]) != centered(t1[i]) ||
                centered(t0[i]) != centered(t2[i])) {
                fprintf(stderr, "six mismatch trial=%d i=%d values=%d/%d/%d\n",
                        trial, i, t0[i], t1[i], t2[i]);
                return 1;
            }
        gt864_forward_poly_ntt_all_one_mul_b3(t0, input);
        gt864_forward_poly_ntt_a1_t1(t1, input);
        gt864_forward_poly_ntt_a1_t2(t2, input);
        if (!match(official, t0, "T0") || !match(official, t1, "T1") ||
            !match(official, t2, "T2")) return 1;
    }
    puts("a1_full_forward_correctness=pass");
    puts("cases_per_variant_and_boundary=48");
    puts("modq_mismatches=0");
    return 0;
}

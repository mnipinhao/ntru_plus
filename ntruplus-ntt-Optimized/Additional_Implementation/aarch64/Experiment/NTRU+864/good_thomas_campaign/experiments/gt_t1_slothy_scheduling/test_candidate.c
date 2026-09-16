#include "gt864_fr0_to_official_map.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define N 864
#define Q 3457

extern void poly_ntt(int16_t *, const int16_t *);
extern void gt864_top_split_ld3(int16_t *, const int16_t *);
extern void gt864_tail_layout_bank_major_inplace(int16_t *, const int16_t *);
extern void gt864_one_bank_a1_t1(int16_t *, const int16_t *);
extern void gt864_one_bank_a1_t1_slothy(int16_t *, const int16_t *);
extern void gt864_forward_six_bank_pass2_a1_t1(int16_t *, const int16_t *);
extern void gt864_forward_six_bank_pass2_a1_t1_slothy(int16_t *, const int16_t *);
extern void gt864_forward_poly_ntt_a1_t1(int16_t *, const int16_t *);
extern void gt864_forward_poly_ntt_a1_t1_slothy(int16_t *, const int16_t *);

static uint32_t rng = 0x51a7a001U;
static uint32_t random_u32(void) { rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; return rng; }
static int centered(int x) { x %= Q; if (x < 0) x += Q; return x > Q / 2 ? x - Q : x; }

static int equal_modq(const int16_t *a, const int16_t *b, int n, const char *tag)
{
    for (int i = 0; i < n; ++i)
        if (centered(a[i]) != centered(b[i])) {
            fprintf(stderr, "%s mismatch i=%d values=%d/%d\n", tag, i, a[i], b[i]);
            return 0;
        }
    return 1;
}

int main(void)
{
    int16_t input[N], official[N], baseline[N], candidate[N];
    int16_t p8[896], one0[144], one1[144];
    for (int trial = 0; trial < 64; ++trial) {
        for (int i = 0; i < N; ++i)
            input[i] = trial < 16 ? (int16_t)(i == trial ? 1 : 0) :
                       (int16_t)((int)(random_u32() % Q) - 1728);
        gt864_top_split_ld3(p8, input);
        gt864_tail_layout_bank_major_inplace(p8 + 768, p8 + 768);
        gt864_one_bank_a1_t1(one0, p8);
        gt864_one_bank_a1_t1_slothy(one1, p8);
        if (!equal_modq(one0, one1, 144, "one-bank")) return 1;
        gt864_forward_six_bank_pass2_a1_t1(baseline, p8);
        gt864_forward_six_bank_pass2_a1_t1_slothy(candidate, p8);
        if (!equal_modq(baseline, candidate, N, "six-bank")) return 1;
        poly_ntt(official, input);
        gt864_forward_poly_ntt_a1_t1_slothy(candidate, input);
        for (int i = 0; i < N; ++i)
            if (centered(official[i]) != centered(candidate[gt864_fr0_for_official[i]])) {
                fprintf(stderr, "full mismatch official=%d\n", i); return 1;
            }
    }
    puts("a1_t1_slothy_correctness=pass");
    puts("one_bank_cases=64,six_bank_cases=64,full_official_cases=64");
    return 0;
}

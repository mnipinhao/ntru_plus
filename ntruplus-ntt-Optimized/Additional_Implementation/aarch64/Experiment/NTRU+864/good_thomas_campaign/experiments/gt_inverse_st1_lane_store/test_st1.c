#include "../gt_fr0_inverse_asm_realization/gt864_fr0_inverse_asm.h"
#include "../gt_fr0_inverse_consumer/gt864_fr0_inverse.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define Q 3457
#define BOUND 2205

void gt864_fr0_inverse_finish_st1(int16_t out[864], const int16_t in[896]);

static uint32_t rng = 0xa216U;

static uint32_t random_u32(void)
{
    rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
    return rng;
}

static int congruent(int16_t a, int16_t b)
{
    return ((int)a - (int)b) % Q == 0;
}

static int check(const int16_t fr0[864], const char *label)
{
    int16_t p8[896] = {0};
    int16_t baseline[880], candidate[880], reference[864];
    for (int i = 0; i < 880; ++i)
        baseline[i] = candidate[i] = (int16_t)0x5a5a;
    gt864_fr0_inverse_ntt9_asm(p8, fr0);
    gt864_fr0_inverse_finish_neon(reference, p8);
    gt864_fr0_inverse_finish_asm(baseline + 8, p8);
    gt864_fr0_inverse_finish_st1(candidate + 8, p8);
    for (int i = 0; i < 864; ++i) {
        if (baseline[i + 8] != candidate[i + 8] ||
            !congruent(reference[i], candidate[i + 8])) {
            fprintf(stderr, "%s mismatch i=%d ref/base/st1=%d/%d/%d\n",
                    label, i, reference[i], baseline[i + 8], candidate[i + 8]);
            return 1;
        }
    }
    for (int i = 0; i < 8; ++i)
        if (baseline[i] != (int16_t)0x5a5a || candidate[i] != (int16_t)0x5a5a ||
            baseline[872 + i] != (int16_t)0x5a5a ||
            candidate[872 + i] != (int16_t)0x5a5a) {
            fprintf(stderr, "%s sentinel overwrite i=%d\n", label, i);
            return 1;
        }
    return 0;
}

int main(void)
{
    int16_t fr0[864];
    static const int16_t edges[] = {-BOUND, BOUND, -1, 0, 1};
    int cases = 0;
    for (unsigned e = 0; e < sizeof(edges) / sizeof(edges[0]); ++e) {
        for (int i = 0; i < 864; ++i) fr0[i] = edges[e];
        if (check(fr0, "edge")) return 1;
        ++cases;
    }
    for (int impulse = 0; impulse < 12; ++impulse) {
        static const int positions[] = {0,7,8,23,24,431,432,575,576,839,862,863};
        memset(fr0, 0, sizeof(fr0));
        fr0[positions[impulse]] = impulse & 1 ? -BOUND : BOUND;
        if (check(fr0, "impulse")) return 1;
        ++cases;
    }
    for (int trial = 0; trial < 64; ++trial) {
        for (int i = 0; i < 864; ++i)
            fr0[i] = (int16_t)((int)(random_u32() % (2 * BOUND + 1)) - BOUND);
        if (check(fr0, "random")) return 1;
        ++cases;
    }
    printf("a2_st1_correctness=pass\ncases=%d\nexact_baseline_mismatches=0\n", cases);
    puts("reference_modq_mismatches=0\nsentinel_writes=0\nproduction_linked=0");
    return 0;
}

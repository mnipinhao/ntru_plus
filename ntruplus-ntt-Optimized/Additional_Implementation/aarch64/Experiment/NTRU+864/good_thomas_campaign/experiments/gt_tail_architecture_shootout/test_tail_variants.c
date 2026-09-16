#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define Q 3457

extern void gt864_tail_t0_current(int16_t *, const int16_t *);
extern void gt864_tail_t1_bank_major(int16_t *, const int16_t *);
extern void gt864_tail_t2_six_bank_simd(int16_t *, const int16_t *);

static uint32_t rng = 0xa1864U;

static uint32_t random_u32(void)
{
    rng ^= rng << 13;
    rng ^= rng >> 17;
    rng ^= rng << 5;
    return rng;
}

static int centered(int value)
{
    value %= Q;
    if (value < 0)
        value += Q;
    if (value > Q / 2)
        value -= Q;
    return value;
}

static void to_bank_major(int16_t bank[96], const int16_t column[128])
{
    for (int b = 0; b < 6; ++b)
        for (int t = 0; t < 16; ++t)
            bank[16 * b + t] = column[8 * t + b];
}

static int compare(const int16_t a[96], const int16_t b[96],
                   const char *name, int exact)
{
    for (int i = 0; i < 96; ++i) {
        if ((exact && a[i] != b[i]) || (!exact && centered(a[i]) != centered(b[i]))) {
            fprintf(stderr, "%s mismatch at %d: %d != %d\n", name, i,
                    a[i], b[i]);
            return 1;
        }
    }
    return 0;
}

int main(void)
{
    int16_t column[128] __attribute__((aligned(64)));
    int16_t bank[96] __attribute__((aligned(64)));
    int16_t t0[96] __attribute__((aligned(64)));
    int16_t t1[96] __attribute__((aligned(64)));
    int16_t t2[96] __attribute__((aligned(64)));
    int cases = 0;

    for (int trial = 0; trial < 80; ++trial) {
        memset(column, 0, sizeof(column));
        for (int t = 0; t < 16; ++t)
            for (int b = 0; b < 6; ++b) {
                int value;
                if (trial < 16)
                    value = t == trial ? b + 1 : 0;
                else if (trial < 22)
                    value = b == trial - 16 ? t + 1 : 0;
                else
                    value = (int)(random_u32() % Q) - 1728;
                column[8 * t + b] = (int16_t)value;
            }
        to_bank_major(bank, column);
        gt864_tail_t0_current(t0, column);
        gt864_tail_t1_bank_major(t1, bank);
        gt864_tail_t2_six_bank_simd(t2, column);
        if (compare(t0, t1, "T0/T1 exact", 1) ||
            compare(t0, t2, "T0/T2 mod-q", 0))
            return 1;
        ++cases;
    }
    printf("a1_tail_correctness=pass\n");
    printf("cases=%d\n", cases);
    printf("t0_t1_exact_mismatches=0\n");
    printf("t0_t2_modq_mismatches=0\n");
    return 0;
}

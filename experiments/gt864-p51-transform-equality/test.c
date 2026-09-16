#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define N 864
#define Q 3457

int gt864_fr0_equal_modq_asm(const int16_t a[N], const int16_t b[N]);

static uint64_t state = UINT64_C(0x50353154455354);
static uint32_t next32(void) {
    state ^= state << 7;
    state ^= state >> 9;
    return (uint32_t)state;
}

static int reference(const int16_t a[N], const int16_t b[N]) {
    uint32_t mismatch = 0;
    for (unsigned i = 0; i < N; ++i) {
        int32_t d = (int32_t)a[i] - b[i];
        mismatch |= (uint32_t)(d % Q != 0);
    }
    return (int)(mismatch != 0);
}

static int check(const int16_t a[N], const int16_t b[N]) {
    int expected = reference(a, b);
    int actual = gt864_fr0_equal_modq_asm(a, b);
    return actual == expected ? 0 : 1;
}

int main(void) {
    _Alignas(16) int16_t a[N], b[N], saved_a[N], saved_b[N];
    static const int16_t edges[] = {
        -27822, -27656, -6914, -3457, -1, 0, 1, 3457, 6914, 27656, 27817
    };

    for (unsigned trial = 0; trial < 4096; ++trial) {
        for (unsigned i = 0; i < N; ++i) {
            b[i] = (int16_t)((int32_t)(next32() % 6047) - 3023);
            int32_t lo = b[i] - 27822;
            int32_t hi = b[i] + 27817;
            (void)lo; (void)hi;
            a[i] = (int16_t)((int32_t)(next32() % 49594) - 24799);
        }
        memcpy(saved_a, a, sizeof a);
        memcpy(saved_b, b, sizeof b);
        if (check(a, b)) return 1;
        if (memcmp(a, saved_a, sizeof a) || memcmp(b, saved_b, sizeof b)) return 2;

        /* Construct an equal representation using an in-range q multiple. */
        for (unsigned i = 0; i < N; ++i) {
            b[i] = (int16_t)((int32_t)(next32() % 6047) - 3023);
            int k = (int)(next32() % 15) - 7;
            int32_t value = (int32_t)b[i] + k * Q;
            while (value < -24799) value += Q;
            while (value > 24794) value -= Q;
            a[i] = (int16_t)value;
        }
        if (check(a, b) || gt864_fr0_equal_modq_asm(a, a)) return 3;
        unsigned index = next32() % N;
        a[index] = (int16_t)(a[index] == 24794 ? a[index] - 1 : a[index] + 1);
        if (reference(a, b) != 1 || gt864_fr0_equal_modq_asm(a, b) != 1) return 4;
    }

    for (unsigned i = 0; i < sizeof edges / sizeof edges[0]; ++i) {
        memset(a, 0, sizeof a); memset(b, 0, sizeof b);
        a[i] = edges[i];
        if (check(a, b)) return 5;
    }
    puts("P51 native differential passed: 4096 random/equal pairs, alias, immutability, and range edges");
    return 0;
}

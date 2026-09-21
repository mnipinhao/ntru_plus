#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { N = 768 };
typedef struct __attribute__((aligned(32))) { int16_t c[N]; } polynomial;

void poly_basemul(polynomial *, const polynomial *, const polynomial *);
void poly_add(polynomial *, const polynomial *, const polynomial *);
void ntruplus768_officialopt_basemul_add(polynomial *, const polynomial *,
    const polynomial *, const polynomial *);
void ntruplus768_officialopt_dup_basemul(polynomial *, const polynomial *,
    const polynomial *);
void ntruplus768_officialopt_shared_basemul(polynomial *, const polynomial *,
    const polynomial *);
void ntruplus768_officialopt_shared_add(polynomial *, const polynomial *,
    const polynomial *, const polynomial *);

static uint64_t state = UINT64_C(0x7680ff1c1a10ab3d);
static uint32_t random32(void) {
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    return (uint32_t)state;
}

int main(void) {
    polynomial h, r, m, h_copy, r_copy, m_copy, control, plain, dup;
    struct { uint64_t before; polynomial fused; uint64_t after; } guarded;
    for (unsigned trial = 0; trial < 10003; trial++) {
        guarded.before = UINT64_C(0x4c4a9d2b75cc801e);
        guarded.after = UINT64_C(0x721aa09943f8702d);
        for (unsigned i = 0; i < N; i++) {
            h.c[i] = (int16_t)((int)(random32() % 3457U));
            r.c[i] = (int16_t)((int)(random32() % 20001U) - 10000);
            m.c[i] = (int16_t)((int)(random32() % 20001U) - 10000);
        }
        if (trial < 4) {
            memset(&h, 0, sizeof h);
            memset(&r, 0, sizeof r);
            memset(&m, 0, sizeof m);
            if (trial == 1) h.c[0] = r.c[0] = m.c[0] = 1;
            if (trial == 2) h.c[N - 1] = 3456, r.c[N - 1] = -1, m.c[N - 1] = -1;
            if (trial == 3) for (unsigned i = 0; i < N; i++)
                h.c[i] = 3456, r.c[i] = 10000, m.c[i] = -10000;
        }
        memcpy(&h_copy, &h, sizeof h);
        memcpy(&r_copy, &r, sizeof r);
        memcpy(&m_copy, &m, sizeof m);
        poly_basemul(&control, &h, &r);
        ntruplus768_officialopt_shared_basemul(&plain, &h, &r);
        ntruplus768_officialopt_dup_basemul(&dup, &h, &r);
        if (memcmp(&plain, &control, sizeof plain) ||
            memcmp(&dup, &control, sizeof dup)) {
            fprintf(stderr, "shared/duplicated plain BaseMul mismatch at %u\n", trial);
            return 1;
        }
        poly_add(&control, &control, &m);
        ntruplus768_officialopt_basemul_add(&guarded.fused, &h, &r, &m);
        if (memcmp(&control, &guarded.fused, sizeof control) ||
            memcmp(&h, &h_copy, sizeof h) ||
            memcmp(&r, &r_copy, sizeof r) ||
            memcmp(&m, &m_copy, sizeof m) ||
            guarded.before != UINT64_C(0x4c4a9d2b75cc801e) ||
            guarded.after != UINT64_C(0x721aa09943f8702d)) {
            fprintf(stderr, "fused BaseMul raw differential failed at %u\n", trial);
            return 1;
        }
        ntruplus768_officialopt_shared_add(&guarded.fused, &h, &r, &m);
        if (memcmp(&control, &guarded.fused, sizeof control) ||
            guarded.before != UINT64_C(0x4c4a9d2b75cc801e) ||
            guarded.after != UINT64_C(0x721aa09943f8702d)) {
            fprintf(stderr, "shared fused BaseMul mismatch at %u\n", trial);
            return 1;
        }
    }
    puts("Official BaseMul + add-m raw differential: pass (10003 cases)");
    return 0;
}

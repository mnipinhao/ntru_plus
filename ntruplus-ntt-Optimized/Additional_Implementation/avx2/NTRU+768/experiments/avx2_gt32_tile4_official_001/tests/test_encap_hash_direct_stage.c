#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#include "fips202.h"
#include "symmetric.h"
#include "util.h"

enum { N = 768, WIRE = 1152, OUT = 192, STAGE = 1153, PAD = 64 };
void ntruplus768_pack_m_lazy10788_avx2(uint8_t *, const int16_t *);
void ntruplus768_ntt_frontend_avx2(int16_t *, const int16_t *);
void ntruplus768_ntt_m_avx2(int16_t *, const int16_t *);

static uint64_t seed = UINT64_C(0x76820260922);
static uint32_t rnd(void) {
    seed ^= seed << 13;
    seed ^= seed >> 7;
    seed ^= seed << 17;
    return (uint32_t)seed;
}

/* Test-only realization.  This relocates the existing hash_g data buffer;
 * it does not specialize the serializer, SHAKE, or Forward implementation. */
static void direct_stage(uint8_t out[OUT], uint8_t data[STAGE], const int16_t *r) {
    data[0] = 0x01;
    ntruplus768_pack_m_lazy10788_avx2(data + 1, r);
    shake256(out, OUT, data, STAGE);
    secure_clear(data, STAGE);
}

static void check(const int16_t r[N], unsigned offset) {
    _Alignas(64) int16_t before[N];
    _Alignas(64) uint8_t backing[PAD + 32 + STAGE + PAD];
    uint8_t baseline[WIRE], bytes[WIRE], got[OUT + 2 * PAD];
    uint8_t *data = backing + PAD + offset;
    memcpy(before, r, sizeof before);
    memset(backing, 0xa5, sizeof backing);
    memset(got, 0x5a, sizeof got);
    ntruplus768_pack_m_lazy10788_avx2(baseline, r);
    memcpy(bytes, baseline, sizeof bytes);
    hash_g(baseline, baseline); /* Match the real caller's input/output alias. */
    data[0] = 1;
    ntruplus768_pack_m_lazy10788_avx2(data + 1, r);
    assert(data[0] == 1 && memcmp(data + 1, bytes, WIRE) == 0);
    direct_stage(got + PAD, data, r);
    assert(memcmp(got + PAD, baseline, OUT) == 0);
    assert(memcmp(before, r, sizeof before) == 0);
    for (size_t i = 0; i < sizeof backing; ++i) {
        int inside = i >= PAD + offset && i < PAD + offset + STAGE;
        assert(backing[i] == (inside ? 0 : 0xa5));
    }
    for (size_t i = 0; i < sizeof got; ++i)
        if (i < PAD || i >= PAD + OUT) assert(got[i] == 0x5a);
}

int main(void) {
    _Alignas(64) int16_t r[N], coeff[N], front[N];
    unsigned cases = 0;
    for (unsigned i = 0; i < 10003; ++i) {
        for (unsigned j = 0; j < N; ++j)
            r[j] = (int16_t)((int)(rnd() % 31185) - 15592);
        check(r, i % 32);
        ++cases;
    }
    const int boundaries[] = {-15592, -3457, -1728, -1, 0, 1, 1728, 3456, 15592};
    for (unsigned b = 0; b < sizeof boundaries / sizeof boundaries[0]; ++b)
        for (unsigned offset = 0; offset < 32; ++offset) {
            for (unsigned j = 0; j < N; ++j)
                r[j] = (int16_t)(j % 2 ? boundaries[b] : -boundaries[b]);
            check(r, offset);
            ++cases;
        }
    for (unsigned i = 0; i < 100; ++i) {
        for (unsigned j = 0; j < N; ++j)
            coeff[j] = (int16_t)((int)(rnd() % 3) - 1);
        ntruplus768_ntt_frontend_avx2(front, coeff);
        ntruplus768_ntt_m_avx2(r, front);
        check(r, i % 32);
        ++cases;
    }
    long page = sysconf(_SC_PAGESIZE);
    assert(page > STAGE);
    uint8_t *mem = mmap(NULL, (size_t)page * 2, PROT_READ | PROT_WRITE,
                        MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    assert(mem != MAP_FAILED);
    assert(mprotect(mem + page, (size_t)page, PROT_NONE) == 0);
    uint8_t expected[WIRE], got[OUT];
    ntruplus768_pack_m_lazy10788_avx2(expected, r);
    hash_g(expected, expected);
    direct_stage(got, mem + page - STAGE, r);
    assert(memcmp(got, expected, OUT) == 0);
    assert(munmap(mem, (size_t)page * 2) == 0);
    printf("{\"cases\":%u,\"actual_ternary_forward_cases\":100,"
           "\"alignment_offsets\":32,\"wire_and_hash_exact\":true,"
           "\"r_immutable\":true,\"stage_wiped\":true,"
           "\"canary\":true,\"guard_page\":true,"
           "\"timing\":false,\"full_kem_kat\":false}\n", cases);
    return 0;
}

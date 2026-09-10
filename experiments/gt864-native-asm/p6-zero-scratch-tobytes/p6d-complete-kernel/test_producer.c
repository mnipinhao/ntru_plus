#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../../../../ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/p3b1_tables.h"

extern void gt864_p6d_pair0_oracle(const int16_t *, const uint8_t *, uint8_t *)
    __asm("gt864_p6d_pair0_oracle");
extern void gt864_p6d_pair1_oracle(const int16_t *, const uint8_t *, uint8_t *)
    __asm("gt864_p6d_pair1_oracle");
extern void byte_pair_block(uint8_t *, const int16_t *, const int16_t *, const void *, const void *);

static uint32_t state = 0x50364431u;
static uint32_t rng32(void) {
    uint32_t x = state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    return state = x;
}

static void make_tables(uint8_t table[368]) {
    static const uint8_t idx0[16] = {0,16,32,1,17,33,2,18,34,3,19,35,4,20,36,5};
    static const uint8_t idx1[16] = {21,37,6,22,38,7,23,39,255,255,255,255,255,255,255,255};
    int16_t q[8], recip[8];
    memset(table, 0, 368);
    memcpy(table, p3b1_prefix, sizeof(p3b1_prefix));
    memcpy(table + 160, p3b1_a_fwd, sizeof(p3b1_a_fwd));
    memcpy(table + 304, idx0, 16);
    memcpy(table + 320, idx1, 16);
    for (int i = 0; i < 8; i++) q[i] = 3457, recip[i] = 9;
    memcpy(table + 336, q, 16);
    memcpy(table + 352, recip, 16);
}

static int check(const int16_t coeffs[864], const uint8_t table[368]) {
    _Alignas(16) uint8_t ref0[216], ref1[216], got0[216], got1[432], dense[432];
    byte_pair_block(ref0, coeffs, coeffs + 8, p3b1_prefix, p3b1_a_fwd);
    byte_pair_block(ref1, coeffs + 16, coeffs + 216, p3b1_prefix, p3b1_a_fwd);
    for (int row = 0; row < 9; row++) {
        memcpy(dense + 48 * row, ref0 + 24 * row, 24);
        memcpy(dense + 48 * row + 24, ref1 + 24 * row, 24);
    }
    memset(got0, 0xa5, sizeof(got0));
    gt864_p6d_pair0_oracle(coeffs, table, got0);
    if (memcmp(got0, ref0, sizeof(got0))) return 1;
    memset(got1, 0xa5, sizeof(got1));
    memcpy(got1, got0, sizeof(got0));
    gt864_p6d_pair1_oracle(coeffs, table, got1);
    if (memcmp(got1, dense, sizeof(got1))) return 2;
    return 0;
}

int main(void) {
    _Alignas(16) int16_t coeffs[864];
    _Alignas(16) uint8_t table[368];
    unsigned cases = 0;
    make_tables(table);
    static const int16_t edge[] = {-32768, -3458, -3457, -3456, -1, 0, 1, 3456, 3457, 3458, 32767};
    for (unsigned e = 0; e < sizeof(edge) / sizeof(edge[0]); e++) {
        for (int i = 0; i < 864; i++) coeffs[i] = edge[(e + i) % (sizeof(edge) / sizeof(edge[0]))];
        int rc = check(coeffs, table);
        if (rc) return fprintf(stderr, "edge mismatch case=%u stage=%d\n", e, rc), 1;
        cases++;
    }
    for (unsigned trial = 0; trial < 4096; trial++) {
        for (int i = 0; i < 864; i++) coeffs[i] = (int16_t)rng32();
        int rc = check(coeffs, table);
        if (rc) return fprintf(stderr, "random mismatch case=%u stage=%d\n", trial, rc), 1;
        cases++;
    }
    printf("PASS producer_cases=%u pair0_bytes=216 pair1_dense_bytes=432\n", cases);
    return 0;
}

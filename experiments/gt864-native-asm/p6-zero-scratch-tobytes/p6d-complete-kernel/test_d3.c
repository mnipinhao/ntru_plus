#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "../../../../ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/p3b1_tables.h"
#include "../../../../ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/byte_merge_tables.h"

extern void candidate(uint8_t *, const int16_t *) __asm("gt864_p6d3_full_asm");
extern void candidate_small(uint8_t *, const int16_t *) __asm("gt864_p6d3_small_asm");
extern void gt864_tobytes_full_asm(uint8_t *, const int16_t *, const void *, const void *, const void *);
extern void gt864_tobytes_small_asm(uint8_t *, const int16_t *, const void *, const void *, const void *);

static uint32_t state = 0x50364433u;
static uint32_t rng32(void) {
    uint32_t x = state; x ^= x << 13; x ^= x >> 17; x ^= x << 5; return state = x;
}

static int check(const int16_t in[864]) {
    _Alignas(16) uint8_t a[1328], b[1328];
    memset(a, 0xa5, sizeof(a)); memset(b, 0x5a, sizeof(b));
    gt864_tobytes_full_asm(a + 16, in, p3b1_prefix, p3b1_a_fwd, gt864_byte_merge_indices);
    candidate(b + 16, in);
    if (memcmp(a + 16, b + 16, 1296)) return 1;
    for (int i = 0; i < 16; i++) if (a[i] != 0xa5 || a[1312+i] != 0xa5 || b[i] != 0x5a || b[1312+i] != 0x5a) return 2;
    return 0;
}

static int check_small(const int16_t in[864]) {
    _Alignas(16) uint8_t a[1328], b[1328];
    memset(a, 0xa5, sizeof(a)); memset(b, 0x5a, sizeof(b));
    gt864_tobytes_small_asm(a + 16, in, p3b1_prefix, p3b1_a_fwd, gt864_byte_merge_indices);
    candidate_small(b + 16, in);
    if (memcmp(a + 16, b + 16, 1296)) return 1;
    for (int i = 0; i < 16; i++) if (a[i] != 0xa5 || a[1312+i] != 0xa5 || b[i] != 0x5a || b[1312+i] != 0x5a) return 2;
    return 0;
}

int main(void) {
    _Alignas(16) int16_t in[864];
    static const int16_t edge[] = {-32768,-3458,-3457,-3456,-1,0,1,3456,3457,3458,32767};
    unsigned cases = 0;
    for (unsigned e = 0; e < sizeof(edge)/sizeof(edge[0]); e++) {
        for (int i = 0; i < 864; i++) in[i] = edge[(i+e) % (sizeof(edge)/sizeof(edge[0]))];
        int rc = check(in); if (rc) return fprintf(stderr,"edge mismatch %u kind %d\n",e,rc),1; cases++;
    }
    for (unsigned t = 0; t < 4096; t++) {
        for (int i = 0; i < 864; i++) in[i] = (int16_t)rng32();
        int rc = check(in); if (rc) return fprintf(stderr,"random mismatch %u kind %d\n",t,rc),1; cases++;
    }
    unsigned small_cases = 0;
    for (unsigned t = 0; t < 4096; t++) {
        for (int i = 0; i < 864; i++) in[i] = (int16_t)((int)(rng32() % 6913) - 3456);
        int rc = check_small(in); if (rc) return fprintf(stderr,"small mismatch %u kind %d\n",t,rc),1; small_cases++;
    }
    printf("PASS full_cases=%u small_cases=%u bytes_per_case=1296 canaries=PASS\n", cases, small_cases);
    return 0;
}

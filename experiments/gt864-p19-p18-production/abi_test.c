#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef void (*tobytes_fn)(uint8_t *, const int16_t *);
int p19_probe(tobytes_fn, uint8_t *, const int16_t *);
void gt864_p18_tobytes_full_asm(uint8_t *, const int16_t *);
void gt864_p18_tobytes_small_asm(uint8_t *, const int16_t *);

static int check(tobytes_fn fn) {
    int16_t input[864], copy[864];
    uint8_t guarded[1328];
    for (unsigned i = 0; i < 864; i++) input[i] = (int16_t)((i * 97u) % 3457u);
    memcpy(copy, input, sizeof input);
    memset(guarded, 0xa5, sizeof guarded);
    if (p19_probe(fn, guarded + 16, input)) return 1;
    if (memcmp(input, copy, sizeof input)) return 2;
    for (unsigned i = 0; i < 16; i++)
        if (guarded[i] != 0xa5 || guarded[1312 + i] != 0xa5) return 3;
    return 0;
}

int main(void) {
    int full = check(gt864_p18_tobytes_full_asm);
    int small = check(gt864_p18_tobytes_small_asm);
    if (full || small) {
        fprintf(stderr, "P19 ABI/cleanup failure full=%d small=%d\n", full, small);
        return 1;
    }
    puts("P19 AAPCS/SIMD-cleanup/input-immutability/canary pass");
    return 0;
}
